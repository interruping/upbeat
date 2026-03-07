from __future__ import annotations

from __future__ import annotations

import httpx
import pytest

from upbeat._auth import Credentials
from upbeat._client import (
    AccountsAPI,
    AsyncAccountsAPI,
    AsyncDepositsAPI,
    AsyncMarketsAPI,
    AsyncOrdersAPI,
    AsyncQuotationAPI,
    AsyncUpbeat,
    AsyncWithdrawalsAPI,
    DepositsAPI,
    MarketsAPI,
    OrdersAPI,
    QuotationAPI,
    Upbeat,
    WithdrawalsAPI,
)
from upbeat._constants import API_BASE_URL


# ── TestUpbeatCreation ───────────────────────────────────────────────────


class TestUpbeatCreation:
    def test_default_creation_no_credentials(self) -> None:
        client = Upbeat()
        assert client._credentials is None
        assert client._owns_http_client is True
        client.close()

    def test_creation_with_credentials(self) -> None:
        client = Upbeat(access_key="test-key", secret_key="test-secret")
        assert client._credentials is not None
        assert isinstance(client._credentials, Credentials)
        assert client._credentials.access_key == "test-key"
        client.close()

    def test_creation_access_key_only_raises(self) -> None:
        with pytest.raises(ValueError, match="Both access_key and secret_key"):
            Upbeat(access_key="test-key")

    def test_creation_secret_key_only_raises(self) -> None:
        with pytest.raises(ValueError, match="Both access_key and secret_key"):
            Upbeat(secret_key="test-secret")

    def test_custom_settings(self) -> None:
        from upbeat._config import Timeout

        custom_timeout = Timeout(connect=5.0, read=15.0)
        client = Upbeat(
            timeout=custom_timeout,
            max_retries=5,
            auto_throttle=False,
        )
        assert client._max_retries == 5
        assert client._auto_throttle is False
        assert client._timeout.connect == 5.0
        client.close()


# ── TestUpbeatClose ──────────────────────────────────────────────────────


class TestUpbeatClose:
    def test_close_internal_client(self) -> None:
        client = Upbeat()
        client.close()
        assert client._closed is True

    def test_close_external_client_not_closed(self) -> None:
        http_client = httpx.Client(base_url=API_BASE_URL)
        client = Upbeat(http_client=http_client)
        assert client._owns_http_client is False
        client.close()
        # External client should still be usable
        assert not http_client.is_closed
        http_client.close()

    def test_close_idempotent(self) -> None:
        client = Upbeat()
        client.close()
        client.close()  # Should not raise
        assert client._closed is True


# ── TestUpbeatContextManager ────────────────────────────────────────────


class TestUpbeatContextManager:
    def test_context_manager_closes(self) -> None:
        with Upbeat() as client:
            assert client._closed is False
        assert client._closed is True

    def test_context_manager_external_client_not_closed(self) -> None:
        http_client = httpx.Client(base_url=API_BASE_URL)
        with Upbeat(http_client=http_client) as client:
            assert client._owns_http_client is False
        assert not http_client.is_closed
        http_client.close()


# ── TestUpbeatWithOptions ────────────────────────────────────────────────


class TestUpbeatWithOptions:
    def test_shares_http_client(self) -> None:
        client = Upbeat()
        new = client.with_options(max_retries=10)
        assert new._transport._client is client._transport._client
        assert new._owns_http_client is False
        client.close()

    def test_overrides_max_retries(self) -> None:
        client = Upbeat(max_retries=3)
        new = client.with_options(max_retries=10)
        assert new._max_retries == 10
        assert new._transport._max_retries == 10
        client.close()

    def test_preserves_credentials(self) -> None:
        client = Upbeat(access_key="test-key", secret_key="test-secret")
        new = client.with_options(max_retries=1)
        assert new._credentials is client._credentials
        client.close()

    def test_overrides_auto_throttle(self) -> None:
        client = Upbeat(auto_throttle=True)
        new = client.with_options(auto_throttle=False)
        assert new._auto_throttle is False
        client.close()


# ── TestUpbeatResources ──────────────────────────────────────────────────


class TestUpbeatResources:
    def test_cached_property_returns_same_instance(self) -> None:
        client = Upbeat()
        q1 = client.quotation
        q2 = client.quotation
        assert q1 is q2
        client.close()

    def test_resource_types(self) -> None:
        client = Upbeat(access_key="test-key", secret_key="test-secret")
        assert isinstance(client.quotation, QuotationAPI)
        assert isinstance(client.accounts, AccountsAPI)
        assert isinstance(client.orders, OrdersAPI)
        assert isinstance(client.deposits, DepositsAPI)
        assert isinstance(client.withdrawals, WithdrawalsAPI)
        assert isinstance(client.markets, MarketsAPI)
        client.close()

    def test_resources_receive_transport_and_credentials(self) -> None:
        client = Upbeat(access_key="test-key", secret_key="test-secret")
        resource = client.quotation
        assert resource._transport is client._transport
        assert resource._credentials is client._credentials
        client.close()


# ── TestAsyncUpbeatCreation ──────────────────────────────────────────────


class TestAsyncUpbeatCreation:
    def test_default_creation_no_credentials(self) -> None:
        client = AsyncUpbeat()
        assert client._credentials is None
        assert client._owns_http_client is True

    def test_creation_with_credentials(self) -> None:
        client = AsyncUpbeat(access_key="test-key", secret_key="test-secret")
        assert client._credentials is not None
        assert isinstance(client._credentials, Credentials)

    def test_creation_access_key_only_raises(self) -> None:
        with pytest.raises(ValueError, match="Both access_key and secret_key"):
            AsyncUpbeat(access_key="test-key")

    def test_creation_secret_key_only_raises(self) -> None:
        with pytest.raises(ValueError, match="Both access_key and secret_key"):
            AsyncUpbeat(secret_key="test-secret")


# ── TestAsyncUpbeatContextManager ────────────────────────────────────────


class TestAsyncUpbeatContextManager:
    @pytest.mark.asyncio
    async def test_context_manager_closes(self) -> None:
        async with AsyncUpbeat() as client:
            assert client._closed is False
        assert client._closed is True

    @pytest.mark.asyncio
    async def test_context_manager_external_client_not_closed(self) -> None:
        http_client = httpx.AsyncClient(base_url=API_BASE_URL)
        async with AsyncUpbeat(http_client=http_client) as client:
            assert client._owns_http_client is False
        assert not http_client.is_closed
        await http_client.aclose()


# ── TestAsyncUpbeatWithOptions ───────────────────────────────────────────


class TestAsyncUpbeatWithOptions:
    def test_shares_http_client(self) -> None:
        client = AsyncUpbeat()
        new = client.with_options(max_retries=10)
        assert new._transport._client is client._transport._client
        assert new._owns_http_client is False

    def test_overrides_max_retries(self) -> None:
        client = AsyncUpbeat(max_retries=3)
        new = client.with_options(max_retries=10)
        assert new._max_retries == 10

    def test_preserves_credentials(self) -> None:
        client = AsyncUpbeat(access_key="test-key", secret_key="test-secret")
        new = client.with_options(max_retries=1)
        assert new._credentials is client._credentials


# ── TestAsyncUpbeatResources ─────────────────────────────────────────────


class TestAsyncUpbeatResources:
    def test_cached_property_returns_same_instance(self) -> None:
        client = AsyncUpbeat()
        q1 = client.quotation
        q2 = client.quotation
        assert q1 is q2

    def test_resource_types(self) -> None:
        client = AsyncUpbeat(access_key="test-key", secret_key="test-secret")
        assert isinstance(client.quotation, AsyncQuotationAPI)
        assert isinstance(client.accounts, AsyncAccountsAPI)
        assert isinstance(client.orders, AsyncOrdersAPI)
        assert isinstance(client.deposits, AsyncDepositsAPI)
        assert isinstance(client.withdrawals, AsyncWithdrawalsAPI)
        assert isinstance(client.markets, AsyncMarketsAPI)

    def test_resources_receive_transport_and_credentials(self) -> None:
        client = AsyncUpbeat(access_key="test-key", secret_key="test-secret")
        resource = client.quotation
        assert resource._transport is client._transport
        assert resource._credentials is client._credentials
