from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import TypeVar

import websockets
import websockets.asyncio.client
import websockets.exceptions
from pydantic import BaseModel

from upbeat._auth import Credentials, build_auth_header
from upbeat._constants import WS_PRIVATE_URL, WS_PUBLIC_URL
from upbeat._errors import (
    WebSocketClosedError,
    WebSocketConnectionError,
    WebSocketError,
)
from upbeat._logger import Logger, WebSocketEventInfo
from upbeat.ws._payload import generate_payload
from upbeat.ws.types import (
    CandleMessage,
    MyAssetMessage,
    MyOrderMessage,
    OrderbookMessage,
    TickerMessage,
    TradeMessage,
    WebSocketMessage,
    parse_message,
)

_T = TypeVar("_T", bound=BaseModel)

_MAX_RECONNECT_DELAY = 60.0
_INITIAL_RECONNECT_DELAY = 1.0


class AsyncUpbeatWebSocket:
    def __init__(
        self,
        credentials: Credentials | None,
        logger: Logger | None,
    ) -> None:
        self._credentials = credentials
        self._logger = logger

    # ── Single-channel convenience methods ────────────────────────────

    async def ticker(
        self,
        codes: list[str],
        *,
        is_only_snapshot: bool = False,
        is_only_realtime: bool = False,
    ) -> AsyncIterator[TickerMessage]:
        payload = generate_payload(
            type="ticker",
            codes=codes,
            is_only_snapshot=is_only_snapshot,
            is_only_realtime=is_only_realtime,
        )
        async for msg in self._stream(WS_PUBLIC_URL, payload, TickerMessage):
            yield msg

    async def trade(
        self,
        codes: list[str],
        *,
        is_only_snapshot: bool = False,
        is_only_realtime: bool = False,
    ) -> AsyncIterator[TradeMessage]:
        payload = generate_payload(
            type="trade",
            codes=codes,
            is_only_snapshot=is_only_snapshot,
            is_only_realtime=is_only_realtime,
        )
        async for msg in self._stream(WS_PUBLIC_URL, payload, TradeMessage):
            yield msg

    async def orderbook(
        self,
        codes: list[str],
        *,
        level: float | None = None,
        is_only_snapshot: bool = False,
        is_only_realtime: bool = False,
    ) -> AsyncIterator[OrderbookMessage]:
        payload = generate_payload(
            type="orderbook",
            codes=codes,
            level=level,
            is_only_snapshot=is_only_snapshot,
            is_only_realtime=is_only_realtime,
        )
        async for msg in self._stream(WS_PUBLIC_URL, payload, OrderbookMessage):
            yield msg

    async def candle(
        self,
        codes: list[str],
        *,
        type: str = "candle.1m",
        is_only_snapshot: bool = False,
        is_only_realtime: bool = False,
    ) -> AsyncIterator[CandleMessage]:
        payload = generate_payload(
            type=type,
            codes=codes,
            is_only_snapshot=is_only_snapshot,
            is_only_realtime=is_only_realtime,
        )
        async for msg in self._stream(WS_PUBLIC_URL, payload, CandleMessage):
            yield msg

    async def my_orders(
        self,
        codes: list[str] | None = None,
    ) -> AsyncIterator[MyOrderMessage]:
        payload = generate_payload(type="myOrder", codes=codes)
        async for msg in self._stream(
            WS_PRIVATE_URL, payload, MyOrderMessage, is_private=True
        ):
            yield msg

    async def my_assets(self) -> AsyncIterator[MyAssetMessage]:
        payload = generate_payload(type="myAsset")
        async for msg in self._stream(
            WS_PRIVATE_URL, payload, MyAssetMessage, is_private=True
        ):
            yield msg

    # ── connect() — multi-channel context manager ─────────────────────

    def connect(self, *, private: bool = False) -> WebSocketConnection:
        return WebSocketConnection(
            credentials=self._credentials,
            logger=self._logger,
            private=private,
        )

    # ── Core stream loop with auto-reconnect ──────────────────────────

    async def _stream(
        self,
        url: str,
        payload: list[dict[str, object]],
        model: type[_T],
        *,
        is_private: bool = False,
    ) -> AsyncIterator[_T]:
        if is_private and self._credentials is None:
            raise WebSocketError("Credentials required for private WebSocket channels")

        delay = _INITIAL_RECONNECT_DELAY
        while True:
            headers: dict[str, str] = {}
            if is_private and self._credentials is not None:
                headers["Authorization"] = build_auth_header(self._credentials)

            try:
                async with websockets.asyncio.client.connect(
                    url,
                    additional_headers=headers,
                    ping_interval=60,
                    ping_timeout=20,
                ) as ws:
                    await ws.send(json.dumps(payload))
                    self._log("connect", url)
                    delay = _INITIAL_RECONNECT_DELAY

                    async for raw in ws:
                        msg = self._process_raw(raw, model)
                        if msg is not None:
                            yield msg

            except websockets.exceptions.ConnectionClosed as exc:
                self._log("disconnect", url, error=exc)
                await asyncio.sleep(delay)
                delay = min(delay * 2, _MAX_RECONNECT_DELAY)
                continue

            except OSError as exc:
                self._log("connection_error", url, error=exc)
                raise WebSocketConnectionError(str(exc)) from exc

    # ── Helpers ───────────────────────────────────────────────────────

    def _process_raw(self, raw: str | bytes, model: type[_T]) -> _T | None:
        text = raw.decode("utf-8") if isinstance(raw, bytes) else raw

        if text.strip() == '"UP"' or text.strip() == "UP":
            return None

        data = json.loads(text)

        if isinstance(data, dict) and "error" in data:
            error_obj = data["error"]
            name = error_obj.get("name", "UNKNOWN")
            message = error_obj.get("message", "")
            raise WebSocketError(f"{name}: {message}")

        return model.model_validate(data)

    def _log(
        self,
        event: str,
        url: str,
        *,
        error: Exception | None = None,
    ) -> None:
        if self._logger is not None:
            self._logger.on_ws_event(
                WebSocketEventInfo(event=event, url=url, error=error)
            )


# ── WebSocketConnection — multi-channel context manager ───────────────


class WebSocketConnection:
    def __init__(
        self,
        *,
        credentials: Credentials | None,
        logger: Logger | None,
        private: bool,
    ) -> None:
        self._credentials = credentials
        self._logger = logger
        self._private = private
        self._subscriptions: list[dict[str, object]] = []
        self._ws: websockets.asyncio.client.ClientConnection | None = None
        self._payload_sent = False

    # ── Subscribe methods (synchronous registration) ──────────────────

    def subscribe_ticker(
        self,
        codes: list[str],
        *,
        is_only_snapshot: bool = False,
        is_only_realtime: bool = False,
    ) -> None:
        sub: dict[str, object] = {"type": "ticker", "codes": codes}
        if is_only_snapshot:
            sub["isOnlySnapshot"] = True
        if is_only_realtime:
            sub["isOnlyRealtime"] = True
        self._subscriptions.append(sub)

    def subscribe_trade(
        self,
        codes: list[str],
        *,
        is_only_snapshot: bool = False,
        is_only_realtime: bool = False,
    ) -> None:
        sub: dict[str, object] = {"type": "trade", "codes": codes}
        if is_only_snapshot:
            sub["isOnlySnapshot"] = True
        if is_only_realtime:
            sub["isOnlyRealtime"] = True
        self._subscriptions.append(sub)

    def subscribe_orderbook(
        self,
        codes: list[str],
        *,
        level: float | None = None,
        is_only_snapshot: bool = False,
        is_only_realtime: bool = False,
    ) -> None:
        sub: dict[str, object] = {"type": "orderbook", "codes": codes}
        if level is not None:
            sub["level"] = level
        if is_only_snapshot:
            sub["isOnlySnapshot"] = True
        if is_only_realtime:
            sub["isOnlyRealtime"] = True
        self._subscriptions.append(sub)

    def subscribe_candle(
        self,
        codes: list[str],
        *,
        type: str = "candle.1m",
        is_only_snapshot: bool = False,
        is_only_realtime: bool = False,
    ) -> None:
        sub: dict[str, object] = {"type": type, "codes": codes}
        if is_only_snapshot:
            sub["isOnlySnapshot"] = True
        if is_only_realtime:
            sub["isOnlyRealtime"] = True
        self._subscriptions.append(sub)

    def subscribe_my_orders(self, codes: list[str] | None = None) -> None:
        sub: dict[str, object] = {"type": "myOrder"}
        if codes is not None:
            sub["codes"] = codes
        self._subscriptions.append(sub)

    def subscribe_my_assets(self) -> None:
        self._subscriptions.append({"type": "myAsset"})

    # ── Async context manager ─────────────────────────────────────────

    async def __aenter__(self) -> WebSocketConnection:
        if self._private and self._credentials is None:
            raise WebSocketError("Credentials required for private WebSocket channels")

        url = WS_PRIVATE_URL if self._private else WS_PUBLIC_URL
        headers: dict[str, str] = {}
        if self._private and self._credentials is not None:
            headers["Authorization"] = build_auth_header(self._credentials)

        self._ws = await websockets.asyncio.client.connect(
            url,
            additional_headers=headers,
            ping_interval=60,
            ping_timeout=20,
        ).__aenter__()

        self._log("connect", url)
        return self

    async def __aexit__(self, *_args: object) -> None:
        if self._ws is not None:
            url = WS_PRIVATE_URL if self._private else WS_PUBLIC_URL
            await self._ws.close()
            self._log("disconnect", url)
            self._ws = None

    # ── Async iterator ────────────────────────────────────────────────

    def __aiter__(self) -> WebSocketConnection:
        return self

    async def __anext__(self) -> WebSocketMessage:
        if self._ws is None:
            raise StopAsyncIteration

        if not self._payload_sent:
            await self._send_subscriptions()
            self._payload_sent = True

        while True:
            try:
                raw = await self._ws.recv()
            except websockets.exceptions.ConnectionClosed as exc:
                code = exc.rcvd.code if exc.rcvd else None
                reason = str(exc.rcvd.reason) if exc.rcvd else None
                raise WebSocketClosedError(str(exc), code=code, reason=reason) from exc

            text = raw.decode("utf-8") if isinstance(raw, bytes) else raw

            if text.strip() == '"UP"' or text.strip() == "UP":
                continue

            data = json.loads(text)

            if isinstance(data, dict) and "error" in data:
                error_obj = data["error"]
                name = error_obj.get("name", "UNKNOWN")
                message = error_obj.get("message", "")
                raise WebSocketError(f"{name}: {message}")

            return parse_message(data)

    # ── Internal ──────────────────────────────────────────────────────

    async def _send_subscriptions(self) -> None:
        if self._ws is None or not self._subscriptions:
            return

        import uuid

        payload: list[dict[str, object]] = [{"ticket": str(uuid.uuid4())}]
        payload.extend(self._subscriptions)
        payload.append({"format": "DEFAULT"})
        await self._ws.send(json.dumps(payload))

    def _log(
        self,
        event: str,
        url: str,
        *,
        error: Exception | None = None,
    ) -> None:
        if self._logger is not None:
            self._logger.on_ws_event(
                WebSocketEventInfo(event=event, url=url, error=error)
            )
