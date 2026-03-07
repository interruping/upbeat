from __future__ import annotations

from functools import cached_property
from typing import Any

import httpx

from upbeat._auth import Credentials
from upbeat._base import _AsyncAPIResource, _SyncAPIResource
from upbeat._config import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, Timeout
from upbeat._constants import API_BASE_URL
from upbeat._http import AsyncTransport, SyncTransport
from upbeat._logger import Logger
from upbeat.api.markets import AsyncMarketsAPI, MarketsAPI
from upbeat.api.quotation import AsyncQuotationAPI, QuotationAPI


# ── Sync API resource stubs ─────────────────────────────────────────────


class AccountsAPI(_SyncAPIResource):
    pass


class OrdersAPI(_SyncAPIResource):
    pass


class DepositsAPI(_SyncAPIResource):
    pass


class WithdrawalsAPI(_SyncAPIResource):
    pass


# ── Async API resource stubs ────────────────────────────────────────────


class AsyncAccountsAPI(_AsyncAPIResource):
    pass


class AsyncOrdersAPI(_AsyncAPIResource):
    pass


class AsyncDepositsAPI(_AsyncAPIResource):
    pass


class AsyncWithdrawalsAPI(_AsyncAPIResource):
    pass


# ── Upbeat (sync client) ────────────────────────────────────────────────


class Upbeat:
    _transport: SyncTransport
    _credentials: Credentials | None
    _owns_http_client: bool
    _closed: bool

    def __init__(
        self,
        *,
        access_key: str | None = None,
        secret_key: str | None = None,
        base_url: str = API_BASE_URL,
        timeout: Timeout = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        auto_throttle: bool = True,
        logger: Logger | None = None,
        http_client: httpx.Client | None = None,
        event_hooks: dict[str, list[Any]] | None = None,
    ) -> None:
        if (access_key is None) != (secret_key is None):
            raise ValueError(
                "Both access_key and secret_key must be provided together, or neither."
            )

        self._credentials = (
            Credentials(access_key=access_key, secret_key=secret_key)
            if access_key is not None and secret_key is not None
            else None
        )

        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries
        self._auto_throttle = auto_throttle
        self._logger = logger
        self._owns_http_client = http_client is None
        self._closed = False

        self._transport = SyncTransport(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            auto_throttle=auto_throttle,
            logger=logger,
            http_client=http_client,
            event_hooks=event_hooks,
        )

    # ── Resource properties ──────────────────────────────────────────

    @cached_property
    def quotation(self) -> QuotationAPI:
        return QuotationAPI(self._transport, self._credentials)

    @cached_property
    def accounts(self) -> AccountsAPI:
        return AccountsAPI(self._transport, self._credentials)

    @cached_property
    def orders(self) -> OrdersAPI:
        return OrdersAPI(self._transport, self._credentials)

    @cached_property
    def deposits(self) -> DepositsAPI:
        return DepositsAPI(self._transport, self._credentials)

    @cached_property
    def withdrawals(self) -> WithdrawalsAPI:
        return WithdrawalsAPI(self._transport, self._credentials)

    @cached_property
    def markets(self) -> MarketsAPI:
        return MarketsAPI(self._transport, self._credentials)

    # ── Lifecycle ────────────────────────────────────────────────────

    def close(self) -> None:
        if not self._closed and self._owns_http_client:
            self._transport.close()
        self._closed = True

    def __enter__(self) -> Upbeat:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    # ── with_options ─────────────────────────────────────────────────

    def with_options(
        self,
        *,
        max_retries: int | None = None,
        auto_throttle: bool | None = None,
        logger: Logger | None = None,
    ) -> Upbeat:
        new = Upbeat.__new__(Upbeat)
        new._credentials = self._credentials
        new._base_url = self._base_url
        new._timeout = self._timeout
        new._max_retries = max_retries if max_retries is not None else self._max_retries
        new._auto_throttle = (
            auto_throttle if auto_throttle is not None else self._auto_throttle
        )
        new._logger = logger if logger is not None else self._logger
        new._owns_http_client = False
        new._closed = False

        new._transport = SyncTransport(
            base_url=new._base_url,
            timeout=new._timeout,
            max_retries=new._max_retries,
            auto_throttle=new._auto_throttle,
            logger=new._logger,
            http_client=self._transport._client,
        )
        return new


# ── AsyncUpbeat (async client) ───────────────────────────────────────────


class AsyncUpbeat:
    _transport: AsyncTransport
    _credentials: Credentials | None
    _owns_http_client: bool
    _closed: bool

    def __init__(
        self,
        *,
        access_key: str | None = None,
        secret_key: str | None = None,
        base_url: str = API_BASE_URL,
        timeout: Timeout = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        auto_throttle: bool = True,
        logger: Logger | None = None,
        http_client: httpx.AsyncClient | None = None,
        event_hooks: dict[str, list[Any]] | None = None,
    ) -> None:
        if (access_key is None) != (secret_key is None):
            raise ValueError(
                "Both access_key and secret_key must be provided together, or neither."
            )

        self._credentials = (
            Credentials(access_key=access_key, secret_key=secret_key)
            if access_key is not None and secret_key is not None
            else None
        )

        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries
        self._auto_throttle = auto_throttle
        self._logger = logger
        self._owns_http_client = http_client is None
        self._closed = False

        self._transport = AsyncTransport(
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            auto_throttle=auto_throttle,
            logger=logger,
            http_client=http_client,
            event_hooks=event_hooks,
        )

    # ── Resource properties ──────────────────────────────────────────

    @cached_property
    def quotation(self) -> AsyncQuotationAPI:
        return AsyncQuotationAPI(self._transport, self._credentials)

    @cached_property
    def accounts(self) -> AsyncAccountsAPI:
        return AsyncAccountsAPI(self._transport, self._credentials)

    @cached_property
    def orders(self) -> AsyncOrdersAPI:
        return AsyncOrdersAPI(self._transport, self._credentials)

    @cached_property
    def deposits(self) -> AsyncDepositsAPI:
        return AsyncDepositsAPI(self._transport, self._credentials)

    @cached_property
    def withdrawals(self) -> AsyncWithdrawalsAPI:
        return AsyncWithdrawalsAPI(self._transport, self._credentials)

    @cached_property
    def markets(self) -> AsyncMarketsAPI:
        return AsyncMarketsAPI(self._transport, self._credentials)

    # ── Lifecycle ────────────────────────────────────────────────────

    async def aclose(self) -> None:
        if not self._closed and self._owns_http_client:
            await self._transport.aclose()
        self._closed = True

    async def __aenter__(self) -> AsyncUpbeat:
        return self

    async def __aexit__(self, *_args: object) -> None:
        await self.aclose()

    # ── with_options ─────────────────────────────────────────────────

    def with_options(
        self,
        *,
        max_retries: int | None = None,
        auto_throttle: bool | None = None,
        logger: Logger | None = None,
    ) -> AsyncUpbeat:
        new = AsyncUpbeat.__new__(AsyncUpbeat)
        new._credentials = self._credentials
        new._base_url = self._base_url
        new._timeout = self._timeout
        new._max_retries = (
            max_retries if max_retries is not None else self._max_retries
        )
        new._auto_throttle = (
            auto_throttle if auto_throttle is not None else self._auto_throttle
        )
        new._logger = logger if logger is not None else self._logger
        new._owns_http_client = False
        new._closed = False

        new._transport = AsyncTransport(
            base_url=new._base_url,
            timeout=new._timeout,
            max_retries=new._max_retries,
            auto_throttle=new._auto_throttle,
            logger=new._logger,
            http_client=self._transport._client,
        )
        return new
