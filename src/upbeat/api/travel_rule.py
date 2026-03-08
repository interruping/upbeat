from __future__ import annotations

from upbeat._base import _AsyncAPIResource, _SyncAPIResource
from upbeat.types.travel_rule import TravelRuleVasp, TravelRuleVerification


class TravelRuleAPI(_SyncAPIResource):
    def list_vasps(self) -> list[TravelRuleVasp]:
        response = self._transport.request(
            "GET", "/v1/travel_rule/vasps", credentials=self._credentials
        )
        return [TravelRuleVasp.model_validate(item) for item in response.data]

    def verify_by_uuid(
        self,
        *,
        deposit_uuid: str,
        vasp_uuid: str,
    ) -> TravelRuleVerification:
        json_body = {"deposit_uuid": deposit_uuid, "vasp_uuid": vasp_uuid}
        response = self._transport.request(
            "POST",
            "/v1/travel_rule/deposit/uuid",
            json_body=json_body,
            credentials=self._credentials,
        )
        return TravelRuleVerification.model_validate(response.data)

    def verify_by_txid(
        self,
        *,
        vasp_uuid: str,
        txid: str,
        currency: str,
        net_type: str,
    ) -> TravelRuleVerification:
        json_body = {
            "vasp_uuid": vasp_uuid,
            "txid": txid,
            "currency": currency,
            "net_type": net_type,
        }
        response = self._transport.request(
            "POST",
            "/v1/travel_rule/deposit/txid",
            json_body=json_body,
            credentials=self._credentials,
        )
        return TravelRuleVerification.model_validate(response.data)


class AsyncTravelRuleAPI(_AsyncAPIResource):
    async def list_vasps(self) -> list[TravelRuleVasp]:
        response = await self._transport.request(
            "GET", "/v1/travel_rule/vasps", credentials=self._credentials
        )
        return [TravelRuleVasp.model_validate(item) for item in response.data]

    async def verify_by_uuid(
        self,
        *,
        deposit_uuid: str,
        vasp_uuid: str,
    ) -> TravelRuleVerification:
        json_body = {"deposit_uuid": deposit_uuid, "vasp_uuid": vasp_uuid}
        response = await self._transport.request(
            "POST",
            "/v1/travel_rule/deposit/uuid",
            json_body=json_body,
            credentials=self._credentials,
        )
        return TravelRuleVerification.model_validate(response.data)

    async def verify_by_txid(
        self,
        *,
        vasp_uuid: str,
        txid: str,
        currency: str,
        net_type: str,
    ) -> TravelRuleVerification:
        json_body = {
            "vasp_uuid": vasp_uuid,
            "txid": txid,
            "currency": currency,
            "net_type": net_type,
        }
        response = await self._transport.request(
            "POST",
            "/v1/travel_rule/deposit/txid",
            json_body=json_body,
            credentials=self._credentials,
        )
        return TravelRuleVerification.model_validate(response.data)
