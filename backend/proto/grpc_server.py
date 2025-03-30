# blockchain/grpc_server.py

import grpc
from concurrent import futures
import asyncio
import json

from proto import blockchain_pb2 as pb2
from proto import blockchain_pb2_grpc as pb2_grpc


class BlockchainService(pb2_grpc.BlockchainServiceServicer):
    def __init__(self, blockchain_instance):
        self.blockchain = blockchain_instance

    async def ResetChain(self, request, context):
        self.blockchain.reset_chain()
        print(f"[gRPC] Blockchain reset to genesis block", flush=True)
        return pb2.Response(status="ok")

    async def Ping(self, request, context):
        return pb2.Response(status="alive")

    async def BroadcastBlock(self, request, context):
        print(f"[gRPC] Received block via broadcast: {request.index}")
        block_dict = {
            "index": request.index,
            "timestamp": request.timestamp,
            "previous_hash": request.previous_hash,
            "hash": request.hash,
            "transactions": json.loads(request.transactions)
        }
        result = self.blockchain.add_block_from_peer(block_dict)
        print(f"[{self.blockchain.get_latest_block().index}] current head after BroadcastBlock")
        return pb2.Response(status="ok" if result else "rejected")

    async def RequestChain(self, request, context):
        chain = self.blockchain.get_full_chain()
        blocks = []
        for b in chain:
            blocks.append(pb2.Block(
                index=b.index,
                timestamp=b.timestamp,
                previous_hash=b.previous_hash,
                hash=b.hash,
                transactions=json.dumps(b.transactions)
            ))
        return pb2.Chain(blocks=blocks)

async def serve(blockchain, port):
    server = grpc.aio.server()
    pb2_grpc.add_BlockchainServiceServicer_to_server(
        BlockchainService(blockchain), server
    )
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    print(f"gRPC server running on port {port}")
    await server.wait_for_termination()
