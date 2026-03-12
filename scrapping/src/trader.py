def get_info_from_traders(binance_trader, bybit_trader):

    binance_info = binance_trader.find()
    bybit_info = bybit_trader.find()

    binance_data = {
        "broker": "BINANCE",
        "timestamp": bybit_info[-1]["T"],
        "name": binance_info[-1]["s"],
        "price": binance_info[-1]["p"],
        "is_sold": binance_info[-1]["m"],
        "volume": binance_info[-1]["q"],
    }

    bybit_data = {
        "broker": "BYBIT",
        "timestamp": bybit_info[-1]["T"],
        "name": bybit_info[-1]["s"],
        "price": bybit_info[-1]["p"],
        "is_sold": bybit_info[-1]["S"] == "Sell",
        "volume": (
            bybit_info[-1]["v"]
            if "v" in bybit_info[-1].keys()
            else bybit_info[-1]["size"]
        ),
    }
    print(bybit_data)
    return [binance_data, bybit_data]
