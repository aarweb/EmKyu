import json
from typing import override

import websockets
from websockets.asyncio.client import connect

from broker.mapper.binance import BinanceDataMapper
from broker.mapper.model.time_series_cripto import TSData
from env.binance import BINANCE_WS

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
            mapped: TSData = BinanceDataMapper.mapResponse(data)
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
