from __future__ import annotations

from typing import Any

import httpx
import pytest

from upbeat._constants import API_BASE_URL
from upbeat._http import AsyncTransport, SyncTransport
from upbeat.api.quotation import AsyncQuotationAPI, QuotationAPI
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

# ── Helpers ──────────────────────────────────────────────────────────────


def _make_transport(handler: Any, **kwargs: Any) -> SyncTransport:
    client = httpx.Client(
        transport=httpx.MockTransport(handler), base_url=API_BASE_URL
    )
    return SyncTransport(http_client=client, **kwargs)


def _make_async_transport(handler: Any, **kwargs: Any) -> AsyncTransport:
    client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url=API_BASE_URL
    )
    return AsyncTransport(http_client=client, **kwargs)


def _json_response(
    data: Any,
    status_code: int = 200,
    remaining_req: str | None = None,
) -> httpx.Response:
    headers = {}
    if remaining_req:
        headers["Remaining-Req"] = remaining_req
    return httpx.Response(status_code, json=data, headers=headers)


# ── Fixture data ─────────────────────────────────────────────────────────


TICKER_DATA = {
    "market": "KRW-BTC",
    "trade_date": "20250704",
    "trade_time": "051400",
    "trade_date_kst": "20250704",
    "trade_time_kst": "141400",
    "trade_timestamp": 1751606040365,
    "opening_price": 148737000.0,
    "high_price": 149360000.0,
    "low_price": 148288000.0,
    "trade_price": 148601000.0,
    "prev_closing_price": 148737000.0,
    "change": "FALL",
    "change_price": 136000.0,
    "change_rate": 0.0009143656,
    "signed_change_price": -136000.0,
    "signed_change_rate": -0.0009143656,
    "trade_volume": 0.00016823,
    "acc_trade_price": 31615925234.05438,
    "acc_trade_price_24h": 178448329314.96686,
    "acc_trade_volume": 212.38911576,
    "acc_trade_volume_24h": 1198.26954807,
    "highest_52_week_price": 163325000.0,
    "highest_52_week_date": "2025-01-20",
    "lowest_52_week_price": 72100000.0,
    "lowest_52_week_date": "2024-08-05",
    "timestamp": 1751606040403,
}

CANDLE_BASE_DATA = {
    "market": "KRW-BTC",
    "candle_date_time_utc": "2025-07-01T12:00:00",
    "candle_date_time_kst": "2025-07-01T21:00:00",
    "opening_price": 145831000.0,
    "high_price": 145831000.0,
    "low_price": 145752000.0,
    "trade_price": 145759000.0,
    "timestamp": 1751327999833,
    "candle_acc_trade_price": 4022470467.03403,
    "candle_acc_trade_volume": 27.58904602,
}

CANDLE_MINUTE_DATA = {**CANDLE_BASE_DATA, "unit": 1}

CANDLE_DAY_DATA = {
    **CANDLE_BASE_DATA,
    "prev_closing_price": 147996000.0,
    "change_price": -2237000.0,
    "change_rate": -0.0151152734,
}

CANDLE_PERIOD_DATA = {**CANDLE_BASE_DATA, "first_day_of_period": "2025-06-30"}

ORDERBOOK_UNIT_DATA = {
    "ask_price": 148520000.0,
    "bid_price": 148490000.0,
    "ask_size": 0.0134662,
    "bid_size": 0.04296774,
}

ORDERBOOK_DATA = {
    "market": "KRW-BTC",
    "timestamp": 1751606867762,
    "total_ask_size": 10.37591054,
    "total_bid_size": 9.49577219,
    "orderbook_units": [ORDERBOOK_UNIT_DATA],
    "level": 10000.0,
}

ORDERBOOK_INSTRUMENT_DATA = {
    "market": "KRW-BTC",
    "quote_currency": "KRW",
    "tick_size": "1000",
    "supported_levels": ["0", "10000", "100000"],
}

TRADE_DATA = {
    "market": "KRW-BTC",
    "trade_date_utc": "2025-06-27",
    "trade_time_utc": "23:59:59",
    "timestamp": 1751068799336,
    "trade_price": 147058000.0,
    "trade_volume": 0.00006043,
    "prev_closing_price": 146852000.0,
    "change_price": 206000.0,
    "ask_bid": "BID",
    "sequential_id": 17510687993360000,
}


# ── TestGetTickers ───────────────────────────────────────────────────────


class TestGetTickers:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/ticker"
            assert request.url.params["markets"] == "KRW-BTC,KRW-ETH"
            return _json_response([TICKER_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = api.get_tickers("KRW-BTC,KRW-ETH")
        assert len(result) == 1
        assert isinstance(result[0], Ticker)
        assert result[0].market == "KRW-BTC"

    def test_no_authorization_header(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "Authorization" not in request.headers
            return _json_response([TICKER_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        api.get_tickers("KRW-BTC")

    def test_parses_ticker_fields(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([TICKER_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        ticker = api.get_tickers("KRW-BTC")[0]
        assert ticker.change == "FALL"
        assert ticker.trade_timestamp == 1751606040365
        assert ticker.highest_52_week_date == "2025-01-20"


# ── TestGetTickersByQuote ────────────────────────────────────────────────


class TestGetTickersByQuote:
    def test_calls_correct_endpoint(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/ticker/all"
            assert request.url.params["quote_currencies"] == "KRW,BTC"
            return _json_response([TICKER_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = api.get_tickers_by_quote("KRW,BTC")
        assert len(result) == 1
        assert isinstance(result[0], Ticker)


# ── TestGetCandlesMinutes ────────────────────────────────────────────────


class TestGetCandlesMinutes:
    def test_path_includes_unit(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/candles/minutes/5"
            assert request.url.params["market"] == "KRW-BTC"
            return _json_response([CANDLE_MINUTE_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = api.get_candles_minutes(market="KRW-BTC", unit=5)
        assert len(result) == 1
        assert isinstance(result[0], CandleMinute)
        assert result[0].unit == 1

    def test_optional_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["to"] == "2025-07-01T00:00:00Z"
            assert request.url.params["count"] == "10"
            return _json_response([CANDLE_MINUTE_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        api.get_candles_minutes(
            market="KRW-BTC", unit=1, to="2025-07-01T00:00:00Z", count=10
        )

    def test_none_params_excluded(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert "to" not in request.url.params
            assert "count" not in request.url.params
            return _json_response([CANDLE_MINUTE_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        api.get_candles_minutes(market="KRW-BTC", unit=1)


# ── TestGetCandlesSeconds ────────────────────────────────────────────────


class TestGetCandlesSeconds:
    def test_basic_call(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/candles/seconds"
            return _json_response([CANDLE_BASE_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = api.get_candles_seconds(market="KRW-BTC")
        assert len(result) == 1
        assert isinstance(result[0], CandleSecond)


# ── TestGetCandlesDays ───────────────────────────────────────────────────


class TestGetCandlesDays:
    def test_basic_call(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/candles/days"
            return _json_response([CANDLE_DAY_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = api.get_candles_days(market="KRW-BTC")
        assert len(result) == 1
        assert isinstance(result[0], CandleDay)
        assert result[0].prev_closing_price == 147996000.0

    def test_converting_price_unit(self) -> None:
        data = {**CANDLE_DAY_DATA, "converted_trade_price": 145759000.0}

        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["converting_price_unit"] == "KRW"
            return _json_response([data])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = api.get_candles_days(
            market="KRW-BTC", converting_price_unit="KRW"
        )
        assert result[0].converted_trade_price == 145759000.0

    def test_converted_trade_price_optional(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([CANDLE_DAY_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = api.get_candles_days(market="KRW-BTC")
        assert result[0].converted_trade_price is None


# ── TestGetCandlesPeriod ─────────────────────────────────────────────────


class TestGetCandlesPeriod:
    @pytest.mark.parametrize(
        "method,path",
        [
            ("get_candles_weeks", "/v1/candles/weeks"),
            ("get_candles_months", "/v1/candles/months"),
            ("get_candles_years", "/v1/candles/years"),
        ],
    )
    def test_period_candles(self, method: str, path: str) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == path
            return _json_response([CANDLE_PERIOD_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = getattr(api, method)(market="KRW-BTC")
        assert len(result) == 1
        assert isinstance(result[0], CandlePeriod)
        assert result[0].first_day_of_period == "2025-06-30"


# ── TestGetOrderbooks ────────────────────────────────────────────────────


class TestGetOrderbooks:
    def test_basic_call(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orderbook"
            assert request.url.params["markets"] == "KRW-BTC"
            return _json_response([ORDERBOOK_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = api.get_orderbooks("KRW-BTC")
        assert len(result) == 1
        assert isinstance(result[0], Orderbook)
        assert len(result[0].orderbook_units) == 1
        assert result[0].orderbook_units[0].ask_price == 148520000.0

    def test_level_and_count_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["level"] == "100000"
            assert request.url.params["count"] == "15"
            return _json_response([ORDERBOOK_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        api.get_orderbooks("KRW-BTC", level="100000", count=15)


# ── TestGetOrderbookInstruments ──────────────────────────────────────────


class TestGetOrderbookInstruments:
    def test_basic_call(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/orderbook/instruments"
            return _json_response([ORDERBOOK_INSTRUMENT_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = api.get_orderbook_instruments("KRW-BTC")
        assert len(result) == 1
        assert isinstance(result[0], OrderbookInstrument)
        assert result[0].supported_levels == ["0", "10000", "100000"]


# ── TestGetTrades ────────────────────────────────────────────────────────


class TestGetTrades:
    def test_basic_call(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/trades/ticks"
            assert request.url.params["market"] == "KRW-BTC"
            return _json_response([TRADE_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        result = api.get_trades("KRW-BTC")
        assert len(result) == 1
        assert isinstance(result[0], Trade)
        assert result[0].ask_bid == "BID"
        assert result[0].sequential_id == 17510687993360000

    def test_optional_params(self) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.params["cursor"] == "12345"
            assert request.url.params["days_ago"] == "3"
            return _json_response([TRADE_DATA])

        transport = _make_transport(handler)
        api = QuotationAPI(transport, None)
        api.get_trades("KRW-BTC", cursor="12345", days_ago=3)


# ── TestAsyncQuotation ───────────────────────────────────────────────────


class TestAsyncQuotation:
    @pytest.mark.asyncio
    async def test_get_tickers(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            assert request.url.path == "/v1/ticker"
            return _json_response([TICKER_DATA])

        transport = _make_async_transport(handler)
        api = AsyncQuotationAPI(transport, None)
        result = await api.get_tickers("KRW-BTC")
        assert len(result) == 1
        assert isinstance(result[0], Ticker)

    @pytest.mark.asyncio
    async def test_get_candles_minutes(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([CANDLE_MINUTE_DATA])

        transport = _make_async_transport(handler)
        api = AsyncQuotationAPI(transport, None)
        result = await api.get_candles_minutes(market="KRW-BTC", unit=1)
        assert len(result) == 1
        assert isinstance(result[0], CandleMinute)

    @pytest.mark.asyncio
    async def test_get_orderbooks(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([ORDERBOOK_DATA])

        transport = _make_async_transport(handler)
        api = AsyncQuotationAPI(transport, None)
        result = await api.get_orderbooks("KRW-BTC")
        assert len(result) == 1
        assert isinstance(result[0], Orderbook)

    @pytest.mark.asyncio
    async def test_get_trades(self) -> None:
        async def handler(request: httpx.Request) -> httpx.Response:
            return _json_response([TRADE_DATA])

        transport = _make_async_transport(handler)
        api = AsyncQuotationAPI(transport, None)
        result = await api.get_trades("KRW-BTC")
        assert len(result) == 1
        assert isinstance(result[0], Trade)
