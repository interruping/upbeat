from __future__ import annotations

from upbeat.types.account import Account


def find_account(accounts: list[Account], currency: str) -> Account | None:
    currency_upper = currency.upper()
    for account in accounts:
        if account.currency == currency_upper:
            return account
    return None
