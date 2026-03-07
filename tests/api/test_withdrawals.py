from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from upbeat._auth import Credentials
from upbeat._constants import API_BASE_URL
from upbeat._http import AsyncTransport, SyncTransport
from upbeat.api.withdrawals import AsyncWithdrawalsAPI, WithdrawalsAPI
from upbeat.types.withdrawal import (
    Withdrawal,
    WithdrawalAddress,
    WithdrawalChance,
    WithdrawalKrw,
)

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

# ── Shared fixture data ─────────────────────────────────────────────────

WITHDRAWAL_DATA: dict[str, Any] = {
    "type": "withdraw",
    "uuid": "wd-uuid-1",
    "currency": "BTC",
    "net_type": "BTC",
    "txid": "txid-xyz789",
    "state": "done",
    "created_at": "2024-01-01T00:00:00+09:00",
    "done_at": "2024-01-01T00:10:00+09:00",
    "amount": "0.01",
    "fee": "0.0005",
    "transaction_type": "default",
    "is_cancelable": False,
}

WITHDRAWAL_KRW_DATA: dict[str, Any] = {
    "type": "withdraw",
    "uuid": "wd-krw-uuid-1",
    "currency": "KRW",
    "txid": None,
    "state": "submitting",
    "created_at": "2024-01-01T00:00:00+09:00",
    "done_at": None,
    "amount": "50000",
    "fee": "1000",
    "transaction_type": "default",
    "is_cancelable": True,
}

WITHDRAWAL_ADDRESS_DATA: dict[str, Any] = {
    "currency": "BTC",
    "net_type": "BTC",
    "network_name": "Bitcoin",
    "withdraw_address": "3NtEbBpFCcAqECjagSVERCCsKKsgdTG8uZ",
    "secondary_address": None,
}

WITHDRAWAL_CHANCE_DATA: dict[str, Any] = {
    "member_level": {
        "security_level": 3,
        "fee_level": 0,
        "email_verified": True,
        "identity_auth_verified": True,
        "bank_account_verified": True,
        "two_factor_auth_verified": True,
        "locked": False,
        "wallet_locked": False,
    },
    "currency": {
        "code": "BTC",
        "withdraw_fee": "0.0005",
        "is_coin": True,
        "wallet_state": "working",
        "wallet_support": ["deposit", "withdraw"],
    },
    "account": {
        "currency": "BTC",
        "balance": "0.5",
        "locked": "0.0",
        "avg_buy_price": "50000000",
        "avg_buy_price_modified": False,
        "unit_currency": "KRW",
    },
    "withdraw_limit": {
        "currency": "BTC",
        "onetime": "10",
        "daily": "100",
        "remaining_daily": "100",
        "remaining_daily_fiat": "5000000000",
        "fiat_currency": "KRW",
        "minimum": "0.001",
        "fixed": 8,
        "can_withdraw": True,
    },
}


# ── TestGetWithdrawal ────────────────────────────────────────────────────


class TestGetWithdrawal:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/withdraw"
            assert request.method == "GET"
            return _json_response(WITHDRAWAL_DATA)

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        api.get(uuid="wd-uuid-1")

    def test_query_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["uuid"] == "wd-uuid-1"
            assert request.url.params["currency"] == "BTC"
            return _json_response(WITHDRAWAL_DATA)

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        api.get(uuid="wd-uuid-1", currency="BTC")

    def test_authorization_header_present(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" in request.headers
            assert request.headers["Authorization"].startswith("Bearer ")
            return _json_response(WITHDRAWAL_DATA)

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        api.get(uuid="wd-uuid-1")

    def test_parses_response(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(WITHDRAWAL_DATA)

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        result = api.get(uuid="wd-uuid-1")
        assert isinstance(result, Withdrawal)
        assert result.uuid == "wd-uuid-1"
        assert result.currency == "BTC"
        assert result.state == "done"


# ── TestListWithdrawals ──────────────────────────────────────────────────


class TestListWithdrawals:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/withdraws"
            assert request.method == "GET"
            return _json_response([WITHDRAWAL_DATA])

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        result = api.list()
        assert len(result) == 1
        assert isinstance(result[0], Withdrawal)

    def test_array_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            params = str(request.url)
            assert "uuids%5B%5D=u1" in params or "uuids[]=u1" in params
            assert "txids%5B%5D=t1" in params or "txids[]=t1" in params
            return _json_response([WITHDRAWAL_DATA])

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        api.list(uuids=["u1", "u2"], txids=["t1"])

    def test_from_cursor_mapping(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["from"] == "cursor-456"
            return _json_response([WITHDRAWAL_DATA])

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        api.list(from_cursor="cursor-456")


# ── TestCreateCoinWithdrawal ─────────────────────────────────────────────


class TestCreateCoinWithdrawal:
    def test_post_with_json_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/withdraws/coin"
            assert request.method == "POST"
            body = json.loads(request.content)
            assert body["currency"] == "BTC"
            assert body["net_type"] == "BTC"
            assert body["amount"] == "0.01"
            assert body["address"] == "3Ntx..."
            return _json_response(WITHDRAWAL_DATA)

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        result = api.create_coin(
            currency="BTC", net_type="BTC", amount="0.01", address="3Ntx..."
        )
        assert isinstance(result, Withdrawal)


# ── TestCancelCoinWithdrawal ─────────────────────────────────────────────


class TestCancelCoinWithdrawal:
    def test_delete_with_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/withdraws/coin"
            assert request.method == "DELETE"
            assert request.url.params["uuid"] == "wd-uuid-1"
            return _json_response(WITHDRAWAL_DATA)

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        result = api.cancel_coin(uuid="wd-uuid-1")
        assert isinstance(result, Withdrawal)


# ── TestCreateKrwWithdrawal ──────────────────────────────────────────────


class TestCreateKrwWithdrawal:
    def test_post_with_json_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/withdraws/krw"
            assert request.method == "POST"
            body = json.loads(request.content)
            assert body["amount"] == "50000"
            assert body["two_factor_type"] == "kakao_pay"
            return _json_response(WITHDRAWAL_KRW_DATA)

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        result = api.create_krw(amount="50000", two_factor_type="kakao_pay")
        assert isinstance(result, WithdrawalKrw)
        assert result.currency == "KRW"


# ── TestListWithdrawalAddresses ──────────────────────────────────────────


class TestListWithdrawalAddresses:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/withdraws/coin_addresses"
            return _json_response([WITHDRAWAL_ADDRESS_DATA])

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        result = api.list_coin_addresses()
        assert len(result) == 1
        assert isinstance(result[0], WithdrawalAddress)
        assert result[0].network_name == "Bitcoin"


# ── TestGetWithdrawalChance ──────────────────────────────────────────────


class TestGetWithdrawalChance:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/withdraws/chance"
            assert request.url.params["currency"] == "BTC"
            return _json_response(WITHDRAWAL_CHANCE_DATA)

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        result = api.get_chance(currency="BTC")
        assert isinstance(result, WithdrawalChance)

    def test_parses_nested_objects(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(WITHDRAWAL_CHANCE_DATA)

        transport = _make_transport(handler)
        api = WithdrawalsAPI(transport, CREDENTIALS)
        result = api.get_chance(currency="BTC")
        assert result.member_level.security_level == 3
        assert result.member_level.locked is False
        assert result.currency.code == "BTC"
        assert result.currency.is_coin is True
        assert result.account.balance == "0.5"
        assert result.withdraw_limit.can_withdraw is True
        assert result.withdraw_limit.fixed == 8


# ── TestAsyncWithdrawals ─────────────────────────────────────────────────


class TestAsyncWithdrawals:
    @pytest.mark.asyncio
    async def test_get(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/withdraw"
            return _json_response(WITHDRAWAL_DATA)

        transport = _make_async_transport(handler)
        api = AsyncWithdrawalsAPI(transport, CREDENTIALS)
        result = await api.get(uuid="wd-uuid-1")
        assert isinstance(result, Withdrawal)

    @pytest.mark.asyncio
    async def test_list(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([WITHDRAWAL_DATA])

        transport = _make_async_transport(handler)
        api = AsyncWithdrawalsAPI(transport, CREDENTIALS)
        result = await api.list()
        assert len(result) == 1
        assert isinstance(result[0], Withdrawal)

    @pytest.mark.asyncio
    async def test_get_chance(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(WITHDRAWAL_CHANCE_DATA)

        transport = _make_async_transport(handler)
        api = AsyncWithdrawalsAPI(transport, CREDENTIALS)
        result = await api.get_chance(currency="BTC")
        assert isinstance(result, WithdrawalChance)

    @pytest.mark.asyncio
    async def test_create_coin(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.method == "POST"
            return _json_response(WITHDRAWAL_DATA)

        transport = _make_async_transport(handler)
        api = AsyncWithdrawalsAPI(transport, CREDENTIALS)
        result = await api.create_coin(
            currency="BTC", net_type="BTC", amount="0.01", address="3Ntx..."
        )
        assert isinstance(result, Withdrawal)
