# <=== IMPORTS ===>
import asyncio
import json
import stat
from typing import override

from websockets.asyncio.client import connect

from broker.mapper.kraken import KrakenDataMapper
from broker.mapper.model.time_series_cripto import TSData
from env.kraken import KRAKEN_WS

from .client import BrokerClient
# <===============>


# <=== CODE ===>
# TODO: Quizás haga falta el SnapShot
class KrakenBroker(BrokerClient):
    @staticmethod
    def create() -> BrokerClient:
        return KrakenBroker(
            KRAKEN_WS,
            "KRAKEN",
            args={
                "method": "subscribe",
                "params": {
                    "channel": "ticker",
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
        if data.get("channel") == "ticker" and "data" in data:
            mapped: TSData = KrakenDataMapper.mapResponse(data)
            print(mapped)

    @override
    async def close(self):
        await self.client.close()


# <============>
