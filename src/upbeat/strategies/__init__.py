from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from upbeat.strategies._base import (
    AsyncClientProtocol,
    DCAResult,
    PortfolioItem,
    RebalanceOrder,
    RebalanceResult,
    SyncClientProtocol,
)
from upbeat.strategies.alerts import async_price_alert, price_alert
from upbeat.strategies.dca import async_dca, dca
from upbeat.strategies.order_helpers import (
    async_cancel_all_orders,
    async_market_buy_krw,
    async_place_and_wait,
    cancel_all_orders,
    market_buy_krw,
    place_and_wait,
)
from upbeat.strategies.portfolio import (
    async_get_portfolio,
    async_get_portfolio_value,
    get_portfolio,
    get_portfolio_value,
)
from upbeat.strategies.rebalance import async_rebalance, rebalance
from upbeat.types.order import CancelResult, OrderCreated, OrderDetail


class SyncStrategies:
    def __init__(self, client: SyncClientProtocol) -> None:
        self._client = client

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

    def dca(
        self,
        *,
        market: str,
        total_amount: float,
        splits: int,
        interval_seconds: float,
    ) -> DCAResult:
        return dca(
            self._client,
            market=market,
            total_amount=total_amount,
            splits=splits,
            interval_seconds=interval_seconds,
        )

    def rebalance(self, *, targets: dict[str, float]) -> RebalanceResult:
        return rebalance(self._client, targets=targets)

    def price_alert(
        self,
        *,
        market: str,
        stop_loss: float | None = None,
        take_profit: float | None = None,
        callback: Callable[[str, Literal["stop_loss", "take_profit"], float], None],
        poll_interval: float = 5.0,
    ) -> None:
        price_alert(
            self._client,
            market=market,
            stop_loss=stop_loss,
            take_profit=take_profit,
            callback=callback,
            poll_interval=poll_interval,
        )


class AsyncStrategies:
    def __init__(self, client: AsyncClientProtocol) -> None:
        self._client = client

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

    async def dca(
        self,
        *,
        market: str,
        total_amount: float,
        splits: int,
        interval_seconds: float,
    ) -> DCAResult:
        return await async_dca(
            self._client,
            market=market,
            total_amount=total_amount,
            splits=splits,
            interval_seconds=interval_seconds,
        )

    async def rebalance(self, *, targets: dict[str, float]) -> RebalanceResult:
        return await async_rebalance(self._client, targets=targets)

    async def price_alert(
        self,
        *,
        market: str,
        stop_loss: float | None = None,
        take_profit: float | None = None,
        callback: Callable[[str, Literal["stop_loss", "take_profit"], float], None],
        poll_interval: float = 5.0,
    ) -> None:
        await async_price_alert(
            self._client,
            market=market,
            stop_loss=stop_loss,
            take_profit=take_profit,
            callback=callback,
            poll_interval=poll_interval,
        )


__all__ = [
    "AsyncStrategies",
    "DCAResult",
    "PortfolioItem",
    "RebalanceOrder",
    "RebalanceResult",
    "SyncStrategies",
]
