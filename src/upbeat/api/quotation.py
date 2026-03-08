from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

from upbeat._base import _AsyncAPIResource, _SyncAPIResource
from upbeat._pandas import candles_to_dataframe
from upbeat.types.quotation import (
    CandleDay,
    CandleMinute,
    CandlePeriod,
    CandleSecond,
    Orderbook,
    OrderbookInstrument,
    Ticker,
    Trade,
)

if TYPE_CHECKING:
    import pandas as pd


def _filter_params(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


class QuotationAPI(_SyncAPIResource):
    def get_tickers(self, markets: str) -> list[Ticker]:
        params = {"markets": markets}
        response = self._transport.request("GET", "/v1/ticker", params=params)
        return [Ticker.model_validate(item) for item in response.data]

    def get_tickers_by_quote(self, quote_currencies: str) -> list[Ticker]:
        params = {"quote_currencies": quote_currencies}
        response = self._transport.request("GET", "/v1/ticker/all", params=params)
        return [Ticker.model_validate(item) for item in response.data]

    def get_candles_minutes(
        self,
        *,
        market: str,
        unit: Literal[1, 3, 5, 10, 15, 30, 60, 240],
        to: str | None = None,
        count: int | None = None,
    ) -> list[CandleMinute]:
        params = _filter_params(market=market, to=to, count=count)
        response = self._transport.request(
            "GET", f"/v1/candles/minutes/{unit}", params=params
        )
        return [CandleMinute.model_validate(item) for item in response.data]

    def get_candles_seconds(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> list[CandleSecond]:
        params = _filter_params(market=market, to=to, count=count)
        response = self._transport.request("GET", "/v1/candles/seconds", params=params)
        return [CandleSecond.model_validate(item) for item in response.data]

    def get_candles_days(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
        converting_price_unit: str | None = None,
    ) -> list[CandleDay]:
        params = _filter_params(
            market=market,
            to=to,
            count=count,
            converting_price_unit=converting_price_unit,
        )
        response = self._transport.request("GET", "/v1/candles/days", params=params)
        return [CandleDay.model_validate(item) for item in response.data]

    def get_candles_weeks(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> list[CandlePeriod]:
        params = _filter_params(market=market, to=to, count=count)
        response = self._transport.request("GET", "/v1/candles/weeks", params=params)
        return [CandlePeriod.model_validate(item) for item in response.data]

    def get_candles_months(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> list[CandlePeriod]:
        params = _filter_params(market=market, to=to, count=count)
        response = self._transport.request("GET", "/v1/candles/months", params=params)
        return [CandlePeriod.model_validate(item) for item in response.data]

    def get_candles_years(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> list[CandlePeriod]:
        params = _filter_params(market=market, to=to, count=count)
        response = self._transport.request("GET", "/v1/candles/years", params=params)
        return [CandlePeriod.model_validate(item) for item in response.data]

    def get_candles_minutes_df(
        self,
        *,
        market: str,
        unit: Literal[1, 3, 5, 10, 15, 30, 60, 240],
        to: str | None = None,
        count: int | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            self.get_candles_minutes(market=market, unit=unit, to=to, count=count)
        )

    def get_candles_seconds_df(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            self.get_candles_seconds(market=market, to=to, count=count)
        )

    def get_candles_days_df(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
        converting_price_unit: str | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            self.get_candles_days(
                market=market,
                to=to,
                count=count,
                converting_price_unit=converting_price_unit,
            )
        )

    def get_candles_weeks_df(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            self.get_candles_weeks(market=market, to=to, count=count)
        )

    def get_candles_months_df(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            self.get_candles_months(market=market, to=to, count=count)
        )

    def get_candles_years_df(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            self.get_candles_years(market=market, to=to, count=count)
        )

    def get_orderbooks(
        self,
        markets: str,
        *,
        level: str | None = None,
        count: int | None = None,
    ) -> list[Orderbook]:
        params = _filter_params(markets=markets, level=level, count=count)
        response = self._transport.request("GET", "/v1/orderbook", params=params)
        return [Orderbook.model_validate(item) for item in response.data]

    def get_orderbook_instruments(self, markets: str) -> list[OrderbookInstrument]:
        params = {"markets": markets}
        response = self._transport.request(
            "GET", "/v1/orderbook/instruments", params=params
        )
        return [OrderbookInstrument.model_validate(item) for item in response.data]

    def get_trades(
        self,
        market: str,
        *,
        to: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        days_ago: int | None = None,
    ) -> list[Trade]:
        params = _filter_params(
            market=market, to=to, count=count, cursor=cursor, days_ago=days_ago
        )
        response = self._transport.request("GET", "/v1/trades/ticks", params=params)
        return [Trade.model_validate(item) for item in response.data]


class AsyncQuotationAPI(_AsyncAPIResource):
    async def get_tickers(self, markets: str) -> list[Ticker]:
        params = {"markets": markets}
        response = await self._transport.request("GET", "/v1/ticker", params=params)
        return [Ticker.model_validate(item) for item in response.data]

    async def get_tickers_by_quote(self, quote_currencies: str) -> list[Ticker]:
        params = {"quote_currencies": quote_currencies}
        response = await self._transport.request("GET", "/v1/ticker/all", params=params)
        return [Ticker.model_validate(item) for item in response.data]

    async def get_candles_minutes(
        self,
        *,
        market: str,
        unit: Literal[1, 3, 5, 10, 15, 30, 60, 240],
        to: str | None = None,
        count: int | None = None,
    ) -> list[CandleMinute]:
        params = _filter_params(market=market, to=to, count=count)
        response = await self._transport.request(
            "GET", f"/v1/candles/minutes/{unit}", params=params
        )
        return [CandleMinute.model_validate(item) for item in response.data]

    async def get_candles_seconds(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> list[CandleSecond]:
        params = _filter_params(market=market, to=to, count=count)
        response = await self._transport.request(
            "GET", "/v1/candles/seconds", params=params
        )
        return [CandleSecond.model_validate(item) for item in response.data]

    async def get_candles_days(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
        converting_price_unit: str | None = None,
    ) -> list[CandleDay]:
        params = _filter_params(
            market=market,
            to=to,
            count=count,
            converting_price_unit=converting_price_unit,
        )
        response = await self._transport.request(
            "GET", "/v1/candles/days", params=params
        )
        return [CandleDay.model_validate(item) for item in response.data]

    async def get_candles_weeks(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> list[CandlePeriod]:
        params = _filter_params(market=market, to=to, count=count)
        response = await self._transport.request(
            "GET", "/v1/candles/weeks", params=params
        )
        return [CandlePeriod.model_validate(item) for item in response.data]

    async def get_candles_months(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> list[CandlePeriod]:
        params = _filter_params(market=market, to=to, count=count)
        response = await self._transport.request(
            "GET", "/v1/candles/months", params=params
        )
        return [CandlePeriod.model_validate(item) for item in response.data]

    async def get_candles_years(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> list[CandlePeriod]:
        params = _filter_params(market=market, to=to, count=count)
        response = await self._transport.request(
            "GET", "/v1/candles/years", params=params
        )
        return [CandlePeriod.model_validate(item) for item in response.data]

    async def get_candles_minutes_df(
        self,
        *,
        market: str,
        unit: Literal[1, 3, 5, 10, 15, 30, 60, 240],
        to: str | None = None,
        count: int | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            await self.get_candles_minutes(
                market=market,
                unit=unit,
                to=to,
                count=count,
            )
        )

    async def get_candles_seconds_df(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            await self.get_candles_seconds(market=market, to=to, count=count)
        )

    async def get_candles_days_df(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
        converting_price_unit: str | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            await self.get_candles_days(
                market=market,
                to=to,
                count=count,
                converting_price_unit=converting_price_unit,
            )
        )

    async def get_candles_weeks_df(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            await self.get_candles_weeks(market=market, to=to, count=count)
        )

    async def get_candles_months_df(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            await self.get_candles_months(market=market, to=to, count=count)
        )

    async def get_candles_years_df(
        self,
        *,
        market: str,
        to: str | None = None,
        count: int | None = None,
    ) -> pd.DataFrame:
        return candles_to_dataframe(
            await self.get_candles_years(market=market, to=to, count=count)
        )

    async def get_orderbooks(
        self,
        markets: str,
        *,
        level: str | None = None,
        count: int | None = None,
    ) -> list[Orderbook]:
        params = _filter_params(markets=markets, level=level, count=count)
        response = await self._transport.request("GET", "/v1/orderbook", params=params)
        return [Orderbook.model_validate(item) for item in response.data]

    async def get_orderbook_instruments(
        self, markets: str
    ) -> list[OrderbookInstrument]:
        params = {"markets": markets}
        response = await self._transport.request(
            "GET", "/v1/orderbook/instruments", params=params
        )
        return [OrderbookInstrument.model_validate(item) for item in response.data]

    async def get_trades(
        self,
        market: str,
        *,
        to: str | None = None,
        count: int | None = None,
        cursor: str | None = None,
        days_ago: int | None = None,
    ) -> list[Trade]:
        params = _filter_params(
            market=market, to=to, count=count, cursor=cursor, days_ago=days_ago
        )
        response = await self._transport.request(
            "GET", "/v1/trades/ticks", params=params
        )
        return [Trade.model_validate(item) for item in response.data]
