from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from upbeat._auth import Credentials
from upbeat._constants import API_BASE_URL
from upbeat._errors import ValidationError
from upbeat._http import AsyncTransport, SyncTransport
from upbeat.api.orders import AsyncOrdersAPI, OrdersAPI
from upbeat.types.order import (
    CancelAndNewOrderResponse,
    CancelResult,
    OrderByIds,
    OrderCanceled,
    OrderChance,
    OrderClosed,
    OrderCreated,
    OrderDetail,
    OrderOpen,
)

# ── Helpers ──────────────────────────────────────────────────────────────


def _make_transport(handler: Any, **kwargs: Any) -> SyncTransport:
    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url=API_BASE_URL
    )
    return SyncTransport(http_client=client, **kwargs)


def _make_async_transport(handler: Any, **kwargs: Any) -> AsyncTransport:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url=API_BASE_URL
    )
    return AsyncTransport(http_client=client, **kwargs)


def _json_response(data: Any, status_code: int = 200) -> httpx.Response:
    return httpx.Response(status_code, json=data)


CREDENTIALS = Credentials(access_key="test-access-key", secret_key="test-secret-key")


# ── Shared fixture data ─────────────────────────────────────────────────

ORDER_CREATED_DATA: dict[str, Any] = {
    "market": "KRW-BTC",
    "uuid": "uuid-1234",
    "side": "bid",
    "ord_type": "limit",
    "price": "50000000",
    "state": "wait",
    "created_at": "2024-01-01T00:00:00+09:00",
    "volume": "0.001",
    "remaining_volume": "0.001",
    "executed_volume": "0",
    "reserved_fee": "25",
    "remaining_fee": "25",
    "paid_fee": "0",
    "locked": "50025",
    "trades_count": 0,
    "prevented_volume": "0",
    "prevented_locked": "0",
}

ORDER_DETAIL_DATA: dict[str, Any] = {
    "market": "KRW-BTC",
    "uuid": "uuid-1234",
    "side": "bid",
    "ord_type": "limit",
    "price": "50000000",
    "state": "done",
    "created_at": "2024-01-01T00:00:00+09:00",
    "volume": "0.001",
    "remaining_volume": "0",
    "executed_volume": "0.001",
    "reserved_fee": "25",
    "remaining_fee": "0",
    "paid_fee": "25",
    "locked": "0",
    "prevented_locked": "0",
    "trades_count": 1,
    "trades": [
        {
            "market": "KRW-BTC",
            "uuid": "trade-uuid-1",
            "price": "50000000",
            "volume": "0.001",
            "funds": "50000",
            "trend": "up",
            "created_at": "2024-01-01T00:00:01.000+09:00",
            "side": "bid",
        }
    ],
}

ORDER_OPEN_DATA: dict[str, Any] = {
    "market": "KRW-BTC",
    "uuid": "uuid-open-1",
    "side": "bid",
    "ord_type": "limit",
    "price": "50000000",
    "state": "wait",
    "created_at": "2024-01-01T00:00:00+09:00",
    "volume": "0.001",
    "remaining_volume": "0.001",
    "executed_volume": "0",
    "executed_funds": "0",
    "reserved_fee": "25",
    "remaining_fee": "25",
    "paid_fee": "0",
    "locked": "50025",
    "prevented_volume": "0",
    "prevented_locked": "0",
    "trades_count": 0,
}

ORDER_CLOSED_DATA: dict[str, Any] = {
    "market": "KRW-BTC",
    "uuid": "uuid-closed-1",
    "side": "bid",
    "ord_type": "limit",
    "price": "50000000",
    "state": "done",
    "created_at": "2024-01-01T00:00:00+09:00",
    "volume": "0.001",
    "remaining_volume": "0",
    "executed_volume": "0.001",
    "executed_funds": "50000",
    "reserved_fee": "25",
    "remaining_fee": "0",
    "paid_fee": "25",
    "locked": "0",
    "prevented_volume": "0",
    "prevented_locked": "0",
    "trades_count": 1,
}

ORDER_BY_IDS_DATA: dict[str, Any] = {
    "market": "KRW-BTC",
    "uuid": "uuid-byid-1",
    "side": "bid",
    "ord_type": "limit",
    "price": "50000000",
    "state": "wait",
    "created_at": "2024-01-01T00:00:00+09:00",
    "volume": "0.001",
    "remaining_volume": "0.001",
    "executed_volume": "0",
    "executed_funds": "0",
    "reserved_fee": "25",
    "remaining_fee": "25",
    "paid_fee": "0",
    "locked": "50025",
    "prevented_locked": "0",
    "trades_count": 0,
}

ORDER_CANCELED_DATA: dict[str, Any] = {
    "market": "KRW-BTC",
    "uuid": "uuid-cancel-1",
    "side": "bid",
    "ord_type": "limit",
    "price": "50000000",
    "state": "wait",
    "created_at": "2024-01-01T00:00:00+09:00",
    "volume": "0.001",
    "remaining_volume": "0.001",
    "executed_volume": "0",
    "reserved_fee": "25",
    "remaining_fee": "25",
    "paid_fee": "0",
    "locked": "50025",
    "prevented_volume": "0",
    "prevented_locked": "0",
    "trades_count": 0,
}

CANCEL_RESULT_DATA: dict[str, Any] = {
    "success": {
        "count": 1,
        "orders": [{"uuid": "uuid-1", "market": "KRW-BTC"}],
    },
    "failed": {
        "count": 0,
        "orders": [],
    },
}

CANCEL_AND_NEW_DATA: dict[str, Any] = {
    "market": "KRW-BTC",
    "uuid": "uuid-old",
    "side": "bid",
    "ord_type": "limit",
    "price": "50000000",
    "state": "wait",
    "created_at": "2024-01-01T00:00:00+09:00",
    "volume": "0.001",
    "remaining_volume": "0.001",
    "executed_volume": "0",
    "reserved_fee": "25",
    "remaining_fee": "25",
    "paid_fee": "0",
    "locked": "50025",
    "prevented_volume": "0",
    "prevented_locked": "0",
    "trades_count": 0,
    "new_order_uuid": "uuid-new",
}

ORDER_CHANCE_DATA: dict[str, Any] = {
    "bid_fee": "0.0005",
    "ask_fee": "0.0005",
    "maker_bid_fee": "0.0005",
    "maker_ask_fee": "0.0005",
    "market": {
        "id": "KRW-BTC",
        "name": "BTC/KRW",
        "order_types": ["limit"],
        "order_sides": ["ask", "bid"],
        "bid_types": ["limit", "price", "best"],
        "ask_types": ["limit", "market", "best"],
        "bid": {"currency": "KRW", "min_total": "5000"},
        "ask": {"currency": "BTC", "min_total": "5000"},
        "max_total": "1000000000",
        "state": "active",
    },
    "bid_account": {
        "currency": "KRW",
        "balance": "1000000.0",
        "locked": "0.0",
        "avg_buy_price": "0",
        "avg_buy_price_modified": False,
        "unit_currency": "KRW",
    },
    "ask_account": {
        "currency": "BTC",
        "balance": "0.5",
        "locked": "0.0",
        "avg_buy_price": "50000000",
        "avg_buy_price_modified": False,
        "unit_currency": "KRW",
    },
}


# ── TestCreateOrder ──────────────────────────────────────────────────────


class TestCreateOrder:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orders"
            assert request.method == "POST"
            return _json_response(ORDER_CREATED_DATA, status_code=201)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        api.create(market="KRW-BTC", side="bid", price="50000000", volume="0.001")

    def test_sends_json_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["market"] == "KRW-BTC"
            assert body["side"] == "bid"
            assert body["price"] == "50000000"
            assert body["ord_type"] == "limit"
            return _json_response(ORDER_CREATED_DATA, status_code=201)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        api.create(market="KRW-BTC", side="bid", price="50000000", volume="0.001")

    def test_authorization_header_present(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" in request.headers
            assert request.headers["Authorization"].startswith("Bearer ")
            return _json_response(ORDER_CREATED_DATA, status_code=201)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        api.create(market="KRW-BTC", side="bid", price="50000000", volume="0.001")

    def test_parses_response(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(ORDER_CREATED_DATA, status_code=201)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.create(
            market="KRW-BTC", side="bid", price="50000000", volume="0.001"
        )
        assert isinstance(result, OrderCreated)
        assert result.market == "KRW-BTC"
        assert result.uuid == "uuid-1234"
        assert result.state == "wait"


# ── TestCreateOrderTest ──────────────────────────────────────────────────


class TestCreateOrderTest:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orders/test"
            assert request.method == "POST"
            return _json_response(ORDER_CREATED_DATA, status_code=201)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        api.create_test(market="KRW-BTC", side="bid", price="50000000", volume="0.001")


# ── TestGetOrder ─────────────────────────────────────────────────────────


class TestGetOrder:
    def test_get_by_uuid(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/order"
            assert request.url.params["uuid"] == "uuid-1234"
            return _json_response(ORDER_DETAIL_DATA)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.get(uuid="uuid-1234")
        assert isinstance(result, OrderDetail)
        assert result.uuid == "uuid-1234"

    def test_get_by_identifier(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["identifier"] == "my-id"
            return _json_response(ORDER_DETAIL_DATA)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        api.get(identifier="my-id")

    def test_parses_trades(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(ORDER_DETAIL_DATA)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.get(uuid="uuid-1234")
        assert len(result.trades) == 1
        assert result.trades[0].trend == "up"
        assert result.trades[0].funds == "50000"


# ── TestCancelOrder ──────────────────────────────────────────────────────


class TestCancelOrder:
    def test_cancel_by_uuid(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/order"
            assert request.method == "DELETE"
            assert request.url.params["uuid"] == "uuid-cancel-1"
            return _json_response(ORDER_CANCELED_DATA)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.cancel(uuid="uuid-cancel-1")
        assert isinstance(result, OrderCanceled)
        assert result.uuid == "uuid-cancel-1"


# ── TestListOpenOrders ───────────────────────────────────────────────────


class TestListOpenOrders:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orders/open"
            assert request.method == "GET"
            return _json_response([ORDER_OPEN_DATA])

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.list_open()
        assert len(result) == 1
        assert isinstance(result[0], OrderOpen)

    def test_states_array_param(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            params = str(request.url)
            assert "states%5B%5D=wait" in params or "states[]=wait" in params
            assert "states%5B%5D=watch" in params or "states[]=watch" in params
            return _json_response([ORDER_OPEN_DATA])

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        api.list_open(states=["wait", "watch"])


# ── TestCancelOpenOrders ─────────────────────────────────────────────────


class TestCancelOpenOrders:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orders/open"
            assert request.method == "DELETE"
            return _json_response(CANCEL_RESULT_DATA)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.cancel_open()
        assert isinstance(result, CancelResult)
        assert result.success.count == 1
        assert result.failed.count == 0


# ── TestListClosedOrders ─────────────────────────────────────────────────


class TestListClosedOrders:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orders/closed"
            return _json_response([ORDER_CLOSED_DATA])

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.list_closed()
        assert len(result) == 1
        assert isinstance(result[0], OrderClosed)
        assert result[0].state == "done"

    def test_states_and_time_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            params = str(request.url)
            assert "states%5B%5D=done" in params or "states[]=done" in params
            assert "start_time=" in params
            return _json_response([ORDER_CLOSED_DATA])

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        api.list_closed(states=["done"], start_time="2024-01-01T00:00:00")


# ── TestListOrdersByIds ──────────────────────────────────────────────────


class TestListOrdersByIds:
    def test_uuids_array_param(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orders/uuids"
            params = str(request.url)
            assert "uuids%5B%5D=uuid-1" in params or "uuids[]=uuid-1" in params
            return _json_response([ORDER_BY_IDS_DATA])

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.list_by_ids(uuids=["uuid-1", "uuid-2"])
        assert len(result) == 1
        assert isinstance(result[0], OrderByIds)


# ── TestCancelOrdersByIds ────────────────────────────────────────────────


class TestCancelOrdersByIds:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orders/uuids"
            assert request.method == "DELETE"
            return _json_response(CANCEL_RESULT_DATA)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.cancel_by_ids(uuids=["uuid-1"])
        assert isinstance(result, CancelResult)


# ── TestCancelAndNewOrder ────────────────────────────────────────────────


class TestCancelAndNewOrder:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orders/cancel_and_new"
            assert request.method == "POST"
            body = json.loads(request.content)
            assert body["prev_order_uuid"] == "uuid-old"
            assert body["new_ord_type"] == "limit"
            return _json_response(CANCEL_AND_NEW_DATA, status_code=201)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.cancel_and_new(
            prev_order_uuid="uuid-old",
            new_ord_type="limit",
            new_price="51000000",
            new_volume="0.001",
        )
        assert isinstance(result, CancelAndNewOrderResponse)
        assert result.new_order_uuid == "uuid-new"


# ── TestGetOrderChance ───────────────────────────────────────────────────


class TestGetOrderChance:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orders/chance"
            assert request.url.params["market"] == "KRW-BTC"
            return _json_response(ORDER_CHANCE_DATA)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.get_chance(market="KRW-BTC")
        assert isinstance(result, OrderChance)
        assert result.bid_fee == "0.0005"

    def test_parses_nested_objects(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(ORDER_CHANCE_DATA)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        result = api.get_chance(market="KRW-BTC")
        assert result.market.id == "KRW-BTC"
        assert result.market.bid is not None
        assert result.market.bid.currency == "KRW"
        assert result.bid_account.currency == "KRW"
        assert result.ask_account.currency == "BTC"


# ── TestAsyncOrders ──────────────────────────────────────────────────────


class TestAsyncOrders:
    @pytest.mark.asyncio
    async def test_create(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orders"
            assert request.method == "POST"
            return _json_response(ORDER_CREATED_DATA, status_code=201)

        transport = _make_async_transport(handler)
        api = AsyncOrdersAPI(transport, CREDENTIALS)
        result = await api.create(
            market="KRW-BTC", side="bid", price="50000000", volume="0.001"
        )
        assert isinstance(result, OrderCreated)

    @pytest.mark.asyncio
    async def test_get(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(ORDER_DETAIL_DATA)

        transport = _make_async_transport(handler)
        api = AsyncOrdersAPI(transport, CREDENTIALS)
        result = await api.get(uuid="uuid-1234")
        assert isinstance(result, OrderDetail)
        assert len(result.trades) == 1

    @pytest.mark.asyncio
    async def test_list_open(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([ORDER_OPEN_DATA])

        transport = _make_async_transport(handler)
        api = AsyncOrdersAPI(transport, CREDENTIALS)
        result = await api.list_open()
        assert len(result) == 1
        assert isinstance(result[0], OrderOpen)

    @pytest.mark.asyncio
    async def test_get_chance(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(ORDER_CHANCE_DATA)

        transport = _make_async_transport(handler)
        api = AsyncOrdersAPI(transport, CREDENTIALS)
        result = await api.get_chance(market="KRW-BTC")
        assert isinstance(result, OrderChance)


# ── TestMinOrderValidation ──────────────────────────────────────────────


def _multi_handler(request: httpx.Request) -> httpx.Response:
    """Handle both /v1/orders/chance and /v1/orders endpoints."""
    if request.url.path == "/v1/orders/chance":
        return _json_response(ORDER_CHANCE_DATA)
    if request.url.path in ("/v1/orders", "/v1/orders/test"):
        return _json_response(ORDER_CREATED_DATA, status_code=201)
    return httpx.Response(404)


async def _async_multi_handler(request: httpx.Request) -> httpx.Response:
    return _multi_handler(request)


class TestMinOrderValidation:
    def test_validation_disabled_by_default(self) -> None:
        called_chance = False

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal called_chance
            if request.url.path == "/v1/orders/chance":
                called_chance = True
            return _multi_handler(request)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS)
        api.create(market="KRW-BTC", side="bid", ord_type="price", price="3000")
        assert not called_chance

    def test_validation_raises_for_low_bid_market_order(self) -> None:
        transport = _make_transport(_multi_handler)
        api = OrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        with pytest.raises(ValidationError) as exc_info:
            api.create(market="KRW-BTC", side="bid", ord_type="price", price="3000")
        assert exc_info.value.market == "KRW-BTC"
        assert exc_info.value.total == "3000"
        assert exc_info.value.min_total == "5000"

    def test_validation_raises_for_low_bid_limit_order(self) -> None:
        transport = _make_transport(_multi_handler)
        api = OrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        with pytest.raises(ValidationError):
            api.create(
                market="KRW-BTC", side="bid", ord_type="limit",
                price="1000", volume="3",
            )

    def test_validation_passes_for_sufficient_bid(self) -> None:
        transport = _make_transport(_multi_handler)
        api = OrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        result = api.create(
            market="KRW-BTC", side="bid", ord_type="price", price="6000"
        )
        assert isinstance(result, OrderCreated)

    def test_validation_skips_ask_orders(self) -> None:
        called_chance = False

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal called_chance
            if request.url.path == "/v1/orders/chance":
                called_chance = True
            return _multi_handler(request)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        api.create(
            market="KRW-BTC", side="ask", ord_type="market", volume="0.001"
        )
        assert not called_chance

    def test_validation_skips_when_price_none(self) -> None:
        called_chance = False

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal called_chance
            if request.url.path == "/v1/orders/chance":
                called_chance = True
            return _multi_handler(request)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        api.create(market="KRW-BTC", side="bid", ord_type="market", volume="0.001")
        assert not called_chance

    def test_validation_on_create_test(self) -> None:
        transport = _make_transport(_multi_handler)
        api = OrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        with pytest.raises(ValidationError):
            api.create_test(
                market="KRW-BTC", side="bid", ord_type="price", price="3000"
            )

    @pytest.mark.asyncio
    async def test_async_validation_raises(self) -> None:
        transport = _make_async_transport(_async_multi_handler)
        api = AsyncOrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        with pytest.raises(ValidationError) as exc_info:
            await api.create(
                market="KRW-BTC", side="bid", ord_type="price", price="3000"
            )
        assert exc_info.value.market == "KRW-BTC"
        assert exc_info.value.min_total == "5000"

    @pytest.mark.asyncio
    async def test_async_validation_passes(self) -> None:
        transport = _make_async_transport(_async_multi_handler)
        api = AsyncOrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        result = await api.create(
            market="KRW-BTC", side="bid", ord_type="price", price="6000"
        )
        assert isinstance(result, OrderCreated)


# ── TestMinOrderCache ──────────────────────────────────────────────────


class TestMinOrderCache:
    def test_cache_hit_skips_get_chance(self) -> None:
        chance_calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal chance_calls
            if request.url.path == "/v1/orders/chance":
                chance_calls += 1
            return _multi_handler(request)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        api.create(market="KRW-BTC", side="bid", ord_type="price", price="6000")
        api.create(market="KRW-BTC", side="bid", ord_type="price", price="6000")
        assert chance_calls == 1

    def test_cache_expires_after_ttl(self) -> None:
        chance_calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal chance_calls
            if request.url.path == "/v1/orders/chance":
                chance_calls += 1
            return _multi_handler(request)

        transport = _make_transport(handler)
        api = OrdersAPI(
            transport, CREDENTIALS, validate_min_order=True, min_total_ttl=0.0
        )
        api.create(market="KRW-BTC", side="bid", ord_type="price", price="6000")
        api.create(market="KRW-BTC", side="bid", ord_type="price", price="6000")
        assert chance_calls == 2

    def test_cache_is_per_market(self) -> None:
        chance_calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal chance_calls
            if request.url.path == "/v1/orders/chance":
                chance_calls += 1
            return _multi_handler(request)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        api.create(market="KRW-BTC", side="bid", ord_type="price", price="6000")
        api.create(market="KRW-ETH", side="bid", ord_type="price", price="6000")
        assert chance_calls == 2

    def test_cache_hit_still_validates(self) -> None:
        transport = _make_transport(_multi_handler)
        api = OrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        # First call populates the cache
        api.create(market="KRW-BTC", side="bid", ord_type="price", price="6000")
        # Second call should use cache but still raise for low total
        with pytest.raises(ValidationError) as exc_info:
            api.create(market="KRW-BTC", side="bid", ord_type="price", price="3000")
        assert exc_info.value.min_total == "5000"

    def test_cache_populated_on_validation_failure(self) -> None:
        chance_calls = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal chance_calls
            if request.url.path == "/v1/orders/chance":
                chance_calls += 1
            return _multi_handler(request)

        transport = _make_transport(handler)
        api = OrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        with pytest.raises(ValidationError):
            api.create(market="KRW-BTC", side="bid", ord_type="price", price="3000")
        with pytest.raises(ValidationError):
            api.create(market="KRW-BTC", side="bid", ord_type="price", price="3000")
        assert chance_calls == 1

    @pytest.mark.asyncio
    async def test_async_cache_hit_skips_get_chance(self) -> None:
        chance_calls = 0

        async def handler(request: httpx.Request) -> httpx.Response:
            nonlocal chance_calls
            if request.url.path == "/v1/orders/chance":
                chance_calls += 1
            return _multi_handler(request)

        transport = _make_async_transport(handler)
        api = AsyncOrdersAPI(transport, CREDENTIALS, validate_min_order=True)
        await api.create(market="KRW-BTC", side="bid", ord_type="price", price="6000")
        await api.create(market="KRW-BTC", side="bid", ord_type="price", price="6000")
        assert chance_calls == 1
