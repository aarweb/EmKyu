"""Tests para la serialización del producer Kafka + contrato con los supervisores de Druid.

No arrancamos Kafka. Reusamos la misma lambda de serialización que usa el producer
real para garantizar que el JSON producido cumple el esquema esperado por Druid.
"""
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from broker import Broker
from orderbook.mapper.binance import BinanceOrderBookMapper
from orderbook.mapper.bybit import BybitOrderBookMapper
from orderbook.mapper.kraken import KrakenOrderBookMapper
from orderbook.mapper.model.order_book import OrderLevel, TSOrderBook
from trades.mapper.binance import BinanceDataMapper
from trades.mapper.bybit import BybitDataMapper
from trades.mapper.kraken import KrakenDataMapper
from trades.mapper.model.time_series_cripto import Side, TSTrade

# Misma función de serialización que define ScrapperProducer.start()
SERIALIZER = lambda v: json.dumps(v, default=lambda o: o.__dict__).encode("utf-8")

DRUID_DIR = Path(__file__).resolve().parent.parent.parent / "druid"


def _druid_fields(supervisor_filename: str) -> dict:
    """Lee un supervisor de Druid y devuelve {dimensions, metric_fields, jq_flatten_fields}."""
    spec = json.loads((DRUID_DIR / supervisor_filename).read_text())
    schema = spec["spec"]["dataSchema"]
    io = spec["spec"]["ioConfig"]
    return {
        "timestamp_col": schema["timestampSpec"]["column"],
        "timestamp_format": schema["timestampSpec"]["format"],
        "dimensions": schema["dimensionsSpec"]["dimensions"],
        "metric_fields": [m["fieldName"] for m in schema["metricsSpec"] if "fieldName" in m],
        "jq_flatten": [f for f in io.get("inputFormat", {}).get("flattenSpec", {}).get("fields", [])],
    }


# ─────────────────────────── Serialización básica ───────────────────────────

class TestSerializer:
    def test_tstrade_roundtrip(self):
        trade = TSTrade(1700, "BTCUSDT", 65000.5, 0.1, Side.BUY, Broker.BINANCE)
        result = json.loads(SERIALIZER(trade).decode())
        assert result == {
            "timestamp": 1700,
            "name": "BTCUSDT",
            "price": 65000.5,
            "volume": 0.1,
            "side": "BUY",
            "broker": "BINANCE",
        }

    def test_tsorderbook_roundtrip_with_nested_levels(self):
        ob = TSOrderBook(
            timestamp=1700,
            symbol="BTCUSDT",
            bids=[OrderLevel(100.0, 1.0), OrderLevel(99.0, 2.0)],
            asks=[OrderLevel(101.0, 1.5)],
            broker=Broker.BYBIT,
        )
        result = json.loads(SERIALIZER(ob).decode())
        assert result["symbol"] == "BTCUSDT"
        assert result["broker"] == "BYBIT"
        assert result["bids"] == [
            {"price": 100.0, "quantity": 1.0},
            {"price": 99.0, "quantity": 2.0},
        ]
        assert result["asks"] == [{"price": 101.0, "quantity": 1.5}]

    def test_enum_side_serialized_as_string(self):
        trade = TSTrade(1, "X", 1.0, 1.0, Side.SELL, Broker.KRAKEN)
        assert json.loads(SERIALIZER(trade))["side"] == "SELL"


# ─────────────────────────── Contrato con Druid ───────────────────────────

class TestDruidContract:
    """Verifica que los JSON enviados a Kafka contienen los campos que el ingestion
    spec de Druid espera (timestampSpec.column, dimensions y metricsSpec.fieldName)."""

    def test_trade_schema_satisfied_by_binance(self, binance_trade_payload_buy):
        fields = _druid_fields("trades-supervisor.json")
        trade = BinanceDataMapper.mapResponse(binance_trade_payload_buy)
        payload = json.loads(SERIALIZER(trade))

        assert fields["timestamp_col"] in payload
        assert fields["timestamp_format"] == "millis"
        assert isinstance(payload[fields["timestamp_col"]], int)
        for dim in fields["dimensions"]:
            assert dim in payload, f"Falta dimensión Druid: {dim}"
        for metric in fields["metric_fields"]:
            assert metric in payload, f"Falta métrica Druid: {metric}"

    def test_trade_schema_satisfied_by_kraken(self, kraken_trade_payload):
        fields = _druid_fields("trades-supervisor.json")
        trade = KrakenDataMapper.mapResponse(kraken_trade_payload)
        payload = json.loads(SERIALIZER(trade))
        for dim in fields["dimensions"]:
            assert dim in payload
        for metric in fields["metric_fields"]:
            assert metric in payload

    def test_orderbook_schema_satisfied_by_binance(self, binance_orderbook_payload):
        fields = _druid_fields("orderbook-supervisor.json")
        ob = BinanceOrderBookMapper.mapResponse(binance_orderbook_payload)
        payload = json.loads(SERIALIZER(ob))

        assert fields["timestamp_col"] in payload
        for dim in fields["dimensions"]:
            assert dim in payload
        # Las expresiones jq usan .bids[0].price / .asks[0].quantity etc.
        # Verifica que los caminos existan.
        assert payload["bids"] and "price" in payload["bids"][0]
        assert payload["bids"] and "quantity" in payload["bids"][0]
        assert payload["asks"] and "price" in payload["asks"][0]
        assert payload["asks"] and "quantity" in payload["asks"][0]

    def test_orderbook_jq_paths_resolve_with_bybit(self, bybit_orderbook_payload):
        ob = BybitOrderBookMapper.mapResponse(bybit_orderbook_payload)
        payload = json.loads(SERIALIZER(ob))
        # Replicamos los jq: .bids[0].price, .bids[0].quantity, .asks[0].price, .asks[0].quantity
        assert payload["bids"][0]["price"] == 65000.10
        assert payload["bids"][0]["quantity"] == 0.5
        assert payload["asks"][0]["price"] == 65001.00
        assert payload["asks"][0]["quantity"] == 0.4

    def test_orderbook_jq_paths_resolve_with_kraken(self, kraken_orderbook_payload):
        ob = KrakenOrderBookMapper.mapResponse(kraken_orderbook_payload)
        payload = json.loads(SERIALIZER(ob))
        assert payload["bids"][0]["price"] == 65000.10
        assert payload["asks"][0]["price"] == 65001.00


# ─────────────────────────── API del ScrapperProducer ───────────────────────────

class TestScrapperProducerAPI:

    async def test_send_trade_calls_kafka_with_topic(self):
        from scrapper_queue import producer as producer_mod
        mock_producer = AsyncMock()
        with patch.object(producer_mod, "SCRAPPER_PRODUCER", mock_producer):
            trade = TSTrade(1, "BTC", 1.0, 1.0, Side.BUY, Broker.BINANCE)
            await producer_mod.ScrapperProducer.sendTrade(trade)
            mock_producer.send.assert_awaited_once()
            args = mock_producer.send.call_args.args
            assert args[0] == "trades"  # TRAIT_TOPIC
            assert args[1] is trade

    async def test_send_orderbook_calls_kafka_with_topic(self):
        from scrapper_queue import producer as producer_mod
        mock_producer = AsyncMock()
        with patch.object(producer_mod, "SCRAPPER_PRODUCER", mock_producer):
            ob = TSOrderBook(1, "BTC", [], [], Broker.BINANCE)
            await producer_mod.ScrapperProducer.sendOrderbook(ob)
            mock_producer.send.assert_awaited_once()
            args = mock_producer.send.call_args.args
            assert args[0] == "orderbook"

    async def test_send_trade_before_start_raises_runtime_error(self):
        from scrapper_queue import producer as producer_mod
        with patch.object(producer_mod, "SCRAPPER_PRODUCER", None):
            trade = TSTrade(1, "BTC", 1.0, 1.0, Side.BUY, Broker.BINANCE)
            with pytest.raises(RuntimeError, match="not started"):
                await producer_mod.ScrapperProducer.sendTrade(trade)

    async def test_send_orderbook_before_start_raises_runtime_error(self):
        from scrapper_queue import producer as producer_mod
        from orderbook.mapper.model.order_book import TSOrderBook
        with patch.object(producer_mod, "SCRAPPER_PRODUCER", None):
            ob = TSOrderBook(1, "BTC", [], [], Broker.BINANCE)
            with pytest.raises(RuntimeError, match="not started"):
                await producer_mod.ScrapperProducer.sendOrderbook(ob)
