from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import upbeat
from upbeat._convenience import (
    get_candles,
    get_markets,
    get_orderbook,
    get_orderbooks,
    get_ticker,
    get_tickers,
    get_trades,
)


@pytest.fixture()
def mock_client():
    with patch("upbeat._convenience.Upbeat") as MockUpbeat:
        client = MagicMock()
        MockUpbeat.return_value.__enter__ = MagicMock(return_value=client)
        MockUpbeat.return_value.__exit__ = MagicMock(return_value=False)
        yield client


class TestGetTicker:
    def test_returns_first_element(self, mock_client: MagicMock) -> None:
        sentinel = object()
        mock_client.quotation.get_tickers.return_value = [sentinel]

        result = get_ticker("KRW-BTC")

        mock_client.quotation.get_tickers.assert_called_once_with("KRW-BTC")
        assert result is sentinel


class TestGetTickers:
    def test_delegates_to_client(self, mock_client: MagicMock) -> None:
        sentinel = [object(), object()]
        mock_client.quotation.get_tickers.return_value = sentinel

        result = get_tickers("KRW-BTC,KRW-ETH")

        mock_client.quotation.get_tickers.assert_called_once_with("KRW-BTC,KRW-ETH")
        assert result is sentinel


class TestGetCandles:
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
        sentinel = [object()]
        mock_client.quotation.get_candles_minutes.return_value = sentinel

        result = get_candles("KRW-BTC", interval=interval)

        mock_client.quotation.get_candles_minutes.assert_called_once_with(
            market="KRW-BTC", unit=expected_unit, to=None, count=None,
        )
        assert result is sentinel

    def test_second_interval(self, mock_client: MagicMock) -> None:
        sentinel = [object()]
        mock_client.quotation.get_candles_seconds.return_value = sentinel

        result = get_candles("KRW-BTC", interval="1s")

        mock_client.quotation.get_candles_seconds.assert_called_once_with(
            market="KRW-BTC", to=None, count=None,
        )
        assert result is sentinel

    def test_day_interval(self, mock_client: MagicMock) -> None:
        sentinel = [object()]
        mock_client.quotation.get_candles_days.return_value = sentinel

        result = get_candles("KRW-BTC", interval="1d")

        mock_client.quotation.get_candles_days.assert_called_once_with(
            market="KRW-BTC", to=None, count=None,
        )
        assert result is sentinel

    def test_week_interval(self, mock_client: MagicMock) -> None:
        sentinel = [object()]
        mock_client.quotation.get_candles_weeks.return_value = sentinel

        result = get_candles("KRW-BTC", interval="1w")

        mock_client.quotation.get_candles_weeks.assert_called_once_with(
            market="KRW-BTC", to=None, count=None,
        )
        assert result is sentinel

    def test_month_interval(self, mock_client: MagicMock) -> None:
        sentinel = [object()]
        mock_client.quotation.get_candles_months.return_value = sentinel

        result = get_candles("KRW-BTC", interval="1M")

        mock_client.quotation.get_candles_months.assert_called_once_with(
            market="KRW-BTC", to=None, count=None,
        )
        assert result is sentinel

    def test_year_interval(self, mock_client: MagicMock) -> None:
        sentinel = [object()]
        mock_client.quotation.get_candles_years.return_value = sentinel

        result = get_candles("KRW-BTC", interval="1y")

        mock_client.quotation.get_candles_years.assert_called_once_with(
            market="KRW-BTC", to=None, count=None,
        )
        assert result is sentinel

    def test_optional_params_forwarded(self, mock_client: MagicMock) -> None:
        mock_client.quotation.get_candles_minutes.return_value = []

        get_candles("KRW-BTC", interval="5m", to="2024-01-01T00:00:00", count=10)

        mock_client.quotation.get_candles_minutes.assert_called_once_with(
            market="KRW-BTC", unit=5, to="2024-01-01T00:00:00", count=10,
        )

    def test_invalid_interval_raises_value_error(self) -> None:
        with patch("upbeat._convenience.Upbeat"):
            with pytest.raises(ValueError, match="Invalid interval"):
                get_candles("KRW-BTC", interval="2h")


class TestGetOrderbook:
    def test_returns_first_element(self, mock_client: MagicMock) -> None:
        sentinel = object()
        mock_client.quotation.get_orderbooks.return_value = [sentinel]

        result = get_orderbook("KRW-BTC")

        mock_client.quotation.get_orderbooks.assert_called_once_with("KRW-BTC")
        assert result is sentinel


class TestGetOrderbooks:
    def test_delegates_to_client(self, mock_client: MagicMock) -> None:
        sentinel = [object(), object()]
        mock_client.quotation.get_orderbooks.return_value = sentinel

        result = get_orderbooks("KRW-BTC,KRW-ETH")

        mock_client.quotation.get_orderbooks.assert_called_once_with("KRW-BTC,KRW-ETH")
        assert result is sentinel


class TestGetTrades:
    def test_delegates_with_defaults(self, mock_client: MagicMock) -> None:
        sentinel = [object()]
        mock_client.quotation.get_trades.return_value = sentinel

        result = get_trades("KRW-BTC")

        mock_client.quotation.get_trades.assert_called_once_with(
            "KRW-BTC", to=None, count=None, cursor=None, days_ago=None,
        )
        assert result is sentinel

    def test_optional_params_forwarded(self, mock_client: MagicMock) -> None:
        mock_client.quotation.get_trades.return_value = []

        get_trades("KRW-BTC", to="12:00:00", count=5, cursor="abc", days_ago=1)

        mock_client.quotation.get_trades.assert_called_once_with(
            "KRW-BTC", to="12:00:00", count=5, cursor="abc", days_ago=1,
        )


class TestGetMarkets:
    def test_delegates_with_default(self, mock_client: MagicMock) -> None:
        sentinel = [object()]
        mock_client.markets.get_trading_pairs.return_value = sentinel

        result = get_markets()

        mock_client.markets.get_trading_pairs.assert_called_once_with(is_details=False)
        assert result is sentinel

    def test_is_details_forwarded(self, mock_client: MagicMock) -> None:
        mock_client.markets.get_trading_pairs.return_value = []

        get_markets(is_details=True)

        mock_client.markets.get_trading_pairs.assert_called_once_with(is_details=True)


class TestModuleLevelAccess:
    def test_functions_accessible_from_upbeat_module(self) -> None:
        assert upbeat.get_ticker is get_ticker
        assert upbeat.get_tickers is get_tickers
        assert upbeat.get_candles is get_candles
        assert upbeat.get_orderbook is get_orderbook
        assert upbeat.get_orderbooks is get_orderbooks
        assert upbeat.get_trades is get_trades
        assert upbeat.get_markets is get_markets
