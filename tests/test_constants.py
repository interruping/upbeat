from decimal import Decimal

import pytest

from upbeat._constants import (
    OrderSide,
    OrderState,
    OrderType,
    SortOrder,
    TimeInForce,
    get_krw_tick_size,
    round_to_tick,
)

# ── Tick size table ──────────────────────────────────────────────────────


class TestGetKrwTickSize:
    @pytest.mark.parametrize(
        ("price", "expected"),
        [
            (Decimal("2_000_000"), Decimal("1000")),
            (Decimal("5_000_000"), Decimal("1000")),
            (Decimal("1_000_000"), Decimal("500")),
            (Decimal("1_999_999"), Decimal("500")),
            (Decimal("500_000"), Decimal("100")),
            (Decimal("999_999"), Decimal("100")),
            (Decimal("100_000"), Decimal("50")),
            (Decimal("499_999"), Decimal("50")),
            (Decimal("10_000"), Decimal("10")),
            (Decimal("99_999"), Decimal("10")),
            (Decimal("1_000"), Decimal("5")),
            (Decimal("9_999"), Decimal("5")),
            (Decimal("100"), Decimal("1")),
            (Decimal("999"), Decimal("1")),
            (Decimal("10"), Decimal("0.1")),
            (Decimal("99"), Decimal("0.1")),
            (Decimal("1"), Decimal("0.01")),
            (Decimal("9.99"), Decimal("0.01")),
            (Decimal("0.999"), Decimal("0.001")),
            (Decimal("0.001"), Decimal("0.001")),
        ],
    )
    def test_tick_size_boundaries(self, price: Decimal, expected: Decimal):
        assert get_krw_tick_size(price) == expected


class TestRoundToTick:
    @pytest.mark.parametrize(
        ("price", "expected"),
        [
            (Decimal("2_000_500"), Decimal("2_000_000")),
            (Decimal("2_001_000"), Decimal("2_001_000")),
            (Decimal("1_500_123"), Decimal("1_500_000")),
            (Decimal("50_005"), Decimal("50_000")),
            (Decimal("1_234"), Decimal("1_230")),
            (Decimal("150"), Decimal("150")),
            (Decimal("15.37"), Decimal("15.3")),
            (Decimal("5.123"), Decimal("5.12")),
            (Decimal("0.5678"), Decimal("0.567")),
        ],
    )
    def test_round_to_tick(self, price: Decimal, expected: Decimal):
        assert round_to_tick(price) == expected


# ── StrEnum constants ────────────────────────────────────────────────────


class TestStrEnumConstants:
    def test_order_side_values(self):
        assert OrderSide.BID == "bid"
        assert OrderSide.ASK == "ask"

    def test_order_type_values(self):
        assert OrderType.LIMIT == "limit"
        assert OrderType.PRICE == "price"
        assert OrderType.MARKET == "market"
        assert OrderType.BEST == "best"

    def test_order_state_values(self):
        assert OrderState.WAIT == "wait"
        assert OrderState.WATCH == "watch"
        assert OrderState.DONE == "done"
        assert OrderState.CANCEL == "cancel"

    def test_time_in_force_values(self):
        assert TimeInForce.IOC == "ioc"
        assert TimeInForce.FOK == "fok"

    def test_sort_order_values(self):
        assert SortOrder.ASC == "asc"
        assert SortOrder.DESC == "desc"

    def test_str_returns_value(self):
        assert str(OrderSide.BID) == "bid"

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError):
            OrderSide("invalid")
