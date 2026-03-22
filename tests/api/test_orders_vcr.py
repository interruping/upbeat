from __future__ import annotations

import os

from tests.conftest import upbeat_vcr
from upbeat import Upbeat
from upbeat.types.order import (
    CancelAndNewOrderResponse,
    CancelResult,
    OrderByIds,
    OrderCanceled,
    OrderChance,
    OrderCreated,
    OrderDetail,
    OrderOpen,
)

_MARKET = "KRW-BTC"
# 절대 체결되지 않는 극저가 지정가 (BTC ~1.4억원 대비 1천만원)
_LIMIT_PRICE = "10000000"
_LIMIT_VOLUME = "0.0005"  # total = 5,000 KRW ≥ 최소주문금액


def _client() -> Upbeat:
    return Upbeat(
        access_key=os.environ.get("UPBIT_ACCESS_KEY", "test-key"),
        secret_key=os.environ.get("UPBIT_SECRET_KEY", "test-secret"),
        max_retries=0,
        auto_throttle=False,
    )


# ── Safe endpoints (거래 불필요) ───────────────────────────────────────


class TestGetChance:
    @upbeat_vcr.use_cassette("orders/get_chance.yaml")
    def test_returns_valid_chance(self) -> None:
        with _client() as client:
            result = client.orders.get_chance(market=_MARKET)

        assert isinstance(result, OrderChance)
        assert isinstance(result.bid_fee, str)
        assert isinstance(result.ask_fee, str)
        assert result.market.id == _MARKET


class TestCreateTest:
    @upbeat_vcr.use_cassette("orders/create_test.yaml")
    def test_creates_test_order(self) -> None:
        with _client() as client:
            result = client.orders.create_test(
                market=_MARKET,
                side="bid",
                ord_type="limit",
                price=_LIMIT_PRICE,
                volume=_LIMIT_VOLUME,
            )

        assert isinstance(result, OrderCreated)
        assert result.market == _MARKET
        assert result.side == "bid"


class TestListOpen:
    @upbeat_vcr.use_cassette("orders/list_open.yaml")
    def test_returns_open_orders(self) -> None:
        with _client() as client:
            result = client.orders.list_open()

        assert isinstance(result, list)
        for order in result:
            assert isinstance(order, OrderOpen)


class TestListClosed:
    @upbeat_vcr.use_cassette("orders/list_closed.yaml")
    def test_returns_closed_orders(self) -> None:
        with _client() as client:
            result = client.orders.list_closed()

        assert isinstance(result, list)


# ── Lifecycle: create → get → cancel (비용 0원) ───────────────────────


class TestOrderLifecycle:
    @upbeat_vcr.use_cassette("orders/lifecycle_create_get_cancel.yaml")
    def test_create_get_and_cancel(self) -> None:
        with _client() as client:
            created = client.orders.create(
                market=_MARKET,
                side="bid",
                ord_type="limit",
                price=_LIMIT_PRICE,
                volume=_LIMIT_VOLUME,
            )
            assert isinstance(created, OrderCreated)
            assert created.side == "bid"
            assert created.state == "wait"

            detail = client.orders.get(uuid=created.uuid)
            assert isinstance(detail, OrderDetail)
            assert detail.uuid == created.uuid
            assert detail.market == _MARKET

            canceled = client.orders.cancel(uuid=created.uuid)
            assert isinstance(canceled, OrderCanceled)
            assert canceled.uuid == created.uuid


# ── Lifecycle: cancel_and_new ─────────────────────────────────────────


class TestCancelAndNew:
    @upbeat_vcr.use_cassette("orders/lifecycle_cancel_and_new.yaml")
    def test_cancel_and_replace(self) -> None:
        with _client() as client:
            created = client.orders.create(
                market=_MARKET,
                side="bid",
                ord_type="limit",
                price=_LIMIT_PRICE,
                volume=_LIMIT_VOLUME,
            )

            replaced = client.orders.cancel_and_new(
                prev_order_uuid=created.uuid,
                new_ord_type="limit",
                new_price="10500000",
                new_volume=_LIMIT_VOLUME,
            )
            assert isinstance(replaced, CancelAndNewOrderResponse)
            assert replaced.new_order_uuid

            client.orders.cancel(uuid=replaced.new_order_uuid)


# ── Lifecycle: list_by_ids ────────────────────────────────────────────


class TestListByIds:
    @upbeat_vcr.use_cassette("orders/lifecycle_list_by_ids.yaml")
    def test_list_by_ids(self) -> None:
        with _client() as client:
            created = client.orders.create(
                market=_MARKET,
                side="bid",
                ord_type="limit",
                price=_LIMIT_PRICE,
                volume=_LIMIT_VOLUME,
            )

            result = client.orders.list_by_ids(uuids=[created.uuid])
            assert len(result) >= 1
            assert isinstance(result[0], OrderByIds)
            assert result[0].uuid == created.uuid

            client.orders.cancel(uuid=created.uuid)


# ── Lifecycle: bulk cancel_by_ids ─────────────────────────────────────


class TestBulkCancelByIds:
    @upbeat_vcr.use_cassette("orders/lifecycle_bulk_cancel_by_ids.yaml")
    def test_cancel_by_ids(self) -> None:
        with _client() as client:
            o1 = client.orders.create(
                market=_MARKET,
                side="bid",
                ord_type="limit",
                price=_LIMIT_PRICE,
                volume=_LIMIT_VOLUME,
            )
            o2 = client.orders.create(
                market=_MARKET,
                side="bid",
                ord_type="limit",
                price="10100000",
                volume=_LIMIT_VOLUME,
            )

            result = client.orders.cancel_by_ids(uuids=[o1.uuid, o2.uuid])
            assert isinstance(result, CancelResult)
            assert result.success.count == 2


# ── Lifecycle: cancel_open (마지막에 실행) ────────────────────────────


class TestCancelOpen:
    @upbeat_vcr.use_cassette("orders/lifecycle_cancel_open.yaml")
    def test_cancel_open(self) -> None:
        with _client() as client:
            client.orders.create(
                market=_MARKET,
                side="bid",
                ord_type="limit",
                price=_LIMIT_PRICE,
                volume=_LIMIT_VOLUME,
            )

            result = client.orders.cancel_open()
            assert isinstance(result, CancelResult)
            assert result.success.count >= 1


# ── Market buy → sell (시장가 체결 테스트) ─────────────────────────────


class TestMarketBuySell:
    @upbeat_vcr.use_cassette("orders/market_buy_sell.yaml")
    def test_market_buy_and_sell(self) -> None:
        with _client() as client:
            # 시장가 매수 (매도 최소금액 확보를 위해 10,000원)
            buy = client.orders.create(
                market=_MARKET,
                side="bid",
                ord_type="price",
                price="10000",
            )
            assert isinstance(buy, OrderCreated)
            assert buy.side == "bid"

            buy_detail = client.orders.get(uuid=buy.uuid)
            assert isinstance(buy_detail, OrderDetail)

            # 매수한 수량 전량 시장가 매도
            sell = client.orders.create(
                market=_MARKET,
                side="ask",
                ord_type="market",
                volume=buy_detail.executed_volume,
            )
            assert isinstance(sell, OrderCreated)
            assert sell.side == "ask"

            sell_detail = client.orders.get(uuid=sell.uuid)
            assert isinstance(sell_detail, OrderDetail)
