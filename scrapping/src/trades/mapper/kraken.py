from datetime import datetime, timezone

from broker import Broker
from trades.mapper.model.time_series_cripto import Side, TSTrade


class KrakenDataMapper:
    @staticmethod
    def mapResponse(data):
        trade = data["data"][0]
        iso_timestamp = trade["timestamp"]
        epoch_ms = int(
            datetime.fromisoformat(iso_timestamp)
            .replace(tzinfo=timezone.utc)
            .timestamp()
            * 1000
        )
        # "side" field is "buy" or "sell"
        side = Side.BUY if trade["side"] == "buy" else Side.SELL

        return TSTrade(
            timestamp=epoch_ms,
            name=trade["symbol"],
            price=trade["price"],
            volume=trade["qty"],
            side=side,
            broker=Broker.KRAKEN,
        )
