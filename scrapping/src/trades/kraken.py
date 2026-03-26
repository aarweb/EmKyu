# <=== IMPORTS ===>
import asyncio
import json
import stat
from typing import override

from websockets.asyncio.client import connect

from trades.mapper.kraken import KrakenDataMapper
from trades.mapper.model.time_series_cripto import TSTrade
from env.kraken import KRAKEN_WS

from .client import BrokerClient


class KrakenBroker(BrokerClient):
    @staticmethod
    def create() -> BrokerClient:
        return KrakenBroker(
            KRAKEN_WS,
            "KRAKEN",
            args={
                "method": "subscribe",
                "params": {
                    "channel": "trade",
                    "symbol": ["BTC/USD", "DOGE/USD", "ETH/USD", "SOL/USD"],
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
        data = json.loads(await self.client.recv())
        if data.get("channel") == "trade" and "data" in data:
            mapped: TSTrade = KrakenDataMapper.mapResponse(data)
            print(mapped)

    @override
    async def close(self):
        await self.client.close()
