from __future__ import annotations

from upbeat._base import _AsyncAPIResource, _SyncAPIResource
from upbeat.types.market import TradingPair


class MarketsAPI(_SyncAPIResource):
    def get_trading_pairs(self, *, is_details: bool = False) -> list[TradingPair]:
        params = {"is_details": "true" if is_details else "false"}
        response = self._transport.request("GET", "/v1/market/all", params=params)
        return [TradingPair.model_validate(item) for item in response.data]


class AsyncMarketsAPI(_AsyncAPIResource):
    async def get_trading_pairs(
        self, *, is_details: bool = False
    ) -> list[TradingPair]:
        params = {"is_details": "true" if is_details else "false"}
        response = await self._transport.request(
            "GET", "/v1/market/all", params=params
        )
        return [TradingPair.model_validate(item) for item in response.data]
