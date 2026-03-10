from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from upbeat.shortcuts._order_helpers import (
    cancel_all_orders,
    market_buy_krw,
    place_and_wait,
)
from upbeat.types.order import (
    CancelResult,
    CancelResultGroup,
    OrderCreated,
    OrderDetail,
)


def _make_order_created(uuid: str = "test-uuid") -> OrderCreated:
    return OrderCreated(
        market="KRW-BTC",
        uuid=uuid,
        side="bid",
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


def _make_order_detail(uuid: str = "test-uuid", state: str = "done") -> OrderDetail:
    return OrderDetail(
        market="KRW-BTC",
        uuid=uuid,
        side="bid",
        ord_type="price",
        price="10000",
        state=state,
        created_at="2026-01-01T00:00:00",
        volume=None,
        remaining_volume="0",
        executed_volume="0.0001",
        reserved_fee="0",
        remaining_fee="0",
        paid_fee="5",
        locked="0",
        prevented_locked="0",
        trades_count=1,
        trades=[],
    )


class TestMarketBuyKrw:
    def test_params_passed(self) -> None:
        client = MagicMock()
        client.orders.create.return_value = _make_order_created()

        result = market_buy_krw(client, "KRW-BTC", 50_000.0)

        client.orders.create.assert_called_once_with(
            market="KRW-BTC",
            side="bid",
            ord_type="price",
            price="50000",
        )
        assert result.uuid == "test-uuid"


class TestPlaceAndWait:
    @patch("upbeat.shortcuts._order_helpers.time.sleep")
    def test_immediate_fill(self, mock_sleep: MagicMock) -> None:
        client = MagicMock()
        client.orders.create.return_value = _make_order_created()
        client.orders.get.return_value = _make_order_detail(state="done")

        result = place_and_wait(
            client,
            market="KRW-BTC",
            side="bid",
            ord_type="limit",
            price="50000000",
            volume="0.001",
            timeout=10.0,
        )

        assert result.state == "done"
        mock_sleep.assert_not_called()

    @patch("upbeat.shortcuts._order_helpers.time.sleep")
    @patch("upbeat.shortcuts._order_helpers.time.monotonic")
    def test_poll_then_fill(
        self, mock_monotonic: MagicMock, mock_sleep: MagicMock
    ) -> None:
        client = MagicMock()
        client.orders.create.return_value = _make_order_created()
        client.orders.get.side_effect = [
            _make_order_detail(state="wait"),
            _make_order_detail(state="done"),
        ]
        mock_monotonic.side_effect = [0.0, 1.0, 2.0]

        result = place_and_wait(
            client,
            market="KRW-BTC",
            side="bid",
            ord_type="limit",
            price="50000000",
            volume="0.001",
            timeout=10.0,
            poll_interval=1.0,
        )

        assert result.state == "done"
        mock_sleep.assert_called_once_with(1.0)

    @patch("upbeat.shortcuts._order_helpers.time.sleep")
    @patch("upbeat.shortcuts._order_helpers.time.monotonic")
    def test_timeout(
        self, mock_monotonic: MagicMock, mock_sleep: MagicMock
    ) -> None:
        client = MagicMock()
        client.orders.create.return_value = _make_order_created()
        client.orders.get.return_value = _make_order_detail(state="wait")
        mock_monotonic.side_effect = [0.0, 1.0, 11.0]

        with pytest.raises(TimeoutError, match="not filled within"):
            place_and_wait(
                client,
                market="KRW-BTC",
                side="bid",
                ord_type="limit",
                price="50000000",
                volume="0.001",
                timeout=10.0,
            )

    @patch("upbeat.shortcuts._order_helpers.time.sleep")
    def test_canceled_order(self, mock_sleep: MagicMock) -> None:
        client = MagicMock()
        client.orders.create.return_value = _make_order_created()
        client.orders.get.return_value = _make_order_detail(state="cancel")

        with pytest.raises(RuntimeError, match="was canceled"):
            place_and_wait(
                client,
                market="KRW-BTC",
                side="bid",
                ord_type="limit",
                price="50000000",
                volume="0.001",
                timeout=10.0,
            )


class TestCancelAllOrders:
    def test_delegates_to_cancel_open(self) -> None:
        client = MagicMock()
        expected = CancelResult(
            success=CancelResultGroup(count=2, orders=[]),
            failed=CancelResultGroup(count=0, orders=[]),
        )
        client.orders.cancel_open.return_value = expected

        result = cancel_all_orders(client)
        client.orders.cancel_open.assert_called_once_with(pairs=None)
        assert result.success.count == 2

    def test_with_market_filter(self) -> None:
        client = MagicMock()
        expected = CancelResult(
            success=CancelResultGroup(count=1, orders=[]),
            failed=CancelResultGroup(count=0, orders=[]),
        )
        client.orders.cancel_open.return_value = expected

        result = cancel_all_orders(client, market="KRW-BTC")
        client.orders.cancel_open.assert_called_once_with(pairs="KRW-BTC")
        assert result.success.count == 1
