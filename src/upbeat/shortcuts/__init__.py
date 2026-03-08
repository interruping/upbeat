from __future__ import annotations

from typing import TYPE_CHECKING

from upbeat.shortcuts._accounts import find_account

if TYPE_CHECKING:
    from upbeat._client import AsyncUpbeat, Upbeat
    from upbeat.types.account import Account


class SyncShortcuts:
    def __init__(self, client: Upbeat) -> None:
        self._client = client

    def get_account(self, currency: str) -> Account | None:
        return find_account(self._client.accounts.list(), currency)


class AsyncShortcuts:
    def __init__(self, client: AsyncUpbeat) -> None:
        self._client = client

    async def get_account(self, currency: str) -> Account | None:
        accounts = await self._client.accounts.list()
        return find_account(accounts, currency)


__all__ = [
    "AsyncShortcuts",
    "SyncShortcuts",
    "find_account",
]
