from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class Withdrawal(BaseModel):
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
    is_cancelable: bool | None = None


class WithdrawalKrw(BaseModel):
    model_config = ConfigDict(frozen=True)

    type: str
    uuid: str
    currency: str
    txid: str | None = None
    state: str
    created_at: str
    done_at: str | None = None
    amount: str
    fee: str
    transaction_type: str
    is_cancelable: bool | None = None


class WithdrawalAddress(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    net_type: str
    network_name: str
    withdraw_address: str
    secondary_address: str | None = None
    beneficiary_name: str | None = None
    beneficiary_company_name: str | None = None
    beneficiary_type: str | None = None
    exchange_name: str | None = None
    wallet_type: str | None = None


class WithdrawalChanceMemberLevel(BaseModel):
    model_config = ConfigDict(frozen=True)

    security_level: int
    fee_level: int
    email_verified: bool
    identity_auth_verified: bool
    bank_account_verified: bool
    two_factor_auth_verified: bool
    locked: bool
    wallet_locked: bool


class WithdrawalChanceCurrency(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    withdraw_fee: str
    is_coin: bool
    wallet_state: str
    wallet_support: list[str]


class WithdrawalChanceAccount(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    balance: str
    locked: str
    avg_buy_price: str
    avg_buy_price_modified: bool
    unit_currency: str


class WithdrawalChanceWithdrawLimit(BaseModel):
    model_config = ConfigDict(frozen=True)

    currency: str
    onetime: str | None = None
    daily: str | None = None
    remaining_daily: str | None = None
    remaining_daily_fiat: str | None = None
    fiat_currency: str | None = None
    minimum: str | None = None
    fixed: int | None = None
    withdraw_delayed_fiat: str | None = None
    can_withdraw: bool | None = None
    remaining_daily_krw: str | None = None


class WithdrawalChance(BaseModel):
    model_config = ConfigDict(frozen=True)

    member_level: WithdrawalChanceMemberLevel
    currency: WithdrawalChanceCurrency
    account: WithdrawalChanceAccount
    withdraw_limit: WithdrawalChanceWithdrawLimit
