import asyncio
import json
import stat
from typing import override

from websockets.asyncio.client import connect

from broker.mapper.bybit import BybitDataMapper
from broker.mapper.model.time_series_cripto import TSData
from env.bybit import BYBIT_WS

from .client import BrokerClient


class BybitBroker(BrokerClient):
    @staticmethod
    def create() -> BrokerClient:
        return BybitBroker(
            BYBIT_WS,
            "BYBIT",
            args={
                "op": "subscribe",
                "args": [
                    "publicTrade.BTCUSDT",
                    "publicTrade.DOGEUSDT",
                    "publicTrade.ETHUSDT",
                    "publicTrade.SOLUSDT",
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
        data = json.loads(await self.client.recv())
        mapped: TSData = BybitDataMapper.mapResponse(data)
        print(mapped)

    @override
    async def close(self):
        await self.client.close()
