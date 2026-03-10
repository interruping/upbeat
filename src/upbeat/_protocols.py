from __future__ import annotations

from typing import Protocol

from upbeat.api.accounts import AccountsAPI, AsyncAccountsAPI
from upbeat.api.orders import AsyncOrdersAPI, OrdersAPI
from upbeat.api.quotation import AsyncQuotationAPI, QuotationAPI


class SyncClientProtocol(Protocol):
    @property
    def accounts(self) -> AccountsAPI: ...

    @property
    def orders(self) -> OrdersAPI: ...

    @property
    def quotation(self) -> QuotationAPI: ...


class AsyncClientProtocol(Protocol):
    @property
    def accounts(self) -> AsyncAccountsAPI: ...

    @property
    def orders(self) -> AsyncOrdersAPI: ...

    @property
    def quotation(self) -> AsyncQuotationAPI: ...
