from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class TickerMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["ticker"]
    code: str
    opening_price: float
    high_price: float
    low_price: float
    trade_price: float
    prev_closing_price: float
    change: Literal["RISE", "EVEN", "FALL"]
    change_price: float
    signed_change_price: float
    change_rate: float
    signed_change_rate: float
    trade_volume: float
    acc_trade_volume: float
    acc_trade_volume_24h: float
    acc_trade_price: float
    acc_trade_price_24h: float
    trade_date: str
    trade_time: str
    trade_timestamp: int
    ask_bid: Literal["ASK", "BID"]
    acc_ask_volume: float
    acc_bid_volume: float
    highest_52_week_price: float
    highest_52_week_date: str
    lowest_52_week_price: float
    lowest_52_week_date: str
    market_state: Literal["PREVIEW", "ACTIVE", "DELISTED"]
    is_trading_suspended: bool
    delisting_date: str | None = None
    market_warning: Literal["NONE", "CAUTION"]
    timestamp: int
    stream_type: Literal["SNAPSHOT", "REALTIME"]


class TradeMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["trade"]
    code: str
    trade_price: float
    trade_volume: float
    ask_bid: Literal["ASK", "BID"]
    prev_closing_price: float
    change: Literal["RISE", "EVEN", "FALL"]
    change_price: float
    trade_date: str
    trade_time: str
    trade_timestamp: int
    timestamp: int
    sequential_id: int
    best_ask_price: float
    best_ask_size: float
    best_bid_price: float
    best_bid_size: float
    stream_type: Literal["SNAPSHOT", "REALTIME"]


class OrderbookUnitMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    ask_price: float
    bid_price: float
    ask_size: float
    bid_size: float


class OrderbookMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["orderbook"]
    code: str
    total_ask_size: float
    total_bid_size: float
    orderbook_units: list[OrderbookUnitMessage]
    timestamp: int
    level: float
    stream_type: Literal["SNAPSHOT", "REALTIME"]


class CandleMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal[
        "candle.1s",
        "candle.1m",
        "candle.3m",
        "candle.5m",
        "candle.10m",
        "candle.15m",
        "candle.30m",
        "candle.60m",
        "candle.240m",
    ]
    code: str
    candle_date_time_utc: str
    candle_date_time_kst: str
    opening_price: float
    high_price: float
    low_price: float
    trade_price: float
    candle_acc_trade_volume: float
    candle_acc_trade_price: float
    timestamp: int
    stream_type: Literal["SNAPSHOT", "REALTIME"]


class MyOrderMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["myOrder"]
    code: str
    uuid: str
    ask_bid: Literal["ASK", "BID"]
    order_type: Literal["limit", "price", "market", "best"]
    state: Literal["wait", "watch", "trade", "done", "cancel", "prevented"]
    price: float
    avg_price: float
    volume: float
    remaining_volume: float
    executed_volume: float
    trades_count: int
    reserved_fee: float
    remaining_fee: float
    paid_fee: float
    locked: float
    executed_funds: float
    trade_timestamp: int
    order_timestamp: int
    timestamp: int
    stream_type: Literal["SNAPSHOT", "REALTIME"]
    trade_uuid: str | None = None
    time_in_force: Literal["ioc", "fok", "post_only"] | None = None
    trade_fee: float | None = None
    is_maker: bool | None = None
    identifier: str | None = None
    smp_type: Literal["reduce", "cancel_maker", "cancel_taker"] | None = None
    prevented_volume: float | None = None
    prevented_locked: float | None = None


class MyAssetItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    balance: float
    locked: float


class MyAssetMessage(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: Literal["myAsset"]
    asset_uuid: str
    assets: list[MyAssetItem]
    asset_timestamp: int
    timestamp: int
    stream_type: Literal["REALTIME"]


# ── parse_message ────────────────────────────────────────────────────────

type WebSocketMessage = (
    TickerMessage
    | TradeMessage
    | OrderbookMessage
    | CandleMessage
    | MyOrderMessage
    | MyAssetMessage
)

_TYPE_TO_MODEL: dict[str, type[WebSocketMessage]] = {
    "ticker": TickerMessage,
    "trade": TradeMessage,
    "orderbook": OrderbookMessage,
    "myOrder": MyOrderMessage,
    "myAsset": MyAssetMessage,
}


def parse_message(data: dict[str, object]) -> WebSocketMessage:
    msg_type = data.get("type", "")
    if isinstance(msg_type, str) and msg_type.startswith("candle."):
        return CandleMessage.model_validate(data)
    model = _TYPE_TO_MODEL.get(msg_type)  # type: ignore[arg-type]
    if model is None:
        raise ValueError(f"Unknown WebSocket message type: {msg_type}")
    return model.model_validate(data)
