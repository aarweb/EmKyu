"""Tests unitarios para los mappers de trades.

Cubren:
  - Lógica de inversión BUY/SELL (especialmente Binance con 'm')
  - Conversión de tipos (price/volume a float)
  - Conversión de timestamps (ISO → epoch ms en Kraken)
  - Mapeo de campos al modelo TSTrade
"""
from datetime import datetime, timezone

import pytest

from broker import Broker
from trades.mapper.binance import BinanceDataMapper
from trades.mapper.bybit import BybitDataMapper
from trades.mapper.kraken import KrakenDataMapper
from trades.mapper.model.time_series_cripto import Side, TSTrade


# ───────────────────────── Binance ─────────────────────────

class TestBinanceDataMapper:
    def test_maps_buy_when_m_is_false(self, binance_trade_payload_buy):
        result = BinanceDataMapper.mapResponse(binance_trade_payload_buy)
        assert result.side == Side.BUY.value

    def test_maps_sell_when_m_is_true(self, binance_trade_payload_sell):
        result = BinanceDataMapper.mapResponse(binance_trade_payload_sell)
        assert result.side == Side.SELL.value

    def test_returns_tstrade_instance(self, binance_trade_payload_buy):
        result = BinanceDataMapper.mapResponse(binance_trade_payload_buy)
        assert isinstance(result, TSTrade)

    def test_preserves_event_timestamp(self, binance_trade_payload_buy):
        result = BinanceDataMapper.mapResponse(binance_trade_payload_buy)
        assert result.timestamp == 1700000000123

    def test_symbol_maps_from_s_field(self, binance_trade_payload_buy):
        result = BinanceDataMapper.mapResponse(binance_trade_payload_buy)
        assert result.name == "BTCUSDT"

    def test_price_is_cast_to_float(self, binance_trade_payload_buy):
        result = BinanceDataMapper.mapResponse(binance_trade_payload_buy)
        assert isinstance(result.price, float)
        assert result.price == 65432.10

    def test_volume_is_cast_to_float(self, binance_trade_payload_buy):
        result = BinanceDataMapper.mapResponse(binance_trade_payload_buy)
        assert isinstance(result.volume, float)
        assert result.volume == pytest.approx(0.00123456)

    def test_broker_is_binance(self, binance_trade_payload_buy):
        result = BinanceDataMapper.mapResponse(binance_trade_payload_buy)
        assert result.broker == Broker.BINANCE.value

    def test_raises_keyerror_on_missing_fields(self):
        with pytest.raises(KeyError):
            BinanceDataMapper.mapResponse({"e": "trade"})


# ───────────────────────── Bybit ─────────────────────────

class TestBybitDataMapper:
    def test_returns_tstrade_instance(self, bybit_trade_payload):
        result = BybitDataMapper.mapResponse(bybit_trade_payload)
        assert isinstance(result, TSTrade)

    def test_maps_buy_side(self, bybit_trade_payload_single_sell):
        # invertido a propósito: este payload tiene Sell
        result = BybitDataMapper.mapResponse(bybit_trade_payload_single_sell)
        assert result.side == Side.SELL.value

    def test_maps_buy_explicit(self):
        data = {"ts": 1, "data": [{"s": "BTCUSDT", "S": "Buy", "v": "1", "p": "100"}]}
        result = BybitDataMapper.mapResponse(data)
        assert result.side == Side.BUY.value

    def test_uses_last_trade_of_batch(self, bybit_trade_payload):
        # El batch tiene dos trades; el mapper usa [-1] (último). Documentamos el comportamiento.
        result = BybitDataMapper.mapResponse(bybit_trade_payload)
        assert result.side == Side.SELL.value  # el segundo es Sell

    def test_timestamp_from_root_ts(self, bybit_trade_payload):
        result = BybitDataMapper.mapResponse(bybit_trade_payload)
        assert result.timestamp == 1700000001000

    def test_symbol_from_trade(self, bybit_trade_payload):
        result = BybitDataMapper.mapResponse(bybit_trade_payload)
        assert result.name == "BTCUSDT"

    def test_broker_is_bybit(self, bybit_trade_payload):
        result = BybitDataMapper.mapResponse(bybit_trade_payload)
        assert result.broker == Broker.BYBIT.value

    def test_price_is_cast_to_float(self, bybit_trade_payload):
        result = BybitDataMapper.mapResponse(bybit_trade_payload)
        assert isinstance(result.price, float)
        assert result.price == 65010.50

    def test_volume_is_cast_to_float(self, bybit_trade_payload):
        result = BybitDataMapper.mapResponse(bybit_trade_payload)
        assert isinstance(result.volume, float)
        assert result.volume == pytest.approx(0.002)


# ───────────────────────── Kraken ─────────────────────────

class TestKrakenDataMapper:
    def test_returns_tstrade_instance(self, kraken_trade_payload):
        result = KrakenDataMapper.mapResponse(kraken_trade_payload)
        assert isinstance(result, TSTrade)

    def test_maps_buy_side(self, kraken_trade_payload):
        result = KrakenDataMapper.mapResponse(kraken_trade_payload)
        assert result.side == Side.BUY.value

    def test_maps_sell_side(self, kraken_trade_payload_sell):
        result = KrakenDataMapper.mapResponse(kraken_trade_payload_sell)
        assert result.side == Side.SELL.value

    def test_iso_timestamp_converted_to_epoch_ms(self, kraken_trade_payload):
        # 2023-11-14T22:13:20.000000Z
        expected = int(
            datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc).timestamp() * 1000
        )
        result = KrakenDataMapper.mapResponse(kraken_trade_payload)
        assert result.timestamp == expected

    def test_microseconds_kept_in_ms(self, kraken_trade_payload_sell):
        # 22:13:21.500000Z → debería terminar en 500
        result = KrakenDataMapper.mapResponse(kraken_trade_payload_sell)
        assert result.timestamp % 1000 == 500

    def test_symbol_from_trade(self, kraken_trade_payload):
        result = KrakenDataMapper.mapResponse(kraken_trade_payload)
        assert result.name == "BTC/USD"

    def test_uses_first_trade_of_batch(self):
        data = {
            "data": [
                {"symbol": "A", "side": "buy",  "price": 1, "qty": 1, "timestamp": "2023-11-14T22:13:20.000000Z"},
                {"symbol": "B", "side": "sell", "price": 2, "qty": 2, "timestamp": "2023-11-14T22:13:21.000000Z"},
            ]
        }
        result = KrakenDataMapper.mapResponse(data)
        # Documenta que se queda con [0] (potencial pérdida de los demás)
        assert result.name == "A"

    def test_broker_is_kraken(self, kraken_trade_payload):
        result = KrakenDataMapper.mapResponse(kraken_trade_payload)
        assert result.broker == Broker.KRAKEN.value
