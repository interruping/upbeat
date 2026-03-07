from __future__ import annotations

from typing import Any

from upbeat._base import _AsyncAPIResource, _SyncAPIResource
from upbeat.types.withdrawal import (
    Withdrawal,
    WithdrawalAddress,
    WithdrawalChance,
    WithdrawalKrw,
)


def _filter_params(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


class WithdrawalsAPI(_SyncAPIResource):
    def get(
        self,
        *,
        uuid: str | None = None,
        txid: str | None = None,
        currency: str | None = None,
    ) -> Withdrawal:
        params = _filter_params(uuid=uuid, txid=txid, currency=currency)
        response = self._transport.request(
            "GET", "/v1/withdraw", params=params, credentials=self._credentials
        )
        return Withdrawal.model_validate(response.data)

    def list(
        self,
        *,
        currency: str | None = None,
        state: str | None = None,
        uuids: list[str] | None = None,
        txids: list[str] | None = None,
        limit: int | None = None,
        page: int | None = None,
        order_by: str | None = None,
        from_cursor: str | None = None,
        to: str | None = None,
    ) -> list[Withdrawal]:
        params: dict[str, Any] = _filter_params(
            currency=currency,
            state=state,
            limit=limit,
            page=page,
            order_by=order_by,
            to=to,
        )
        if from_cursor is not None:
            params["from"] = from_cursor
        if uuids is not None:
            params["uuids[]"] = uuids
        if txids is not None:
            params["txids[]"] = txids
        response = self._transport.request(
            "GET", "/v1/withdraws", params=params, credentials=self._credentials
        )
        return [Withdrawal.model_validate(item) for item in response.data]

    def create_coin(
        self,
        *,
        currency: str,
        net_type: str,
        amount: str,
        address: str,
        secondary_address: str | None = None,
        transaction_type: str | None = None,
    ) -> Withdrawal:
        json_body = _filter_params(
            currency=currency,
            net_type=net_type,
            amount=amount,
            address=address,
            secondary_address=secondary_address,
            transaction_type=transaction_type,
        )
        response = self._transport.request(
            "POST",
            "/v1/withdraws/coin",
            json_body=json_body,
            credentials=self._credentials,
        )
        return Withdrawal.model_validate(response.data)

    def cancel_coin(self, *, uuid: str) -> Withdrawal:
        params = {"uuid": uuid}
        response = self._transport.request(
            "DELETE",
            "/v1/withdraws/coin",
            params=params,
            credentials=self._credentials,
        )
        return Withdrawal.model_validate(response.data)

    def create_krw(
        self,
        *,
        amount: str,
        two_factor_type: str,
    ) -> WithdrawalKrw:
        json_body = {"amount": amount, "two_factor_type": two_factor_type}
        response = self._transport.request(
            "POST",
            "/v1/withdraws/krw",
            json_body=json_body,
            credentials=self._credentials,
        )
        return WithdrawalKrw.model_validate(response.data)

    def list_coin_addresses(self) -> list[WithdrawalAddress]:
        response = self._transport.request(
            "GET",
            "/v1/withdraws/coin_addresses",
            credentials=self._credentials,
        )
        return [WithdrawalAddress.model_validate(item) for item in response.data]

    def get_chance(
        self,
        *,
        currency: str,
        net_type: str | None = None,
    ) -> WithdrawalChance:
        params = _filter_params(currency=currency, net_type=net_type)
        response = self._transport.request(
            "GET",
            "/v1/withdraws/chance",
            params=params,
            credentials=self._credentials,
        )
        return WithdrawalChance.model_validate(response.data)


class AsyncWithdrawalsAPI(_AsyncAPIResource):
    async def get(
        self,
        *,
        uuid: str | None = None,
        txid: str | None = None,
        currency: str | None = None,
    ) -> Withdrawal:
        params = _filter_params(uuid=uuid, txid=txid, currency=currency)
        response = await self._transport.request(
            "GET", "/v1/withdraw", params=params, credentials=self._credentials
        )
        return Withdrawal.model_validate(response.data)

    async def list(
        self,
        *,
        currency: str | None = None,
        state: str | None = None,
        uuids: list[str] | None = None,
        txids: list[str] | None = None,
        limit: int | None = None,
        page: int | None = None,
        order_by: str | None = None,
        from_cursor: str | None = None,
        to: str | None = None,
    ) -> list[Withdrawal]:
        params: dict[str, Any] = _filter_params(
            currency=currency,
            state=state,
            limit=limit,
            page=page,
            order_by=order_by,
            to=to,
        )
        if from_cursor is not None:
            params["from"] = from_cursor
        if uuids is not None:
            params["uuids[]"] = uuids
        if txids is not None:
            params["txids[]"] = txids
        response = await self._transport.request(
            "GET", "/v1/withdraws", params=params, credentials=self._credentials
        )
        return [Withdrawal.model_validate(item) for item in response.data]

    async def create_coin(
        self,
        *,
        currency: str,
        net_type: str,
        amount: str,
        address: str,
        secondary_address: str | None = None,
        transaction_type: str | None = None,
    ) -> Withdrawal:
        json_body = _filter_params(
            currency=currency,
            net_type=net_type,
            amount=amount,
            address=address,
            secondary_address=secondary_address,
            transaction_type=transaction_type,
        )
        response = await self._transport.request(
            "POST",
            "/v1/withdraws/coin",
            json_body=json_body,
            credentials=self._credentials,
        )
        return Withdrawal.model_validate(response.data)

    async def cancel_coin(self, *, uuid: str) -> Withdrawal:
        params = {"uuid": uuid}
        response = await self._transport.request(
            "DELETE",
            "/v1/withdraws/coin",
            params=params,
            credentials=self._credentials,
        )
        return Withdrawal.model_validate(response.data)

    async def create_krw(
        self,
        *,
        amount: str,
        two_factor_type: str,
    ) -> WithdrawalKrw:
        json_body = {"amount": amount, "two_factor_type": two_factor_type}
        response = await self._transport.request(
            "POST",
            "/v1/withdraws/krw",
            json_body=json_body,
            credentials=self._credentials,
        )
        return WithdrawalKrw.model_validate(response.data)

    async def list_coin_addresses(self) -> list[WithdrawalAddress]:
        response = await self._transport.request(
            "GET",
            "/v1/withdraws/coin_addresses",
            credentials=self._credentials,
        )
        return [WithdrawalAddress.model_validate(item) for item in response.data]

    async def get_chance(
        self,
        *,
        currency: str,
        net_type: str | None = None,
    ) -> WithdrawalChance:
        params = _filter_params(currency=currency, net_type=net_type)
        response = await self._transport.request(
            "GET",
            "/v1/withdraws/chance",
            params=params,
            credentials=self._credentials,
        )
        return WithdrawalChance.model_validate(response.data)
