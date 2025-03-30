import time
import hashlib
import json

class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None, hash=None):
        self.index = index
        self.timestamp = timestamp if timestamp is not None else time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        # hash is always explicitly passed or calculated after all attributes are set
        self.hash = hash if hash is not None else self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            'index': self.index,
            'timestamp': self.timestamp,
            'transactions': self.transactions,
            'previous_hash': self.previous_hash
        }
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        genesis = Block(
            index=0,
            transactions=[],
            previous_hash="0",
            timestamp=0
        )
        # Ensure consistent hash across all nodes
        genesis.hash = genesis.calculate_hash()
        return genesis

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def reset_chain(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_block(self):
        new_block = Block(
            index=len(self.chain),
            transactions=self.pending_transactions,
            previous_hash=self.get_latest_block().hash
        )
        self.chain.append(new_block)
        self.pending_transactions = []
        return new_block

    def add_block_from_peer(self, block_dict):
        new_block = Block(
            index=block_dict["index"],
            transactions=block_dict["transactions"],
            previous_hash=block_dict["previous_hash"],
            timestamp=block_dict["timestamp"],
            hash=block_dict["hash"]
        )

        if self.validate_new_block(new_block, self.get_latest_block()):
            self.chain.append(new_block)
            print (f"[BC] {self.chain}")
            return True
        return False

    def validate_new_block(self, new_block, previous_block):
        if previous_block.index + 1 != new_block.index:
            return False
        if previous_block.hash != new_block.previous_hash:
            return False
        if new_block.hash != new_block.calculate_hash():
            return False
        return True

    def get_full_chain(self):
        return self.chain

    def __repr__(self):
        return json.dumps([{
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': block.transactions,
            'previous_hash': block.previous_hash,
            'hash': block.hash
        } for block in self.chain], indent=2)

