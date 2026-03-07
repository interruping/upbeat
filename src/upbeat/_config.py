from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Timeout:
    connect: float = 10.0
    read: float = 30.0


DEFAULT_TIMEOUT = Timeout()
DEFAULT_MAX_RETRIES = 3


@dataclass(frozen=True, slots=True)
class UpbeatConfig:
    timeout: Timeout = DEFAULT_TIMEOUT
    max_retries: int = DEFAULT_MAX_RETRIES
    auto_throttle: bool = True
