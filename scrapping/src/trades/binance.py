import json
from typing import override

import websockets
from websockets.asyncio.client import connect

from trades.mapper.binance import BinanceDataMapper
from trades.mapper.model.time_series_cripto import TSTrade
from env.binance import BINANCE_WS
from scrapper_queue.producer import ScrapperProducer

from .client import BrokerClient


class BinanceBroker(BrokerClient):
    @staticmethod
    def create() -> BrokerClient:
        return BinanceBroker(
            BINANCE_WS,
            "BINANCE",
            args={
                "method": "SUBSCRIBE",
                "params": [
                    "btcusdt@trade",
                    "dogeusdt@trade",
                    "ethusdt@trade",
                    "solusdt@trade",
                ],
                "id": 1,
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
            mapped: TSTrade = BinanceDataMapper.mapResponse(data)
            await ScrapperProducer.sendTrait(mapped)
            print(mapped)
        except websockets.exceptions.ConnectionClosed:
            await self.connect()
        except Exception as e:
            await self.close()
            print(f"Error processing Binance data: {e}")

    @override
    async def close(self):
        if self.client:
            await self.client.close()
