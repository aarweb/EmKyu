import asyncio

from trades.bybit import BybitTrade
from trades.kraken import KrakenTrade
from trades.client import BrokerClient
from trades.binance import BinanceTrade

from orderbook.binance import BinanceOrderBook
from orderbook.bybit import BybitOrderBook
from orderbook.kraken import KrakenOrderBook
from scrapper_queue.producer import ScrapperProducer


async def main():

    await ScrapperProducer.start()

    brokers: list[BrokerClient] = [
        BybitTrade.create(),
        BinanceTrade.create(),
        KrakenTrade.create(),
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
        await ScrapperProducer.stop()


asyncio.run(main())
