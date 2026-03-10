from __future__ import annotations

import asyncio
import time

from upbeat._protocols import AsyncClientProtocol, SyncClientProtocol
from upbeat.types.order import CancelResult, OrderCreated, OrderDetail


def market_buy_krw(
    client: SyncClientProtocol, market: str, krw_amount: float
) -> OrderCreated:
    return client.orders.create(
        market=market,
        side="bid",
        ord_type="price",
        price=str(int(krw_amount)),
    )


def place_and_wait(
    client: SyncClientProtocol,
    *,
    market: str,
    side: str,
    ord_type: str,
    price: str | None = None,
    volume: str | None = None,
    timeout: float,
    poll_interval: float = 1.0,
) -> OrderDetail:
    order = client.orders.create(
        market=market, side=side, ord_type=ord_type, price=price, volume=volume
    )
    deadline = time.monotonic() + timeout
    while True:
        detail = client.orders.get(uuid=order.uuid)
        if detail.state == "done":
            return detail
        if detail.state == "cancel":
            raise RuntimeError(f"Order {order.uuid} was canceled")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Order {order.uuid} not filled within {timeout}s")
        time.sleep(poll_interval)


def cancel_all_orders(
    client: SyncClientProtocol, market: str | None = None
) -> CancelResult:
    return client.orders.cancel_open(pairs=market)


async def async_market_buy_krw(
    client: AsyncClientProtocol, market: str, krw_amount: float
) -> OrderCreated:
    return await client.orders.create(
        market=market,
        side="bid",
        ord_type="price",
        price=str(int(krw_amount)),
    )


async def async_place_and_wait(
    client: AsyncClientProtocol,
    *,
    market: str,
    side: str,
    ord_type: str,
    price: str | None = None,
    volume: str | None = None,
    timeout: float,
    poll_interval: float = 1.0,
) -> OrderDetail:
    order = await client.orders.create(
        market=market, side=side, ord_type=ord_type, price=price, volume=volume
    )
    deadline = time.monotonic() + timeout
    while True:
        detail = await client.orders.get(uuid=order.uuid)
        if detail.state == "done":
            return detail
        if detail.state == "cancel":
            raise RuntimeError(f"Order {order.uuid} was canceled")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Order {order.uuid} not filled within {timeout}s")
        await asyncio.sleep(poll_interval)


async def async_cancel_all_orders(
    client: AsyncClientProtocol, market: str | None = None
) -> CancelResult:
    return await client.orders.cancel_open(pairs=market)
