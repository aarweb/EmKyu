import json
from typing import override

import websockets
from websockets.asyncio.client import connect

from scrapper_queue.producer import ScrapperProducer
from trades.client import BrokerClient
from env.binance import BINANCE_WS
from orderbook.mapper.binance import BinanceOrderBookMapper
from orderbook.mapper.model.order_book import TSOrderBook


class BinanceOrderBook(BrokerClient):
    @staticmethod
    def create() -> BrokerClient:
        return BinanceOrderBook(
            BINANCE_WS,
            "BINANCE_ORDERBOOK",
            args={
                "method": "SUBSCRIBE",
                "params": [
                    "btcusdt@depth20@100ms",
                    "dogeusdt@depth20@100ms",
                    "ethusdt@depth20@100ms",
                    "solusdt@depth20@100ms",
                ],
                "id": 2,
            },
        )

    @override
    async def connect(self):
        # Binance orderbook mapper espera formato combined-stream ({stream, data}),
        # que solo se entrega en el endpoint /stream, no en /ws.
        combined_url = self.url.rsplit("/ws", 1)[0] + "/stream"
        self.client = await connect(combined_url)
        _ = await self.client.send(json.dumps(self.args))
        _ = await self.client.recv()

    @override
    async def onListen(self):
        try:
            data = json.loads(await self.client.recv())
            if "data" in data:
                mapped: TSOrderBook = BinanceOrderBookMapper.mapResponse(data)
                await ScrapperProducer.sendOrderbook(mapped)
        except websockets.exceptions.ConnectionClosed:
            await self.connect()
        except Exception as e:
            await self.close()
            print(f"Error processing Binance OrderBook data: {e}")

    @override
    async def close(self):
        if self.client:
            await self.client.close()
