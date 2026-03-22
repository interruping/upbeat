from __future__ import annotations

import time
from decimal import Decimal
from typing import Any

from upbeat._auth import Credentials
from upbeat._base import _AsyncAPIResource, _SyncAPIResource
from upbeat._errors import ValidationError
from upbeat._http import AsyncTransport, SyncTransport
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


def _filter_params(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


def _compute_bid_total(
    price: str | None, volume: str | None, ord_type: str
) -> Decimal | None:
    """Return the total KRW value of a bid order, or None if indeterminate."""
    if price is None:
        return None
    if ord_type == "limit":
        return Decimal(price) * Decimal(volume) if volume is not None else None
    return Decimal(price)


_DEFAULT_MIN_TOTAL_TTL: float = 60.0


class OrdersAPI(_SyncAPIResource):
    _validate_min_order: bool

    def __init__(
        self,
        transport: SyncTransport,
        credentials: Credentials | None,
        *,
        validate_min_order: bool = False,
        min_total_ttl: float = _DEFAULT_MIN_TOTAL_TTL,
    ) -> None:
        super().__init__(transport, credentials)
        self._validate_min_order = validate_min_order
        self._min_total_ttl = min_total_ttl
        self._min_total_cache: dict[str, tuple[str, float]] = {}

    def _get_cached_min_total(self, market: str) -> str | None:
        entry = self._min_total_cache.get(market)
        if entry is not None:
            value, expiry = entry
            if time.monotonic() < expiry:
                return value
        return None

    def _check_min_order(
        self,
        market: str,
        side: str,
        price: str | None,
        volume: str | None,
        ord_type: str,
    ) -> None:
        if not self._validate_min_order or side != "bid":
            return
        total = _compute_bid_total(price, volume, ord_type)
        if total is None:
            return

        cached = self._get_cached_min_total(market)
        if cached is not None:
            min_total = Decimal(cached)
            if total < min_total:
                raise ValidationError(
                    f"Order total {total} is below minimum {min_total} for {market}",
                    market=market,
                    total=str(total),
                    min_total=cached,
                )
            return

        chance = self.get_chance(market=market)
        if chance.market.bid is not None:
            self._min_total_cache[market] = (
                chance.market.bid.min_total,
                time.monotonic() + self._min_total_ttl,
            )
            min_total = Decimal(chance.market.bid.min_total)
            if total < min_total:
                raise ValidationError(
                    f"Order total {total} is below minimum {min_total} for {market}",
                    market=market,
                    total=str(total),
                    min_total=chance.market.bid.min_total,
                )

    def create(
        self,
        *,
        market: str,
        side: str,
        volume: str | None = None,
        price: str | None = None,
        ord_type: str = "limit",
        identifier: str | None = None,
        time_in_force: str | None = None,
        smp_type: str | None = None,
    ) -> OrderCreated:
        self._check_min_order(market, side, price, volume, ord_type)
        json_body = _filter_params(
            market=market,
            side=side,
            volume=volume,
            price=price,
            ord_type=ord_type,
            identifier=identifier,
            time_in_force=time_in_force,
            smp_type=smp_type,
        )
        response = self._transport.request(
            "POST", "/v1/orders", json_body=json_body, credentials=self._credentials
        )
        return OrderCreated.model_validate(response.data)

    def create_test(
        self,
        *,
        market: str,
        side: str,
        volume: str | None = None,
        price: str | None = None,
        ord_type: str = "limit",
        identifier: str | None = None,
        time_in_force: str | None = None,
        smp_type: str | None = None,
    ) -> OrderCreated:
        self._check_min_order(market, side, price, volume, ord_type)
        json_body = _filter_params(
            market=market,
            side=side,
            volume=volume,
            price=price,
            ord_type=ord_type,
            identifier=identifier,
            time_in_force=time_in_force,
            smp_type=smp_type,
        )
        response = self._transport.request(
            "POST",
            "/v1/orders/test",
            json_body=json_body,
            credentials=self._credentials,
        )
        return OrderCreated.model_validate(response.data)

    def get(
        self,
        *,
        uuid: str | None = None,
        identifier: str | None = None,
    ) -> OrderDetail:
        params = _filter_params(uuid=uuid, identifier=identifier)
        response = self._transport.request(
            "GET", "/v1/order", params=params, credentials=self._credentials
        )
        return OrderDetail.model_validate(response.data)

    def cancel(
        self,
        *,
        uuid: str | None = None,
        identifier: str | None = None,
    ) -> OrderCanceled:
        params = _filter_params(uuid=uuid, identifier=identifier)
        response = self._transport.request(
            "DELETE", "/v1/order", params=params, credentials=self._credentials
        )
        return OrderCanceled.model_validate(response.data)

    def list_open(
        self,
        *,
        market: str | None = None,
        state: str | None = None,
        states: list[str] | None = None,
        page: int | None = None,
        limit: int | None = None,
        order_by: str | None = None,
    ) -> list[OrderOpen]:
        params: dict[str, Any] = _filter_params(
            market=market, state=state, page=page, limit=limit, order_by=order_by
        )
        if states is not None:
            params["states[]"] = states
        response = self._transport.request(
            "GET", "/v1/orders/open", params=params, credentials=self._credentials
        )
        return [OrderOpen.model_validate(item) for item in response.data]

    def cancel_open(
        self,
        *,
        quote_currencies: str | None = None,
        cancel_side: str | None = None,
        count: int | None = None,
        order_by: str | None = None,
        pairs: str | None = None,
        exclude_pairs: str | None = None,
    ) -> CancelResult:
        params = _filter_params(
            quote_currencies=quote_currencies,
            cancel_side=cancel_side,
            count=count,
            order_by=order_by,
            pairs=pairs,
            exclude_pairs=exclude_pairs,
        )
        response = self._transport.request(
            "DELETE", "/v1/orders/open", params=params, credentials=self._credentials
        )
        return CancelResult.model_validate(response.data)

    def list_closed(
        self,
        *,
        market: str | None = None,
        state: str | None = None,
        states: list[str] | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int | None = None,
        order_by: str | None = None,
    ) -> list[OrderClosed]:
        params: dict[str, Any] = _filter_params(
            market=market,
            state=state,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            order_by=order_by,
        )
        if states is not None:
            params["states[]"] = states
        response = self._transport.request(
            "GET", "/v1/orders/closed", params=params, credentials=self._credentials
        )
        return [OrderClosed.model_validate(item) for item in response.data]

    def list_by_ids(
        self,
        *,
        market: str | None = None,
        uuids: list[str] | None = None,
        identifiers: list[str] | None = None,
        order_by: str | None = None,
    ) -> list[OrderByIds]:
        params: dict[str, Any] = _filter_params(market=market, order_by=order_by)
        if uuids is not None:
            params["uuids[]"] = uuids
        if identifiers is not None:
            params["identifiers[]"] = identifiers
        response = self._transport.request(
            "GET", "/v1/orders/uuids", params=params, credentials=self._credentials
        )
        return [OrderByIds.model_validate(item) for item in response.data]

    def cancel_by_ids(
        self,
        *,
        uuids: list[str] | None = None,
        identifiers: list[str] | None = None,
    ) -> CancelResult:
        params: dict[str, Any] = {}
        if uuids is not None:
            params["uuids[]"] = uuids
        if identifiers is not None:
            params["identifiers[]"] = identifiers
        response = self._transport.request(
            "DELETE", "/v1/orders/uuids", params=params, credentials=self._credentials
        )
        return CancelResult.model_validate(response.data)

    def cancel_and_new(
        self,
        *,
        new_ord_type: str,
        prev_order_uuid: str | None = None,
        prev_order_identifier: str | None = None,
        new_volume: str | None = None,
        new_price: str | None = None,
        new_identifier: str | None = None,
        new_time_in_force: str | None = None,
        new_smp_type: str | None = None,
    ) -> CancelAndNewOrderResponse:
        json_body = _filter_params(
            new_ord_type=new_ord_type,
            prev_order_uuid=prev_order_uuid,
            prev_order_identifier=prev_order_identifier,
            new_volume=new_volume,
            new_price=new_price,
            new_identifier=new_identifier,
            new_time_in_force=new_time_in_force,
            new_smp_type=new_smp_type,
        )
        response = self._transport.request(
            "POST",
            "/v1/orders/cancel_and_new",
            json_body=json_body,
            credentials=self._credentials,
        )
        return CancelAndNewOrderResponse.model_validate(response.data)

    def get_chance(self, *, market: str) -> OrderChance:
        params = {"market": market}
        response = self._transport.request(
            "GET", "/v1/orders/chance", params=params, credentials=self._credentials
        )
        return OrderChance.model_validate(response.data)


class AsyncOrdersAPI(_AsyncAPIResource):
    _validate_min_order: bool

    def __init__(
        self,
        transport: AsyncTransport,
        credentials: Credentials | None,
        *,
        validate_min_order: bool = False,
        min_total_ttl: float = _DEFAULT_MIN_TOTAL_TTL,
    ) -> None:
        super().__init__(transport, credentials)
        self._validate_min_order = validate_min_order
        self._min_total_ttl = min_total_ttl
        self._min_total_cache: dict[str, tuple[str, float]] = {}

    def _get_cached_min_total(self, market: str) -> str | None:
        entry = self._min_total_cache.get(market)
        if entry is not None:
            value, expiry = entry
            if time.monotonic() < expiry:
                return value
        return None

    async def _check_min_order(
        self,
        market: str,
        side: str,
        price: str | None,
        volume: str | None,
        ord_type: str,
    ) -> None:
        if not self._validate_min_order or side != "bid":
            return
        total = _compute_bid_total(price, volume, ord_type)
        if total is None:
            return

        cached = self._get_cached_min_total(market)
        if cached is not None:
            min_total = Decimal(cached)
            if total < min_total:
                raise ValidationError(
                    f"Order total {total} is below minimum {min_total} for {market}",
                    market=market,
                    total=str(total),
                    min_total=cached,
                )
            return

        chance = await self.get_chance(market=market)
        if chance.market.bid is not None:
            self._min_total_cache[market] = (
                chance.market.bid.min_total,
                time.monotonic() + self._min_total_ttl,
            )
            min_total = Decimal(chance.market.bid.min_total)
            if total < min_total:
                raise ValidationError(
                    f"Order total {total} is below minimum {min_total} for {market}",
                    market=market,
                    total=str(total),
                    min_total=chance.market.bid.min_total,
                )

    async def create(
        self,
        *,
        market: str,
        side: str,
        volume: str | None = None,
        price: str | None = None,
        ord_type: str = "limit",
        identifier: str | None = None,
        time_in_force: str | None = None,
        smp_type: str | None = None,
    ) -> OrderCreated:
        await self._check_min_order(market, side, price, volume, ord_type)
        json_body = _filter_params(
            market=market,
            side=side,
            volume=volume,
            price=price,
            ord_type=ord_type,
            identifier=identifier,
            time_in_force=time_in_force,
            smp_type=smp_type,
        )
        response = await self._transport.request(
            "POST", "/v1/orders", json_body=json_body, credentials=self._credentials
        )
        return OrderCreated.model_validate(response.data)

    async def create_test(
        self,
        *,
        market: str,
        side: str,
        volume: str | None = None,
        price: str | None = None,
        ord_type: str = "limit",
        identifier: str | None = None,
        time_in_force: str | None = None,
        smp_type: str | None = None,
    ) -> OrderCreated:
        await self._check_min_order(market, side, price, volume, ord_type)
        json_body = _filter_params(
            market=market,
            side=side,
            volume=volume,
            price=price,
            ord_type=ord_type,
            identifier=identifier,
            time_in_force=time_in_force,
            smp_type=smp_type,
        )
        response = await self._transport.request(
            "POST",
            "/v1/orders/test",
            json_body=json_body,
            credentials=self._credentials,
        )
        return OrderCreated.model_validate(response.data)

    async def get(
        self,
        *,
        uuid: str | None = None,
        identifier: str | None = None,
    ) -> OrderDetail:
        params = _filter_params(uuid=uuid, identifier=identifier)
        response = await self._transport.request(
            "GET", "/v1/order", params=params, credentials=self._credentials
        )
        return OrderDetail.model_validate(response.data)

    async def cancel(
        self,
        *,
        uuid: str | None = None,
        identifier: str | None = None,
    ) -> OrderCanceled:
        params = _filter_params(uuid=uuid, identifier=identifier)
        response = await self._transport.request(
            "DELETE", "/v1/order", params=params, credentials=self._credentials
        )
        return OrderCanceled.model_validate(response.data)

    async def list_open(
        self,
        *,
        market: str | None = None,
        state: str | None = None,
        states: list[str] | None = None,
        page: int | None = None,
        limit: int | None = None,
        order_by: str | None = None,
    ) -> list[OrderOpen]:
        params: dict[str, Any] = _filter_params(
            market=market, state=state, page=page, limit=limit, order_by=order_by
        )
        if states is not None:
            params["states[]"] = states
        response = await self._transport.request(
            "GET", "/v1/orders/open", params=params, credentials=self._credentials
        )
        return [OrderOpen.model_validate(item) for item in response.data]

    async def cancel_open(
        self,
        *,
        quote_currencies: str | None = None,
        cancel_side: str | None = None,
        count: int | None = None,
        order_by: str | None = None,
        pairs: str | None = None,
        exclude_pairs: str | None = None,
    ) -> CancelResult:
        params = _filter_params(
            quote_currencies=quote_currencies,
            cancel_side=cancel_side,
            count=count,
            order_by=order_by,
            pairs=pairs,
            exclude_pairs=exclude_pairs,
        )
        response = await self._transport.request(
            "DELETE", "/v1/orders/open", params=params, credentials=self._credentials
        )
        return CancelResult.model_validate(response.data)

    async def list_closed(
        self,
        *,
        market: str | None = None,
        state: str | None = None,
        states: list[str] | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        limit: int | None = None,
        order_by: str | None = None,
    ) -> list[OrderClosed]:
        params: dict[str, Any] = _filter_params(
            market=market,
            state=state,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            order_by=order_by,
        )
        if states is not None:
            params["states[]"] = states
        response = await self._transport.request(
            "GET", "/v1/orders/closed", params=params, credentials=self._credentials
        )
        return [OrderClosed.model_validate(item) for item in response.data]

    async def list_by_ids(
        self,
        *,
        market: str | None = None,
        uuids: list[str] | None = None,
        identifiers: list[str] | None = None,
        order_by: str | None = None,
    ) -> list[OrderByIds]:
        params: dict[str, Any] = _filter_params(market=market, order_by=order_by)
        if uuids is not None:
            params["uuids[]"] = uuids
        if identifiers is not None:
            params["identifiers[]"] = identifiers
        response = await self._transport.request(
            "GET", "/v1/orders/uuids", params=params, credentials=self._credentials
        )
        return [OrderByIds.model_validate(item) for item in response.data]

    async def cancel_by_ids(
        self,
        *,
        uuids: list[str] | None = None,
        identifiers: list[str] | None = None,
    ) -> CancelResult:
        params: dict[str, Any] = {}
        if uuids is not None:
            params["uuids[]"] = uuids
        if identifiers is not None:
            params["identifiers[]"] = identifiers
        response = await self._transport.request(
            "DELETE", "/v1/orders/uuids", params=params, credentials=self._credentials
        )
        return CancelResult.model_validate(response.data)

    async def cancel_and_new(
        self,
        *,
        new_ord_type: str,
        prev_order_uuid: str | None = None,
        prev_order_identifier: str | None = None,
        new_volume: str | None = None,
        new_price: str | None = None,
        new_identifier: str | None = None,
        new_time_in_force: str | None = None,
        new_smp_type: str | None = None,
    ) -> CancelAndNewOrderResponse:
        json_body = _filter_params(
            new_ord_type=new_ord_type,
            prev_order_uuid=prev_order_uuid,
            prev_order_identifier=prev_order_identifier,
            new_volume=new_volume,
            new_price=new_price,
            new_identifier=new_identifier,
            new_time_in_force=new_time_in_force,
            new_smp_type=new_smp_type,
        )
        response = await self._transport.request(
            "POST",
            "/v1/orders/cancel_and_new",
            json_body=json_body,
            credentials=self._credentials,
        )
        return CancelAndNewOrderResponse.model_validate(response.data)

    async def get_chance(self, *, market: str) -> OrderChance:
        params = {"market": market}
        response = await self._transport.request(
            "GET", "/v1/orders/chance", params=params, credentials=self._credentials
        )
        return OrderChance.model_validate(response.data)
