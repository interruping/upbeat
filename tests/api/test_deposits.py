from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from upbeat._auth import Credentials
from upbeat._constants import API_BASE_URL
from upbeat._http import AsyncTransport, SyncTransport
from upbeat.api.deposits import AsyncDepositsAPI, DepositsAPI
from upbeat.types.deposit import (
    Deposit,
    DepositAddress,
    DepositAddressCreated,
    DepositChanceCoin,
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

DEPOSIT_DATA: dict[str, Any] = {
    "type": "deposit",
    "uuid": "dep-uuid-1",
    "currency": "BTC",
    "net_type": "BTC",
    "txid": "txid-abc123",
    "state": "accepted",
    "created_at": "2024-01-01T00:00:00+09:00",
    "done_at": "2024-01-01T00:01:00+09:00",
    "amount": "0.005",
    "fee": "0",
    "transaction_type": "default",
}

DEPOSIT_ADDRESS_DATA: dict[str, Any] = {
    "currency": "BTC",
    "net_type": "BTC",
    "deposit_address": "3NtEbBpFCcAqECjagSVERCCsKKsgdTG8uZ",
    "secondary_address": None,
}

DEPOSIT_ADDRESS_CREATED_DATA: dict[str, Any] = {
    "success": True,
    "message": "BTC 입금주소를 생성중입니다.",
}

DEPOSIT_CHANCE_COIN_DATA: dict[str, Any] = {
    "currency": "BTC",
    "net_type": "BTC",
    "is_deposit_possible": True,
    "deposit_impossible_reason": "",
    "minimum_deposit_amount": "0.0005",
    "minimum_deposit_confirmations": 3,
    "decimal_precision": 8,
}


# ── TestGetDeposit ───────────────────────────────────────────────────────


class TestGetDeposit:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/deposit"
            assert request.method == "GET"
            return _json_response(DEPOSIT_DATA)

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        api.get(uuid="dep-uuid-1")

    def test_query_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["uuid"] == "dep-uuid-1"
            assert request.url.params["currency"] == "BTC"
            return _json_response(DEPOSIT_DATA)

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        api.get(uuid="dep-uuid-1", currency="BTC")

    def test_authorization_header_present(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" in request.headers
            assert request.headers["Authorization"].startswith("Bearer ")
            return _json_response(DEPOSIT_DATA)

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        api.get(uuid="dep-uuid-1")

    def test_parses_response(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(DEPOSIT_DATA)

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        result = api.get(uuid="dep-uuid-1")
        assert isinstance(result, Deposit)
        assert result.uuid == "dep-uuid-1"
        assert result.currency == "BTC"
        assert result.state == "accepted"


# ── TestListDeposits ─────────────────────────────────────────────────────


class TestListDeposits:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/deposits"
            assert request.method == "GET"
            return _json_response([DEPOSIT_DATA])

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        result = api.list()
        assert len(result) == 1
        assert isinstance(result[0], Deposit)

    def test_array_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            params = str(request.url)
            assert "uuids%5B%5D=u1" in params or "uuids[]=u1" in params
            assert "txids%5B%5D=t1" in params or "txids[]=t1" in params
            return _json_response([DEPOSIT_DATA])

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        api.list(uuids=["u1", "u2"], txids=["t1"])

    def test_from_cursor_mapping(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["from"] == "cursor-123"
            return _json_response([DEPOSIT_DATA])

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        api.list(from_cursor="cursor-123")


# ── TestGenerateCoinAddress ──────────────────────────────────────────────


class TestGenerateCoinAddress:
    def test_post_request(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/deposits/generate_coin_address"
            assert request.method == "POST"
            body = json.loads(request.content)
            assert body["currency"] == "BTC"
            assert body["net_type"] == "BTC"
            return _json_response(DEPOSIT_ADDRESS_DATA)

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        result = api.generate_coin_address(currency="BTC", net_type="BTC")
        assert isinstance(result, DepositAddress)

    def test_returns_deposit_address_on_200(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(DEPOSIT_ADDRESS_DATA, status_code=200)

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        result = api.generate_coin_address(currency="BTC", net_type="BTC")
        assert isinstance(result, DepositAddress)
        assert result.deposit_address == "3NtEbBpFCcAqECjagSVERCCsKKsgdTG8uZ"

    def test_returns_deposit_address_created_on_201(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(DEPOSIT_ADDRESS_CREATED_DATA, status_code=201)

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        result = api.generate_coin_address(currency="BTC", net_type="BTC")
        assert isinstance(result, DepositAddressCreated)
        assert result.success is True


# ── TestGetCoinAddress ───────────────────────────────────────────────────


class TestGetCoinAddress:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/deposits/coin_address"
            assert request.url.params["currency"] == "BTC"
            assert request.url.params["net_type"] == "BTC"
            return _json_response(DEPOSIT_ADDRESS_DATA)

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        result = api.get_coin_address(currency="BTC", net_type="BTC")
        assert isinstance(result, DepositAddress)


# ── TestListCoinAddresses ────────────────────────────────────────────────


class TestListCoinAddresses:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/deposits/coin_addresses"
            return _json_response([DEPOSIT_ADDRESS_DATA])

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        result = api.list_coin_addresses()
        assert len(result) == 1
        assert isinstance(result[0], DepositAddress)


# ── TestCreateKrwDeposit ─────────────────────────────────────────────────


class TestCreateKrwDeposit:
    def test_post_with_json_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/deposits/krw"
            assert request.method == "POST"
            body = json.loads(request.content)
            assert body["amount"] == "10000"
            assert body["two_factor_type"] == "kakao"
            return _json_response(DEPOSIT_DATA)

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        result = api.create_krw(amount="10000", two_factor_type="kakao")
        assert isinstance(result, Deposit)


# ── TestGetDepositChanceCoin ─────────────────────────────────────────────


class TestGetDepositChanceCoin:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/deposits/chance/coin"
            assert request.url.params["currency"] == "BTC"
            assert request.url.params["net_type"] == "BTC"
            return _json_response(DEPOSIT_CHANCE_COIN_DATA)

        transport = _make_transport(handler)
        api = DepositsAPI(transport, CREDENTIALS)
        result = api.get_chance_coin(currency="BTC", net_type="BTC")
        assert isinstance(result, DepositChanceCoin)
        assert result.is_deposit_possible is True
        assert result.minimum_deposit_confirmations == 3


# ── TestAsyncDeposits ────────────────────────────────────────────────────


class TestAsyncDeposits:
    @pytest.mark.asyncio
    async def test_get(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/deposit"
            return _json_response(DEPOSIT_DATA)

        transport = _make_async_transport(handler)
        api = AsyncDepositsAPI(transport, CREDENTIALS)
        result = await api.get(uuid="dep-uuid-1")
        assert isinstance(result, Deposit)

    @pytest.mark.asyncio
    async def test_list(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([DEPOSIT_DATA])

        transport = _make_async_transport(handler)
        api = AsyncDepositsAPI(transport, CREDENTIALS)
        result = await api.list()
        assert len(result) == 1
        assert isinstance(result[0], Deposit)

    @pytest.mark.asyncio
    async def test_generate_coin_address_201(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(DEPOSIT_ADDRESS_CREATED_DATA, status_code=201)

        transport = _make_async_transport(handler)
        api = AsyncDepositsAPI(transport, CREDENTIALS)
        result = await api.generate_coin_address(currency="BTC", net_type="BTC")
        assert isinstance(result, DepositAddressCreated)

    @pytest.mark.asyncio
    async def test_get_chance_coin(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(DEPOSIT_CHANCE_COIN_DATA)

        transport = _make_async_transport(handler)
        api = AsyncDepositsAPI(transport, CREDENTIALS)
        result = await api.get_chance_coin(currency="BTC", net_type="BTC")
        assert isinstance(result, DepositChanceCoin)
