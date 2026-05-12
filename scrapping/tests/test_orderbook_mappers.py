"""Tests unitarios para los mappers de orderbook.

Cubren:
  - Extracción de símbolo desde diferentes formatos
  - Parsing de bids/asks (formato lista vs dict)
  - Conversión de precios y cantidades a float
  - Timestamps (locales vs del exchange)
"""
import time
from datetime import datetime, timezone

import pytest

from broker import Broker
from orderbook.mapper.binance import BinanceOrderBookMapper
from orderbook.mapper.bybit import BybitOrderBookMapper
from orderbook.mapper.kraken import KrakenOrderBookMapper
from orderbook.mapper.model.order_book import OrderLevel, TSOrderBook


# ───────────────────────── Binance ─────────────────────────

class TestBinanceOrderBookMapper:
    def test_returns_tsorderbook(self, binance_orderbook_payload):
        result = BinanceOrderBookMapper.mapResponse(binance_orderbook_payload)
        assert isinstance(result, TSOrderBook)

    def test_symbol_extracted_from_stream(self, binance_orderbook_payload):
        result = BinanceOrderBookMapper.mapResponse(binance_orderbook_payload)
        assert result.symbol == "BTCUSDT"

    def test_bids_are_order_levels_with_floats(self, binance_orderbook_payload):
        result = BinanceOrderBookMapper.mapResponse(binance_orderbook_payload)
        assert len(result.bids) == 3
        assert all(isinstance(b, OrderLevel) for b in result.bids)
        assert result.bids[0].price == 65000.10
        assert result.bids[0].quantity == 0.5
        assert isinstance(result.bids[0].price, float)
        assert isinstance(result.bids[0].quantity, float)

    def test_asks_are_order_levels_with_floats(self, binance_orderbook_payload):
        result = BinanceOrderBookMapper.mapResponse(binance_orderbook_payload)
        assert len(result.asks) == 2
        assert result.asks[0].price == 65001.00

    def test_timestamp_is_local_in_ms(self, binance_orderbook_payload):
        # Binance usa time.time() local: comprobamos que está cerca del ahora
        before = int(time.time() * 1000)
        result = BinanceOrderBookMapper.mapResponse(binance_orderbook_payload)
        after = int(time.time() * 1000)
        assert before <= result.timestamp <= after

    def test_handles_empty_bids_and_asks(self):
        result = BinanceOrderBookMapper.mapResponse({"stream": "btcusdt@depth20@100ms", "data": {"bids": [], "asks": []}})
        assert result.bids == []
        assert result.asks == []

    def test_handles_missing_data_field_returns_empty(self):
        # data ausente → bids/asks vacíos (no excepción)
        result = BinanceOrderBookMapper.mapResponse({"stream": "btcusdt@depth"})
        assert result.bids == []
        assert result.asks == []
        assert result.symbol == "BTCUSDT"

    def test_handles_missing_stream_returns_empty_symbol(self):
        result = BinanceOrderBookMapper.mapResponse({"data": {"bids": [], "asks": []}})
        assert result.symbol == ""

    def test_broker_is_binance(self, binance_orderbook_payload):
        result = BinanceOrderBookMapper.mapResponse(binance_orderbook_payload)
        assert result.broker == Broker.BINANCE.value


# ───────────────────────── Bybit ─────────────────────────

class TestBybitOrderBookMapper:
    def test_returns_tsorderbook(self, bybit_orderbook_payload):
        result = BybitOrderBookMapper.mapResponse(bybit_orderbook_payload)
        assert isinstance(result, TSOrderBook)

    def test_uses_exchange_timestamp(self, bybit_orderbook_payload):
        result = BybitOrderBookMapper.mapResponse(bybit_orderbook_payload)
        assert result.timestamp == 1700000003000

    def test_symbol_from_data_s(self, bybit_orderbook_payload):
        result = BybitOrderBookMapper.mapResponse(bybit_orderbook_payload)
        assert result.symbol == "BTCUSDT"

    def test_bids_parsed_from_b_key(self, bybit_orderbook_payload):
        result = BybitOrderBookMapper.mapResponse(bybit_orderbook_payload)
        assert len(result.bids) == 2
        assert result.bids[0].price == 65000.10
        assert result.bids[0].quantity == 0.5
        assert isinstance(result.bids[0].price, float)

    def test_asks_parsed_from_a_key(self, bybit_orderbook_payload):
        result = BybitOrderBookMapper.mapResponse(bybit_orderbook_payload)
        assert len(result.asks) == 2
        assert result.asks[0].price == 65001.00

    def test_broker_is_bybit(self, bybit_orderbook_payload):
        result = BybitOrderBookMapper.mapResponse(bybit_orderbook_payload)
        assert result.broker == Broker.BYBIT.value

    def test_handles_empty_book(self):
        data = {"ts": 1, "data": {"s": "BTCUSDT", "b": [], "a": []}}
        result = BybitOrderBookMapper.mapResponse(data)
        assert result.bids == [] and result.asks == []

    def test_raises_if_ts_missing(self):
        # 'ts' se accede como data["ts"] (sin default) → KeyError esperado
        with pytest.raises(KeyError):
            BybitOrderBookMapper.mapResponse({"data": {"s": "BTC", "b": [], "a": []}})


# ───────────────────────── Kraken ─────────────────────────

class TestKrakenOrderBookMapper:
    def test_returns_tsorderbook(self, kraken_orderbook_payload):
        result = KrakenOrderBookMapper.mapResponse(kraken_orderbook_payload)
        assert isinstance(result, TSOrderBook)

    def test_symbol_from_data(self, kraken_orderbook_payload):
        result = KrakenOrderBookMapper.mapResponse(kraken_orderbook_payload)
        assert result.symbol == "BTC/USD"

    def test_timestamp_converted_to_epoch_ms(self, kraken_orderbook_payload):
        expected = int(
            datetime(2023, 11, 14, 22, 13, 22, 123000, tzinfo=timezone.utc).timestamp() * 1000
        )
        result = KrakenOrderBookMapper.mapResponse(kraken_orderbook_payload)
        assert result.timestamp == expected

    def test_missing_timestamp_defaults_to_zero(self):
        data = {
            "data": [{"symbol": "BTC/USD", "bids": [], "asks": []}]
        }
        result = KrakenOrderBookMapper.mapResponse(data)
        assert result.timestamp == 0

    def test_bids_parsed_from_dict_format(self, kraken_orderbook_payload):
        result = KrakenOrderBookMapper.mapResponse(kraken_orderbook_payload)
        assert len(result.bids) == 2
        assert result.bids[0].price == 65000.10
        assert result.bids[0].quantity == 0.5

    def test_asks_parsed_from_dict_format(self, kraken_orderbook_payload):
        result = KrakenOrderBookMapper.mapResponse(kraken_orderbook_payload)
        assert len(result.asks) == 2
        assert result.asks[1].price == 65001.10

    def test_broker_is_kraken(self, kraken_orderbook_payload):
        result = KrakenOrderBookMapper.mapResponse(kraken_orderbook_payload)
        assert result.broker == Broker.KRAKEN.value

    def test_raises_on_empty_data_array(self):
        with pytest.raises(IndexError):
            KrakenOrderBookMapper.mapResponse({"data": []})
