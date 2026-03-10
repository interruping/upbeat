from __future__ import annotations

import asyncio
import time

from upbeat._protocols import AsyncClientProtocol, SyncClientProtocol
from upbeat.shortcuts._order_helpers import async_market_buy_krw, market_buy_krw
from upbeat.strategies._base import DCAResult
from upbeat.types.order import OrderCreated


def dca(
    client: SyncClientProtocol,
    *,
    market: str,
    total_amount: float,
    splits: int,
    interval_seconds: float,
) -> DCAResult:
    amount_per_split = total_amount / splits
    orders: list[OrderCreated] = []

    for i in range(splits):
        try:
            order = market_buy_krw(client, market, amount_per_split)
            orders.append(order)
        except Exception:
            pass

        if i < splits - 1:
            time.sleep(interval_seconds)

    return DCAResult(
        orders=orders,
        total_spent=amount_per_split * len(orders),
        splits_completed=len(orders),
    )


async def async_dca(
    client: AsyncClientProtocol,
    *,
    market: str,
    total_amount: float,
    splits: int,
    interval_seconds: float,
) -> DCAResult:
    amount_per_split = total_amount / splits
    orders: list[OrderCreated] = []

    for i in range(splits):
        try:
            order = await async_market_buy_krw(client, market, amount_per_split)
            orders.append(order)
        except Exception:
            pass

        if i < splits - 1:
            await asyncio.sleep(interval_seconds)

    return DCAResult(
        orders=orders,
        total_spent=amount_per_split * len(orders),
        splits_completed=len(orders),
    )
