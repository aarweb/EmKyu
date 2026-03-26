import asyncio

from trades.client import BrokerClient
from orderbook.binance import BinanceOrderBook
from orderbook.bybit import BybitOrderBook
from orderbook.kraken import KrakenOrderBook


async def main():

    brokers: list[BrokerClient] = [
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


asyncio.run(main())
