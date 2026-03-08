from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from upbeat.strategies.alerts import price_alert
from upbeat.types.quotation import Ticker


def _make_ticker(market: str, trade_price: float) -> Ticker:
    return Ticker(
        market=market,
        trade_date="20260101",
        trade_time="000000",
        trade_date_kst="20260101",
        trade_time_kst="090000",
        trade_timestamp=0,
        opening_price=trade_price,
        high_price=trade_price,
        low_price=trade_price,
        trade_price=trade_price,
        prev_closing_price=trade_price,
        change="EVEN",
        change_price=0.0,
        change_rate=0.0,
        signed_change_price=0.0,
        signed_change_rate=0.0,
        trade_volume=0.0,
        acc_trade_price=0.0,
        acc_trade_price_24h=0.0,
        acc_trade_volume=0.0,
        acc_trade_volume_24h=0.0,
        highest_52_week_price=trade_price,
        highest_52_week_date="20260101",
        lowest_52_week_price=trade_price,
        lowest_52_week_date="20260101",
        timestamp=0,
    )


class TestPriceAlert:
    def test_no_thresholds_raises(self) -> None:
        client = MagicMock()
        callback = MagicMock()

        with pytest.raises(ValueError, match="At least one"):
            price_alert(client, market="KRW-BTC", callback=callback)

    @patch("upbeat.strategies.alerts.time.sleep")
    def test_stop_loss_trigger(self, mock_sleep: MagicMock) -> None:
        client = MagicMock()
        callback = MagicMock()
        client.quotation.get_tickers.return_value = [
            _make_ticker("KRW-BTC", 45_000_000.0),
        ]

        price_alert(
            client,
            market="KRW-BTC",
            stop_loss=50_000_000.0,
            callback=callback,
            poll_interval=1.0,
        )

        callback.assert_called_once_with("KRW-BTC", "stop_loss", 45_000_000.0)
        mock_sleep.assert_not_called()

    @patch("upbeat.strategies.alerts.time.sleep")
    def test_take_profit_trigger(self, mock_sleep: MagicMock) -> None:
        client = MagicMock()
        callback = MagicMock()
        client.quotation.get_tickers.return_value = [
            _make_ticker("KRW-BTC", 60_000_000.0),
        ]

        price_alert(
            client,
            market="KRW-BTC",
            take_profit=55_000_000.0,
            callback=callback,
            poll_interval=1.0,
        )

        callback.assert_called_once_with("KRW-BTC", "take_profit", 60_000_000.0)

    @patch("upbeat.strategies.alerts.time.sleep")
    def test_polling_until_trigger(self, mock_sleep: MagicMock) -> None:
        client = MagicMock()
        callback = MagicMock()
        client.quotation.get_tickers.side_effect = [
            [_make_ticker("KRW-BTC", 52_000_000.0)],
            [_make_ticker("KRW-BTC", 51_000_000.0)],
            [_make_ticker("KRW-BTC", 49_000_000.0)],
        ]

        price_alert(
            client,
            market="KRW-BTC",
            stop_loss=50_000_000.0,
            callback=callback,
            poll_interval=5.0,
        )

        assert client.quotation.get_tickers.call_count == 3
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(5.0)
        callback.assert_called_once_with("KRW-BTC", "stop_loss", 49_000_000.0)

    @patch("upbeat.strategies.alerts.time.sleep")
    def test_callback_args(self, mock_sleep: MagicMock) -> None:
        client = MagicMock()
        callback = MagicMock()
        client.quotation.get_tickers.return_value = [
            _make_ticker("KRW-ETH", 3_500_000.0),
        ]

        price_alert(
            client,
            market="KRW-ETH",
            take_profit=3_000_000.0,
            callback=callback,
        )

        callback.assert_called_once_with("KRW-ETH", "take_profit", 3_500_000.0)
