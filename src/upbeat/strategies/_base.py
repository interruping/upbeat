from __future__ import annotations

from typing import Protocol

from pydantic import BaseModel, ConfigDict

from upbeat.api.accounts import AccountsAPI, AsyncAccountsAPI
from upbeat.api.orders import AsyncOrdersAPI, OrdersAPI
from upbeat.api.quotation import AsyncQuotationAPI, QuotationAPI
from upbeat.types.order import OrderCreated


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


class PortfolioItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    balance: float
    locked: float
    current_price: float
    market: str
    estimated_value_krw: float


class RebalanceOrder(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    side: str
    ord_type: str
    amount: float
    order: OrderCreated


class RebalanceResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    orders: list[RebalanceOrder]
    total_value: float


class DCAResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    orders: list[OrderCreated]
    total_spent: float
    splits_completed: int
