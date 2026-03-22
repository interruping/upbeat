"""VCR 설정 및 커스텀 YAML serializer.

- 기본 record_mode="none" → CI에서 실 API 호출 차단
- VCR_RECORD_MODE 환경변수로 녹화 모드 전환
- 응답 body를 pretty-print JSON + YAML literal block scalar(|)로 저장
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any

import vcr
import yaml
from vcr.record_mode import RecordMode

# ── Pretty JSON body ────────────────────────────────────────────────────


def _pretty_json_body(response: dict) -> dict:
    """응답 body가 JSON이면 정렬·들여쓰기하여 카세트에 읽기 좋게 저장한다."""
    body = response.get("body", {}).get("string", "")
    # 리플레이 시 bytes로 로드된 body는 건드리지 않는다
    if isinstance(body, bytes):
        return response
    try:
        parsed = json.loads(body)
        response["body"]["string"] = json.dumps(
            parsed, indent=2, ensure_ascii=False, sort_keys=False
        )
    except (json.JSONDecodeError, TypeError):
        pass
    return response


# ── YAML literal block scalar ───────────────────────────────────────────


class _LiteralStr(str):
    """yaml dumper가 literal block scalar(|)로 출력하도록 표시하는 래퍼."""


def _literal_representer(dumper: yaml.Dumper, data: _LiteralStr) -> Any:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(_LiteralStr, _literal_representer)


def _mark_multiline(obj: Any) -> Any:
    """dict/list를 재귀 탐색하며 개행이 포함된 문자열을 _LiteralStr로 감싼다."""
    if isinstance(obj, dict):
        return {k: _mark_multiline(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_mark_multiline(v) for v in obj]
    if isinstance(obj, str) and "\n" in obj:
        return _LiteralStr(obj)
    return obj


# ── Serialize / Deserialize ─────────────────────────────────────────────


def _ensure_body_bytes(cassette_dict: dict) -> dict:
    """vcrpy 리플레이 시 body를 bytes로 기대하므로 str → bytes 변환."""
    for interaction in cassette_dict.get("interactions", []):
        for key in ("request", "response"):
            body = interaction.get(key, {}).get("body")
            if isinstance(body, dict) and isinstance(
                body.get("string"), str
            ):
                body["string"] = body["string"].encode("utf-8")
    return cassette_dict


def _prettify_response_bodies(cassette_dict: dict) -> None:
    """serialize 직전에 bytes body를 pretty JSON 문자열로 변환한다."""
    for interaction in cassette_dict.get("interactions", []):
        body = interaction.get("response", {}).get("body")
        if not isinstance(body, dict):
            continue
        raw = body.get("string", "")
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        try:
            parsed = json.loads(raw)
            body["string"] = json.dumps(
                parsed, indent=2, ensure_ascii=False, sort_keys=False
            )
        except (json.JSONDecodeError, TypeError):
            # JSON이 아니어도 bytes → str 변환은 필요 (YAML 저장용)
            if isinstance(body.get("string"), bytes):
                body["string"] = body["string"].decode("utf-8")


def serialize(cassette_dict: dict) -> str:
    _prettify_response_bodies(cassette_dict)
    return yaml.dump(
        _mark_multiline(cassette_dict),
        default_flow_style=False,
        allow_unicode=True,
    )


def deserialize(cassette_string: str) -> Any:
    data = yaml.safe_load(cassette_string)
    return _ensure_body_bytes(data)


# ── VCR 인스턴스 ────────────────────────────────────────────────────────

# tests/_vcr 모듈 자체가 serialize/deserialize를 갖고 있으므로
# register_serializer에 모듈을 직접 등록한다.
_this_module = sys.modules[__name__]

upbeat_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes",
    filter_headers=[("Authorization", "REDACTED")],
    filter_query_parameters=["access_key"],
    decode_compressed_response=True,
    record_mode=RecordMode(os.environ.get("VCR_RECORD_MODE", "none")),
    before_record_response=_pretty_json_body,
)
upbeat_vcr.register_serializer("pretty-yaml", _this_module)
upbeat_vcr.serializer = "pretty-yaml"
