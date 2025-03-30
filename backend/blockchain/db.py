import asyncpg
import os
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/blockchain_db")

class Database:
    def __init__(self):
        self.pool: asyncpg.Pool | None = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(DATABASE_URL)
        print("[DB] Connection established")

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def drop_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("DROP TABLE IF EXISTS transactions")
            await conn.execute("DROP TABLE IF EXISTS wallets")
            print("[DB] Dropped all tables.")

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS wallets (
                    address TEXT PRIMARY KEY,
                    balance REAL
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    sender TEXT,
                    recipient TEXT,
                    amount REAL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("[DB] Created tables.")

       # await self.init_wallets()

    async def init_wallets(self):
        async with self.pool.acquire() as conn:
            await conn.execute("INSERT INTO wallets (address, balance) VALUES ('UserA', 100)")
            await conn.execute("INSERT INTO wallets (address, balance) VALUES ('UserB', 100)")
            print("[DB] Wallets initialized.")

    async def save_transaction(self, tx: dict):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO transactions (sender, recipient, amount)
                VALUES ($1, $2, $3)
            """, tx["sender"], tx["recipient"], tx["amount"])
            await self._update_wallet_balances(conn, tx["sender"], tx["recipient"], tx["amount"])
        print("[DB] Transaction saved")

    async def _update_wallet_balances(self, conn, sender, recipient, amount):
        await conn.execute("""
            UPDATE wallets SET balance = balance - $1 WHERE address = $2
        """, amount, sender)
        await conn.execute("""
            UPDATE wallets SET balance = balance + $1 WHERE address = $2
        """, amount, recipient)
        print("[DB] Updated wallet balance")

    async def get_wallet_balance(self, address: str):
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("SELECT balance FROM wallets WHERE address = $1", address)
            return result["balance"] if result else -5

    async def get_transaction_history(self, address: str):
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM transactions
                WHERE sender = $1 OR recipient = $1
                ORDER BY timestamp DESC
            """, address)
            return [dict(row) for row in rows]
