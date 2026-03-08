from __future__ import annotations

from unittest.mock import MagicMock, patch

from upbeat.strategies.dca import dca
from upbeat.types.order import OrderCreated


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


class TestDCA:
    @patch("upbeat.strategies.dca.time.sleep")
    def test_splits(self, mock_sleep: MagicMock) -> None:
        client = MagicMock()
        client.orders.create.return_value = _make_order_created()

        result = dca(
            client,
            market="KRW-BTC",
            total_amount=100_000.0,
            splits=4,
            interval_seconds=60.0,
        )

        assert result.splits_completed == 4
        assert len(result.orders) == 4
        assert result.total_spent == 100_000.0
        assert client.orders.create.call_count == 4
        assert mock_sleep.call_count == 3
        mock_sleep.assert_called_with(60.0)

    @patch("upbeat.strategies.dca.time.sleep")
    def test_partial_failure(self, mock_sleep: MagicMock) -> None:
        client = MagicMock()
        client.orders.create.side_effect = [
            _make_order_created("uuid-1"),
            RuntimeError("API error"),
            _make_order_created("uuid-3"),
        ]

        result = dca(
            client,
            market="KRW-BTC",
            total_amount=150_000.0,
            splits=3,
            interval_seconds=30.0,
        )

        assert result.splits_completed == 2
        assert len(result.orders) == 2
        assert result.total_spent == 100_000.0
        assert mock_sleep.call_count == 2

    @patch("upbeat.strategies.dca.time.sleep")
    def test_no_sleep_after_last_split(self, mock_sleep: MagicMock) -> None:
        client = MagicMock()
        client.orders.create.return_value = _make_order_created()

        dca(
            client,
            market="KRW-BTC",
            total_amount=10_000.0,
            splits=1,
            interval_seconds=60.0,
        )

        mock_sleep.assert_not_called()

    @patch("upbeat.strategies.dca.time.sleep")
    def test_amount_per_split(self, mock_sleep: MagicMock) -> None:
        client = MagicMock()
        client.orders.create.return_value = _make_order_created()

        dca(
            client,
            market="KRW-BTC",
            total_amount=100_000.0,
            splits=5,
            interval_seconds=10.0,
        )

        for call in client.orders.create.call_args_list:
            assert call.kwargs["price"] == "20000"
