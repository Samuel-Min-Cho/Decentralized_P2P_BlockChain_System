import asyncio, asyncpg
import os, time
import sys
from pydantic import BaseModel


# Add project root to sys.path
sys.path.append("/app")

from blockchain import Blockchain
from kafka_service import kafka_consumer
from proto import grpc_server
from proto import grpc_client
from db import Database

# === CONFIGURATION (from docker-compose env only) ===
NODE_ID = os.environ["NODE_ID"]
GRPC_PORT = int(os.environ["GRPC_PORT"])
PEER_ADDRESS = os.environ["PEER_ADDRESS"]
KAFKA_BOOTSTRAP = os.environ["KAFKA_BOOTSTRAP"]

blockchain = Blockchain()
db = Database()

# === BLOCK PROCESSING HANDLER ===
async def handle_block(block):
    for tx in block.transactions:
        await db.save_transaction(tx)
    await grpc_client.send_block_to_peer(PEER_ADDRESS, block)
    print(f"[{NODE_ID}] Created block {block.index} and sent to {PEER_ADDRESS}", flush=True)

async def wait_for_wallets_initialized(retries=30, delay=2):
    print(f"[{NODE_ID}] Waiting for wallets to be fully initialized...", flush=True)

    for attempt in range(retries):
        try:
            conn = await asyncpg.connect(
                user="postgres",
                password="password",
                database="blockchain_db",
                host="postgres"
            )

            # Fetch both balances
            rows = await conn.fetch("""
                SELECT address, balance FROM wallets
                WHERE address IN ('UserA', 'UserB')
            """)
            await conn.close()

            wallet_map = {row['address']: row['balance'] for row in rows}

            if wallet_map.get('UserA') == 100 and wallet_map.get('UserB') == 100:
                print(f"[{NODE_ID}] Wallets are fully initialized.", flush=True)
                return
            else:
                print(f"[{NODE_ID}] Found wallets: {wallet_map} — waiting...", flush=True)

        except Exception as e:
            print(f"[{NODE_ID}] Wallet check failed ({e})", flush=True)

        await asyncio.sleep(delay)

    raise RuntimeError(f"[{NODE_ID}] Timeout waiting for wallet initialization (UserA & UserB with 100)")



async def main():
    print(f"starting node {NODE_ID}", flush=True)

    await wait_for_wallets_initialized()

    await db.connect()
    print(f"[{NODE_ID}] Connected to database", flush=True)

    await asyncio.gather(
        grpc_server.serve(blockchain, GRPC_PORT),
        kafka_consumer.start_kafka_consumer(
            blockchain=blockchain,
            bootstrap_servers=KAFKA_BOOTSTRAP,
            group_id=NODE_ID,
            block_callback=handle_block,
            node_id=NODE_ID
        )
    )

if __name__ == "__main__":
    asyncio.run(main())
