import enum


class Provider(enum.Enum):
    BYBIT = "BYBIT"
    BINANCE = "BINANCE"
    KRAKEN = "KRAKEN"


class TSData:
    timestamp: int
    name: str
    price: float
    volume: float
    provider: str

    def __init__(
        self, timestamp: int, name: str, price: float, volume: float, provider: Provider
    ) -> None:
        self.timestamp = timestamp
        self.name = name
        self.price = price
        self.volume = volume
        self.provider = provider.value

    def __str__(self) -> str:
        return f"TSData(timestamp={self.timestamp}, name='{self.name}', price={self.price}, volume={float(self.volume):.8f}, provider='{self.provider}')"
