from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from upbeat.types.order import OrderCreated


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
