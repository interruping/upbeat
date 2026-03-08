from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import websockets.exceptions
from pydantic import ValidationError

from upbeat._auth import Credentials
from upbeat._errors import WebSocketClosedError, WebSocketError
from upbeat._logger import WebSocketEventInfo
from upbeat.ws._client import AsyncUpbeatWebSocket, WebSocketConnection
from upbeat.ws._payload import generate_multi_payload, generate_payload
from upbeat.ws.types import (
    CandleMessage,
    MyAssetMessage,
    MyOrderMessage,
    OrderbookMessage,
    TickerMessage,
    TradeMessage,
    parse_message,
)

# ── Fixture data ─────────────────────────────────────────────────────────

TICKER_MSG_DATA: dict[str, Any] = {
    "type": "ticker",
    "code": "KRW-BTC",
    "opening_price": 148737000.0,
    "high_price": 149360000.0,
    "low_price": 148288000.0,
    "trade_price": 148601000.0,
    "prev_closing_price": 148737000.0,
    "change": "FALL",
    "change_price": 136000.0,
    "signed_change_price": -136000.0,
    "change_rate": 0.0009143656,
    "signed_change_rate": -0.0009143656,
    "trade_volume": 0.00016823,
    "acc_trade_volume": 212.38911576,
    "acc_trade_volume_24h": 1198.26954807,
    "acc_trade_price": 31615925234.05438,
    "acc_trade_price_24h": 178448329314.96686,
    "trade_date": "20250704",
    "trade_time": "051400",
    "trade_timestamp": 1751606040365,
    "ask_bid": "BID",
    "acc_ask_volume": 100.0,
    "acc_bid_volume": 112.0,
    "highest_52_week_price": 163325000.0,
    "highest_52_week_date": "2025-01-20",
    "lowest_52_week_price": 72100000.0,
    "lowest_52_week_date": "2024-08-05",
    "market_state": "ACTIVE",
    "is_trading_suspended": False,
    "delisting_date": None,
    "market_warning": "NONE",
    "timestamp": 1751606040403,
    "stream_type": "REALTIME",
}

TRADE_MSG_DATA: dict[str, Any] = {
    "type": "trade",
    "code": "KRW-BTC",
    "trade_price": 148601000.0,
    "trade_volume": 0.00016823,
    "ask_bid": "BID",
    "prev_closing_price": 148737000.0,
    "change": "FALL",
    "change_price": 136000.0,
    "trade_date": "2025-07-04",
    "trade_time": "05:14:00",
    "trade_timestamp": 1751606040365,
    "timestamp": 1751606040403,
    "sequential_id": 17516060403650001,
    "best_ask_price": 148602000.0,
    "best_ask_size": 0.5,
    "best_bid_price": 148601000.0,
    "best_bid_size": 0.3,
    "stream_type": "REALTIME",
}

ORDERBOOK_MSG_DATA: dict[str, Any] = {
    "type": "orderbook",
    "code": "KRW-BTC",
    "total_ask_size": 10.37591054,
    "total_bid_size": 9.49577219,
    "orderbook_units": [
        {
            "ask_price": 148520000.0,
            "bid_price": 148490000.0,
            "ask_size": 0.0134662,
            "bid_size": 0.04296774,
        }
    ],
    "timestamp": 1751606867762,
    "level": 0.0,
    "stream_type": "REALTIME",
}

CANDLE_MSG_DATA: dict[str, Any] = {
    "type": "candle.1m",
    "code": "KRW-BTC",
    "candle_date_time_utc": "2025-01-02T04:28:05",
    "candle_date_time_kst": "2025-01-02T13:28:05",
    "opening_price": 145831000.0,
    "high_price": 145831000.0,
    "low_price": 145752000.0,
    "trade_price": 145759000.0,
    "candle_acc_trade_volume": 27.58904602,
    "candle_acc_trade_price": 4022470467.03403,
    "timestamp": 1751327999833,
    "stream_type": "REALTIME",
}

MY_ORDER_MSG_DATA: dict[str, Any] = {
    "type": "myOrder",
    "code": "KRW-BTC",
    "uuid": "test-uuid-1234",
    "ask_bid": "BID",
    "order_type": "limit",
    "state": "wait",
    "price": 148000000.0,
    "avg_price": 0.0,
    "volume": 0.001,
    "remaining_volume": 0.001,
    "executed_volume": 0.0,
    "trades_count": 0,
    "reserved_fee": 74.0,
    "remaining_fee": 74.0,
    "paid_fee": 0.0,
    "locked": 148074.0,
    "executed_funds": 0.0,
    "trade_timestamp": 1751606040365,
    "order_timestamp": 1751606040000,
    "timestamp": 1751606040403,
    "stream_type": "REALTIME",
}

MY_ASSET_MSG_DATA: dict[str, Any] = {
    "type": "myAsset",
    "asset_uuid": "asset-uuid-5678",
    "assets": [
        {"currency": "KRW", "balance": 1000000.0, "locked": 148074.0},
        {"currency": "BTC", "balance": 0.5, "locked": 0.0},
    ],
    "asset_timestamp": 1751606040365,
    "timestamp": 1751606040403,
    "stream_type": "REALTIME",
}


# ── Mock WebSocket ───────────────────────────────────────────────────────


class MockWebSocket:
    def __init__(self, messages: list[str]) -> None:
        self._messages = list(messages)
        self._index = 0
        self.sent: list[str] = []

    async def send(self, data: str) -> None:
        self.sent.append(data)

    async def recv(self) -> str:
        if self._index >= len(self._messages):
            raise websockets.exceptions.ConnectionClosed(None, None)
        msg = self._messages[self._index]
        self._index += 1
        return msg

    async def close(self) -> None:
        pass

    async def __aenter__(self) -> MockWebSocket:
        return self

    async def __aexit__(self, *args: object) -> None:
        pass

    def __aiter__(self) -> MockWebSocket:
        return self

    async def __anext__(self) -> str:
        if self._index >= len(self._messages):
            raise StopAsyncIteration
        msg = self._messages[self._index]
        self._index += 1
        return msg


# ── Payload Tests ────────────────────────────────────────────────────────


class TestGeneratePayload:
    def test_basic_structure(self) -> None:
        result = generate_payload(type="ticker", codes=["KRW-BTC"])
        assert len(result) == 3
        assert "ticket" in result[0]
        assert result[1]["type"] == "ticker"
        assert result[1]["codes"] == ["KRW-BTC"]
        assert result[2] == {"format": "DEFAULT"}

    def test_custom_ticket(self) -> None:
        result = generate_payload(type="ticker", codes=["KRW-BTC"], ticket="my-ticket")
        assert result[0]["ticket"] == "my-ticket"

    def test_custom_format(self) -> None:
        result = generate_payload(type="ticker", codes=["KRW-BTC"], format="SIMPLE")
        assert result[2]["format"] == "SIMPLE"

    def test_public_channel_requires_codes(self) -> None:
        with pytest.raises(ValueError, match="requires codes"):
            generate_payload(type="ticker")

    def test_trade_requires_codes(self) -> None:
        with pytest.raises(ValueError, match="requires codes"):
            generate_payload(type="trade")

    def test_orderbook_requires_codes(self) -> None:
        with pytest.raises(ValueError, match="requires codes"):
            generate_payload(type="orderbook")

    def test_candle_requires_codes(self) -> None:
        with pytest.raises(ValueError, match="requires codes"):
            generate_payload(type="candle.1m")

    def test_my_asset_rejects_codes(self) -> None:
        with pytest.raises(ValueError, match="does not accept codes"):
            generate_payload(type="myAsset", codes=["KRW-BTC"])

    def test_my_asset_without_codes(self) -> None:
        result = generate_payload(type="myAsset")
        assert result[1] == {"type": "myAsset"}

    def test_my_order_without_codes(self) -> None:
        result = generate_payload(type="myOrder")
        assert result[1] == {"type": "myOrder"}

    def test_my_order_with_codes(self) -> None:
        result = generate_payload(type="myOrder", codes=["KRW-BTC"])
        assert result[1]["codes"] == ["KRW-BTC"]

    def test_is_only_snapshot(self) -> None:
        result = generate_payload(
            type="ticker", codes=["KRW-BTC"], is_only_snapshot=True
        )
        assert result[1]["is_only_snapshot"] is True
        assert "is_only_realtime" not in result[1]

    def test_is_only_realtime(self) -> None:
        result = generate_payload(
            type="ticker", codes=["KRW-BTC"], is_only_realtime=True
        )
        assert result[1]["is_only_realtime"] is True
        assert "is_only_snapshot" not in result[1]

    def test_snapshot_and_realtime_false_excluded(self) -> None:
        result = generate_payload(
            type="ticker",
            codes=["KRW-BTC"],
            is_only_snapshot=False,
            is_only_realtime=False,
        )
        assert "is_only_snapshot" not in result[1]
        assert "is_only_realtime" not in result[1]

    def test_my_order_rejects_snapshot_realtime(self) -> None:
        with pytest.raises(ValueError, match="does not support"):
            generate_payload(type="myOrder", is_only_snapshot=True)
        with pytest.raises(ValueError, match="does not support"):
            generate_payload(type="myOrder", is_only_realtime=True)

    def test_my_asset_rejects_snapshot_realtime(self) -> None:
        with pytest.raises(ValueError, match="does not support"):
            generate_payload(type="myAsset", is_only_snapshot=True)
        with pytest.raises(ValueError, match="does not support"):
            generate_payload(type="myAsset", is_only_realtime=True)

    def test_orderbook_level(self) -> None:
        result = generate_payload(type="orderbook", codes=["KRW-BTC"], level=10000.0)
        assert result[1]["level"] == 10000.0

    def test_level_ignored_for_non_orderbook(self) -> None:
        result = generate_payload(type="ticker", codes=["KRW-BTC"], level=10000.0)
        assert "level" not in result[1]


class TestGenerateMultiPayload:
    def test_basic_merge(self) -> None:
        subs = [
            {"type": "ticker", "codes": ["KRW-BTC"]},
            {"type": "orderbook", "codes": ["KRW-ETH"]},
        ]
        result = generate_multi_payload(subs)
        assert len(result) == 4
        assert "ticket" in result[0]
        assert result[1] == subs[0]
        assert result[2] == subs[1]
        assert result[3] == {"format": "DEFAULT"}

    def test_custom_ticket_and_format(self) -> None:
        subs = [{"type": "trade", "codes": ["KRW-BTC"]}]
        result = generate_multi_payload(subs, ticket="custom-ticket", format="SIMPLE")
        assert result[0]["ticket"] == "custom-ticket"
        assert result[-1]["format"] == "SIMPLE"


# ── Type Tests ───────────────────────────────────────────────────────────


class TestMessageTypes:
    def test_ticker_message(self) -> None:
        msg = TickerMessage.model_validate(TICKER_MSG_DATA)
        assert msg.type == "ticker"
        assert msg.code == "KRW-BTC"
        assert msg.change == "FALL"
        assert msg.stream_type == "REALTIME"

    def test_trade_message(self) -> None:
        msg = TradeMessage.model_validate(TRADE_MSG_DATA)
        assert msg.type == "trade"
        assert msg.code == "KRW-BTC"
        assert msg.sequential_id == 17516060403650001

    def test_orderbook_message(self) -> None:
        msg = OrderbookMessage.model_validate(ORDERBOOK_MSG_DATA)
        assert msg.type == "orderbook"
        assert len(msg.orderbook_units) == 1
        assert msg.orderbook_units[0].ask_price == 148520000.0

    def test_candle_message(self) -> None:
        msg = CandleMessage.model_validate(CANDLE_MSG_DATA)
        assert msg.type == "candle.1m"
        assert msg.candle_date_time_utc == "2025-01-02T04:28:05"

    def test_candle_1s(self) -> None:
        data = {**CANDLE_MSG_DATA, "type": "candle.1s"}
        msg = CandleMessage.model_validate(data)
        assert msg.type == "candle.1s"

    def test_candle_240m(self) -> None:
        data = {**CANDLE_MSG_DATA, "type": "candle.240m"}
        msg = CandleMessage.model_validate(data)
        assert msg.type == "candle.240m"

    def test_my_order_message(self) -> None:
        msg = MyOrderMessage.model_validate(MY_ORDER_MSG_DATA)
        assert msg.type == "myOrder"
        assert msg.uuid == "test-uuid-1234"
        assert msg.trade_uuid is None
        assert msg.time_in_force is None

    def test_my_order_with_optional_fields(self) -> None:
        data = {
            **MY_ORDER_MSG_DATA,
            "trade_uuid": "trade-uuid",
            "time_in_force": "ioc",
            "trade_fee": 50.0,
            "is_maker": True,
            "identifier": "my-id",
            "smp_type": "reduce",
            "prevented_volume": 0.001,
            "prevented_locked": 100.0,
        }
        msg = MyOrderMessage.model_validate(data)
        assert msg.trade_uuid == "trade-uuid"
        assert msg.time_in_force == "ioc"
        assert msg.is_maker is True

    def test_my_asset_message(self) -> None:
        msg = MyAssetMessage.model_validate(MY_ASSET_MSG_DATA)
        assert msg.type == "myAsset"
        assert len(msg.assets) == 2
        assert msg.assets[0].currency == "KRW"
        assert msg.assets[1].balance == 0.5
        assert msg.stream_type == "REALTIME"

    def test_frozen_immutability(self) -> None:
        msg = TickerMessage.model_validate(TICKER_MSG_DATA)
        with pytest.raises(ValidationError):
            msg.trade_price = 999.0  # type: ignore[misc]


class TestParseMessage:
    def test_dispatch_ticker(self) -> None:
        msg = parse_message(TICKER_MSG_DATA)
        assert isinstance(msg, TickerMessage)

    def test_dispatch_trade(self) -> None:
        msg = parse_message(TRADE_MSG_DATA)
        assert isinstance(msg, TradeMessage)

    def test_dispatch_orderbook(self) -> None:
        msg = parse_message(ORDERBOOK_MSG_DATA)
        assert isinstance(msg, OrderbookMessage)

    def test_dispatch_candle(self) -> None:
        msg = parse_message(CANDLE_MSG_DATA)
        assert isinstance(msg, CandleMessage)

    def test_dispatch_candle_variants(self) -> None:
        for suffix in ["1s", "3m", "5m", "10m", "15m", "30m", "60m", "240m"]:
            data = {**CANDLE_MSG_DATA, "type": f"candle.{suffix}"}
            msg = parse_message(data)
            assert isinstance(msg, CandleMessage)

    def test_dispatch_my_order(self) -> None:
        msg = parse_message(MY_ORDER_MSG_DATA)
        assert isinstance(msg, MyOrderMessage)

    def test_dispatch_my_asset(self) -> None:
        msg = parse_message(MY_ASSET_MSG_DATA)
        assert isinstance(msg, MyAssetMessage)

    def test_unknown_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown WebSocket message type"):
            parse_message({"type": "unknown"})

    def test_empty_type_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown WebSocket message type"):
            parse_message({})


# ── Client Tests ─────────────────────────────────────────────────────────

_WS_CONNECT = "websockets.asyncio.client.connect"


class TestAsyncUpbeatWebSocket:
    @pytest.mark.asyncio
    async def test_ticker_stream(self) -> None:
        mock_ws = MockWebSocket([json.dumps(TICKER_MSG_DATA)])
        with patch(_WS_CONNECT, return_value=mock_ws):
            client = AsyncUpbeatWebSocket(None, None)
            messages = []
            async for msg in client.ticker(["KRW-BTC"]):
                messages.append(msg)
                break
            assert len(messages) == 1
            assert isinstance(messages[0], TickerMessage)

    @pytest.mark.asyncio
    async def test_trade_stream(self) -> None:
        mock_ws = MockWebSocket([json.dumps(TRADE_MSG_DATA)])
        with patch(_WS_CONNECT, return_value=mock_ws):
            client = AsyncUpbeatWebSocket(None, None)
            messages = []
            async for msg in client.trade(["KRW-BTC"]):
                messages.append(msg)
                break
            assert len(messages) == 1
            assert isinstance(messages[0], TradeMessage)

    @pytest.mark.asyncio
    async def test_orderbook_stream(self) -> None:
        mock_ws = MockWebSocket([json.dumps(ORDERBOOK_MSG_DATA)])
        with patch(_WS_CONNECT, return_value=mock_ws):
            client = AsyncUpbeatWebSocket(None, None)
            messages = []
            async for msg in client.orderbook(["KRW-BTC"]):
                messages.append(msg)
                break
            assert len(messages) == 1
            assert isinstance(messages[0], OrderbookMessage)

    @pytest.mark.asyncio
    async def test_candle_stream(self) -> None:
        mock_ws = MockWebSocket([json.dumps(CANDLE_MSG_DATA)])
        with patch(_WS_CONNECT, return_value=mock_ws):
            client = AsyncUpbeatWebSocket(None, None)
            messages = []
            async for msg in client.candle(["KRW-BTC"]):
                messages.append(msg)
                break
            assert len(messages) == 1
            assert isinstance(messages[0], CandleMessage)

    @pytest.mark.asyncio
    async def test_skips_up_status_message(self) -> None:
        mock_ws = MockWebSocket(['"UP"', json.dumps(TICKER_MSG_DATA)])
        with patch(_WS_CONNECT, return_value=mock_ws):
            client = AsyncUpbeatWebSocket(None, None)
            messages = []
            async for msg in client.ticker(["KRW-BTC"]):
                messages.append(msg)
                break
            assert len(messages) == 1
            assert isinstance(messages[0], TickerMessage)

    @pytest.mark.asyncio
    async def test_error_message_raises(self) -> None:
        error_msg = json.dumps(
            {"error": {"name": "NO_CODES", "message": "codes is required"}}
        )
        mock_ws = MockWebSocket([error_msg])
        with patch(_WS_CONNECT, return_value=mock_ws):
            client = AsyncUpbeatWebSocket(None, None)
            with pytest.raises(WebSocketError, match="NO_CODES"):
                async for _ in client.ticker(["KRW-BTC"]):
                    pass

    @pytest.mark.asyncio
    async def test_private_requires_credentials(self) -> None:
        client = AsyncUpbeatWebSocket(None, None)
        with pytest.raises(WebSocketError, match="Credentials required"):
            async for _ in client.my_orders():
                pass

    @pytest.mark.asyncio
    async def test_private_sends_auth_header(self) -> None:
        mock_ws = MockWebSocket([json.dumps(MY_ORDER_MSG_DATA)])
        creds = Credentials(access_key="test-key", secret_key="test-secret")

        with patch(_WS_CONNECT, return_value=mock_ws) as mock_connect:
            client = AsyncUpbeatWebSocket(creds, None)
            async for _msg in client.my_orders():
                break
            call_kwargs = mock_connect.call_args
            headers = call_kwargs.kwargs.get("additional_headers", {})
            assert "Authorization" in headers
            assert headers["Authorization"].startswith("Bearer ")

    @pytest.mark.asyncio
    async def test_sends_subscription_payload(self) -> None:
        mock_ws = MockWebSocket([json.dumps(TICKER_MSG_DATA)])
        with patch(_WS_CONNECT, return_value=mock_ws):
            client = AsyncUpbeatWebSocket(None, None)
            async for _ in client.ticker(["KRW-BTC", "KRW-ETH"]):
                break
            assert len(mock_ws.sent) == 1
            payload = json.loads(mock_ws.sent[0])
            assert len(payload) == 3
            assert payload[1]["type"] == "ticker"
            assert payload[1]["codes"] == ["KRW-BTC", "KRW-ETH"]

    @pytest.mark.asyncio
    async def test_logger_on_connect(self) -> None:
        mock_ws = MockWebSocket([json.dumps(TICKER_MSG_DATA)])
        logger = MagicMock()
        with patch(_WS_CONNECT, return_value=mock_ws):
            client = AsyncUpbeatWebSocket(None, logger)
            async for _ in client.ticker(["KRW-BTC"]):
                break
        logger.on_ws_event.assert_called()
        call_args = logger.on_ws_event.call_args_list[0]
        info = call_args[0][0]
        assert isinstance(info, WebSocketEventInfo)
        assert info.event == "connect"

    @pytest.mark.asyncio
    async def test_handles_bytes_message(self) -> None:
        mock_ws = MockWebSocket([])
        mock_ws._messages = [json.dumps(TICKER_MSG_DATA).encode("utf-8")]
        with patch(_WS_CONNECT, return_value=mock_ws):
            client = AsyncUpbeatWebSocket(None, None)
            async for msg in client.ticker(["KRW-BTC"]):
                assert isinstance(msg, TickerMessage)
                break


class TestWebSocketConnection:
    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        mock_ws = MockWebSocket(
            [json.dumps(TICKER_MSG_DATA), json.dumps(TRADE_MSG_DATA)]
        )
        mock_connect = AsyncMock(return_value=mock_ws)
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch(_WS_CONNECT, return_value=mock_connect):
            conn = WebSocketConnection(credentials=None, logger=None, private=False)
            async with conn as ws:
                ws.subscribe_ticker(["KRW-BTC"])
                msg = await ws.__anext__()
                assert isinstance(msg, TickerMessage)

    @pytest.mark.asyncio
    async def test_subscribe_methods_register(self) -> None:
        conn = WebSocketConnection(credentials=None, logger=None, private=False)
        conn.subscribe_ticker(["KRW-BTC"])
        conn.subscribe_trade(["KRW-ETH"], is_only_realtime=True)
        conn.subscribe_orderbook(["KRW-BTC"], level=10000.0)
        conn.subscribe_candle(["KRW-BTC"], type="candle.5m")
        conn.subscribe_my_orders(codes=["KRW-BTC"])
        conn.subscribe_my_assets()

        assert len(conn._subscriptions) == 6
        assert conn._subscriptions[0]["type"] == "ticker"
        assert conn._subscriptions[1]["is_only_realtime"] is True
        assert conn._subscriptions[2]["level"] == 10000.0
        assert conn._subscriptions[3]["type"] == "candle.5m"
        assert conn._subscriptions[4]["type"] == "myOrder"
        assert conn._subscriptions[5]["type"] == "myAsset"

    @pytest.mark.asyncio
    async def test_private_requires_credentials(self) -> None:
        conn = WebSocketConnection(credentials=None, logger=None, private=True)
        with pytest.raises(WebSocketError, match="Credentials required"):
            async with conn:
                pass

    @pytest.mark.asyncio
    async def test_connection_closed_raises(self) -> None:
        mock_ws = MockWebSocket([])
        mock_connect = AsyncMock(return_value=mock_ws)
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch(_WS_CONNECT, return_value=mock_connect):
            conn = WebSocketConnection(credentials=None, logger=None, private=False)
            async with conn as ws:
                ws.subscribe_ticker(["KRW-BTC"])
                with pytest.raises(WebSocketClosedError):
                    await ws.__anext__()

    @pytest.mark.asyncio
    async def test_skips_up_message(self) -> None:
        mock_ws = MockWebSocket(['"UP"', json.dumps(TICKER_MSG_DATA)])
        mock_connect = AsyncMock(return_value=mock_ws)
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch(_WS_CONNECT, return_value=mock_connect):
            conn = WebSocketConnection(credentials=None, logger=None, private=False)
            async with conn as ws:
                ws.subscribe_ticker(["KRW-BTC"])
                msg = await ws.__anext__()
                assert isinstance(msg, TickerMessage)

    @pytest.mark.asyncio
    async def test_error_message_raises(self) -> None:
        error_msg = json.dumps(
            {"error": {"name": "WRONG_FORMAT", "message": "wrong format"}}
        )
        mock_ws = MockWebSocket([error_msg])
        mock_connect = AsyncMock(return_value=mock_ws)
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch(_WS_CONNECT, return_value=mock_connect):
            conn = WebSocketConnection(credentials=None, logger=None, private=False)
            async with conn as ws:
                ws.subscribe_ticker(["KRW-BTC"])
                with pytest.raises(WebSocketError, match="WRONG_FORMAT"):
                    await ws.__anext__()

    @pytest.mark.asyncio
    async def test_sends_payload_on_first_next(self) -> None:
        mock_ws = MockWebSocket([json.dumps(TICKER_MSG_DATA)])
        mock_connect = AsyncMock(return_value=mock_ws)
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch(_WS_CONNECT, return_value=mock_connect):
            conn = WebSocketConnection(credentials=None, logger=None, private=False)
            async with conn as ws:
                ws.subscribe_ticker(["KRW-BTC"])
                assert len(mock_ws.sent) == 0
                await ws.__anext__()
                assert len(mock_ws.sent) == 1
                payload = json.loads(mock_ws.sent[0])
                assert "ticket" in payload[0]
                assert payload[1]["type"] == "ticker"
                assert payload[-1] == {"format": "DEFAULT"}

    @pytest.mark.asyncio
    async def test_private_sends_auth(self) -> None:
        mock_ws = MockWebSocket([json.dumps(MY_ORDER_MSG_DATA)])
        creds = Credentials(access_key="test-key", secret_key="test-secret")
        mock_connect = AsyncMock(return_value=mock_ws)
        mock_connect.__aenter__ = AsyncMock(return_value=mock_ws)
        mock_connect.__aexit__ = AsyncMock(return_value=None)

        with patch(_WS_CONNECT, return_value=mock_connect) as mock_conn:
            conn = WebSocketConnection(credentials=creds, logger=None, private=True)
            async with conn as ws:
                ws.subscribe_my_orders()
                await ws.__anext__()
            call_kwargs = mock_conn.call_args
            headers = call_kwargs.kwargs.get("additional_headers", {})
            assert "Authorization" in headers
