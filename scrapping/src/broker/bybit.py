import json
import stat
from typing import override

from websockets.asyncio.client import ClientConnection, connect

from env.bybit import BYBIT_WS
from scrapping.src.broker.mapper.bybit import BybitDataMapper

from .broker_client import BrokerClient


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
        data = await self.client.recv()
        print(data)
        response = BybitDataMapper.mapResponse(data)
        response

    @override
    async def close(self):
        await self.client.close()
