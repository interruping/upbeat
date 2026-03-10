from __future__ import annotations

from typing import TYPE_CHECKING

from upbeat.shortcuts._accounts import find_account
from upbeat.shortcuts._order_helpers import (
    async_cancel_all_orders,
    async_market_buy_krw,
    async_place_and_wait,
    cancel_all_orders,
    market_buy_krw,
    place_and_wait,
)
from upbeat.shortcuts._portfolio import (
    PortfolioItem,
    async_get_portfolio,
    async_get_portfolio_value,
    get_portfolio,
    get_portfolio_value,
)

if TYPE_CHECKING:
    from upbeat._client import AsyncUpbeat, Upbeat
    from upbeat.types.account import Account
    from upbeat.types.order import CancelResult, OrderCreated, OrderDetail


class SyncShortcuts:
    def __init__(self, client: Upbeat) -> None:
        self._client = client

    def get_account(self, currency: str) -> Account | None:
        return find_account(self._client.accounts.list(), currency)

    def get_portfolio_value(self) -> float:
        return get_portfolio_value(self._client)

    def get_portfolio(self) -> list[PortfolioItem]:
        return get_portfolio(self._client)

    def market_buy_krw(self, market: str, krw_amount: float) -> OrderCreated:
        return market_buy_krw(self._client, market, krw_amount)

    def place_and_wait(
        self,
        *,
        market: str,
        side: str,
        ord_type: str,
        price: str | None = None,
        volume: str | None = None,
        timeout: float,
        poll_interval: float = 1.0,
    ) -> OrderDetail:
        return place_and_wait(
            self._client,
            market=market,
            side=side,
            ord_type=ord_type,
            price=price,
            volume=volume,
            timeout=timeout,
            poll_interval=poll_interval,
        )

    def cancel_all_orders(self, market: str | None = None) -> CancelResult:
        return cancel_all_orders(self._client, market)


class AsyncShortcuts:
    def __init__(self, client: AsyncUpbeat) -> None:
        self._client = client

    async def get_account(self, currency: str) -> Account | None:
        accounts = await self._client.accounts.list()
        return find_account(accounts, currency)

    async def get_portfolio_value(self) -> float:
        return await async_get_portfolio_value(self._client)

    async def get_portfolio(self) -> list[PortfolioItem]:
        return await async_get_portfolio(self._client)

    async def market_buy_krw(self, market: str, krw_amount: float) -> OrderCreated:
        return await async_market_buy_krw(self._client, market, krw_amount)

    async def place_and_wait(
        self,
        *,
        market: str,
        side: str,
        ord_type: str,
        price: str | None = None,
        volume: str | None = None,
        timeout: float,
        poll_interval: float = 1.0,
    ) -> OrderDetail:
        return await async_place_and_wait(
            self._client,
            market=market,
            side=side,
            ord_type=ord_type,
            price=price,
            volume=volume,
            timeout=timeout,
            poll_interval=poll_interval,
        )

    async def cancel_all_orders(self, market: str | None = None) -> CancelResult:
        return await async_cancel_all_orders(self._client, market)


__all__ = [
    "AsyncShortcuts",
    "PortfolioItem",
    "SyncShortcuts",
    "find_account",
]
