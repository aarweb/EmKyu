import asyncio

import pybotters
from stores import BINANCE_WS, BYBIT_WS
from trader import get_info_from_traders


async def main():

    async with pybotters.Client() as client:
        binance = pybotters.BinanceSpotDataStore()
        bybit = pybotters.BybitDataStore()

        await asyncio.gather(
            client.ws_connect(BINANCE_WS, hdlr_json=binance.onmessage),
            client.ws_connect(
                BYBIT_WS,
                send_json={
                    "op": "subscribe",
                    "args": [
                        "publicTrade.BTCUSDT",
                        "publicTrade.DOGEUSDT",
                        "publicTrade.ETHUSDT",
                        "publicTrade.SOLUSDT",
                    ],
                },
                hdlr_json=bybit.onmessage,
            ),
        )

        for i in range(100):
            await asyncio.gather(binance.wait(), bybit.wait())
            info = get_info_from_traders(binance.trade, bybit.trade)
            orderbooks = get_orderbook_from_broker(binance, bybit)


asyncio.run(main())
