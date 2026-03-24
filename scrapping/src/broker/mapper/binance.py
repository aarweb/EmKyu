from broker.mapper.model.time_series_cripto import Provider, TSData


class BinanceDataMapper:
    @staticmethod
    def mapResponse(data: dict) -> TSData:
        return TSData(
            timestamp=data["E"],
            name=data["s"],
            price=float(data["p"]),
            volume=float(data["q"]),
            provider=Provider.BINANCE,
        )
