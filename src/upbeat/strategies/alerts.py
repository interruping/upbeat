from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from typing import Literal

from upbeat.strategies._base import AsyncClientProtocol, SyncClientProtocol


def price_alert(
    client: SyncClientProtocol,
    *,
    market: str,
    stop_loss: float | None = None,
    take_profit: float | None = None,
    callback: Callable[[str, Literal["stop_loss", "take_profit"], float], None],
    poll_interval: float = 5.0,
) -> None:
    if stop_loss is None and take_profit is None:
        raise ValueError("At least one of stop_loss or take_profit must be set")

    while True:
        tickers = client.quotation.get_tickers(market)
        price = tickers[0].trade_price

        if stop_loss is not None and price <= stop_loss:
            callback(market, "stop_loss", price)
            return
        if take_profit is not None and price >= take_profit:
            callback(market, "take_profit", price)
            return

        time.sleep(poll_interval)


async def async_price_alert(
    client: AsyncClientProtocol,
    *,
    market: str,
    stop_loss: float | None = None,
    take_profit: float | None = None,
    callback: Callable[[str, Literal["stop_loss", "take_profit"], float], None],
    poll_interval: float = 5.0,
) -> None:
    if stop_loss is None and take_profit is None:
        raise ValueError("At least one of stop_loss or take_profit must be set")

    while True:
        tickers = await client.quotation.get_tickers(market)
        price = tickers[0].trade_price

        if stop_loss is not None and price <= stop_loss:
            callback(market, "stop_loss", price)
            return
        if take_profit is not None and price >= take_profit:
            callback(market, "take_profit", price)
            return

        await asyncio.sleep(poll_interval)
