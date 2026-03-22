from __future__ import annotations

import os

from tests.conftest import upbeat_vcr
from upbeat import Upbeat
from upbeat.types.account import Account


def _client() -> Upbeat:
    return Upbeat(
        access_key=os.environ.get("UPBIT_ACCESS_KEY", "test-key"),
        secret_key=os.environ.get("UPBIT_SECRET_KEY", "test-secret"),
        max_retries=0,
        auto_throttle=False,
    )


# ── Accounts ───────────────────────────────────────────────────────────


class TestListAccounts:
    @upbeat_vcr.use_cassette("accounts/list.yaml")
    def test_returns_valid_accounts(self) -> None:
        with _client() as client:
            result = client.accounts.list()

        assert len(result) >= 1
        account = result[0]
        assert isinstance(account, Account)
        assert isinstance(account.currency, str)
        assert isinstance(account.balance, str)
        assert isinstance(account.locked, str)
        assert isinstance(account.unit_currency, str)
