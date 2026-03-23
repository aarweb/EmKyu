class TSData:

    timestamp: int
    name: str
    price: float
    volume: float

    def __init__(self, timestamp: int, name: str, price: float, volume: float) -> None:
        self.timestamp = timestamp
        self.name = name
        self.price = price
        self.volume = volume
