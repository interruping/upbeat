from __future__ import annotations

import logging

import pytest

from upbeat._logger import (
    DefaultLogger,
    ErrorInfo,
    Logger,
    NullLogger,
    RequestInfo,
    ResponseInfo,
    RetryInfo,
    WebSocketEventInfo,
)


class TestContextTypes:
    def test_request_info(self) -> None:
        info = RequestInfo(method="GET", url="https://api.upbit.com", headers={"a": "b"})
        assert info.method == "GET"
        assert info.url == "https://api.upbit.com"
        assert info.headers == {"a": "b"}

    def test_response_info(self) -> None:
        info = ResponseInfo(
            status_code=200,
            url="https://api.upbit.com",
            headers={"x": "y"},
            elapsed_ms=12.5,
        )
        assert info.status_code == 200
        assert info.elapsed_ms == 12.5

    def test_retry_info(self) -> None:
        info = RetryInfo(
            attempt=1,
            max_retries=3,
            delay_seconds=1.0,
            reason="rate limit",
            method="POST",
            url="https://api.upbit.com",
        )
        assert info.attempt == 1
        assert info.reason == "rate limit"

    def test_error_info(self) -> None:
        err = ValueError("test")
        info = ErrorInfo(error=err, method="GET", url="https://api.upbit.com")
        assert info.error is err

    def test_ws_event_info_defaults(self) -> None:
        info = WebSocketEventInfo(event="open", url="wss://api.upbit.com")
        assert info.message is None
        assert info.error is None

    def test_ws_event_info_with_optionals(self) -> None:
        err = ConnectionError("closed")
        info = WebSocketEventInfo(
            event="error", url="wss://api.upbit.com", message="fail", error=err
        )
        assert info.message == "fail"
        assert info.error is err

    def test_frozen_immutability(self) -> None:
        info = RequestInfo(method="GET", url="https://api.upbit.com", headers={})
        with pytest.raises(AttributeError):
            info.method = "POST"  # type: ignore[misc]


class TestLoggerProtocol:
    def test_default_logger_is_logger(self) -> None:
        assert isinstance(DefaultLogger(), Logger)

    def test_null_logger_is_logger(self) -> None:
        assert isinstance(NullLogger(), Logger)

    def test_custom_class_implements_logger(self) -> None:
        class CustomLogger:
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

        assert isinstance(CustomLogger(), Logger)

    def test_non_conforming_class(self) -> None:
        class NotALogger:
            pass

        assert not isinstance(NotALogger(), Logger)


class TestDefaultLogger:
    def test_on_request_debug(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = DefaultLogger()
        with caplog.at_level(logging.DEBUG, logger="upbeat"):
            logger.on_request(
                RequestInfo(method="GET", url="https://api.upbit.com", headers={})
            )
        assert "Request: GET https://api.upbit.com" in caplog.text

    def test_on_response_debug(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = DefaultLogger()
        with caplog.at_level(logging.DEBUG, logger="upbeat"):
            logger.on_response(
                ResponseInfo(
                    status_code=200,
                    url="https://api.upbit.com",
                    headers={},
                    elapsed_ms=15.3,
                )
            )
        assert "200" in caplog.text
        assert "15.3ms" in caplog.text

    def test_on_retry_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = DefaultLogger()
        with caplog.at_level(logging.WARNING, logger="upbeat"):
            logger.on_retry(
                RetryInfo(
                    attempt=2,
                    max_retries=3,
                    delay_seconds=1.5,
                    reason="server error",
                    method="POST",
                    url="https://api.upbit.com",
                )
            )
        assert "Retry 2/3" in caplog.text
        assert "server error" in caplog.text

    def test_on_error_error(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = DefaultLogger()
        with caplog.at_level(logging.ERROR, logger="upbeat"):
            logger.on_error(
                ErrorInfo(
                    error=RuntimeError("boom"),
                    method="GET",
                    url="https://api.upbit.com",
                )
            )
        assert "boom" in caplog.text

    def test_on_ws_event_debug(self, caplog: pytest.LogCaptureFixture) -> None:
        logger = DefaultLogger()
        with caplog.at_level(logging.DEBUG, logger="upbeat"):
            logger.on_ws_event(
                WebSocketEventInfo(event="open", url="wss://api.upbit.com")
            )
        assert "WebSocket open" in caplog.text

    def test_on_ws_event_with_error_warning(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        logger = DefaultLogger()
        with caplog.at_level(logging.WARNING, logger="upbeat"):
            logger.on_ws_event(
                WebSocketEventInfo(
                    event="error",
                    url="wss://api.upbit.com",
                    error=ConnectionError("lost"),
                )
            )
        assert "lost" in caplog.text


class TestNullLogger:
    def test_all_methods_return_none(self) -> None:
        logger = NullLogger()
        req = RequestInfo(method="GET", url="https://api.upbit.com", headers={})
        resp = ResponseInfo(
            status_code=200, url="https://api.upbit.com", headers={}, elapsed_ms=1.0
        )
        retry = RetryInfo(
            attempt=1,
            max_retries=3,
            delay_seconds=1.0,
            reason="err",
            method="GET",
            url="https://api.upbit.com",
        )
        err = ErrorInfo(
            error=Exception("x"), method="GET", url="https://api.upbit.com"
        )
        ws = WebSocketEventInfo(event="open", url="wss://api.upbit.com")

        assert logger.on_request(req) is None
        assert logger.on_response(resp) is None
        assert logger.on_retry(retry) is None
        assert logger.on_error(err) is None
        assert logger.on_ws_event(ws) is None
