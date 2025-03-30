import uvicorn, random, subprocess, asyncio, json, time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager

from fastapi.middleware.cors import CORSMiddleware

from kafka_service.kafka_producer import KafkaTxProducer
from blockchain.db import Database

from proto import blockchain_pb2_grpc, blockchain_pb2
import grpc

KAFKA_BOOTSTRAP = "kafka_service:9092"

producer = KafkaTxProducer(KAFKA_BOOTSTRAP)
db = Database()


async def safe_start_producer(retries=10, delay=3):
    for attempt in range(retries):
        try:
            await producer.start()
            await asyncio.sleep(1)
            print("[Kafka] Producer connected ", flush=True)
            return
        except Exception as e:
            print(f"[Kafka] Retry {attempt + 1}/{retries} — not ready yet: {e}")
            await asyncio.sleep(delay)
    raise RuntimeError("[Kafka] Failed to connect to Kafka after retries")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # === Startup ===
    await db.connect()
    await db.create_tables()
    await db.init_wallets()
    print("[SERVER] DB connected", flush=True)

    await safe_start_producer()
    print("[SERVER] Kafka producer is ready", flush=True)

    app.state.first_transaction_processed = False  # 👈 Add this line


    yield  # App runs while inside this block

    # === Shutdown ===
    await producer.stop()
    await db.disconnect()
    print("[SERVER] Clean shutdown.")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Transaction(BaseModel):
    sender: str
    recipient: str
    amount: float


async def get_chain_via_grpc(address):
    async with grpc.aio.insecure_channel(address) as channel:
        stub = blockchain_pb2_grpc.BlockchainServiceStub(channel)
        try:
            response = await stub.RequestChain(blockchain_pb2.Empty())
            return [
                {
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "previous_hash": block.previous_hash,
                    "hash": block.hash,
                    "transactions": block.transactions,
                }
                for block in response.blocks
            ]
        except Exception as e:
            return f"Failed to reach {address}: {str(e)}"

@app.post("/reset")
async def reset_blockchain():
    try:
        # Reset DB: Drop and recreate tables and wallets
        await db.drop_tables()
        await db.create_tables()
        await db.init_wallets()

        # Notify both nodes to reset their blockchains
        for node in ["node1:50051", "node2:50052"]:
            async with grpc.aio.insecure_channel(node) as channel:
                stub = blockchain_pb2_grpc.BlockchainServiceStub(channel)
                await stub.ResetChain(blockchain_pb2.Empty())

        return {"status": "Blockchain and database reset to initial state."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transaction")
async def send_transaction(tx: Transaction):
    tx_data = tx.model_dump()
    tx_data["processor"] = random.choice(["node1", "node2"])
    tx_json = json.dumps(tx_data)

    try:
        await producer.send(tx_data)

        if not app.state.first_transaction_processed:
            assigned_node = tx_data["processor"]
            peer_address = f"{assigned_node}:50051" if assigned_node == "node1" else "node2:50052"

            timeout = 10
            interval = 1
            start = time.time()

            while time.time() - start < timeout:
                chain = await get_chain_via_grpc(peer_address)
                if any(tx_json in block["transactions"] for block in chain):
                    break
                await asyncio.sleep(interval)

            app.state.first_transaction_processed = True

        # === Get updated data
        sender_balance = await db.get_wallet_balance(tx_data["sender"])
        recipient_balance = await db.get_wallet_balance(tx_data["recipient"])
        node1_chain = await get_chain_via_grpc("node1:50051")
        node2_chain = await get_chain_via_grpc("node2:50052")

        result = {
            "status": f"Transaction assigned to {tx_data['processor']}",
            "sender": {"address": tx_data["sender"], "balance": sender_balance},
            "recipient": {"address": tx_data["recipient"], "balance": recipient_balance},
            "blockchains": {
                "node1": node1_chain,
                "node2": node2_chain
            }
        }

        print(json.dumps(result, indent=2))
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# if __name__ == "__main__":
#     uvicorn.run("server:app", host="0.0.0.0", port=8000)
