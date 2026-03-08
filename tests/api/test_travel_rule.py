from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from upbeat._auth import Credentials
from upbeat._constants import API_BASE_URL
from upbeat._http import AsyncTransport, SyncTransport
from upbeat.api.travel_rule import AsyncTravelRuleAPI, TravelRuleAPI
from upbeat.types.travel_rule import TravelRuleVasp, TravelRuleVerification

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

VASP_DATA: dict[str, Any] = {
    "vasp_name": "업비트",
    "vasp_uuid": "vasp-uuid-1",
    "depositable": True,
    "withdrawable": True,
}

VERIFICATION_DATA: dict[str, Any] = {
    "deposit_uuid": "dep-uuid-1",
    "verification_result": "verified",
    "deposit_state": "ACCEPTED",
}


# ── TestListVasps ────────────────────────────────────────────────────────


class TestListVasps:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/travel_rule/vasps"
            assert request.method == "GET"
            return _json_response([VASP_DATA])

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        result = api.list_vasps()
        assert len(result) == 1
        assert isinstance(result[0], TravelRuleVasp)

    def test_authorization_header_present(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" in request.headers
            assert request.headers["Authorization"].startswith("Bearer ")
            return _json_response([VASP_DATA])

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        api.list_vasps()

    def test_parses_response(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([VASP_DATA])

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        result = api.list_vasps()
        assert result[0].vasp_name == "업비트"
        assert result[0].vasp_uuid == "vasp-uuid-1"
        assert result[0].depositable is True
        assert result[0].withdrawable is True


# ── TestVerifyByUuid ─────────────────────────────────────────────────────


class TestVerifyByUuid:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/travel_rule/deposit/uuid"
            assert request.method == "POST"
            return _json_response(VERIFICATION_DATA, status_code=201)

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        api.verify_by_uuid(deposit_uuid="dep-uuid-1", vasp_uuid="vasp-uuid-1")

    def test_json_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["deposit_uuid"] == "dep-uuid-1"
            assert body["vasp_uuid"] == "vasp-uuid-1"
            return _json_response(VERIFICATION_DATA, status_code=201)

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        api.verify_by_uuid(deposit_uuid="dep-uuid-1", vasp_uuid="vasp-uuid-1")

    def test_authorization_header_present(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" in request.headers
            assert request.headers["Authorization"].startswith("Bearer ")
            return _json_response(VERIFICATION_DATA, status_code=201)

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        api.verify_by_uuid(deposit_uuid="dep-uuid-1", vasp_uuid="vasp-uuid-1")

    def test_parses_response(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(VERIFICATION_DATA, status_code=201)

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        result = api.verify_by_uuid(
            deposit_uuid="dep-uuid-1", vasp_uuid="vasp-uuid-1"
        )
        assert isinstance(result, TravelRuleVerification)
        assert result.deposit_uuid == "dep-uuid-1"
        assert result.verification_result == "verified"
        assert result.deposit_state == "ACCEPTED"


# ── TestVerifyByTxid ─────────────────────────────────────────────────────


class TestVerifyByTxid:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/travel_rule/deposit/txid"
            assert request.method == "POST"
            return _json_response(VERIFICATION_DATA, status_code=201)

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        api.verify_by_txid(
            vasp_uuid="vasp-uuid-1",
            txid="txid-abc123",
            currency="BTC",
            net_type="BTC",
        )

    def test_json_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["vasp_uuid"] == "vasp-uuid-1"
            assert body["txid"] == "txid-abc123"
            assert body["currency"] == "BTC"
            assert body["net_type"] == "BTC"
            return _json_response(VERIFICATION_DATA, status_code=201)

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        api.verify_by_txid(
            vasp_uuid="vasp-uuid-1",
            txid="txid-abc123",
            currency="BTC",
            net_type="BTC",
        )

    def test_authorization_header_present(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" in request.headers
            assert request.headers["Authorization"].startswith("Bearer ")
            return _json_response(VERIFICATION_DATA, status_code=201)

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        api.verify_by_txid(
            vasp_uuid="vasp-uuid-1",
            txid="txid-abc123",
            currency="BTC",
            net_type="BTC",
        )

    def test_parses_response(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(VERIFICATION_DATA, status_code=201)

        transport = _make_transport(handler)
        api = TravelRuleAPI(transport, CREDENTIALS)
        result = api.verify_by_txid(
            vasp_uuid="vasp-uuid-1",
            txid="txid-abc123",
            currency="BTC",
            net_type="BTC",
        )
        assert isinstance(result, TravelRuleVerification)
        assert result.deposit_uuid == "dep-uuid-1"
        assert result.verification_result == "verified"


# ── TestAsyncTravelRule ──────────────────────────────────────────────────


class TestAsyncTravelRule:
    @pytest.mark.asyncio
    async def test_list_vasps(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/travel_rule/vasps"
            return _json_response([VASP_DATA])

        transport = _make_async_transport(handler)
        api = AsyncTravelRuleAPI(transport, CREDENTIALS)
        result = await api.list_vasps()
        assert len(result) == 1
        assert isinstance(result[0], TravelRuleVasp)

    @pytest.mark.asyncio
    async def test_verify_by_uuid(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["deposit_uuid"] == "dep-uuid-1"
            return _json_response(VERIFICATION_DATA, status_code=201)

        transport = _make_async_transport(handler)
        api = AsyncTravelRuleAPI(transport, CREDENTIALS)
        result = await api.verify_by_uuid(
            deposit_uuid="dep-uuid-1", vasp_uuid="vasp-uuid-1"
        )
        assert isinstance(result, TravelRuleVerification)

    @pytest.mark.asyncio
    async def test_verify_by_txid(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["vasp_uuid"] == "vasp-uuid-1"
            assert body["txid"] == "txid-abc123"
            assert body["currency"] == "BTC"
            assert body["net_type"] == "BTC"
            return _json_response(VERIFICATION_DATA, status_code=201)

        transport = _make_async_transport(handler)
        api = AsyncTravelRuleAPI(transport, CREDENTIALS)
        result = await api.verify_by_txid(
            vasp_uuid="vasp-uuid-1",
            txid="txid-abc123",
            currency="BTC",
            net_type="BTC",
        )
        assert isinstance(result, TravelRuleVerification)
        assert result.deposit_uuid == "dep-uuid-1"
