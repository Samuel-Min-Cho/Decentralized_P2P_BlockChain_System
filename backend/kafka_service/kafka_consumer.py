import json
import asyncio
from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaConnectionError

TOPIC = "transactions"

async def start_kafka_consumer(
    blockchain,
    bootstrap_servers,
    group_id,
    block_callback,
    node_id,
    retries=10,
    delay=3
):
    for attempt in range(1, retries + 1):
        try:
            consumer = AIOKafkaConsumer(
                TOPIC,
                bootstrap_servers=bootstrap_servers,
                group_id=group_id,
                value_deserializer=lambda m: json.loads(m.decode())
            )
            await consumer.start()
            print(f"[{node_id}] Kafka consumer started", flush=True)
            break  # Exit retry loop once connected
        except KafkaConnectionError as e:
            print(f"[{node_id}] Kafka not ready, retry {attempt}/{retries}... ({e})", flush=True)
            await asyncio.sleep(delay)
    else:
        raise RuntimeError(f"[{node_id}] Failed to connect to Kafka after {retries} retries.")

    try:
        async for msg in consumer:
            tx = msg.value

            if tx.get("processor") != node_id:
                print(f"[{node_id}] Ignoring tx assigned to {tx.get('processor')}", flush=True)
                continue

            blockchain.add_transaction(tx)
            block = blockchain.create_block()
            await block_callback(block)

    finally:
        await consumer.stop()
        print(f"[{node_id}] Kafka consumer stopped", flush=True)
