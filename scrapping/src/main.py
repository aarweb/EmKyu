import asyncio

from broker.binance import BinanceBroker
from broker.bybit import BybitBroker
from broker.client import BrokerClient
from broker.kraken import KrakenBroker
from quee.producer import SCRAPPER_PRODUCER


async def main():

    await SCRAPPER_PRODUCER.start()

    brokers: list[BrokerClient] = [
        BybitBroker.create(),
        BinanceBroker.create(),
        KrakenBroker.create(),
    ]
    _ = await asyncio.gather(*[b.connect() for b in brokers])

    try:
        while True:
            _ = await asyncio.gather(*[b.onListen() for b in brokers])
    except KeyboardInterrupt:
        _ = await asyncio.gather(*[b.close() for b in brokers])
        await SCRAPPER_PRODUCER.stop()


asyncio.run(main())
