import json
from typing import override

from websockets.asyncio.client import connect

from trades.client import BrokerClient
from env.bybit import BYBIT_WS
from orderbook.mapper.bybit import BybitOrderBookMapper
from orderbook.mapper.model.order_book import TSOrderBook


class BybitOrderBook(BrokerClient):
    @staticmethod
    def create() -> BrokerClient:
        return BybitOrderBook(
            BYBIT_WS,
            "BYBIT_ORDERBOOK",
            args={
                "op": "subscribe",
                "args": [
                    "orderbook.50.BTCUSDT",
                    "orderbook.50.DOGEUSDT",
                    "orderbook.50.ETHUSDT",
                    "orderbook.50.SOLUSDT",
                ],
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
            if "data" in data:
                mapped: TSOrderBook = BybitOrderBookMapper.mapResponse(data)
                await ScrapperProducer.sendOrderbook(mapped)
        except websockets.exceptions.ConnectionClosed:
            await self.connect()
        except Exception as e:
            await self.close()
            print(f"Error processing Binance OrderBook data: {e}")

    @override
    async def close(self):
        await self.client.close()
