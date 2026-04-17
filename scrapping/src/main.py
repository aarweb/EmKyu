import asyncio

from trades.bybit import BybitBroker
from trades.kraken import KrakenBroker
from trades.client import BrokerClient
from trades.binance import BinanceBroker
from orderbook.binance import BinanceOrderBook
from orderbook.bybit import BybitOrderBook
from orderbook.kraken import KrakenOrderBook
from queue.producer import SCRAPPER_PRODUCER


async def main():

    await SCRAPPER_PRODUCER.start()

    brokers: list[BrokerClient] = [
        BybitBroker.create(),
        BinanceBroker.create(),
        KrakenBroker.create(),
        BybitOrderBook.create(),
        BinanceOrderBook.create(),
        KrakenOrderBook.create(),
    ]
    _ = await asyncio.gather(*[b.connect() for b in brokers])

    try:
        while True:
            _ = await asyncio.gather(*[b.onListen() for b in brokers])
    except KeyboardInterrupt:
        _ = await asyncio.gather(*[b.close() for b in brokers])
        await SCRAPPER_PRODUCER.stop()


asyncio.run(main())
