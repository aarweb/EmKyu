import enum

from broker import Broker


class Side(enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class TSTrade:
    timestamp: int
    name: str
    price: float
    volume: float
    side: str
    broker: str

    def __init__(
        self, timestamp: int, name: str, price: float, volume: float, side: Side, broker: Broker
    ) -> None:
        self.timestamp = timestamp
        self.name = name
        self.price = price
        self.volume = volume
        self.side = side.value
        self.broker = broker.value

    def __str__(self) -> str:
        return f"TSTrade(timestamp={self.timestamp}, name='{self.name}', {self.side} price={self.price}, volume={float(self.volume):.8f}, broker='{self.broker}')"
