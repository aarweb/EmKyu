"""Tests para los clientes WebSocket de trades y orderbook.

Mockean el WS y ScrapperProducer para verificar:
  - Subscripciones correctas en connect()
  - Camino feliz: onListen() decodifica y publica en Kafka
  - Reconexión en ConnectionClosed
  - Cierre + log en excepción genérica
  - Filtrado de mensajes que no son de datos (heartbeats, acks)
"""
import json
from unittest.mock import AsyncMock, patch

import pytest
import websockets

from broker import Broker


# ───────────────────────── helpers ─────────────────────────

def make_ws_mock(recv_messages: list[str]):
    """Crea un mock de WebSocket que devuelve mensajes en orden y luego se queda 'colgado'."""
    ws = AsyncMock()
    ws.send = AsyncMock()
    ws.recv = AsyncMock(side_effect=recv_messages)
    ws.close = AsyncMock()
    return ws


# ───────────────────────── BinanceTrade ─────────────────────────

class TestBinanceTradeClient:
    async def test_connect_sends_subscription_payload(self):
        from trades.binance import BinanceTrade
        client = BinanceTrade.create()
        ws = make_ws_mock(["{}"])  # respuesta inicial del subscribe
        with patch("trades.binance.connect", AsyncMock(return_value=ws)):
            await client.connect()
        ws.send.assert_awaited_once()
        sent = json.loads(ws.send.await_args.args[0])
        assert sent["method"] == "SUBSCRIBE"
        assert "btcusdt@trade" in sent["params"]

    async def test_on_listen_publishes_trade(self, binance_trade_payload_buy):
        from trades.binance import BinanceTrade
        client = BinanceTrade.create()
        client.client = make_ws_mock([json.dumps(binance_trade_payload_buy)])
        with patch("trades.binance.ScrapperProducer.sendTrade", AsyncMock()) as send:
            await client.onListen()
        send.assert_awaited_once()
        published = send.await_args.args[0]
        assert published.broker == Broker.BINANCE.value
        assert published.name == "BTCUSDT"

    async def test_on_listen_reconnects_on_connection_closed(self):
        from trades.binance import BinanceTrade
        client = BinanceTrade.create()
        client.client = AsyncMock()
        client.client.recv = AsyncMock(side_effect=websockets.exceptions.ConnectionClosed(None, None))
        new_ws = make_ws_mock(["{}"])
        with patch("trades.binance.connect", AsyncMock(return_value=new_ws)):
            await client.onListen()
        # Tras reconectar, self.client apunta al nuevo WS
        assert client.client is new_ws

    async def test_on_listen_closes_on_generic_exception(self):
        from trades.binance import BinanceTrade
        client = BinanceTrade.create()
        client.client = AsyncMock()
        client.client.recv = AsyncMock(return_value="not-json{{{")
        client.client.close = AsyncMock()
        await client.onListen()  # no debe propagar
        client.client.close.assert_awaited_once()


# ───────────────────────── BybitTrade ─────────────────────────

class TestBybitTradeClient:
    async def test_subscription_args(self):
        from trades.bybit import BybitTrade
        client = BybitTrade.create()
        assert client.args["op"] == "subscribe"
        assert "publicTrade.BTCUSDT" in client.args["args"]

    async def test_on_listen_publishes(self, bybit_trade_payload):
        from trades.bybit import BybitTrade
        client = BybitTrade.create()
        client.client = make_ws_mock([json.dumps(bybit_trade_payload)])
        with patch("trades.bybit.ScrapperProducer.sendTrade", AsyncMock()) as send:
            await client.onListen()
        send.assert_awaited_once()


# ───────────────────────── KrakenTrade ─────────────────────────

class TestKrakenTradeClient:
    async def test_publishes_only_trade_channel(self, kraken_trade_payload):
        from trades.kraken import KrakenTrade
        client = KrakenTrade.create()
        client.client = make_ws_mock([json.dumps(kraken_trade_payload)])
        with patch("trades.kraken.ScrapperProducer.sendTrade", AsyncMock()) as send:
            await client.onListen()
        send.assert_awaited_once()

    async def test_ignores_heartbeat(self, kraken_trade_heartbeat):
        from trades.kraken import KrakenTrade
        client = KrakenTrade.create()
        client.client = make_ws_mock([json.dumps(kraken_trade_heartbeat)])
        with patch("trades.kraken.ScrapperProducer.sendTrade", AsyncMock()) as send:
            await client.onListen()
        send.assert_not_awaited()

    async def test_ignores_messages_without_data_key(self):
        from trades.kraken import KrakenTrade
        client = KrakenTrade.create()
        # channel=trade pero sin 'data' → no publicar
        client.client = make_ws_mock([json.dumps({"channel": "trade"})])
        with patch("trades.kraken.ScrapperProducer.sendTrade", AsyncMock()) as send:
            await client.onListen()
        send.assert_not_awaited()


# ───────────────────────── BinanceOrderBook ─────────────────────────

class TestBinanceOrderBookClient:
    async def test_connect_uses_combined_stream_endpoint(self):
        from orderbook.binance import BinanceOrderBook
        client = BinanceOrderBook.create()
        ws = make_ws_mock(["{}"])
        captured = {}

        async def fake_connect(url):
            captured["url"] = url
            return ws

        with patch("orderbook.binance.connect", side_effect=fake_connect):
            await client.connect()
        # El cliente reescribe /ws → /stream
        assert captured["url"].endswith("/stream")

    async def test_on_listen_publishes_when_data_present(self, binance_orderbook_payload):
        from orderbook.binance import BinanceOrderBook
        client = BinanceOrderBook.create()
        client.client = make_ws_mock([json.dumps(binance_orderbook_payload)])
        with patch("orderbook.binance.ScrapperProducer.sendOrderbook", AsyncMock()) as send:
            await client.onListen()
        send.assert_awaited_once()
        published = send.await_args.args[0]
        assert published.symbol == "BTCUSDT"

    async def test_on_listen_skips_subscribe_ack(self, binance_orderbook_payload_no_data):
        from orderbook.binance import BinanceOrderBook
        client = BinanceOrderBook.create()
        client.client = make_ws_mock([json.dumps(binance_orderbook_payload_no_data)])
        with patch("orderbook.binance.ScrapperProducer.sendOrderbook", AsyncMock()) as send:
            await client.onListen()
        send.assert_not_awaited()


# ───────────────────────── BybitOrderBook ─────────────────────────

class TestBybitOrderBookClient:
    async def test_subscription_args(self):
        from orderbook.bybit import BybitOrderBook
        client = BybitOrderBook.create()
        assert "orderbook.50.BTCUSDT" in client.args["args"]

    async def test_on_listen_publishes(self, bybit_orderbook_payload):
        from orderbook.bybit import BybitOrderBook
        client = BybitOrderBook.create()
        client.client = make_ws_mock([json.dumps(bybit_orderbook_payload)])
        with patch("orderbook.bybit.ScrapperProducer.sendOrderbook", AsyncMock()) as send:
            await client.onListen()
        send.assert_awaited_once()


# ───────────────────────── KrakenOrderBook ─────────────────────────

class TestKrakenOrderBookClient:
    async def test_on_listen_publishes(self, kraken_orderbook_payload):
        from orderbook.kraken import KrakenOrderBook
        client = KrakenOrderBook.create()
        client.client = make_ws_mock([json.dumps(kraken_orderbook_payload)])
        with patch("orderbook.kraken.ScrapperProducer.sendOrderbook", AsyncMock()) as send:
            await client.onListen()
        send.assert_awaited_once()
