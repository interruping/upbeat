from __future__ import annotations

from typing import Any

import httpx
import pytest

from upbeat._auth import Credentials
from upbeat._constants import API_BASE_URL
from upbeat._http import AsyncTransport, SyncTransport
from upbeat.api.accounts import AccountsAPI, AsyncAccountsAPI
from upbeat.types.account import Account

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


def _json_response(data: Any, status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code, json=data)


CREDENTIALS = Credentials(access_key="test-access-key", secret_key="test-secret-key")

# ── Fixture data ─────────────────────────────────────────────────────────

ACCOUNT_DATA = {
    "currency": "KRW",
    "balance": "1000000.0",
    "locked": "0.0",
    "avg_buy_price": "0",
    "avg_buy_price_modified": False,
    "unit_currency": "KRW",
}

ACCOUNT_BTC_DATA = {
    "currency": "BTC",
    "balance": "0.5",
    "locked": "0.1",
    "avg_buy_price": "50000000",
    "avg_buy_price_modified": False,
    "unit_currency": "KRW",
}


# ── TestListAccounts ─────────────────────────────────────────────────────


class TestListAccounts:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/accounts"
            assert request.method == "GET"
            return _json_response([ACCOUNT_DATA])

        transport = _make_transport(handler)
        api = AccountsAPI(transport, CREDENTIALS)
        api.list()

    def test_authorization_header_present(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" in request.headers
            assert request.headers["Authorization"].startswith("Bearer ")
            return _json_response([ACCOUNT_DATA])

        transport = _make_transport(handler)
        api = AccountsAPI(transport, CREDENTIALS)
        api.list()

    def test_parses_account_fields(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([ACCOUNT_DATA])

        transport = _make_transport(handler)
        api = AccountsAPI(transport, CREDENTIALS)
        result = api.list()
        assert len(result) == 1
        account = result[0]
        assert isinstance(account, Account)
        assert account.currency == "KRW"
        assert account.balance == "1000000.0"
        assert account.locked == "0.0"
        assert account.avg_buy_price == "0"
        assert account.avg_buy_price_modified is False
        assert account.unit_currency == "KRW"

    def test_returns_multiple_accounts(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([ACCOUNT_DATA, ACCOUNT_BTC_DATA])

        transport = _make_transport(handler)
        api = AccountsAPI(transport, CREDENTIALS)
        result = api.list()
        assert len(result) == 2
        assert result[0].currency == "KRW"
        assert result[1].currency == "BTC"


# ── TestAsyncListAccounts ────────────────────────────────────────────────


class TestAsyncListAccounts:
    @pytest.mark.asyncio
    async def test_basic_call(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/accounts"
            return _json_response([ACCOUNT_DATA])

        transport = _make_async_transport(handler)
        api = AsyncAccountsAPI(transport, CREDENTIALS)
        result = await api.list()
        assert len(result) == 1
        assert isinstance(result[0], Account)

    @pytest.mark.asyncio
    async def test_authorization_header_present(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" in request.headers
            assert request.headers["Authorization"].startswith("Bearer ")
            return _json_response([ACCOUNT_DATA])

        transport = _make_async_transport(handler)
        api = AsyncAccountsAPI(transport, CREDENTIALS)
        await api.list()
