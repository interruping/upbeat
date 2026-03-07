from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import patch

import httpx
import pytest

from upbeat._config import DEFAULT_MAX_RETRIES
from upbeat._constants import API_BASE_URL
from upbeat._errors import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    RemainingRequest,
    UnprocessableEntityError,
)
from upbeat._http import (
    AsyncTransport,
    RateLimitTracker,
    SyncTransport,
    _calculate_delay,
    _should_retry,
)
from upbeat._logger import ErrorInfo, Logger, RequestInfo, ResponseInfo, RetryInfo, WebSocketEventInfo
from upbeat.types.common import APIResponse
from upbeat._auth import Credentials


# ── Helpers ──────────────────────────────────────────────────────────────


def _make_transport(handler: Any, **kwargs: Any) -> SyncTransport:
    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url=API_BASE_URL
    )
    return SyncTransport(http_client=client, **kwargs)


def _make_async_transport(handler: Any, **kwargs: Any) -> AsyncTransport:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url=API_BASE_URL
    )
    return AsyncTransport(http_client=client, **kwargs)


def _json_response(
    data: Any,
    status_code: int = 200,
    remaining_req: str | None = None,
) -> httpx.Response:
    headers = {}
    if remaining_req:
        headers["Remaining-Req"] = remaining_req
    return httpx.Response(
        status_code,
        json=data,
        headers=headers,
    )


def _error_response(
    status_code: int,
    error_name: str = "some_error",
    error_message: str = "something went wrong",
    remaining_req: str | None = None,
) -> httpx.Response:
    headers = {}
    if remaining_req:
        headers["Remaining-Req"] = remaining_req
    body = {"error": {"name": error_name, "message": error_message}}
    return httpx.Response(status_code, json=body, headers=headers)


class RecordingLogger:
    """Logger that records all calls for testing."""

    def __init__(self) -> None:
        self.requests: list[RequestInfo] = []
        self.responses: list[ResponseInfo] = []
        self.retries: list[RetryInfo] = []
        self.errors: list[ErrorInfo] = []
        self.ws_events: list[WebSocketEventInfo] = []

    def on_request(self, info: RequestInfo) -> None:
        self.requests.append(info)

    def on_response(self, info: ResponseInfo) -> None:
        self.responses.append(info)

    def on_retry(self, info: RetryInfo) -> None:
        self.retries.append(info)

    def on_error(self, info: ErrorInfo) -> None:
        self.errors.append(info)

    def on_ws_event(self, info: WebSocketEventInfo) -> None:
        self.ws_events.append(info)


# ── TestShouldRetry ──────────────────────────────────────────────────────


class TestShouldRetry:
    def test_rate_limit_error_is_retryable(self) -> None:
        resp = _error_response(429)
        error = RateLimitError(
            message="rate limited",
            status_code=429,
            error_name=None,
            error_message=None,
            response=resp,
            remaining_request=None,
        )
        assert _should_retry(error) is True

    def test_internal_server_error_is_retryable(self) -> None:
        resp = _error_response(500)
        error = InternalServerError(
            message="server error",
            status_code=500,
            error_name=None,
            error_message=None,
            response=resp,
            remaining_request=None,
        )
        assert _should_retry(error) is True

    def test_connection_error_is_retryable(self) -> None:
        error = APIConnectionError("connection failed")
        assert _should_retry(error) is True

    def test_timeout_error_is_retryable(self) -> None:
        error = APITimeoutError("timed out")
        assert _should_retry(error) is True

    def test_bad_request_not_retryable(self) -> None:
        resp = _error_response(400)
        error = BadRequestError(
            message="bad request",
            status_code=400,
            error_name=None,
            error_message=None,
            response=resp,
            remaining_request=None,
        )
        assert _should_retry(error) is False

    def test_auth_error_not_retryable(self) -> None:
        resp = _error_response(401)
        error = AuthenticationError(
            message="unauthorized",
            status_code=401,
            error_name=None,
            error_message=None,
            response=resp,
            remaining_request=None,
        )
        assert _should_retry(error) is False

    def test_not_found_not_retryable(self) -> None:
        resp = _error_response(404)
        error = NotFoundError(
            message="not found",
            status_code=404,
            error_name=None,
            error_message=None,
            response=resp,
            remaining_request=None,
        )
        assert _should_retry(error) is False


# ── TestCalculateDelay ───────────────────────────────────────────────────


class TestCalculateDelay:
    def test_delay_increases_with_attempt(self) -> None:
        d0 = _calculate_delay(0, base=0.5, max_delay=8.0)
        d1 = _calculate_delay(1, base=0.5, max_delay=8.0)
        # base delay doubles each attempt (before jitter)
        assert d0 >= 0.5
        assert d1 >= 1.0

    def test_delay_capped_at_max(self) -> None:
        d = _calculate_delay(100, base=0.5, max_delay=8.0)
        # max_delay + 25% jitter = 10.0
        assert d <= 10.0

    def test_delay_includes_jitter(self) -> None:
        # Run multiple times - at least one should differ
        delays = {_calculate_delay(0) for _ in range(20)}
        assert len(delays) > 1


# ── TestRateLimitTracker ─────────────────────────────────────────────────


class TestRateLimitTracker:
    def test_sec_remaining_returns_zero_delay(self) -> None:
        tracker = RateLimitTracker(auto_throttle=True)
        tracker.update(RemainingRequest(group="default", remaining_min=1800, remaining_sec=29))
        assert tracker.get_delay() == 0.0

    def test_sec_zero_returns_one_second(self) -> None:
        tracker = RateLimitTracker(auto_throttle=True)
        tracker.update(RemainingRequest(group="default", remaining_min=1800, remaining_sec=0))
        assert tracker.get_delay() == 1.0

    def test_auto_throttle_false_always_zero(self) -> None:
        tracker = RateLimitTracker(auto_throttle=False)
        tracker.update(RemainingRequest(group="default", remaining_min=1800, remaining_sec=0))
        assert tracker.get_delay() == 0.0

    def test_independent_group_tracking(self) -> None:
        tracker = RateLimitTracker(auto_throttle=True)
        tracker.update(RemainingRequest(group="order", remaining_min=1800, remaining_sec=5))
        tracker.update(RemainingRequest(group="default", remaining_min=1800, remaining_sec=0))
        # default group has sec=0, so delay should be 1.0
        assert tracker.get_delay() == 1.0


# ── TestSyncTransportSuccess ─────────────────────────────────────────────


class TestSyncTransportSuccess:
    def test_get_json_200(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([{"currency": "BTC"}])

        transport = _make_transport(handler)
        result = transport.request("GET", "/v1/accounts")
        assert result.data == [{"currency": "BTC"}]
        assert result.status_code == 200

    def test_post_201_with_body(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            assert body["market"] == "KRW-BTC"
            return _json_response({"uuid": "abc123"}, status_code=201)

        transport = _make_transport(handler)
        result = transport.request(
            "POST", "/v1/orders", json_body={"market": "KRW-BTC", "side": "bid"}
        )
        assert result.data["uuid"] == "abc123"
        assert result.status_code == 201

    def test_remaining_req_header_parsed(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response(
                {"ok": True},
                remaining_req="group=default; min=1800; sec=29",
            )

        transport = _make_transport(handler)
        result = transport.request("GET", "/v1/accounts")
        assert result.remaining_request is not None
        assert result.remaining_request.group == "default"
        assert result.remaining_request.remaining_sec == 29

    def test_credentials_add_authorization_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" in request.headers
            assert request.headers["Authorization"].startswith("Bearer ")
            return _json_response({"ok": True})

        creds = Credentials(access_key="test-key", secret_key="test-secret")
        transport = _make_transport(handler)
        result = transport.request("GET", "/v1/accounts", credentials=creds)
        assert result.status_code == 200

    def test_no_credentials_no_authorization_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" not in request.headers
            return _json_response({"ok": True})

        transport = _make_transport(handler)
        result = transport.request("GET", "/v1/ticker")
        assert result.status_code == 200


# ── TestSyncTransportErrors ──────────────────────────────────────────────


class TestSyncTransportErrors:
    @pytest.mark.parametrize(
        "status_code,error_type",
        [
            (400, BadRequestError),
            (401, AuthenticationError),
            (403, PermissionDeniedError),
            (404, NotFoundError),
            (422, UnprocessableEntityError),
        ],
    )
    def test_non_retryable_errors_raise_immediately(
        self, status_code: int, error_type: type
    ) -> None:
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            return _error_response(status_code)

        transport = _make_transport(handler)
        with pytest.raises(error_type):
            transport.request("GET", "/v1/test")
        assert call_count == 1  # No retries


# ── TestSyncTransportRetry ───────────────────────────────────────────────


class TestSyncTransportRetry:
    @patch("upbeat._http.time.sleep")
    def test_429_retries_then_succeeds(self, mock_sleep: Any) -> None:
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return _error_response(429)
            return _json_response({"ok": True})

        transport = _make_transport(handler)
        result = transport.request("GET", "/v1/test")
        assert result.data == {"ok": True}
        assert call_count == 3
        assert mock_sleep.call_count == 2

    @patch("upbeat._http.time.sleep")
    def test_500_retries_then_succeeds(self, mock_sleep: Any) -> None:
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                return _error_response(500)
            return _json_response({"ok": True})

        transport = _make_transport(handler)
        result = transport.request("GET", "/v1/test")
        assert result.data == {"ok": True}
        assert call_count == 2

    @patch("upbeat._http.time.sleep")
    def test_connection_error_retries_then_succeeds(self, mock_sleep: Any) -> None:
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                raise httpx.ConnectError("connection refused")
            return _json_response({"ok": True})

        transport = _make_transport(handler)
        result = transport.request("GET", "/v1/test")
        assert result.data == {"ok": True}
        assert call_count == 2

    @patch("upbeat._http.time.sleep")
    def test_timeout_retries_then_succeeds(self, mock_sleep: Any) -> None:
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                raise httpx.ReadTimeout("read timed out")
            return _json_response({"ok": True})

        transport = _make_transport(handler)
        result = transport.request("GET", "/v1/test")
        assert result.data == {"ok": True}
        assert call_count == 2

    @patch("upbeat._http.time.sleep")
    def test_retries_exhausted_raises(self, mock_sleep: Any) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _error_response(500)

        transport = _make_transport(handler)
        with pytest.raises(InternalServerError):
            transport.request("GET", "/v1/test")

    @patch("upbeat._http.time.sleep")
    def test_max_retries_zero_no_retry(self, mock_sleep: Any) -> None:
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            return _error_response(500)

        transport = _make_transport(handler, max_retries=0)
        with pytest.raises(InternalServerError):
            transport.request("GET", "/v1/test")
        assert call_count == 1
        mock_sleep.assert_not_called()


# ── TestSyncTransportLogger ──────────────────────────────────────────────


class TestSyncTransportLogger:
    def test_on_request_and_response_called(self) -> None:
        logger = RecordingLogger()

        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response({"ok": True})

        transport = _make_transport(handler, logger=logger)
        transport.request("GET", "/v1/test")
        assert len(logger.requests) == 1
        assert len(logger.responses) == 1
        assert logger.requests[0].method == "GET"

    @patch("upbeat._http.time.sleep")
    def test_on_retry_called(self, mock_sleep: Any) -> None:
        logger = RecordingLogger()
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                return _error_response(500)
            return _json_response({"ok": True})

        transport = _make_transport(handler, logger=logger)
        transport.request("GET", "/v1/test")
        assert len(logger.retries) == 1
        assert logger.retries[0].attempt == 1

    def test_on_error_called(self) -> None:
        logger = RecordingLogger()

        def handler(request: httpx.Request) -> httpx.Response:
            return _error_response(400)

        transport = _make_transport(handler, logger=logger)
        with pytest.raises(BadRequestError):
            transport.request("GET", "/v1/test")
        assert len(logger.errors) == 1


# ── TestSyncTransportThrottle ────────────────────────────────────────────


class TestSyncTransportThrottle:
    @patch("upbeat._http.time.sleep")
    def test_proactive_throttle_sleeps(self, mock_sleep: Any) -> None:
        call_count = 0

        def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return _json_response(
                    {"ok": True},
                    remaining_req="group=default; min=1800; sec=0",
                )
            return _json_response(
                {"ok": True},
                remaining_req="group=default; min=1800; sec=29",
            )

        transport = _make_transport(handler)
        # First request: sets sec=0
        transport.request("GET", "/v1/test")
        # Second request: should trigger proactive throttle
        transport.request("GET", "/v1/test")
        # sleep called once for proactive throttle on second request
        mock_sleep.assert_called_once_with(1.0)


# ── TestAsyncTransport ───────────────────────────────────────────────────


class TestAsyncTransport:
    @pytest.mark.asyncio
    async def test_get_success(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([{"currency": "BTC"}])

        transport = _make_async_transport(handler)
        result = await transport.request("GET", "/v1/accounts")
        assert result.data == [{"currency": "BTC"}]
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_error_raises(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _error_response(400)

        transport = _make_async_transport(handler, max_retries=0)
        with pytest.raises(BadRequestError):
            await transport.request("GET", "/v1/test")

    @pytest.mark.asyncio
    @patch("upbeat._http.asyncio.sleep", return_value=None)
    async def test_retry_then_success(self, mock_sleep: Any) -> None:
        call_count = 0

        async def handler(request: httpx.Request) -> httpx.Response:
            nonlocal call_count
            call_count += 1
            if call_count <= 1:
                return _error_response(500)
            return _json_response({"ok": True})

        transport = _make_async_transport(handler)
        result = await transport.request("GET", "/v1/test")
        assert result.data == {"ok": True}
        assert call_count == 2
