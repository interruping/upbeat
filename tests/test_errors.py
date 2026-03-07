import httpx
import pytest

from upbeat._errors import (
    APIConnectionError,
    APIError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InsufficientFundsError,
    InternalServerError,
    MinimumOrderError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    RemainingRequest,
    UnprocessableEntityError,
    UpbeatError,
    WebSocketClosedError,
    WebSocketConnectionError,
    WebSocketError,
)


def _make_response(
    status_code: int,
    *,
    json: dict | None = None,
    text: str | None = None,
    headers: dict[str, str] | None = None,
) -> httpx.Response:
    kwargs: dict = {
        "status_code": status_code,
        "request": httpx.Request("GET", "https://api.upbit.com/v1/test"),
    }
    if headers:
        kwargs["headers"] = headers
    if json is not None:
        kwargs["json"] = json
    elif text is not None:
        kwargs["text"] = text
    else:
        kwargs["json"] = {"error": {"name": "test_error", "message": "test message"}}
    return httpx.Response(**kwargs)


# ── Inheritance ──────────────────────────────────────────────────────────


class TestInheritance:
    def test_base_hierarchy(self):
        assert issubclass(APIError, UpbeatError)
        assert issubclass(APIStatusError, APIError)
        assert issubclass(APIConnectionError, APIError)
        assert issubclass(APITimeoutError, APIConnectionError)
        assert issubclass(WebSocketError, UpbeatError)
        assert issubclass(WebSocketConnectionError, WebSocketError)
        assert issubclass(WebSocketClosedError, WebSocketError)

    def test_status_error_subclasses(self):
        assert issubclass(BadRequestError, APIStatusError)
        assert issubclass(AuthenticationError, APIStatusError)
        assert issubclass(PermissionDeniedError, APIStatusError)
        assert issubclass(NotFoundError, APIStatusError)
        assert issubclass(UnprocessableEntityError, APIStatusError)
        assert issubclass(RateLimitError, APIStatusError)
        assert issubclass(InternalServerError, APIStatusError)

    def test_special_subclasses(self):
        assert issubclass(InsufficientFundsError, BadRequestError)
        assert issubclass(MinimumOrderError, BadRequestError)


# ── Attribute storage ────────────────────────────────────────────────────


class TestAttributes:
    def test_upbeat_error(self):
        err = UpbeatError("something broke")
        assert err.message == "something broke"
        assert str(err) == "something broke"

    def test_api_status_error_attributes(self):
        resp = _make_response(400)
        err = APIStatusError(
            "bad",
            status_code=400,
            error_name="test_error",
            error_message="test message",
            response=resp,
            remaining_request=None,
        )
        assert err.status_code == 400
        assert err.error_name == "test_error"
        assert err.error_message == "test message"
        assert err.response is resp
        assert err.remaining_request is None

    def test_api_connection_error(self):
        cause = TimeoutError("timed out")
        err = APIConnectionError("connection failed", cause=cause)
        assert err.cause is cause
        assert err.message == "connection failed"

    def test_websocket_closed_error(self):
        err = WebSocketClosedError("closed", code=1000, reason="normal")
        assert err.code == 1000
        assert err.reason == "normal"


# ── RemainingRequest ─────────────────────────────────────────────────────


class TestRemainingRequest:
    def test_from_header(self):
        rr = RemainingRequest.from_header("group=default; min=1800; sec=29")
        assert rr.group == "default"
        assert rr.remaining_min == 1800
        assert rr.remaining_sec == 29

    def test_from_header_trade_group(self):
        rr = RemainingRequest.from_header("group=trade; min=200; sec=5")
        assert rr.group == "trade"
        assert rr.remaining_min == 200
        assert rr.remaining_sec == 5

    def test_frozen(self):
        rr = RemainingRequest.from_header("group=default; min=100; sec=10")
        with pytest.raises(AttributeError):
            rr.group = "other"  # type: ignore[misc]


# ── from_response factory ────────────────────────────────────────────────


class TestFromResponse:
    def test_400_bad_request(self):
        resp = _make_response(400)
        err = APIStatusError.from_response(resp)
        assert type(err) is BadRequestError
        assert err.status_code == 400

    def test_401_authentication(self):
        resp = _make_response(401)
        err = APIStatusError.from_response(resp)
        assert type(err) is AuthenticationError

    def test_403_permission_denied(self):
        resp = _make_response(403)
        err = APIStatusError.from_response(resp)
        assert type(err) is PermissionDeniedError

    def test_404_not_found(self):
        resp = _make_response(404)
        err = APIStatusError.from_response(resp)
        assert type(err) is NotFoundError

    def test_422_unprocessable(self):
        resp = _make_response(422)
        err = APIStatusError.from_response(resp)
        assert type(err) is UnprocessableEntityError

    def test_429_rate_limit(self):
        resp = _make_response(429)
        err = APIStatusError.from_response(resp)
        assert type(err) is RateLimitError

    def test_418_rate_limit_ip_ban(self):
        resp = _make_response(418)
        err = APIStatusError.from_response(resp)
        assert type(err) is RateLimitError

    def test_500_internal_server(self):
        resp = _make_response(500)
        err = APIStatusError.from_response(resp)
        assert type(err) is InternalServerError

    def test_502_maps_to_internal_server(self):
        resp = _make_response(502)
        err = APIStatusError.from_response(resp)
        assert type(err) is InternalServerError

    def test_insufficient_funds(self):
        resp = _make_response(
            400,
            json={
                "error": {
                    "name": "insufficient_funds_bid",
                    "message": "Not enough KRW",
                }
            },
        )
        err = APIStatusError.from_response(resp)
        assert type(err) is InsufficientFundsError
        assert err.error_name == "insufficient_funds_bid"

    def test_minimum_order(self):
        resp = _make_response(
            400,
            json={
                "error": {
                    "name": "under_min_total_bid",
                    "message": "Minimum order total",
                }
            },
        )
        err = APIStatusError.from_response(resp)
        assert type(err) is MinimumOrderError

    def test_non_json_body(self):
        resp = _make_response(500, text="Internal Server Error")
        err = APIStatusError.from_response(resp)
        assert type(err) is InternalServerError
        assert err.error_message == "Internal Server Error"
        assert err.error_name is None

    def test_remaining_request_header(self):
        resp = _make_response(
            429,
            headers={"Remaining-Req": "group=default; min=0; sec=0"},
        )
        err = APIStatusError.from_response(resp)
        assert err.remaining_request is not None
        assert err.remaining_request.group == "default"
        assert err.remaining_request.remaining_min == 0

    def test_unknown_status_code(self):
        resp = _make_response(499)
        err = APIStatusError.from_response(resp)
        assert type(err) is APIStatusError


# ── Catchability ─────────────────────────────────────────────────────────


class TestCatchability:
    def test_catch_insufficient_funds_as_bad_request(self):
        resp = _make_response(
            400,
            json={
                "error": {
                    "name": "insufficient_funds_ask",
                    "message": "Not enough",
                }
            },
        )
        err = APIStatusError.from_response(resp)
        with pytest.raises(BadRequestError):
            raise err

    def test_catch_minimum_order_as_bad_request(self):
        resp = _make_response(
            400,
            json={
                "error": {
                    "name": "under_min_total_ask",
                    "message": "Too small",
                }
            },
        )
        err = APIStatusError.from_response(resp)
        with pytest.raises(BadRequestError):
            raise err

    def test_catch_api_status_error_as_api_error(self):
        resp = _make_response(404)
        err = APIStatusError.from_response(resp)
        with pytest.raises(APIError):
            raise err

    def test_catch_api_error_as_upbeat_error(self):
        resp = _make_response(500)
        err = APIStatusError.from_response(resp)
        with pytest.raises(UpbeatError):
            raise err

    def test_catch_timeout_as_connection_error(self):
        err = APITimeoutError("timeout")
        with pytest.raises(APIConnectionError):
            raise err
