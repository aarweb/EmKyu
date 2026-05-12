"""Tests para los enums y modelos.

Estos valores forman parte del contrato con Druid (dimensions). Cualquier renombrado
debe ser intencional y reflejarse en los supervisores.
"""
import pytest

from broker import Broker
from orderbook.mapper.model.order_book import OrderLevel, TSOrderBook
from trades.mapper.model.time_series_cripto import Side, TSTrade


class TestEnums:
    def test_side_values_stable(self):
        assert Side.BUY.value == "BUY"
        assert Side.SELL.value == "SELL"
        assert {s.value for s in Side} == {"BUY", "SELL"}

    def test_broker_values_stable(self):
        assert Broker.BYBIT.value == "BYBIT"
        assert Broker.BINANCE.value == "BINANCE"
        assert Broker.KRAKEN.value == "KRAKEN"
        assert {b.value for b in Broker} == {"BYBIT", "BINANCE", "KRAKEN"}


class TestTSTrade:
    def test_init_stores_enum_values_as_strings(self):
        t = TSTrade(123, "BTC", 10.0, 1.0, Side.BUY, Broker.KRAKEN)
        assert t.side == "BUY"
        assert t.broker == "KRAKEN"
        assert isinstance(t.side, str)
        assert isinstance(t.broker, str)

    def test_repr_contains_key_fields(self):
        t = TSTrade(1, "BTCUSDT", 65000.0, 0.5, Side.BUY, Broker.BINANCE)
        s = str(t)
        assert "BTCUSDT" in s
        assert "BUY" in s
        assert "BINANCE" in s
        assert "65000" in s

    def test_fails_if_side_is_plain_string(self):
        # El init espera Side, no str → falla al acceder .value
        with pytest.raises(AttributeError):
            TSTrade(1, "X", 1.0, 1.0, "BUY", Broker.BINANCE)  # type: ignore[arg-type]


class TestOrderLevel:
    def test_init(self):
        ol = OrderLevel(100.5, 0.25)
        assert ol.price == 100.5
        assert ol.quantity == 0.25

    def test_str_formats_with_decimals(self):
        assert str(OrderLevel(100.0, 0.5)) == "[100.00 x 0.50000000]"


class TestTSOrderBook:
    def test_init_stores_broker_value(self):
        ob = TSOrderBook(1, "BTC", [], [], Broker.BYBIT)
        assert ob.broker == "BYBIT"

    def test_str_summary_includes_top_three(self):
        levels = [OrderLevel(i, i / 10) for i in range(1, 10)]
        ob = TSOrderBook(1, "BTC", levels, levels, Broker.BINANCE)
        s = str(ob)
        assert "BTC" in s
        assert "BINANCE" in s
        # Solo top 3 bids/asks
        assert "1.00" in s and "2.00" in s and "3.00" in s
