from __future__ import annotations

from upbeat._base import _AsyncAPIResource, _SyncAPIResource
from upbeat.types.account import Account


class AccountsAPI(_SyncAPIResource):
    def list(self) -> list[Account]:
        response = self._transport.request(
            "GET", "/v1/accounts", credentials=self._credentials
        )
        return [Account.model_validate(item) for item in response.data]


class AsyncAccountsAPI(_AsyncAPIResource):
    async def list(self) -> list[Account]:
        response = await self._transport.request(
            "GET", "/v1/accounts", credentials=self._credentials
        )
        return [Account.model_validate(item) for item in response.data]
