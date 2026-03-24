import asyncio

from broker.bybit import BybitBroker
from broker.kraken import KrakenBroker
from broker.client import BrokerClient
from broker.binance import BinanceBroker


async def main():

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


asyncio.run(main())
