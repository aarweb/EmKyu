from broker import Broker


class OrderLevel:
    price: float
    quantity: float

    def __init__(self, price: float, quantity: float) -> None:
        self.price = price
        self.quantity = quantity

    def __str__(self) -> str:
        return f"[{self.price:.2f} x {self.quantity:.8f}]"


class TSOrderBook:
    timestamp: int
    symbol: str
    bids: list[OrderLevel]
    asks: list[OrderLevel]
    broker: str

    def __init__(
        self,
        timestamp: int,
        symbol: str,
        bids: list[OrderLevel],
        asks: list[OrderLevel],
        broker: Broker,
    ) -> None:
        self.timestamp = timestamp
        self.symbol = symbol
        self.bids = bids
        self.asks = asks
        self.broker = broker.value

    def __str__(self) -> str:
        top_bids = ", ".join(str(b) for b in self.bids[:3])
        top_asks = ", ".join(str(a) for a in self.asks[:3])
        return (
            f"OrderBook({self.broker} {self.symbol} ts={self.timestamp} "
            f"bids=[{top_bids}...] asks=[{top_asks}...])"
        )
