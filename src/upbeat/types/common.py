from dataclasses import dataclass
from typing import Any

from upbeat._errors import RemainingRequest


@dataclass(frozen=True, slots=True)
class APIResponse:
    data: Any
    remaining_request: RemainingRequest | None
    status_code: int
