# CLAUDE.md

## 패키지 관리

이 프로젝트는 **uv**를 사용하여 패키지를 관리합니다.

- 의존성 추가: `uv add <package>`
- 개발 의존성 추가: `uv add --dev <package>`
- 테스트 실행: `uv run pytest`
- 스크립트 실행: `uv run python <script>`

`pip install`이나 `pip`를 직접 사용하지 마세요. 모든 의존성 관리와 실행은 `uv`를 통해 수행합니다.

## LSP

이 프로젝트는 **Pyright** LSP를 사용합니다. 코드 작성 및 수정 시 LSP 진단(diagnostics)을 활용하여 타입 오류나 경고를 파악하세요.

## GitHub 이슈 라벨

이슈 생성 시 아래 라벨을 적절히 지정하세요:

- `bug` — 버그 수정
- `enhancement` — 새 기능 또는 개선
- `chore` — 빌드, 툴링, 의존성, 설정 변경
- `documentation` — 문서 추가/수정
- `setup` — 프로젝트 초기화 및 환경 설정
- `priority: high` — 긴급 처리 필요
- `good first issue` — 입문자용
- `help wanted` — 추가 관심 필요
- `question` — 추가 정보 요청
