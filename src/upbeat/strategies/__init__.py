from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from upbeat._protocols import AsyncClientProtocol, SyncClientProtocol
from upbeat.strategies._base import (
    DCAResult,
    RebalanceOrder,
    RebalanceResult,
)
from upbeat.strategies.alerts import async_price_alert, price_alert
from upbeat.strategies.dca import async_dca, dca
from upbeat.strategies.rebalance import async_rebalance, rebalance


class SyncStrategies:
    def __init__(self, client: SyncClientProtocol) -> None:
        self._client = client

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
    "RebalanceOrder",
    "RebalanceResult",
    "SyncStrategies",
]
