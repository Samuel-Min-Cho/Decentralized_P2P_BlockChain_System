from aiokafka import AIOKafkaProducer
import json

TOPIC = "transactions"

class KafkaTxProducer:
    def __init__(self, bootstrap_servers="kafka_service:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def send(self, tx: dict):
        if not self.producer:
            return
        await self.producer.send_and_wait(TOPIC, json.dumps(tx).encode())
