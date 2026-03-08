from __future__ import annotations

from decimal import Decimal

from upbeat._constants import round_to_tick
from upbeat.strategies._base import (
    AsyncClientProtocol,
    RebalanceOrder,
    RebalanceResult,
    SyncClientProtocol,
)
from upbeat.strategies.portfolio import (
    async_get_portfolio,
    async_get_portfolio_value,
    get_portfolio,
    get_portfolio_value,
)

_MIN_ORDER_KRW = 5_000.0


def rebalance(
    client: SyncClientProtocol,
    *,
    targets: dict[str, float],
) -> RebalanceResult:
    weight_sum = sum(targets.values())
    if abs(weight_sum - 1.0) > 1e-6:
        raise ValueError(f"Target weights must sum to 1.0, got {weight_sum}")

    total_value = get_portfolio_value(client)
    portfolio = get_portfolio(client)

    current_map: dict[str, float] = {}
    price_map: dict[str, float] = {}
    for item in portfolio:
        current_map[item.market] = item.estimated_value_krw
        if item.market != "KRW":
            price_map[item.market] = item.current_price

    all_markets = set(targets.keys()) | set(current_map.keys())

    diffs: list[tuple[str, float]] = []
    for market in all_markets:
        target_value = total_value * targets.get(market, 0.0)
        current_value = current_map.get(market, 0.0)
        diff = target_value - current_value
        diffs.append((market, diff))

    sells = [(m, d) for m, d in diffs if d < -_MIN_ORDER_KRW and m != "KRW"]
    buys = [(m, d) for m, d in diffs if d > _MIN_ORDER_KRW and m != "KRW"]

    result_orders: list[RebalanceOrder] = []

    for market, diff in sells:
        price = price_map[market]
        volume = abs(diff) / price
        order = client.orders.create(
            market=market,
            side="ask",
            ord_type="market",
            volume=str(volume),
        )
        result_orders.append(
            RebalanceOrder(
                market=market,
                side="ask",
                ord_type="market",
                amount=abs(diff),
                order=order,
            )
        )

    for market, diff in buys:
        rounded = round_to_tick(Decimal(str(diff)))
        order = client.orders.create(
            market=market,
            side="bid",
            ord_type="price",
            price=str(int(rounded)),
        )
        result_orders.append(
            RebalanceOrder(
                market=market,
                side="bid",
                ord_type="price",
                amount=diff,
                order=order,
            )
        )

    return RebalanceResult(orders=result_orders, total_value=total_value)


async def async_rebalance(
    client: AsyncClientProtocol,
    *,
    targets: dict[str, float],
) -> RebalanceResult:
    weight_sum = sum(targets.values())
    if abs(weight_sum - 1.0) > 1e-6:
        raise ValueError(f"Target weights must sum to 1.0, got {weight_sum}")

    total_value = await async_get_portfolio_value(client)
    portfolio = await async_get_portfolio(client)

    current_map: dict[str, float] = {}
    price_map: dict[str, float] = {}
    for item in portfolio:
        current_map[item.market] = item.estimated_value_krw
        if item.market != "KRW":
            price_map[item.market] = item.current_price

    all_markets = set(targets.keys()) | set(current_map.keys())

    diffs: list[tuple[str, float]] = []
    for market in all_markets:
        target_value = total_value * targets.get(market, 0.0)
        current_value = current_map.get(market, 0.0)
        diff = target_value - current_value
        diffs.append((market, diff))

    sells = [(m, d) for m, d in diffs if d < -_MIN_ORDER_KRW and m != "KRW"]
    buys = [(m, d) for m, d in diffs if d > _MIN_ORDER_KRW and m != "KRW"]

    result_orders: list[RebalanceOrder] = []

    for market, diff in sells:
        price = price_map[market]
        volume = abs(diff) / price
        order = await client.orders.create(
            market=market,
            side="ask",
            ord_type="market",
            volume=str(volume),
        )
        result_orders.append(
            RebalanceOrder(
                market=market,
                side="ask",
                ord_type="market",
                amount=abs(diff),
                order=order,
            )
        )

    for market, diff in buys:
        rounded = round_to_tick(Decimal(str(diff)))
        order = await client.orders.create(
            market=market,
            side="bid",
            ord_type="price",
            price=str(int(rounded)),
        )
        result_orders.append(
            RebalanceOrder(
                market=market,
                side="bid",
                ord_type="price",
                amount=diff,
                order=order,
            )
        )

    return RebalanceResult(orders=result_orders, total_value=total_value)
