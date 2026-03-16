import asyncio

from broker.broker_client import BrokerClient
from broker.bybit import BybitBroker


async def main():

    brokers: list[BrokerClient] = [BybitBroker.create()]

    _ = await asyncio.gather(*[b.connect() for b in brokers])

    try:
        while True:
            _ = await asyncio.gather(*[b.onListen() for b in brokers])
    except:
        _ = await asyncio.gather(*[b.close() for b in brokers])


asyncio.run(main())
