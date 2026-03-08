from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from upbeat.types.quotation import CandleBase

if TYPE_CHECKING:
    import pandas as pd

_COLUMNS = [
    "market",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "timestamp",
]


def candles_to_dataframe(candles: Sequence[CandleBase]) -> pd.DataFrame:
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame support. "
            "Install it with: pip install 'upbeat[pandas]'"
        ) from None

    if not candles:
        df = pd.DataFrame(columns=_COLUMNS)
        df.index = pd.DatetimeIndex([], name="datetime", tz="UTC")
        return df

    rows = [
        {
            "market": c.market,
            "open": c.opening_price,
            "high": c.high_price,
            "low": c.low_price,
            "close": c.trade_price,
            "volume": c.candle_acc_trade_volume,
            "timestamp": c.timestamp,
        }
        for c in candles
    ]
    df = pd.DataFrame(rows)
    df.index = pd.DatetimeIndex(
        pd.to_datetime([c.candle_date_time_utc for c in candles], utc=True),
        name="datetime",
    )
    return df
