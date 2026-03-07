from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Deposit(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: str
    uuid: str
    currency: str
    net_type: str | None = None
    txid: str | None = None
    state: str
    created_at: str
    done_at: str | None = None
    amount: str
    fee: str
    transaction_type: str


class DepositAddress(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    net_type: str | None = None
    deposit_address: str | None = None
    secondary_address: str | None = None


class DepositAddressCreated(BaseModel):
    model_config = ConfigDict(frozen=True)

    success: bool
    message: str


class DepositChanceCoin(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    net_type: str | None = None
    is_deposit_possible: bool
    deposit_impossible_reason: str | None = None
    minimum_deposit_amount: str | None = None
    minimum_deposit_confirmations: int | None = None
    decimal_precision: int | None = None
