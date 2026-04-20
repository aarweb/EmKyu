import json
from typing import override

import websockets
from websockets.asyncio.client import connect

from scrapper_queue.producer import ScrapperProducer
from trades.client import BrokerClient
from env.kraken import KRAKEN_WS
from orderbook.mapper.kraken import KrakenOrderBookMapper
from orderbook.mapper.model.order_book import TSOrderBook


class KrakenOrderBook(BrokerClient):
    @staticmethod
    def create() -> BrokerClient:
        return KrakenOrderBook(
            KRAKEN_WS,
            "KRAKEN_ORDERBOOK",
            args={
                "method": "subscribe",
                "params": {
                    "channel": "book",
                    "symbol": ["BTC/USD", "DOGE/USD", "ETH/USD", "SOL/USD"],
                    "depth": 25,
                },
            },
        )

    @override
    async def connect(self):
        self.client = await connect(self.url)
        _ = await self.client.send(json.dumps(self.args))
        _ = await self.client.recv()

    @override
    async def onListen(self):
        try:
            data = json.loads(await self.client.recv())
            if data.get("channel") == "book" and "data" in data:
                mapped: TSOrderBook = KrakenOrderBookMapper.mapResponse(data)
                await ScrapperProducer.sendOrderbook(mapped)
        except websockets.exceptions.ConnectionClosed:
            await self.connect()
        except Exception as e:
            await self.close()
            print(f"Error processing Kraken OrderBook data: {e}")

    @override
    async def close(self):
        if self.client:
            await self.client.close()
