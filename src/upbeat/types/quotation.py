from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict


class Ticker(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    trade_date: str
    trade_time: str
    trade_date_kst: str
    trade_time_kst: str
    trade_timestamp: int
    opening_price: float
    high_price: float
    low_price: float
    trade_price: float
    prev_closing_price: float
    change: Literal["EVEN", "RISE", "FALL"]
    change_price: float
    change_rate: float
    signed_change_price: float
    signed_change_rate: float
    trade_volume: float
    acc_trade_price: float
    acc_trade_price_24h: float
    acc_trade_volume: float
    acc_trade_volume_24h: float
    highest_52_week_price: float
    highest_52_week_date: str
    lowest_52_week_price: float
    lowest_52_week_date: str
    timestamp: int


# ── Candles ──────────────────────────────────────────────────────────────


class CandleBase(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    candle_date_time_utc: str
    candle_date_time_kst: str
    opening_price: float
    high_price: float
    low_price: float
    trade_price: float
    timestamp: int
    candle_acc_trade_price: float
    candle_acc_trade_volume: float


class CandleMinute(CandleBase):
    unit: int


class CandleSecond(CandleBase):
    pass


class CandleDay(CandleBase):
    prev_closing_price: float
    change_price: float
    change_rate: float
    converted_trade_price: float | None = None


class CandlePeriod(CandleBase):
    first_day_of_period: str


# ── Orderbook ────────────────────────────────────────────────────────────


class OrderbookUnit(BaseModel):
    model_config = ConfigDict(frozen=True)

    ask_price: float
    bid_price: float
    ask_size: float
    bid_size: float


class Orderbook(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    timestamp: int
    total_ask_size: float
    total_bid_size: float
    orderbook_units: list[OrderbookUnit]
    level: float


class OrderbookInstrument(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    quote_currency: str
    tick_size: str
    supported_levels: list[str]


# ── Trade ────────────────────────────────────────────────────────────────


class Trade(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    trade_date_utc: str
    trade_time_utc: str
    timestamp: int
    trade_price: float
    trade_volume: float
    prev_closing_price: float
    change_price: float
    ask_bid: Literal["ASK", "BID"]
    sequential_id: int
