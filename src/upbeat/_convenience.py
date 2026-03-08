from __future__ import annotations

from typing import TYPE_CHECKING

from upbeat._client import Upbeat
from upbeat.types.market import TradingPair
from upbeat.types.quotation import (
    CandleDay,
    CandleMinute,
    CandlePeriod,
    CandleSecond,
    Orderbook,
    Ticker,
    Trade,
)

if TYPE_CHECKING:
    import pandas as pd

_MINUTE_UNITS: dict[str, int] = {
    "1m": 1,
    "3m": 3,
    "5m": 5,
    "10m": 10,
    "15m": 15,
    "30m": 30,
    "60m": 60,
    "240m": 240,
}


def get_ticker(market: str) -> Ticker:
    with Upbeat() as client:
        return client.quotation.get_tickers(market)[0]


def get_tickers(markets: str) -> list[Ticker]:
    with Upbeat() as client:
        return client.quotation.get_tickers(markets)


def get_candles(
    market: str,
    *,
    interval: str,
    to: str | None = None,
    count: int | None = None,
) -> list[CandleMinute] | list[CandleSecond] | list[CandleDay] | list[CandlePeriod]:
    with Upbeat() as client:
        if interval in _MINUTE_UNITS:
            return client.quotation.get_candles_minutes(
                market=market,
                unit=_MINUTE_UNITS[interval],
                to=to,
                count=count,  # type: ignore[arg-type]
            )
        if interval == "1s":
            return client.quotation.get_candles_seconds(
                market=market,
                to=to,
                count=count,
            )
        if interval == "1d":
            return client.quotation.get_candles_days(
                market=market,
                to=to,
                count=count,
            )
        if interval == "1w":
            return client.quotation.get_candles_weeks(
                market=market,
                to=to,
                count=count,
            )
        if interval == "1M":
            return client.quotation.get_candles_months(
                market=market,
                to=to,
                count=count,
            )
        if interval == "1y":
            return client.quotation.get_candles_years(
                market=market,
                to=to,
                count=count,
            )
        raise ValueError(
            f"Invalid interval: {interval!r}. "
            f"Expected one of: 1s, 1m, 3m, 5m, 10m, 15m, 30m, 60m, 240m, 1d, 1w, 1M, 1y"
        )


def get_candles_df(
    market: str,
    *,
    interval: str,
    to: str | None = None,
    count: int | None = None,
) -> pd.DataFrame:
    with Upbeat() as client:
        if interval in _MINUTE_UNITS:
            return client.quotation.get_candles_minutes_df(
                market=market,
                unit=_MINUTE_UNITS[interval],
                to=to,
                count=count,  # type: ignore[arg-type]
            )
        if interval == "1s":
            return client.quotation.get_candles_seconds_df(
                market=market,
                to=to,
                count=count,
            )
        if interval == "1d":
            return client.quotation.get_candles_days_df(
                market=market,
                to=to,
                count=count,
            )
        if interval == "1w":
            return client.quotation.get_candles_weeks_df(
                market=market,
                to=to,
                count=count,
            )
        if interval == "1M":
            return client.quotation.get_candles_months_df(
                market=market,
                to=to,
                count=count,
            )
        if interval == "1y":
            return client.quotation.get_candles_years_df(
                market=market,
                to=to,
                count=count,
            )
        raise ValueError(
            f"Invalid interval: {interval!r}. "
            f"Expected one of: 1s, 1m, 3m, 5m, 10m, 15m, 30m, 60m, 240m, 1d, 1w, 1M, 1y"
        )


def get_orderbook(market: str) -> Orderbook:
    with Upbeat() as client:
        return client.quotation.get_orderbooks(market)[0]


def get_orderbooks(markets: str) -> list[Orderbook]:
    with Upbeat() as client:
        return client.quotation.get_orderbooks(markets)


def get_trades(
    market: str,
    *,
    to: str | None = None,
    count: int | None = None,
    cursor: str | None = None,
    days_ago: int | None = None,
) -> list[Trade]:
    with Upbeat() as client:
        return client.quotation.get_trades(
            market,
            to=to,
            count=count,
            cursor=cursor,
            days_ago=days_ago,
        )


def get_markets(*, is_details: bool = False) -> list[TradingPair]:
    with Upbeat() as client:
        return client.markets.get_trading_pairs(is_details=is_details)
