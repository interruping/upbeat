from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class TravelRuleVasp(BaseModel):
    model_config = ConfigDict(frozen=True)

    vasp_name: str
    vasp_uuid: str
    depositable: bool
    withdrawable: bool


class TravelRuleVerification(BaseModel):
    model_config = ConfigDict(frozen=True)

    deposit_uuid: str
    verification_result: str
    deposit_state: str
