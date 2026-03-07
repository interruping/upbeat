from __future__ import annotations

from typing import Any

from upbeat._base import _AsyncAPIResource, _SyncAPIResource
from upbeat.types.deposit import (
    Deposit,
    DepositAddress,
    DepositAddressCreated,
    DepositChanceCoin,
)


def _filter_params(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


class DepositsAPI(_SyncAPIResource):
    def get(
        self,
        *,
        uuid: str | None = None,
        txid: str | None = None,
        currency: str | None = None,
    ) -> Deposit:
        params = _filter_params(uuid=uuid, txid=txid, currency=currency)
        response = self._transport.request(
            "GET", "/v1/deposit", params=params, credentials=self._credentials
        )
        return Deposit.model_validate(response.data)

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
    ) -> list[Deposit]:
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
            "GET", "/v1/deposits", params=params, credentials=self._credentials
        )
        return [Deposit.model_validate(item) for item in response.data]

    def generate_coin_address(
        self,
        *,
        currency: str,
        net_type: str,
    ) -> DepositAddress | DepositAddressCreated:
        json_body = {"currency": currency, "net_type": net_type}
        response = self._transport.request(
            "POST",
            "/v1/deposits/generate_coin_address",
            json_body=json_body,
            credentials=self._credentials,
        )
        if response.status_code == 201:
            return DepositAddressCreated.model_validate(response.data)
        return DepositAddress.model_validate(response.data)

    def get_coin_address(
        self,
        *,
        currency: str,
        net_type: str,
    ) -> DepositAddress:
        params = {"currency": currency, "net_type": net_type}
        response = self._transport.request(
            "GET",
            "/v1/deposits/coin_address",
            params=params,
            credentials=self._credentials,
        )
        return DepositAddress.model_validate(response.data)

    def list_coin_addresses(self) -> list[DepositAddress]:
        response = self._transport.request(
            "GET",
            "/v1/deposits/coin_addresses",
            credentials=self._credentials,
        )
        return [DepositAddress.model_validate(item) for item in response.data]

    def create_krw(
        self,
        *,
        amount: str,
        two_factor_type: str,
    ) -> Deposit:
        json_body = {"amount": amount, "two_factor_type": two_factor_type}
        response = self._transport.request(
            "POST",
            "/v1/deposits/krw",
            json_body=json_body,
            credentials=self._credentials,
        )
        return Deposit.model_validate(response.data)

    def get_chance_coin(
        self,
        *,
        currency: str,
        net_type: str,
    ) -> DepositChanceCoin:
        params = {"currency": currency, "net_type": net_type}
        response = self._transport.request(
            "GET",
            "/v1/deposits/chance/coin",
            params=params,
            credentials=self._credentials,
        )
        return DepositChanceCoin.model_validate(response.data)


class AsyncDepositsAPI(_AsyncAPIResource):
    async def get(
        self,
        *,
        uuid: str | None = None,
        txid: str | None = None,
        currency: str | None = None,
    ) -> Deposit:
        params = _filter_params(uuid=uuid, txid=txid, currency=currency)
        response = await self._transport.request(
            "GET", "/v1/deposit", params=params, credentials=self._credentials
        )
        return Deposit.model_validate(response.data)

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
    ) -> list[Deposit]:
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
            "GET", "/v1/deposits", params=params, credentials=self._credentials
        )
        return [Deposit.model_validate(item) for item in response.data]

    async def generate_coin_address(
        self,
        *,
        currency: str,
        net_type: str,
    ) -> DepositAddress | DepositAddressCreated:
        json_body = {"currency": currency, "net_type": net_type}
        response = await self._transport.request(
            "POST",
            "/v1/deposits/generate_coin_address",
            json_body=json_body,
            credentials=self._credentials,
        )
        if response.status_code == 201:
            return DepositAddressCreated.model_validate(response.data)
        return DepositAddress.model_validate(response.data)

    async def get_coin_address(
        self,
        *,
        currency: str,
        net_type: str,
    ) -> DepositAddress:
        params = {"currency": currency, "net_type": net_type}
        response = await self._transport.request(
            "GET",
            "/v1/deposits/coin_address",
            params=params,
            credentials=self._credentials,
        )
        return DepositAddress.model_validate(response.data)

    async def list_coin_addresses(self) -> list[DepositAddress]:
        response = await self._transport.request(
            "GET",
            "/v1/deposits/coin_addresses",
            credentials=self._credentials,
        )
        return [DepositAddress.model_validate(item) for item in response.data]

    async def create_krw(
        self,
        *,
        amount: str,
        two_factor_type: str,
    ) -> Deposit:
        json_body = {"amount": amount, "two_factor_type": two_factor_type}
        response = await self._transport.request(
            "POST",
            "/v1/deposits/krw",
            json_body=json_body,
            credentials=self._credentials,
        )
        return Deposit.model_validate(response.data)

    async def get_chance_coin(
        self,
        *,
        currency: str,
        net_type: str,
    ) -> DepositChanceCoin:
        params = {"currency": currency, "net_type": net_type}
        response = await self._transport.request(
            "GET",
            "/v1/deposits/chance/coin",
            params=params,
            credentials=self._credentials,
        )
        return DepositChanceCoin.model_validate(response.data)
