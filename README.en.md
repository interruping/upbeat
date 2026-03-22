# upbeat

**Unofficial** modern Python client for the [Upbit](https://upbit.com) cryptocurrency exchange API.

> [!WARNING]
> This library does not guarantee investment returns. We accept no responsibility for any investment losses caused by software bugs, API changes, network failures, or any other reason. All investment decisions and their consequences are entirely your own responsibility.

---

*Tired of manually buying the top and selling the bottom? Now you can automate your losses with code!*

```python
from upbeat import AsyncUpbeat

async with AsyncUpbeat(access_key="...", secret_key="...") as client:
    # Watch the real-time ticker...
    async for tick in client.ws.ticker(["KRW-BTC"]):
        change = tick.signed_change_rate  # Change rate from previous day

        if change > 0.05:
            # Up 5%! It's definitely going higher — chase the pump (aka FOMO)
            await client.orders.create(
                market="KRW-BTC", side="bid",
                ord_type="price", price="100000",
            )

        elif change < -0.03:
            # Down 3%! Panic sell!
            btc = await client.shortcuts.get_account("BTC")
            await client.orders.create(
                market="KRW-BTC", side="ask",
                ord_type="market", volume=btc.balance,
            )
        # Expected return of this strategy: -∞
```

*(Just kidding. Please don't actually do this.)*

## Why Upbeat?

- **AI-friendly** — Ships with built-in OpenAPI 3.1 + AsyncAPI 3.0 specs, so LLMs and AI agents can instantly understand the API structure and generate code.
- **Full Upbit API coverage** — 12 quotation endpoints, 31 exchange endpoints, 6 WebSocket channels. Every API Upbit offers, covered.
- **Type safety** — Every request and response is defined as a Pydantic v2 model, giving you IDE autocompletion and runtime validation. Bad parameters get caught before your code runs.

> [!NOTE]
> This project was built with agentic coding. It was designed, implemented, and tested in collaboration with an AI coding agent (Claude Code). The [`CLAUDE.md`](CLAUDE.md) and [`AGENTS.md`](AGENTS.md) files in the project root contain project context — code style, architecture, commands — so AI agents can start contributing right away.

## Features

- **Sync + Async** support (`Upbeat` / `AsyncUpbeat`)
- Full REST API coverage (Quotation + Exchange)
- WebSocket real-time data streaming
- Type-safe with Pydantic v2 models
- Client-side minimum order amount validation (`validate_min_order`)
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

> [!TIP]
> Public APIs (market data, tickers, etc.) work without authentication, but trading APIs (orders, accounts, deposits/withdrawals) require API keys from Upbit.
> Get your `access_key` and `secret_key` from the [Upbit Open API Management page](https://upbit.com/mypage/open_api_management).

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
    tickers = client.quotation.get_tickers("KRW-BTC")

    # Exchange (authenticated)
    accounts = client.accounts.list()
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
    tickers = await client.quotation.get_tickers("KRW-BTC")
    accounts = await client.accounts.list()
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
    validate_min_order=True,  # Pre-validate minimum order amount
)

# Per-request override
cautious_client = client.with_options(max_retries=5)
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
from upbeat import (
    Upbeat,
    RateLimitError,
    InsufficientFundsError,
    NotFoundError,
    ValidationError,
)

client = Upbeat(access_key="...", secret_key="...", validate_min_order=True)

try:
    order = client.orders.create(
        market="KRW-BTC",
        side="bid",
        ord_type="limit",
        volume="0.001",
        price="50000000",
    )
except ValidationError as e:
    print(f"Below minimum: {e.total} < min {e.min_total} ({e.market})")
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
  ValidationError
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
| `client.shortcuts` | Convenience helpers (account lookup, portfolio, market buy, etc.) | Yes |
| `client.strategies` | Trading strategies (DCA, rebalancing, price alerts) | Yes |

For detailed endpoint documentation, see the OpenAPI specs:

- [Quotation API](specs/quotation.yaml) -- 12 endpoints (public, no auth)
- [Exchange API](specs/exchange.yaml) -- 31 endpoints (JWT auth required)
- [WebSocket Channels](specs/websocket.yaml) -- 6 channels (ticker, trade, orderbook, candle, myOrder, myAsset)

## Contributing

Contributions are welcome! Please follow the steps below before opening a PR.

```bash
# 1. Fork and clone
git clone https://github.com/<your-username>/upbeat.git
cd upbeat

# 2. Install dependencies
uv sync --group dev

# 3. Create a branch
git checkout -b feat/my-feature

# 4. After making changes, make sure all checks pass
uv run ruff check src/            # Lint
uv run ruff format src/           # Format
uv run mypy src/upbeat/           # Type check
uv run pytest                     # Tests
```

When opening a PR:

- Use branch name prefixes like `feat/`, `fix/`, `chore/`, etc.
- Write commit messages that briefly explain the "why" behind the change.
- Include tests for new features.
- Ensure lint, format, type check, and tests all pass.

## License

[MIT](LICENSE)
