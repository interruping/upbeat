from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from upbeat.strategies.rebalance import rebalance
from upbeat.types.account import Account
from upbeat.types.order import OrderCreated
from upbeat.types.quotation import Ticker


def _make_account(currency: str, balance: str = "0.0", locked: str = "0.0") -> Account:
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


def _make_order_created(
    market: str = "KRW-BTC", side: str = "bid"
) -> OrderCreated:
    return OrderCreated(
        market=market,
        uuid="test-uuid",
        side=side,
        ord_type="price",
        price="10000",
        state="wait",
        created_at="2026-01-01T00:00:00",
        volume=None,
        remaining_volume="0",
        executed_volume="0",
        reserved_fee="0",
        remaining_fee="0",
        paid_fee="0",
        locked="10000",
        trades_count=0,
        prevented_volume="0",
        prevented_locked="0",
    )


class TestRebalance:
    def test_weight_sum_validation(self) -> None:
        client = MagicMock()

        with pytest.raises(ValueError, match="must sum to 1.0"):
            rebalance(client, targets={"KRW-BTC": 0.5, "KRW-ETH": 0.3})

    def test_sell_before_buy(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="200000.0"),
            _make_account("BTC", balance="0.01"),
            _make_account("ETH", balance="0.1"),
        ]
        client.quotation.get_tickers.return_value = [
            _make_ticker("KRW-BTC", 50_000_000.0),
            _make_ticker("KRW-ETH", 3_000_000.0),
        ]
        client.orders.create.return_value = _make_order_created()

        # Total = 200K + 500K + 300K = 1M
        # Target: BTC 30% (sell 200K), ETH 50% (buy 200K), KRW 20%
        result = rebalance(
            client,
            targets={"KRW-BTC": 0.3, "KRW-ETH": 0.5, "KRW": 0.2},
        )

        calls = client.orders.create.call_args_list
        # First call should be sell (ask)
        assert calls[0].kwargs["side"] == "ask"
        assert calls[0].kwargs["market"] == "KRW-BTC"
        assert calls[0].kwargs["ord_type"] == "market"
        # Second call should be buy (bid)
        assert calls[1].kwargs["side"] == "bid"
        assert calls[1].kwargs["market"] == "KRW-ETH"
        assert calls[1].kwargs["ord_type"] == "price"
        assert result.total_value == 1_000_000.0

    def test_min_order_filter(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="10000.0"),
            _make_account("BTC", balance="0.0002"),
        ]
        client.quotation.get_tickers.return_value = [
            _make_ticker("KRW-BTC", 50_000_000.0),
        ]

        # Total = 10K + 10K = 20K
        # BTC target 50% = 10K, current 10K, diff = 0 → skip
        result = rebalance(
            client, targets={"KRW-BTC": 0.5, "KRW": 0.5}
        )

        assert len(result.orders) == 0
        client.orders.create.assert_not_called()

    def test_sell_uses_market_order(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="0.0"),
            _make_account("BTC", balance="0.02"),
        ]
        client.quotation.get_tickers.return_value = [
            _make_ticker("KRW-BTC", 50_000_000.0),
        ]
        client.orders.create.return_value = _make_order_created(side="ask")

        # Total = 1M, target KRW 100% → sell all BTC
        result = rebalance(
            client, targets={"KRW": 1.0}
        )

        assert len(result.orders) == 1
        call = client.orders.create.call_args
        assert call.kwargs["side"] == "ask"
        assert call.kwargs["ord_type"] == "market"
        assert "volume" in call.kwargs

    def test_buy_uses_price_order(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW", balance="1000000.0"),
        ]

        client.orders.create.return_value = _make_order_created()

        # Total = 1M, target BTC 50% → buy 500K of BTC
        result = rebalance(
            client, targets={"KRW-BTC": 0.5, "KRW": 0.5}
        )

        assert len(result.orders) == 1
        call = client.orders.create.call_args
        assert call.kwargs["side"] == "bid"
        assert call.kwargs["ord_type"] == "price"
        assert "price" in call.kwargs
