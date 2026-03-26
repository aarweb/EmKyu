import time

from broker import Broker
from orderbook.mapper.model.order_book import OrderLevel, TSOrderBook


class BinanceOrderBookMapper:
    @staticmethod
    def mapResponse(data: dict) -> TSOrderBook:
        return TSOrderBook(
            timestamp=int(time.time() * 1000),
            symbol=data.get("stream", "").split("@")[0].upper(),
            bids=[
                OrderLevel(price=float(entry[0]), quantity=float(entry[1]))
                for entry in data.get("data", {}).get("bids", [])
            ],
            asks=[
                OrderLevel(price=float(entry[0]), quantity=float(entry[1]))
                for entry in data.get("data", {}).get("asks", [])
            ],
            broker=Broker.BINANCE,
        )
