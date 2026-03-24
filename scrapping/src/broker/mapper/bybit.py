from broker.mapper.model.time_series_cripto import Provider, TSData


class BybitDataMapper:
    @staticmethod
    def mapResponse(data):
        return TSData(
            timestamp=data["ts"],
            name=data["data"][-1]["s"],
            price=data["data"][-1]["p"],
            volume=data["data"][-1]["v"],
            provider=Provider.BYBIT,
        )
