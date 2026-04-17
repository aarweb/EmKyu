from aiokafka import AIOKafkaProducer

from env.kafka import KAFKA_URL
from env.topic import ORDERBOOK_TOPIC, TRAIT_TOPIC
from orderbook.mapper.model.order_book import TSOrderBook
from trades.mapper.model.time_series_cripto import TSTrade

SCRAPPER_PRODUCER = AIOKafkaProducer(bootstrap_servers=KAFKA_URL)


class ScrapperProducer:

    @staticmethod
    async def sendTrait(trait: TSTrade):
        await SCRAPPER_PRODUCER.send(TRAIT_TOPIC, trait)

    @staticmethod
    async def sendOrderbook(orderbook: TSOrderBook):
        await SCRAPPER_PRODUCER.send(ORDERBOOK_TOPIC, orderbook)
