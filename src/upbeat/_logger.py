from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class RequestInfo:
    method: str
    url: str
    headers: dict[str, str]


@dataclass(frozen=True, slots=True)
class ResponseInfo:
    status_code: int
    url: str
    headers: dict[str, str]
    elapsed_ms: float


@dataclass(frozen=True, slots=True)
class RetryInfo:
    attempt: int
    max_retries: int
    delay_seconds: float
    reason: str
    method: str
    url: str


@dataclass(frozen=True, slots=True)
class ErrorInfo:
    error: Exception
    method: str
    url: str


@dataclass(frozen=True, slots=True)
class WebSocketEventInfo:
    event: str
    url: str
    message: str | None = None
    error: Exception | None = None


@runtime_checkable
class Logger(Protocol):
    def on_request(self, info: RequestInfo) -> None: ...
    def on_response(self, info: ResponseInfo) -> None: ...
    def on_retry(self, info: RetryInfo) -> None: ...
    def on_error(self, info: ErrorInfo) -> None: ...
    def on_ws_event(self, info: WebSocketEventInfo) -> None: ...


class DefaultLogger:
    def __init__(self) -> None:
        self._logger = logging.getLogger("upbeat")
        self._logger.addHandler(logging.NullHandler())

    def on_request(self, info: RequestInfo) -> None:
        self._logger.debug("Request: %s %s", info.method, info.url)

    def on_response(self, info: ResponseInfo) -> None:
        self._logger.debug(
            "Response: %s %s (%.1fms)", info.status_code, info.url, info.elapsed_ms
        )

    def on_retry(self, info: RetryInfo) -> None:
        self._logger.warning(
            "Retry %s/%s for %s %s in %.1fs: %s",
            info.attempt,
            info.max_retries,
            info.method,
            info.url,
            info.delay_seconds,
            info.reason,
        )

    def on_error(self, info: ErrorInfo) -> None:
        self._logger.error("Error on %s %s: %s", info.method, info.url, info.error)

    def on_ws_event(self, info: WebSocketEventInfo) -> None:
        if info.error is not None:
            self._logger.warning(
                "WebSocket %s %s: %s", info.event, info.url, info.error
            )
        else:
            self._logger.debug("WebSocket %s %s", info.event, info.url)


class NullLogger:
    def on_request(self, info: RequestInfo) -> None:
        pass

    def on_response(self, info: ResponseInfo) -> None:
        pass

    def on_retry(self, info: RetryInfo) -> None:
        pass

    def on_error(self, info: ErrorInfo) -> None:
        pass

    def on_ws_event(self, info: WebSocketEventInfo) -> None:
        pass
