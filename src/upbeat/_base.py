from __future__ import annotations

from upbeat._auth import Credentials
from upbeat._http import AsyncTransport, SyncTransport


class _SyncAPIResource:
    def __init__(
        self, transport: SyncTransport, credentials: Credentials | None
    ) -> None:
        self._transport = transport
        self._credentials = credentials


class _AsyncAPIResource:
    def __init__(
        self, transport: AsyncTransport, credentials: Credentials | None
    ) -> None:
        self._transport = transport
        self._credentials = credentials
