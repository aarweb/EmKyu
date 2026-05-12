"""Fixtures globales: payloads reales de cada exchange para trades y orderbook."""
import os
import sys
from pathlib import Path

# Asegura que src/ esté en el path aunque pytest se invoque desde otro cwd
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Defaults para variables de entorno (los módulos env/*.py las requieren al importar)
os.environ.setdefault("BYBIT_WS", "wss://test/bybit")
os.environ.setdefault("BINANCE_WS", "wss://test/binance/ws")
os.environ.setdefault("KRAKEN_WS", "wss://test/kraken")
os.environ.setdefault("KAFKA_URL", "localhost:29092")
os.environ.setdefault("TRAIT_TOPIC", "trades")
os.environ.setdefault("ORDERBOOK_TOPIC", "orderbook")

import pytest


# ─────────────────────────── TRADES ───────────────────────────

@pytest.fixture
def binance_trade_payload_buy():
    # m=false → BUY (buyer NO es market maker)
    return {
        "e": "trade",
        "E": 1700000000123,
        "s": "BTCUSDT",
        "t": 12345,
        "p": "65432.10",
        "q": "0.00123456",
        "T": 1700000000120,
        "m": False,
        "M": True,
    }


@pytest.fixture
def binance_trade_payload_sell():
    # m=true → SELL (buyer ES market maker)
    return {
        "e": "trade",
        "E": 1700000000999,
        "s": "ETHUSDT",
        "p": "3500.55",
        "q": "1.5",
        "m": True,
    }


@pytest.fixture
def bybit_trade_payload():
    return {
        "topic": "publicTrade.BTCUSDT",
        "ts": 1700000001000,
        "type": "snapshot",
        "data": [
            {"T": 1700000000950, "s": "BTCUSDT", "S": "Buy",  "v": "0.001", "p": "65000.00", "L": "PlusTick", "i": "a1", "BT": False},
            {"T": 1700000000990, "s": "BTCUSDT", "S": "Sell", "v": "0.002", "p": "65010.50", "L": "MinusTick", "i": "a2", "BT": False},
        ],
    }


@pytest.fixture
def bybit_trade_payload_single_sell():
    return {
        "ts": 1700000002000,
        "data": [
            {"s": "DOGEUSDT", "S": "Sell", "v": "100.5", "p": "0.082"}
        ],
    }


@pytest.fixture
def kraken_trade_payload():
    return {
        "channel": "trade",
        "type": "update",
        "data": [
            {
                "symbol": "BTC/USD",
                "side": "buy",
                "price": 65000.5,
                "qty": 0.0123,
                "ord_type": "market",
                "trade_id": 11111,
                "timestamp": "2023-11-14T22:13:20.000000Z",
            }
        ],
    }


@pytest.fixture
def kraken_trade_payload_sell():
    return {
        "channel": "trade",
        "data": [
            {
                "symbol": "ETH/USD",
                "side": "sell",
                "price": 3500.0,
                "qty": 1.0,
                "timestamp": "2023-11-14T22:13:21.500000Z",
            }
        ],
    }


@pytest.fixture
def kraken_trade_heartbeat():
    return {"channel": "heartbeat"}


# ─────────────────────────── ORDERBOOK ───────────────────────────

@pytest.fixture
def binance_orderbook_payload():
    return {
        "stream": "btcusdt@depth20@100ms",
        "data": {
            "lastUpdateId": 1234567,
            "bids": [
                ["65000.10", "0.5"],
                ["65000.00", "1.2"],
                ["64999.90", "0.3"],
            ],
            "asks": [
                ["65001.00", "0.4"],
                ["65001.10", "0.7"],
            ],
        },
    }


@pytest.fixture
def binance_orderbook_payload_no_data():
    # Respuesta inicial de SUBSCRIBE confirmación
    return {"result": None, "id": 2}


@pytest.fixture
def bybit_orderbook_payload():
    return {
        "topic": "orderbook.50.BTCUSDT",
        "ts": 1700000003000,
        "type": "snapshot",
        "data": {
            "s": "BTCUSDT",
            "b": [["65000.10", "0.5"], ["65000.00", "1.2"]],
            "a": [["65001.00", "0.4"], ["65001.10", "0.7"]],
            "u": 1,
            "seq": 1,
        },
    }


@pytest.fixture
def kraken_orderbook_payload():
    return {
        "channel": "book",
        "type": "snapshot",
        "data": [
            {
                "symbol": "BTC/USD",
                "bids": [
                    {"price": 65000.10, "qty": 0.5},
                    {"price": 65000.00, "qty": 1.2},
                ],
                "asks": [
                    {"price": 65001.00, "qty": 0.4},
                    {"price": 65001.10, "qty": 0.7},
                ],
                "checksum": 12345,
                "timestamp": "2023-11-14T22:13:22.123000Z",
            }
        ],
    }
