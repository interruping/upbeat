from __future__ import annotations

from typing import Any

from upbeat._base import _AsyncAPIResource, _SyncAPIResource
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


class OrdersAPI(_SyncAPIResource):
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
