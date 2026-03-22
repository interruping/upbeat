from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import httpx


@dataclass(frozen=True, slots=True)
class RemainingRequest:
    group: str
    remaining_min: int
    remaining_sec: int

    @classmethod
    def from_header(cls, header_value: str) -> RemainingRequest:
        """Parse ``"group=default; min=1800; sec=29"`` format."""
        parts: dict[str, str] = {}
        for item in header_value.split(";"):
            key, _, value = item.strip().partition("=")
            parts[key.strip()] = value.strip()
        return cls(
            group=parts.get("group", ""),
            remaining_min=int(parts.get("min", 0)),
            remaining_sec=int(parts.get("sec", 0)),
        )


# ── Base ─────────────────────────────────────────────────────────────────


class UpbeatError(Exception):
    message: str

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


# ── Validation errors ─────────────────────────────────────────────────


class ValidationError(UpbeatError):
    """Raised when client-side validation catches an invalid order before sending."""

    market: str
    total: str
    min_total: str

    def __init__(
        self,
        message: str,
        *,
        market: str,
        total: str,
        min_total: str,
    ) -> None:
        super().__init__(message)
        self.market = market
        self.total = total
        self.min_total = min_total


# ── API errors ───────────────────────────────────────────────────────────


class APIError(UpbeatError):
    pass


class APIStatusError(APIError):
    status_code: int
    error_name: str | None
    error_message: str | None
    response: httpx.Response
    remaining_request: RemainingRequest | None

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        error_name: str | None,
        error_message: str | None,
        response: httpx.Response,
        remaining_request: RemainingRequest | None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_name = error_name
        self.error_message = error_message
        self.response = response
        self.remaining_request = remaining_request

    @classmethod
    def from_response(cls, response: httpx.Response) -> APIStatusError:
        status_code = response.status_code
        error_name: str | None = None
        error_message: str | None = None

        try:
            body = response.json()
            error_obj = body.get("error", {})
            error_name = error_obj.get("name")
            error_message = error_obj.get("message")
        except Exception:
            error_message = response.text

        remaining_request: RemainingRequest | None = None
        remaining_header = response.headers.get("Remaining-Req")
        if remaining_header:
            remaining_request = RemainingRequest.from_header(remaining_header)

        message = error_message or f"HTTP {status_code}"

        kwargs = {
            "message": message,
            "status_code": status_code,
            "error_name": error_name,
            "error_message": error_message,
            "response": response,
            "remaining_request": remaining_request,
        }

        # Pattern-based subclass matching
        if error_name and re.match(r"^insufficient_funds_", error_name):
            return InsufficientFundsError(**kwargs)
        if error_name and re.match(r"^under_min_total_", error_name):
            return MinimumOrderError(**kwargs)

        # Status code mapping
        subclass = _STATUS_CODE_MAP.get(status_code)
        if subclass is not None:
            return subclass(**kwargs)

        if status_code >= 500:
            return InternalServerError(**kwargs)

        return APIStatusError(**kwargs)


class BadRequestError(APIStatusError):
    pass


class AuthenticationError(APIStatusError):
    pass


class PermissionDeniedError(APIStatusError):
    pass


class NotFoundError(APIStatusError):
    pass


class UnprocessableEntityError(APIStatusError):
    pass


class RateLimitError(APIStatusError):
    pass


class InternalServerError(APIStatusError):
    pass


class InsufficientFundsError(BadRequestError):
    pass


class MinimumOrderError(BadRequestError):
    pass


_STATUS_CODE_MAP: dict[int, type[APIStatusError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    418: RateLimitError,
    422: UnprocessableEntityError,
    429: RateLimitError,
}


# ── Connection errors ────────────────────────────────────────────────────


class APIConnectionError(APIError):
    cause: Exception | None

    def __init__(self, message: str, *, cause: Exception | None = None) -> None:
        super().__init__(message)
        self.cause = cause


class APITimeoutError(APIConnectionError):
    pass


# ── WebSocket errors ─────────────────────────────────────────────────────


class WebSocketError(UpbeatError):
    pass


class WebSocketConnectionError(WebSocketError):
    pass


class WebSocketClosedError(WebSocketError):
    code: int | None
    reason: str | None

    def __init__(
        self,
        message: str,
        *,
        code: int | None = None,
        reason: str | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.reason = reason
