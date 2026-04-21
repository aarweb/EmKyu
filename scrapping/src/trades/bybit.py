import json
from typing import override

import websockets
from websockets.asyncio.client import connect

from trades.mapper.bybit import BybitDataMapper
from trades.mapper.model.time_series_cripto import TSTrade
from env.bybit import BYBIT_WS
from scrapper_queue.producer import ScrapperProducer

from .client import BrokerClient


class BybitTrade(BrokerClient):
    @staticmethod
    def create() -> BrokerClient:
        return BybitTrade(
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
        try:
            data = json.loads(await self.client.recv())
            mapped: TSTrade = BybitDataMapper.mapResponse(data)
            await ScrapperProducer.sendTrade(mapped)
        except websockets.exceptions.ConnectionClosed:
            await self.connect()
        except Exception as e:
            await self.close()
            print(f"Error processing Bybit data: {e}")

    @override
    async def close(self):
        if self.client:
            await self.client.close()
