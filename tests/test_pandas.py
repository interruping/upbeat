from __future__ import annotations

import builtins
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from upbeat._convenience import get_candles_df
from upbeat._pandas import candles_to_dataframe
from upbeat.types.quotation import (
    CandleDay,
    CandleMinute,
    CandlePeriod,
    CandleSecond,
)

_CANDLE_BASE_FIELDS = {
    "market": "KRW-BTC",
    "candle_date_time_utc": "2024-01-15T09:00:00",
    "candle_date_time_kst": "2024-01-15T18:00:00",
    "opening_price": 60000000.0,
    "high_price": 61000000.0,
    "low_price": 59000000.0,
    "trade_price": 60500000.0,
    "timestamp": 1705305600000,
    "candle_acc_trade_price": 1000000000.0,
    "candle_acc_trade_volume": 16.5,
}


class TestCandlesToDataFrame:
    def test_returns_dataframe(self) -> None:
        candle = CandleMinute(**_CANDLE_BASE_FIELDS, unit=1)
        result = candles_to_dataframe([candle])
        assert isinstance(result, pd.DataFrame)

    def test_ohlcv_columns(self) -> None:
        candle = CandleMinute(**_CANDLE_BASE_FIELDS, unit=1)
        df = candles_to_dataframe([candle])

        assert df["open"].iloc[0] == 60000000.0
        assert df["high"].iloc[0] == 61000000.0
        assert df["low"].iloc[0] == 59000000.0
        assert df["close"].iloc[0] == 60500000.0
        assert df["volume"].iloc[0] == 16.5
        assert df["timestamp"].iloc[0] == 1705305600000

    def test_market_column(self) -> None:
        candle = CandleMinute(**_CANDLE_BASE_FIELDS, unit=1)
        df = candles_to_dataframe([candle])
        assert df["market"].iloc[0] == "KRW-BTC"

    def test_datetime_index(self) -> None:
        candle = CandleMinute(**_CANDLE_BASE_FIELDS, unit=1)
        df = candles_to_dataframe([candle])

        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index.name == "datetime"
        assert str(df.index.tz) == "UTC"

    def test_empty_list(self) -> None:
        df = candles_to_dataframe([])

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert "open" in df.columns
        assert "high" in df.columns
        assert "low" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns
        assert isinstance(df.index, pd.DatetimeIndex)
        assert df.index.name == "datetime"

    def test_multiple_candles(self) -> None:
        c1 = CandleMinute(
            **{**_CANDLE_BASE_FIELDS, "candle_date_time_utc": "2024-01-15T09:00:00"},
            unit=1,
        )
        c2 = CandleMinute(
            **{**_CANDLE_BASE_FIELDS, "candle_date_time_utc": "2024-01-15T09:01:00"},
            unit=1,
        )
        df = candles_to_dataframe([c1, c2])
        assert len(df) == 2

    def test_candle_second(self) -> None:
        candle = CandleSecond(**_CANDLE_BASE_FIELDS)
        df = candles_to_dataframe([candle])
        assert len(df) == 1
        assert df["close"].iloc[0] == 60500000.0

    def test_candle_day(self) -> None:
        candle = CandleDay(
            **_CANDLE_BASE_FIELDS,
            prev_closing_price=59500000.0,
            change_price=1000000.0,
            change_rate=0.0168,
        )
        df = candles_to_dataframe([candle])
        assert len(df) == 1
        assert df["close"].iloc[0] == 60500000.0

    def test_candle_period(self) -> None:
        candle = CandlePeriod(
            **_CANDLE_BASE_FIELDS,
            first_day_of_period="2024-01-15",
        )
        df = candles_to_dataframe([candle])
        assert len(df) == 1
        assert df["close"].iloc[0] == 60500000.0


class TestImportError:
    def test_missing_pandas_raises_import_error(self) -> None:
        real_import = builtins.__import__

        def mock_import(name: str, *args, **kwargs):
            if name == "pandas":
                raise ImportError
            return real_import(name, *args, **kwargs)

        with patch.object(builtins, "__import__", side_effect=mock_import):
            candle = CandleMinute(**_CANDLE_BASE_FIELDS, unit=1)
            with pytest.raises(ImportError, match="upbeat\\[pandas\\]"):
                candles_to_dataframe([candle])


@pytest.fixture()
def mock_client():
    with patch("upbeat._convenience.Upbeat") as MockUpbeat:
        client = MagicMock()
        MockUpbeat.return_value.__enter__ = MagicMock(return_value=client)
        MockUpbeat.return_value.__exit__ = MagicMock(return_value=False)
        yield client


class TestGetCandlesDf:
    @pytest.mark.parametrize(
        ("interval", "expected_unit"),
        [
            ("1m", 1), ("3m", 3), ("5m", 5), ("10m", 10),
            ("15m", 15), ("30m", 30), ("60m", 60), ("240m", 240),
        ],
    )
    def test_minute_intervals(
        self, mock_client: MagicMock, interval: str, expected_unit: int,
    ) -> None:
        sentinel = MagicMock()
        mock_client.quotation.get_candles_minutes_df.return_value = sentinel

        result = get_candles_df("KRW-BTC", interval=interval)

        mock_client.quotation.get_candles_minutes_df.assert_called_once_with(
            market="KRW-BTC", unit=expected_unit, to=None, count=None,
        )
        assert result is sentinel

    def test_second_interval(self, mock_client: MagicMock) -> None:
        sentinel = MagicMock()
        mock_client.quotation.get_candles_seconds_df.return_value = sentinel

        result = get_candles_df("KRW-BTC", interval="1s")

        mock_client.quotation.get_candles_seconds_df.assert_called_once_with(
            market="KRW-BTC", to=None, count=None,
        )
        assert result is sentinel

    def test_day_interval(self, mock_client: MagicMock) -> None:
        sentinel = MagicMock()
        mock_client.quotation.get_candles_days_df.return_value = sentinel

        result = get_candles_df("KRW-BTC", interval="1d")

        mock_client.quotation.get_candles_days_df.assert_called_once_with(
            market="KRW-BTC", to=None, count=None,
        )
        assert result is sentinel

    def test_week_interval(self, mock_client: MagicMock) -> None:
        sentinel = MagicMock()
        mock_client.quotation.get_candles_weeks_df.return_value = sentinel

        result = get_candles_df("KRW-BTC", interval="1w")

        mock_client.quotation.get_candles_weeks_df.assert_called_once_with(
            market="KRW-BTC", to=None, count=None,
        )
        assert result is sentinel

    def test_month_interval(self, mock_client: MagicMock) -> None:
        sentinel = MagicMock()
        mock_client.quotation.get_candles_months_df.return_value = sentinel

        result = get_candles_df("KRW-BTC", interval="1M")

        mock_client.quotation.get_candles_months_df.assert_called_once_with(
            market="KRW-BTC", to=None, count=None,
        )
        assert result is sentinel

    def test_year_interval(self, mock_client: MagicMock) -> None:
        sentinel = MagicMock()
        mock_client.quotation.get_candles_years_df.return_value = sentinel

        result = get_candles_df("KRW-BTC", interval="1y")

        mock_client.quotation.get_candles_years_df.assert_called_once_with(
            market="KRW-BTC", to=None, count=None,
        )
        assert result is sentinel

    def test_invalid_interval_raises_value_error(self) -> None:
        with patch("upbeat._convenience.Upbeat"), pytest.raises(
            ValueError, match="Invalid interval"
        ):
            get_candles_df("KRW-BTC", interval="2h")
