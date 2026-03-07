from __future__ import annotations

from typing import Any

import httpx
import pytest

from upbeat._constants import API_BASE_URL
from upbeat._http import AsyncTransport, SyncTransport
from upbeat.api.markets import AsyncMarketsAPI, MarketsAPI
from upbeat.types.market import TradingPair

# ── Helpers ──────────────────────────────────────────────────────────────


def _make_transport(handler: Any, **kwargs: Any) -> SyncTransport:
    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url=API_BASE_URL
    )
    return SyncTransport(http_client=client, **kwargs)


def _make_async_transport(handler: Any, **kwargs: Any) -> AsyncTransport:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url=API_BASE_URL
    )
    return AsyncTransport(http_client=client, **kwargs)


def _json_response(
    data: Any,
    status_code: int = 200,
    remaining_req: str | None = None,
) -> httpx.Response:
    headers = {}
    if remaining_req:
        headers["Remaining-Req"] = remaining_req
    return httpx.Response(status_code, json=data, headers=headers)


# ── Fixture data ─────────────────────────────────────────────────────────


TRADING_PAIR_DATA = {
    "market": "KRW-BTC",
    "korean_name": "비트코인",
    "english_name": "Bitcoin",
}

TRADING_PAIR_DETAIL_DATA = {
    "market": "KRW-BTC",
    "korean_name": "비트코인",
    "english_name": "Bitcoin",
    "market_event": {
        "warning": False,
        "caution": {
            "PRICE_FLUCTUATIONS": False,
            "TRADING_VOLUME_SOARING": False,
            "DEPOSIT_AMOUNT_SOARING": False,
            "GLOBAL_PRICE_DIFFERENCES": False,
            "CONCENTRATION_OF_SMALL_ACCOUNTS": False,
        },
    },
}


# ── TestGetTradingPairs ──────────────────────────────────────────────────


class TestGetTradingPairs:
    def test_basic_call(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/market/all"
            assert request.url.params["is_details"] == "false"
            return _json_response([TRADING_PAIR_DATA])

        transport = _make_transport(handler)
        api = MarketsAPI(transport, None)
        result = api.get_trading_pairs()
        assert len(result) == 1
        assert isinstance(result[0], TradingPair)
        assert result[0].market == "KRW-BTC"
        assert result[0].market_event is None

    def test_is_details_true(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["is_details"] == "true"
            return _json_response([TRADING_PAIR_DETAIL_DATA])

        transport = _make_transport(handler)
        api = MarketsAPI(transport, None)
        result = api.get_trading_pairs(is_details=True)
        assert result[0].market_event is not None
        assert result[0].market_event.warning is False
        assert result[0].market_event.caution.PRICE_FLUCTUATIONS is False

    def test_no_authorization_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" not in request.headers
            return _json_response([TRADING_PAIR_DATA])

        transport = _make_transport(handler)
        api = MarketsAPI(transport, None)
        api.get_trading_pairs()


# ── TestAsyncGetTradingPairs ─────────────────────────────────────────────


class TestAsyncGetTradingPairs:
    @pytest.mark.asyncio
    async def test_basic_call(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/market/all"
            return _json_response([TRADING_PAIR_DATA])

        transport = _make_async_transport(handler)
        api = AsyncMarketsAPI(transport, None)
        result = await api.get_trading_pairs()
        assert len(result) == 1
        assert isinstance(result[0], TradingPair)

    @pytest.mark.asyncio
    async def test_is_details_true(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([TRADING_PAIR_DETAIL_DATA])

        transport = _make_async_transport(handler)
        api = AsyncMarketsAPI(transport, None)
        result = await api.get_trading_pairs(is_details=True)
        assert result[0].market_event is not None
