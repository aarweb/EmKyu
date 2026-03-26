from broker import Broker
from trades.mapper.model.time_series_cripto import Side, TSTrade


class BinanceDataMapper:
    @staticmethod
    def mapResponse(data: dict) -> TSTrade:
        # "m" = true means buyer is market maker → SELL, false → BUY
        side = Side.SELL if data["m"] else Side.BUY

        return TSTrade(
            timestamp=data["E"],
            name=data["s"],
            price=float(data["p"]),
            volume=float(data["q"]),
            side=side,
            broker=Broker.BINANCE,
        )
