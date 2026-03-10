from __future__ import annotations

from unittest.mock import MagicMock

from upbeat.shortcuts._portfolio import get_portfolio, get_portfolio_value
from upbeat.types.account import Account
from upbeat.types.quotation import Ticker


def _make_account(
    currency: str,
    balance: str = "0.0",
    locked: str = "0.0",
) -> Account:
    return Account(
        currency=currency,
        balance=balance,
        locked=locked,
        avg_buy_price="0",
        avg_buy_price_modified=False,
        unit_currency="KRW",
    )


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


class TestGetPortfolioValue:
    def test_krw_only(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="500000.0"),
        ]

        result = get_portfolio_value(client)
        assert result == 500_000.0
        client.quotation.get_tickers.assert_not_called()

    def test_mixed_portfolio(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="100000.0"),
            _make_account("BTC", balance="0.01"),
            _make_account("ETH", balance="1.0"),
        ]
        client.quotation.get_tickers.return_value = [
            _make_ticker("KRW-BTC", 50_000_000.0),
            _make_ticker("KRW-ETH", 3_000_000.0),
        ]

        result = get_portfolio_value(client)
        expected = 100_000.0 + 0.01 * 50_000_000.0 + 1.0 * 3_000_000.0
        assert result == expected
        client.quotation.get_tickers.assert_called_once_with("KRW-BTC,KRW-ETH")

    def test_zero_balance_excluded(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="100000.0"),
            _make_account("BTC", balance="0.0", locked="0.0"),
        ]

        result = get_portfolio_value(client)
        assert result == 100_000.0
        client.quotation.get_tickers.assert_not_called()

    def test_locked_included(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="100000.0", locked="50000.0"),
            _make_account("BTC", balance="0.005", locked="0.005"),
        ]
        client.quotation.get_tickers.return_value = [
            _make_ticker("KRW-BTC", 50_000_000.0),
        ]

        result = get_portfolio_value(client)
        expected = 150_000.0 + 0.01 * 50_000_000.0
        assert result == expected


class TestGetPortfolio:
    def test_krw_only(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="500000.0", locked="10000.0"),
        ]

        items = get_portfolio(client)
        assert len(items) == 1
        assert items[0].currency == "KRW"
        assert items[0].balance == 500_000.0
        assert items[0].locked == 10_000.0
        assert items[0].current_price == 1.0
        assert items[0].market == "KRW"
        assert items[0].estimated_value_krw == 510_000.0

    def test_mixed_portfolio(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="100000.0"),
            _make_account("BTC", balance="0.01"),
        ]
        client.quotation.get_tickers.return_value = [
            _make_ticker("KRW-BTC", 50_000_000.0),
        ]

        items = get_portfolio(client)
        assert len(items) == 2

        krw_item = next(i for i in items if i.currency == "KRW")
        assert krw_item.estimated_value_krw == 100_000.0

        btc_item = next(i for i in items if i.currency == "BTC")
        assert btc_item.balance == 0.01
        assert btc_item.current_price == 50_000_000.0
        assert btc_item.market == "KRW-BTC"
        assert btc_item.estimated_value_krw == 0.01 * 50_000_000.0

    def test_zero_balance_excluded(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="100000.0"),
            _make_account("BTC", balance="0.0", locked="0.0"),
        ]

        items = get_portfolio(client)
        assert len(items) == 1
        assert items[0].currency == "KRW"
