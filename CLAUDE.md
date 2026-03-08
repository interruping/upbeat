# Upbeat

업비트(Upbit) 암호화폐 거래소 API를 위한 Python 클라이언트 라이브러리. 동기/비동기 REST API, WebSocket 실시간 스트리밍, Pydantic v2 타입 안전성을 지원한다.

## 코드 스타일

- Python 3.13+, 타입 힌트 필수
- Ruff로 린트/포맷 (`line-length = 88`, 규칙: E, F, I, UP, B, SIM)
- Pydantic v2 모델 사용 (types/ 디렉토리)
- 내부 모듈은 `_` 접두사 (예: `_client.py`, `_auth.py`)
- 공개 API는 `__init__.py`에서 re-export

## 명령어

- `uv run pytest` — 테스트 실행
- `uv run pytest tests/<path>` — 특정 테스트 실행
- `uv run ruff check src/` — 린트 검사
- `uv run ruff format src/` — 코드 포맷팅
- `uv add <package>` — 의존성 추가
- `uv add --dev <package>` — 개발 의존성 추가

IMPORTANT: `pip`을 직접 사용하지 않는다. 모든 의존성 관리와 실행은 `uv`를 통해 수행한다.

## 아키텍처

- `src/upbeat/` — 메인 패키지
  - `api/` — REST API 리소스 (quotation, accounts, orders, deposits, withdrawals, markets, travel_rule)
  - `types/` — Pydantic 응답 모델
  - `ws/` — WebSocket 클라이언트
  - `strategies/` — 트레이딩 전략 헬퍼 (포트폴리오, DCA, 리밸런싱, 알림)
  - `_client.py` — 동기/비동기 클라이언트 (Upbeat, AsyncUpbeat)
  - `_auth.py` — JWT(HS512) 인증
  - `_http.py` — HTTP 레이어 (재시도, 레이트 리밋)
- `tests/` — src/ 구조를 미러링
- `specs/` — API 스펙 (OpenAPI 3.1 + AsyncAPI 3.0)

## 테스트

- pytest + pytest-asyncio 사용
- HTTP 모킹은 vcrpy (cassette 방식)
- 테스트 파일은 src/ 디렉토리 구조를 따른다

## LSP

Pyright LSP를 사용한다. 코드 작성/수정 시 LSP 진단을 활용하여 타입 오류를 파악하세요.

## GitHub 이슈 라벨

- `bug` — 버그 수정
- `enhancement` — 새 기능 또는 개선
- `chore` — 빌드, 툴링, 의존성, 설정 변경
- `documentation` — 문서 추가/수정
- `setup` — 프로젝트 초기화 및 환경 설정
- `priority: high` — 긴급 처리 필요
- `good first issue` — 입문자용
- `help wanted` — 추가 관심 필요
- `question` — 추가 정보 요청
