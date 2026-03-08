from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from upbeat.shortcuts import AsyncShortcuts, SyncShortcuts, find_account
from upbeat.types.account import Account


def _make_account(currency: str, balance: str = "0.0") -> Account:
    return Account(
        currency=currency,
        balance=balance,
        locked="0.0",
        avg_buy_price="0",
        avg_buy_price_modified=False,
        unit_currency="KRW",
    )


class TestFindAccount:
    def test_found(self) -> None:
        accounts = [_make_account("KRW"), _make_account("BTC", "0.01")]
        result = find_account(accounts, "BTC")
        assert result is not None
        assert result.currency == "BTC"

    def test_not_found(self) -> None:
        accounts = [_make_account("KRW"), _make_account("BTC")]
        result = find_account(accounts, "ETH")
        assert result is None

    def test_case_insensitive(self) -> None:
        accounts = [_make_account("BTC", "0.01")]
        assert find_account(accounts, "btc") is not None
        assert find_account(accounts, "Btc") is not None

    def test_empty_list(self) -> None:
        assert find_account([], "BTC") is None


class TestSyncShortcutsGetAccount:
    def test_returns_account(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [
            _make_account("KRW"),
            _make_account("BTC", "0.01"),
        ]
        shortcuts = SyncShortcuts(client)

        result = shortcuts.get_account("BTC")
        assert result is not None
        assert result.currency == "BTC"
        client.accounts.list.assert_called_once()

    def test_returns_none_when_not_found(self) -> None:
        client = MagicMock()
        client.accounts.list.return_value = [_make_account("KRW")]
        shortcuts = SyncShortcuts(client)

        result = shortcuts.get_account("ETH")
        assert result is None


class TestAsyncShortcutsGetAccount:
    @pytest.mark.asyncio
    async def test_returns_account(self) -> None:
        client = MagicMock()
        client.accounts.list = AsyncMock(
            return_value=[_make_account("KRW"), _make_account("BTC", "0.01")]
        )
        shortcuts = AsyncShortcuts(client)

        result = await shortcuts.get_account("BTC")
        assert result is not None
        assert result.currency == "BTC"
        client.accounts.list.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_returns_none_when_not_found(self) -> None:
        client = MagicMock()
        client.accounts.list = AsyncMock(return_value=[_make_account("KRW")])
        shortcuts = AsyncShortcuts(client)

        result = await shortcuts.get_account("ETH")
        assert result is None
