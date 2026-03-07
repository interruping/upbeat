# upbeat

Modern Python client for the [Upbit](https://upbit.com) cryptocurrency exchange API.

## Features

- **Sync + Async** support (`Upbeat` / `AsyncUpbeat`)
- Full REST API coverage (Quotation + Exchange)
- WebSocket real-time data streaming
- Type-safe with Pydantic v2 models
- Automatic retry with exponential backoff
- Smart rate limiting (`Remaining-Req` header tracking)
- JWT authentication (HS512)
- Context manager support for resource cleanup
- Customizable HTTP client, logging, and timeouts

## Installation

```bash
pip install upbeat
```

With pandas support:

```bash
pip install upbeat[pandas]
```

## Quick Start

### Public API (no authentication)

```python
import upbeat

# Module-level convenience functions
ticker = upbeat.get_ticker("KRW-BTC")
candles = upbeat.get_candles("KRW-BTC", interval="1m", count=200)
orderbook = upbeat.get_orderbook("KRW-BTC")
markets = upbeat.get_markets()
```

### Client Instance

```python
from upbeat import Upbeat

with Upbeat(access_key="...", secret_key="...") as client:
    # Quotation (public)
    ticker = client.quotation.get_ticker("KRW-BTC")

    # Exchange (authenticated)
    balance = client.accounts.get_balance()
    order = client.orders.create(
        market="KRW-BTC",
        side="bid",
        ord_type="limit",
        volume="0.001",
        price="50000000",
    )
```

### Async Client

```python
from upbeat import AsyncUpbeat

async with AsyncUpbeat(access_key="...", secret_key="...") as client:
    ticker = await client.quotation.get_ticker("KRW-BTC")
    balance = await client.accounts.get_balance()
```

### WebSocket

```python
from upbeat import AsyncUpbeat

async with AsyncUpbeat(access_key="...", secret_key="...") as client:
    async for msg in client.ws.ticker(["KRW-BTC", "KRW-ETH"]):
        print(msg.trade_price)
```

## Configuration

```python
from upbeat import Upbeat, Timeout

client = Upbeat(
    access_key="...",
    secret_key="...",
    timeout=Timeout(connect=10.0, read=30.0),
    max_retries=3,
    logger=my_custom_logger,  # Logger Protocol implementation
)

# Per-request override
slow_client = client.with_options(timeout=Timeout(connect=10.0, read=120.0))
```

### Custom HTTP Client

```python
import httpx
from upbeat import Upbeat

client = Upbeat(
    access_key="...",
    secret_key="...",
    http_client=httpx.Client(proxy="http://proxy:8080"),
)
```

## Error Handling

```python
from upbeat import Upbeat, RateLimitError, InsufficientFundsError, NotFoundError

client = Upbeat(access_key="...", secret_key="...")

try:
    order = client.orders.create(
        market="KRW-BTC",
        side="bid",
        ord_type="limit",
        volume="0.001",
        price="50000000",
    )
except InsufficientFundsError as e:
    print(f"Insufficient funds: {e.error_message}")
except RateLimitError as e:
    print(f"Rate limited. Remaining: {e.remaining_request}")
except NotFoundError as e:
    print(f"Not found: {e.error_message}")
```

### Exception Hierarchy

```
UpbeatError
  APIError
    APIStatusError
      BadRequestError (400)
      AuthenticationError (401)
      PermissionDeniedError (403)
      NotFoundError (404)
      UnprocessableEntityError (422)
      RateLimitError (418, 429)
      InternalServerError (5xx)
      InsufficientFundsError (400)
      MinimumOrderError (400)
    APIConnectionError
      APITimeoutError
  WebSocketError
    WebSocketConnectionError
    WebSocketClosedError
```

## API Reference

Available resource groups:

| Resource | Description | Auth |
|----------|-------------|------|
| `client.quotation` | Market data (ticker, candles, orderbook, trades) | No |
| `client.markets` | Trading pair information | No |
| `client.accounts` | Account balance | Yes |
| `client.orders` | Order management | Yes |
| `client.deposits` | Deposit operations | Yes |
| `client.withdrawals` | Withdrawal operations | Yes |
| `client.ws` | WebSocket real-time streaming | Varies |

For detailed endpoint documentation, see the OpenAPI specs:

- [Quotation API](specs/quotation.yaml) -- 12 endpoints (public, no auth)
- [Exchange API](specs/exchange.yaml) -- 28 endpoints (JWT auth required)
- [WebSocket Channels](specs/websocket.yaml) -- 6 channels (ticker, trade, orderbook, candle, myOrder, myAsset)

## Development

```bash
# Install dependencies
uv sync --group dev

# Run tests
uv run pytest

# Type checking
uv run mypy src/upbeat/

# Lint & format
uv run ruff check . && uv run ruff format .
```

## License

MIT
