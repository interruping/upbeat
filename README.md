# upbeat

[Upbit](https://upbit.com) 암호화폐 거래소를 위한 **비공식** Python 클라이언트 라이브러리.

> Looking for English documentation? See [README.en.md](README.en.md).

> [!WARNING]
> 이 라이브러리는 투자 수익을 보장하지 않습니다. 버그, API 변경, 네트워크 장애 등 어떤 원인으로든 발생하는 투자 손실에 대해 일체의 책임을 지지 않습니다. 투자 판단과 결과는 전적으로 사용자 본인에게 있습니다.

---

*손으로 직접 고점에 매수하고 저점에 매도하느라 지치셨나요? 이제 코드로 손실을 자동화하세요!*

```python
from upbeat import AsyncUpbeat

async with AsyncUpbeat(access_key="...", secret_key="...") as client:
    # 실시간 시세를 감시하다가...
    async for tick in client.ws.ticker(["KRW-BTC"]):
        change = tick.signed_change_rate  # 전일 대비 변동률

        if change > 0.05:
            # 5% 올랐다! 더 오를 것 같으니 추격 매수 (일명 FOMO)
            await client.orders.create(
                market="KRW-BTC", side="bid",
                ord_type="price", price="100000",
            )

        elif change < -0.03:
            # 3% 빠졌다! 패닉셀!
            accounts = await client.accounts.list()
            btc = next(a for a in accounts if a.currency == "BTC")
            await client.orders.create(
                market="KRW-BTC", side="ask",
                ord_type="market", volume=btc.balance,
            )
        # 이 전략의 기대수익률: -∞
```

*(농담입니다. 제발 이렇게 쓰지 마세요.)*

## 왜 Upbeat?

- **AI 친화적** — OpenAPI 3.1 + AsyncAPI 3.0 스펙이 내장되어 있어서 LLM이나 AI 에이전트가 API 구조를 바로 파악하고 코드를 생성할 수 있습니다.
- **Upbit API 전체 커버리지** — 시세 조회 12개, 거래 31개, WebSocket 6개 채널. 업비트가 제공하는 API를 빠짐없이 지원합니다.
- **타입 안전성** — 모든 요청과 응답이 Pydantic v2 모델로 정의되어 있어서 IDE 자동완성이 잘 됩니다. 잘못된 파라미터는 실행 전에 잡힙니다.

> [!NOTE]
> 이 프로젝트는 Agentic 코딩으로 개발되었습니다. AI 코딩 에이전트(Claude Code)와 함께 설계, 구현, 테스트를 진행했습니다. 프로젝트 루트의 [`CLAUDE.md`](CLAUDE.md)와 [`AGENTS.md`](AGENTS.md)에 코드 스타일, 아키텍처, 명령어 등 프로젝트 컨텍스트가 정리되어 있어 AI 에이전트가 바로 기여를 시작할 수 있습니다.

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
    tickers = client.quotation.get_tickers("KRW-BTC")

    # 거래 (인증 필요)
    accounts = client.accounts.list()
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
cautious_client = client.with_options(max_retries=5)
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

## 기여

기여는 언제나 환영합니다! PR을 올리기 전에 아래 과정을 따라주세요.

```bash
# 1. 포크 후 클론
git clone https://github.com/<your-username>/upbeat.git
cd upbeat

# 2. 의존성 설치
uv sync --group dev

# 3. 브랜치 생성
git checkout -b feat/my-feature

# 4. 코드 작성 후, PR 전에 아래를 모두 통과시켜 주세요
uv run ruff check src/            # 린트
uv run ruff format src/           # 포맷
uv run mypy src/upbeat/           # 타입 체크
uv run pytest                     # 테스트
```

PR을 올릴 때:

- 브랜치 이름은 `feat/`, `fix/`, `chore/` 등 접두사를 사용해 주세요.
- 커밋 메시지는 변경의 "왜"를 간결하게 담아주세요.
- 새로운 기능에는 테스트를 함께 추가해 주세요.
- 린트, 포맷, 타입 체크, 테스트가 모두 통과하는지 확인해 주세요.

## 라이선스

[MIT](LICENSE)
