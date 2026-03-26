from aiokafka import AIOKafkaProducer

from env.kafka import KAFKA_URL
from env.topic import ORDERBOOK_TOPIC, TRAIT_TOPIC

SCRAPPER_PRODUCER = AIOKafkaProducer(bootstrap_servers=KAFKA_URL)


class ScrapperProducer:

    @staticmethod
    async def sendTrait(trait: TSTrait):
        await SCRAPPER_PRODUCER.send(TRAIT_TOPIC, trait)

    @staticmethod
    async def sendOrderbook(orderbook: TSOrderBook):
        await SCRAPPER_PRODUCER.send(ORDERBOOK_TOPIC, orderbook)
