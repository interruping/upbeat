from __future__ import annotations

import uuid

_PUBLIC_CHANNELS = {"ticker", "trade", "orderbook"}
_CANDLE_PREFIXES = "candle."


def generate_payload(
    *,
    type: str,
    codes: list[str] | None = None,
    is_only_snapshot: bool = False,
    is_only_realtime: bool = False,
    level: float | None = None,
    ticket: str | None = None,
    format: str = "DEFAULT",
) -> list[dict[str, object]]:
    ticket_value = ticket or str(uuid.uuid4())

    is_public = type in _PUBLIC_CHANNELS or type.startswith(_CANDLE_PREFIXES)

    if type == "myAsset" and codes is not None:
        raise ValueError("myAsset channel does not accept codes parameter")

    if type in ("myOrder", "myAsset") and (is_only_snapshot or is_only_realtime):
        raise ValueError(
            f"{type} channel does not support is_only_snapshot/is_only_realtime"
        )

    if is_public and not codes:
        raise ValueError(f"{type} channel requires codes parameter")

    type_obj: dict[str, object] = {"type": type}

    if codes is not None:
        type_obj["codes"] = codes

    if is_only_snapshot:
        type_obj["is_only_snapshot"] = True
    if is_only_realtime:
        type_obj["is_only_realtime"] = True

    if level is not None and type == "orderbook":
        type_obj["level"] = level

    return [
        {"ticket": ticket_value},
        type_obj,
        {"format": format},
    ]


def generate_multi_payload(
    subscriptions: list[dict[str, object]],
    *,
    ticket: str | None = None,
    format: str = "DEFAULT",
) -> list[dict[str, object]]:
    ticket_value = ticket or str(uuid.uuid4())
    result: list[dict[str, object]] = [{"ticket": ticket_value}]
    result.extend(subscriptions)
    result.append({"format": format})
    return result
