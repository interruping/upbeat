from __future__ import annotations

from tests.conftest import upbeat_vcr
from upbeat import Upbeat
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


def _client() -> Upbeat:
    return Upbeat(max_retries=0, auto_throttle=False)


# ── Tickers ─────────────────────────────────────────────────────────────


class TestGetTickers:
    @upbeat_vcr.use_cassette("quotation/get_tickers.yaml")
    def test_returns_valid_tickers(self) -> None:
        with _client() as client:
            result = client.quotation.get_tickers("KRW-BTC")

        assert len(result) >= 1
        ticker = result[0]
        assert isinstance(ticker, Ticker)
        assert ticker.market == "KRW-BTC"
        assert ticker.change in ("EVEN", "RISE", "FALL")
        assert isinstance(ticker.trade_price, float)
        assert isinstance(ticker.timestamp, int)


class TestGetTickersByQuote:
    @upbeat_vcr.use_cassette("quotation/get_tickers_by_quote.yaml")
    def test_returns_valid_tickers(self) -> None:
        with _client() as client:
            result = client.quotation.get_tickers_by_quote("KRW")

        assert len(result) >= 1
        for ticker in result:
            assert isinstance(ticker, Ticker)
            assert ticker.market.startswith("KRW-")


# ── Candles ─────────────────────────────────────────────────────────────


class TestGetCandlesMinutes:
    @upbeat_vcr.use_cassette("quotation/get_candles_minutes.yaml")
    def test_returns_valid_candles(self) -> None:
        with _client() as client:
            result = client.quotation.get_candles_minutes(market="KRW-BTC", unit=1)

        assert len(result) >= 1
        candle = result[0]
        assert isinstance(candle, CandleMinute)
        assert candle.market == "KRW-BTC"
        assert isinstance(candle.unit, int)
        assert isinstance(candle.opening_price, float)


class TestGetCandlesSeconds:
    @upbeat_vcr.use_cassette("quotation/get_candles_seconds.yaml")
    def test_returns_valid_candles(self) -> None:
        with _client() as client:
            result = client.quotation.get_candles_seconds(market="KRW-BTC")

        assert len(result) >= 1
        candle = result[0]
        assert isinstance(candle, CandleSecond)
        assert candle.market == "KRW-BTC"
        assert isinstance(candle.opening_price, float)


class TestGetCandlesDays:
    @upbeat_vcr.use_cassette("quotation/get_candles_days.yaml")
    def test_returns_valid_candles(self) -> None:
        with _client() as client:
            result = client.quotation.get_candles_days(market="KRW-BTC")

        assert len(result) >= 1
        candle = result[0]
        assert isinstance(candle, CandleDay)
        assert candle.market == "KRW-BTC"
        assert isinstance(candle.prev_closing_price, float)
        assert isinstance(candle.change_price, float)
        assert isinstance(candle.change_rate, float)


class TestGetCandlesWeeks:
    @upbeat_vcr.use_cassette("quotation/get_candles_weeks.yaml")
    def test_returns_valid_candles(self) -> None:
        with _client() as client:
            result = client.quotation.get_candles_weeks(market="KRW-BTC")

        assert len(result) >= 1
        candle = result[0]
        assert isinstance(candle, CandlePeriod)
        assert candle.market == "KRW-BTC"
        assert isinstance(candle.first_day_of_period, str)


class TestGetCandlesMonths:
    @upbeat_vcr.use_cassette("quotation/get_candles_months.yaml")
    def test_returns_valid_candles(self) -> None:
        with _client() as client:
            result = client.quotation.get_candles_months(market="KRW-BTC")

        assert len(result) >= 1
        candle = result[0]
        assert isinstance(candle, CandlePeriod)
        assert candle.market == "KRW-BTC"
        assert isinstance(candle.first_day_of_period, str)


class TestGetCandlesYears:
    @upbeat_vcr.use_cassette("quotation/get_candles_years.yaml")
    def test_returns_valid_candles(self) -> None:
        with _client() as client:
            result = client.quotation.get_candles_years(market="KRW-BTC")

        assert len(result) >= 1
        candle = result[0]
        assert isinstance(candle, CandlePeriod)
        assert candle.market == "KRW-BTC"
        assert isinstance(candle.first_day_of_period, str)


# ── Orderbooks ──────────────────────────────────────────────────────────


class TestGetOrderbooks:
    @upbeat_vcr.use_cassette("quotation/get_orderbooks.yaml")
    def test_returns_valid_orderbooks(self) -> None:
        with _client() as client:
            result = client.quotation.get_orderbooks("KRW-BTC")

        assert len(result) >= 1
        ob = result[0]
        assert isinstance(ob, Orderbook)
        assert ob.market == "KRW-BTC"
        assert len(ob.orderbook_units) >= 1
        unit = ob.orderbook_units[0]
        assert isinstance(unit.ask_price, float)
        assert isinstance(unit.bid_price, float)


class TestGetOrderbookInstruments:
    @upbeat_vcr.use_cassette("quotation/get_orderbook_instruments.yaml")
    def test_returns_valid_instruments(self) -> None:
        with _client() as client:
            result = client.quotation.get_orderbook_instruments("KRW-BTC")

        assert len(result) >= 1
        inst = result[0]
        assert isinstance(inst, OrderbookInstrument)
        assert inst.market == "KRW-BTC"
        assert isinstance(inst.supported_levels, list)


# ── Trades ──────────────────────────────────────────────────────────────


class TestGetTrades:
    @upbeat_vcr.use_cassette("quotation/get_trades.yaml")
    def test_returns_valid_trades(self) -> None:
        with _client() as client:
            result = client.quotation.get_trades("KRW-BTC")

        assert len(result) >= 1
        trade = result[0]
        assert isinstance(trade, Trade)
        assert trade.market == "KRW-BTC"
        assert trade.ask_bid in ("ASK", "BID")
        assert isinstance(trade.trade_price, float)
        assert isinstance(trade.sequential_id, int)
