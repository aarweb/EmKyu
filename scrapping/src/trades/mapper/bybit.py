from broker import Broker
from trades.mapper.model.time_series_cripto import Side, TSTrade


class BybitDataMapper:
    @staticmethod
    def mapResponse(data):
        trade = data["data"][-1]
        # "S" field is "Buy" or "Sell"
        side = Side.BUY if trade["S"] == "Buy" else Side.SELL

        return TSTrade(
            timestamp=data["ts"],
            name=trade["s"],
            price=trade["p"],
            volume=trade["v"],
            side=side,
            broker=Broker.BYBIT,
        )
