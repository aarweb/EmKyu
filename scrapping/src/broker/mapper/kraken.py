from datetime import datetime, timezone

from broker.mapper.model.time_series_cripto import Provider, TSData


class KrakenDataMapper:
    @staticmethod
    def mapResponse(data):
        iso_timestamp = data["data"][0]["timestamp"]
        epoch_ms = int(
            datetime.fromisoformat(iso_timestamp)
            .replace(tzinfo=timezone.utc)
            .timestamp()
            * 1000
        )
        return TSData(
            timestamp=epoch_ms,
            name=data["data"][0]["symbol"],
            price=data["data"][0]["bid"],
            volume=data["data"][0]["volume"],
            provider=Provider.KRAKEN,
        )
