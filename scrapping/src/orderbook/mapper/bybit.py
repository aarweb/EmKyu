from broker import Broker
from orderbook.mapper.model.order_book import OrderLevel, TSOrderBook


class BybitOrderBookMapper:
    @staticmethod
    def mapResponse(data: dict) -> TSOrderBook:
        book = data.get("data", {})
        return TSOrderBook(
            timestamp=data["ts"],
            symbol=book.get("s", ""),
            bids=[
                OrderLevel(price=float(entry[0]), quantity=float(entry[1]))
                for entry in book.get("b", [])
            ],
            asks=[
                OrderLevel(price=float(entry[0]), quantity=float(entry[1]))
                for entry in book.get("a", [])
            ],
            broker=Broker.BYBIT,
        )
