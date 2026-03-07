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
