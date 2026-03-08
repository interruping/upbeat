from __future__ import annotations

from pydantic import BaseModel, ConfigDict

# ── OrderTrade (체결 내역, OrderDetail 내부) ────────────────────────────


class OrderTrade(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    uuid: str
    price: str
    volume: str
    funds: str
    trend: str
    created_at: str
    side: str


# ── OrderCreated (POST /v1/orders 응답) ─────────────────────────────────


class OrderCreated(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    uuid: str
    side: str
    ord_type: str
    price: str | None = None
    state: str
    created_at: str
    volume: str | None = None
    remaining_volume: str
    executed_volume: str
    reserved_fee: str
    remaining_fee: str
    paid_fee: str
    locked: str
    trades_count: int
    time_in_force: str | None = None
    identifier: str | None = None
    smp_type: str | None = None
    prevented_volume: str
    prevented_locked: str


# ── OrderDetail (GET /v1/order 응답) ────────────────────────────────────


class OrderDetail(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    uuid: str
    side: str
    ord_type: str
    price: str | None = None
    state: str
    created_at: str
    volume: str | None = None
    remaining_volume: str | None = None
    executed_volume: str
    reserved_fee: str
    remaining_fee: str
    paid_fee: str
    locked: str
    time_in_force: str | None = None
    smp_type: str | None = None
    prevented_volume: str | None = None
    prevented_locked: str
    identifier: str | None = None
    trades_count: int
    trades: list[OrderTrade]


# ── OrderOpen (GET /v1/orders/open 응답) ────────────────────────────────


class OrderOpen(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    uuid: str
    side: str
    ord_type: str
    price: str | None = None
    state: str
    created_at: str
    volume: str | None = None
    remaining_volume: str
    executed_volume: str
    executed_funds: str
    reserved_fee: str
    remaining_fee: str
    paid_fee: str
    locked: str
    time_in_force: str | None = None
    identifier: str | None = None
    smp_type: str | None = None
    prevented_volume: str
    prevented_locked: str
    trades_count: int


# ── OrderClosed (GET /v1/orders/closed 응답) ────────────────────────────


class OrderClosed(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    uuid: str
    side: str
    ord_type: str
    price: str
    state: str
    created_at: str
    volume: str
    remaining_volume: str
    executed_volume: str
    executed_funds: str
    reserved_fee: str
    remaining_fee: str
    paid_fee: str
    locked: str
    time_in_force: str | None = None
    identifier: str | None = None
    smp_type: str | None = None
    prevented_volume: str
    prevented_locked: str
    trades_count: int


# ── OrderByIds (GET /v1/orders/uuids 응답) ──────────────────────────────


class OrderByIds(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    uuid: str
    side: str
    ord_type: str
    price: str | None = None
    state: str
    created_at: str
    volume: str | None = None
    remaining_volume: str | None = None
    executed_volume: str
    executed_funds: str
    reserved_fee: str
    remaining_fee: str
    paid_fee: str
    locked: str
    time_in_force: str | None = None
    identifier: str | None = None
    smp_type: str | None = None
    prevented_volume: str | None = None
    prevented_locked: str
    trades_count: int


# ── OrderCanceled (DELETE /v1/order 응답) ───────────────────────────────


class OrderCanceled(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    uuid: str
    side: str
    ord_type: str
    price: str | None = None
    state: str
    created_at: str
    volume: str | None = None
    remaining_volume: str
    executed_volume: str
    reserved_fee: str
    remaining_fee: str
    paid_fee: str
    locked: str
    time_in_force: str | None = None
    identifier: str | None = None
    smp_type: str | None = None
    prevented_volume: str
    prevented_locked: str
    trades_count: int


# ── CancelResult (DELETE /v1/orders/open, /uuids 응답) ─────────────────


class CancelResultOrder(BaseModel):
    model_config = ConfigDict(frozen=True)

    uuid: str
    market: str
    identifier: str | None = None


class CancelResultGroup(BaseModel):
    model_config = ConfigDict(frozen=True)

    count: int
    orders: list[CancelResultOrder]


class CancelResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    success: CancelResultGroup
    failed: CancelResultGroup


# ── CancelAndNewOrderResponse (POST /v1/orders/cancel_and_new 응답) ─────


class CancelAndNewOrderResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    uuid: str
    identifier: str | None = None
    side: str
    ord_type: str
    price: str | None = None
    state: str
    created_at: str
    volume: str | None = None
    remaining_volume: str
    executed_volume: str
    reserved_fee: str
    remaining_fee: str
    paid_fee: str
    locked: str
    prevented_volume: str
    prevented_locked: str
    smp_type: str | None = None
    trades_count: int
    time_in_force: str | None = None
    new_order_uuid: str
    new_order_identifier: str | None = None


# ── OrderChance (GET /v1/orders/chance 응답) ────────────────────────────


class OrderChanceMarketBidAsk(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    min_total: str


class OrderChanceMarket(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    order_types: list[str] | None = None
    order_sides: list[str] | None = None
    bid_types: list[str] | None = None
    ask_types: list[str] | None = None
    bid: OrderChanceMarketBidAsk | None = None
    ask: OrderChanceMarketBidAsk | None = None
    max_total: str | None = None
    state: str | None = None


class OrderChanceAccount(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    balance: str
    locked: str
    avg_buy_price: str
    avg_buy_price_modified: bool
    unit_currency: str


class OrderChance(BaseModel):
    model_config = ConfigDict(frozen=True)

    bid_fee: str
    ask_fee: str
    maker_bid_fee: str
    maker_ask_fee: str
    market: OrderChanceMarket
    bid_account: OrderChanceAccount
    ask_account: OrderChanceAccount
