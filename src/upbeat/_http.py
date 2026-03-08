import asyncio
import random
import time
from typing import Any

import httpx

from upbeat._auth import Credentials, build_auth_header, build_query_string
from upbeat._config import DEFAULT_MAX_RETRIES, DEFAULT_TIMEOUT, Timeout
from upbeat._constants import API_BASE_URL
from upbeat._errors import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    InternalServerError,
    RateLimitError,
    RemainingRequest,
)
from upbeat._logger import (
    DefaultLogger,
    ErrorInfo,
    Logger,
    RequestInfo,
    ResponseInfo,
    RetryInfo,
)
from upbeat.types.common import APIResponse

# ── Helper functions ─────────────────────────────────────────────────────


def _should_retry(error: Exception) -> bool:
    if isinstance(error, (RateLimitError, InternalServerError)):
        return True
    return isinstance(error, (APIConnectionError, APITimeoutError))


def _calculate_delay(attempt: int, base: float = 0.5, max_delay: float = 8.0) -> float:
    delay = min(base * (2**attempt), max_delay)
    jitter = delay * random.uniform(0, 0.25)  # noqa: S311
    return delay + jitter


def _calculate_rate_limit_delay(error: RateLimitError) -> float:
    if (
        error.remaining_request is not None
        and error.remaining_request.remaining_sec <= 0
    ):
        return 1.0
    return 1.0


# ── RateLimitTracker ─────────────────────────────────────────────────────


class RateLimitTracker:
    def __init__(self, *, auto_throttle: bool = True) -> None:
        self._state: dict[str, RemainingRequest] = {}
        self._auto_throttle = auto_throttle

    def update(self, remaining: RemainingRequest | None) -> None:
        if remaining is not None:
            self._state[remaining.group] = remaining

    def get_delay(self) -> float:
        if not self._auto_throttle:
            return 0.0
        for remaining in self._state.values():
            if remaining.remaining_sec <= 0:
                return 1.0
        return 0.0


# ── SyncTransport ────────────────────────────────────────────────────────


class SyncTransport:
    def __init__(
        self,
        *,
        base_url: str = API_BASE_URL,
        timeout: Timeout = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        auto_throttle: bool = True,
        logger: Logger | None = None,
        http_client: httpx.Client | None = None,
        event_hooks: dict[str, list[Any]] | None = None,
    ) -> None:
        self._base_url = base_url
        self._max_retries = max_retries
        self._logger: Logger = logger or DefaultLogger()
        self._rate_limiter = RateLimitTracker(auto_throttle=auto_throttle)

        if http_client is not None:
            self._client = http_client
            self._owns_client = False
        else:
            client_kwargs: dict[str, Any] = {
                "base_url": base_url,
                "timeout": httpx.Timeout(timeout.read, connect=timeout.connect),
            }
            if event_hooks is not None:
                client_kwargs["event_hooks"] = event_hooks
            self._client = httpx.Client(**client_kwargs)
            self._owns_client = True

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        credentials: Credentials | None = None,
    ) -> APIResponse:
        last_error: Exception | None = None

        for attempt in range(1 + self._max_retries):
            # Proactive throttle
            delay = self._rate_limiter.get_delay()
            if delay > 0:
                time.sleep(delay)

            # Build headers
            headers: dict[str, str] = {}
            if credentials is not None:
                if json_body is not None:
                    query_string = build_query_string(json_body)
                elif params is not None:
                    query_string = build_query_string(params)
                else:
                    query_string = ""
                headers["Authorization"] = build_auth_header(credentials, query_string)

            if json_body is not None:
                headers["Content-Type"] = "application/json; charset=utf-8"

            # Build URL
            url = path if path.startswith("http") else f"{self._base_url}{path}"

            self._logger.on_request(
                RequestInfo(method=method, url=url, headers=headers)
            )

            try:
                start = time.monotonic()
                response = self._client.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    headers=headers,
                )
                elapsed_ms = (time.monotonic() - start) * 1000

                self._logger.on_response(
                    ResponseInfo(
                        status_code=response.status_code,
                        url=str(response.url),
                        headers=dict(response.headers),
                        elapsed_ms=elapsed_ms,
                    )
                )

                # Parse Remaining-Req header
                remaining_request = _parse_remaining_req(response)
                self._rate_limiter.update(remaining_request)

                # Error responses
                if response.status_code >= 400:
                    error = APIStatusError.from_response(response)
                    if _should_retry(error) and attempt < self._max_retries:
                        if isinstance(error, RateLimitError):
                            retry_delay = _calculate_rate_limit_delay(error)
                        else:
                            retry_delay = _calculate_delay(attempt)
                        self._logger.on_retry(
                            RetryInfo(
                                attempt=attempt + 1,
                                max_retries=self._max_retries,
                                delay_seconds=retry_delay,
                                reason=str(error),
                                method=method,
                                url=url,
                            )
                        )
                        time.sleep(retry_delay)
                        last_error = error
                        continue
                    self._logger.on_error(
                        ErrorInfo(error=error, method=method, url=url)
                    )
                    raise error

                # Success
                return APIResponse(
                    data=response.json(),
                    remaining_request=remaining_request,
                    status_code=response.status_code,
                )

            except httpx.TimeoutException as exc:
                last_error = APITimeoutError(f"Request timed out: {exc}", cause=exc)
                if attempt < self._max_retries:
                    retry_delay = _calculate_delay(attempt)
                    self._logger.on_retry(
                        RetryInfo(
                            attempt=attempt + 1,
                            max_retries=self._max_retries,
                            delay_seconds=retry_delay,
                            reason=str(last_error),
                            method=method,
                            url=url,
                        )
                    )
                    time.sleep(retry_delay)
                    continue
                self._logger.on_error(
                    ErrorInfo(error=last_error, method=method, url=url)
                )
                raise last_error from exc

            except (
                httpx.ConnectError,
                httpx.NetworkError,
                httpx.RemoteProtocolError,
            ) as exc:
                last_error = APIConnectionError(f"Connection error: {exc}", cause=exc)
                if attempt < self._max_retries:
                    retry_delay = _calculate_delay(attempt)
                    self._logger.on_retry(
                        RetryInfo(
                            attempt=attempt + 1,
                            max_retries=self._max_retries,
                            delay_seconds=retry_delay,
                            reason=str(last_error),
                            method=method,
                            url=url,
                        )
                    )
                    time.sleep(retry_delay)
                    continue
                self._logger.on_error(
                    ErrorInfo(error=last_error, method=method, url=url)
                )
                raise last_error from exc

        # Should not reach here, but just in case
        assert last_error is not None
        raise last_error

    def close(self) -> None:
        if self._owns_client:
            self._client.close()


# ── AsyncTransport ───────────────────────────────────────────────────────


class AsyncTransport:
    def __init__(
        self,
        *,
        base_url: str = API_BASE_URL,
        timeout: Timeout = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        auto_throttle: bool = True,
        logger: Logger | None = None,
        http_client: httpx.AsyncClient | None = None,
        event_hooks: dict[str, list[Any]] | None = None,
    ) -> None:
        self._base_url = base_url
        self._max_retries = max_retries
        self._logger: Logger = logger or DefaultLogger()
        self._rate_limiter = RateLimitTracker(auto_throttle=auto_throttle)

        if http_client is not None:
            self._client = http_client
            self._owns_client = False
        else:
            client_kwargs: dict[str, Any] = {
                "base_url": base_url,
                "timeout": httpx.Timeout(timeout.read, connect=timeout.connect),
            }
            if event_hooks is not None:
                client_kwargs["event_hooks"] = event_hooks
            self._client = httpx.AsyncClient(**client_kwargs)
            self._owns_client = True

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        credentials: Credentials | None = None,
    ) -> APIResponse:
        last_error: Exception | None = None

        for attempt in range(1 + self._max_retries):
            delay = self._rate_limiter.get_delay()
            if delay > 0:
                await asyncio.sleep(delay)

            headers: dict[str, str] = {}
            if credentials is not None:
                if json_body is not None:
                    query_string = build_query_string(json_body)
                elif params is not None:
                    query_string = build_query_string(params)
                else:
                    query_string = ""
                headers["Authorization"] = build_auth_header(credentials, query_string)

            if json_body is not None:
                headers["Content-Type"] = "application/json; charset=utf-8"

            url = path if path.startswith("http") else f"{self._base_url}{path}"

            self._logger.on_request(
                RequestInfo(method=method, url=url, headers=headers)
            )

            try:
                start = time.monotonic()
                response = await self._client.request(
                    method,
                    url,
                    params=params,
                    json=json_body,
                    headers=headers,
                )
                elapsed_ms = (time.monotonic() - start) * 1000

                self._logger.on_response(
                    ResponseInfo(
                        status_code=response.status_code,
                        url=str(response.url),
                        headers=dict(response.headers),
                        elapsed_ms=elapsed_ms,
                    )
                )

                remaining_request = _parse_remaining_req(response)
                self._rate_limiter.update(remaining_request)

                if response.status_code >= 400:
                    error = APIStatusError.from_response(response)
                    if _should_retry(error) and attempt < self._max_retries:
                        if isinstance(error, RateLimitError):
                            retry_delay = _calculate_rate_limit_delay(error)
                        else:
                            retry_delay = _calculate_delay(attempt)
                        self._logger.on_retry(
                            RetryInfo(
                                attempt=attempt + 1,
                                max_retries=self._max_retries,
                                delay_seconds=retry_delay,
                                reason=str(error),
                                method=method,
                                url=url,
                            )
                        )
                        await asyncio.sleep(retry_delay)
                        last_error = error
                        continue
                    self._logger.on_error(
                        ErrorInfo(error=error, method=method, url=url)
                    )
                    raise error

                return APIResponse(
                    data=response.json(),
                    remaining_request=remaining_request,
                    status_code=response.status_code,
                )

            except httpx.TimeoutException as exc:
                last_error = APITimeoutError(f"Request timed out: {exc}", cause=exc)
                if attempt < self._max_retries:
                    retry_delay = _calculate_delay(attempt)
                    self._logger.on_retry(
                        RetryInfo(
                            attempt=attempt + 1,
                            max_retries=self._max_retries,
                            delay_seconds=retry_delay,
                            reason=str(last_error),
                            method=method,
                            url=url,
                        )
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                self._logger.on_error(
                    ErrorInfo(error=last_error, method=method, url=url)
                )
                raise last_error from exc

            except (
                httpx.ConnectError,
                httpx.NetworkError,
                httpx.RemoteProtocolError,
            ) as exc:
                last_error = APIConnectionError(f"Connection error: {exc}", cause=exc)
                if attempt < self._max_retries:
                    retry_delay = _calculate_delay(attempt)
                    self._logger.on_retry(
                        RetryInfo(
                            attempt=attempt + 1,
                            max_retries=self._max_retries,
                            delay_seconds=retry_delay,
                            reason=str(last_error),
                            method=method,
                            url=url,
                        )
                    )
                    await asyncio.sleep(retry_delay)
                    continue
                self._logger.on_error(
                    ErrorInfo(error=last_error, method=method, url=url)
                )
                raise last_error from exc

        assert last_error is not None
        raise last_error

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()


# ── Shared helpers ───────────────────────────────────────────────────────


def _parse_remaining_req(response: httpx.Response) -> RemainingRequest | None:
    header = response.headers.get("Remaining-Req")
    if header:
        return RemainingRequest.from_header(header)
    return None
