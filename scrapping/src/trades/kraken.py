import json
from typing import override

import websockets
from websockets.asyncio.client import connect

from trades.mapper.kraken import KrakenDataMapper
from trades.mapper.model.time_series_cripto import TSTrade
from env.kraken import KRAKEN_WS
from scrapper_queue.producer import ScrapperProducer

from .client import BrokerClient


class KrakenTrade(BrokerClient):
    @staticmethod
    def create() -> BrokerClient:
        return KrakenTrade(
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
        try:
            data = json.loads(await self.client.recv())
            if data.get("channel") == "trade" and "data" in data:
                mapped: TSTrade = KrakenDataMapper.mapResponse(data)
                await ScrapperProducer.sendTrade(mapped)
        except websockets.exceptions.ConnectionClosed:
            await self.connect()
        except Exception as e:
            await self.close()
            print(f"Error processing Kraken data: {e}")

    @override
    async def close(self):
        if self.client:
            await self.client.close()
