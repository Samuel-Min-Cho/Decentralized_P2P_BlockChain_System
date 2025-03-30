import asyncio
import grpc
import json
from proto import blockchain_pb2 as pb2
from proto import blockchain_pb2_grpc as pb2_grpc



async def wait_for_peer_ready(stub, retries=5, delay=1):
    for _ in range(retries):
        try:
            response = await stub.Ping(pb2.Empty())
            if response.status == "alive":
                return True
        except grpc.aio.AioRpcError:
            await asyncio.sleep(delay)
    return False

async def send_block_to_peer(peer_address, block):
    print(f"[gRPC Client] Sending block {block.index} to {peer_address}")
    async with grpc.aio.insecure_channel(peer_address) as channel:
        stub = pb2_grpc.BlockchainServiceStub(channel)
        block_proto = pb2.Block(
            index=block.index,
            timestamp=block.timestamp,
            previous_hash=block.previous_hash,
            hash=block.hash,
            transactions=json.dumps(block.transactions)
        )
        response = await stub.BroadcastBlock(block_proto)
        print(f"[gRPC Client] Received response: {response.status}")
        return response.status

