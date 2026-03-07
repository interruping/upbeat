# upbeat

[Upbit](https://upbit.com) 암호화폐 거래소를 위한 모던 Python 클라이언트 라이브러리.

> Looking for English documentation? See [README.en.md](README.en.md).

## 주요 기능

- **Sync + Async** 동시 지원 (`Upbeat` / `AsyncUpbeat`)
- REST API 전체 커버리지 (시세 + 거래)
- WebSocket 실시간 데이터 스트리밍
- Pydantic v2 기반 타입 안전한 모델
- 지수 백오프 자동 재시도
- `Remaining-Req` 헤더 기반 스마트 Rate Limit 관리
- JWT 인증 (HS512)
- 컨텍스트 매니저를 통한 리소스 정리
- HTTP 클라이언트, 로깅, 타임아웃 커스터마이징

## 설치

```bash
pip install upbeat
```

pandas 지원 포함:

```bash
pip install upbeat[pandas]
```

## 빠른 시작

### 공개 API (인증 불필요)

```python
import upbeat

# 모듈 레벨 편의 함수
ticker = upbeat.get_ticker("KRW-BTC")
candles = upbeat.get_candles("KRW-BTC", interval="1m", count=200)
orderbook = upbeat.get_orderbook("KRW-BTC")
markets = upbeat.get_markets()
```

### 클라이언트 인스턴스

```python
from upbeat import Upbeat

with Upbeat(access_key="...", secret_key="...") as client:
    # 시세 조회 (공개)
    ticker = client.quotation.get_ticker("KRW-BTC")

    # 거래 (인증 필요)
    balance = client.accounts.get_balance()
    order = client.orders.create(
        market="KRW-BTC",
        side="bid",
        ord_type="limit",
        volume="0.001",
        price="50000000",
    )
```

### 비동기 클라이언트

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

## 설정

```python
from upbeat import Upbeat, Timeout

client = Upbeat(
    access_key="...",
    secret_key="...",
    timeout=Timeout(connect=10.0, read=30.0),
    max_retries=3,
    logger=my_custom_logger,  # Logger Protocol 구현체
)

# 퍼-리퀘스트 오버라이드
slow_client = client.with_options(timeout=Timeout(connect=10.0, read=120.0))
```

### 커스텀 HTTP 클라이언트

```python
import httpx
from upbeat import Upbeat

client = Upbeat(
    access_key="...",
    secret_key="...",
    http_client=httpx.Client(proxy="http://proxy:8080"),
)
```

## 에러 처리

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
    print(f"잔고 부족: {e.error_message}")
except RateLimitError as e:
    print(f"요청 초과. 잔여 횟수: {e.remaining_request}")
except NotFoundError as e:
    print(f"리소스 없음: {e.error_message}")
```

### 예외 계층

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

## API 레퍼런스

사용 가능한 리소스 그룹:

| 리소스 | 설명 | 인증 |
|--------|------|------|
| `client.quotation` | 시세 데이터 (현재가, 캔들, 호가, 체결) | 불필요 |
| `client.markets` | 페어(거래쌍) 정보 | 불필요 |
| `client.accounts` | 계정 잔고 | 필요 |
| `client.orders` | 주문 관리 | 필요 |
| `client.deposits` | 입금 관련 | 필요 |
| `client.withdrawals` | 출금 관련 | 필요 |
| `client.ws` | WebSocket 실시간 스트리밍 | 채널별 상이 |

엔드포인트 상세 문서는 OpenAPI 스펙을 참고하세요:

- [시세 API (Quotation)](specs/quotation.yaml) -- 12개 엔드포인트 (공개, 인증 불필요)
- [거래 API (Exchange)](specs/exchange.yaml) -- 31개 엔드포인트 (JWT 인증 필요)
- [WebSocket 채널](specs/websocket.yaml) -- 6개 채널 (ticker, trade, orderbook, candle, myOrder, myAsset)

## 개발

```bash
# 의존성 설치
uv sync --group dev

# 테스트 실행
uv run pytest

# 타입 체크
uv run mypy src/upbeat/

# 린트 & 포맷
uv run ruff check . && uv run ruff format .
```

## 라이선스

MIT
