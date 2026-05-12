import json

from aiokafka import AIOKafkaProducer

from env.kafka import KAFKA_URL
from env.topic import ORDERBOOK_TOPIC, TRAIT_TOPIC
from orderbook.mapper.model.order_book import TSOrderBook
from trades.mapper.model.time_series_cripto import TSTrade

SCRAPPER_PRODUCER: AIOKafkaProducer | None = None


class ScrapperProducer:
    @staticmethod
    def _producer() -> AIOKafkaProducer:
        if SCRAPPER_PRODUCER is None:
            raise RuntimeError("ScrapperProducer not started — call start() first")
        return SCRAPPER_PRODUCER

    @staticmethod
    async def sendTrade(trade: TSTrade):
        await ScrapperProducer._producer().send(TRAIT_TOPIC, trade)

    @staticmethod
    async def sendOrderbook(orderbook: TSOrderBook):
        await ScrapperProducer._producer().send(ORDERBOOK_TOPIC, orderbook)

    @staticmethod
    async def start():
        global SCRAPPER_PRODUCER
        SCRAPPER_PRODUCER = AIOKafkaProducer(
            bootstrap_servers=KAFKA_URL,
            value_serializer=lambda v: json.dumps(
                v, default=lambda o: o.__dict__
            ).encode("utf-8"),
        )
        await SCRAPPER_PRODUCER.start()

    @staticmethod
    async def stop():
        await SCRAPPER_PRODUCER.stop()
