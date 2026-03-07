from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Account(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    balance: str
    locked: str
    avg_buy_price: str
    avg_buy_price_modified: bool
    unit_currency: str
