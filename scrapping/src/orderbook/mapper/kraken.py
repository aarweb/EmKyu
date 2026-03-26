from datetime import datetime, timezone

from broker import Broker
from orderbook.mapper.model.order_book import OrderLevel, TSOrderBook


class KrakenOrderBookMapper:
    @staticmethod
    def mapResponse(data: dict) -> TSOrderBook:
        book = data["data"][0]
        iso_timestamp = book.get("timestamp", "")
        epoch_ms = int(
            datetime.fromisoformat(iso_timestamp)
            .replace(tzinfo=timezone.utc)
            .timestamp()
            * 1000
        ) if iso_timestamp else 0

        return TSOrderBook(
            timestamp=epoch_ms,
            symbol=book.get("symbol", ""),
            bids=[
                OrderLevel(price=float(entry["price"]), quantity=float(entry["qty"]))
                for entry in book.get("bids", [])
            ],
            asks=[
                OrderLevel(price=float(entry["price"]), quantity=float(entry["qty"]))
                for entry in book.get("asks", [])
            ],
            broker=Broker.KRAKEN,
        )
