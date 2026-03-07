from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MarketCaution(BaseModel):
    model_config = ConfigDict(frozen=True)

    PRICE_FLUCTUATIONS: bool = False
    TRADING_VOLUME_SOARING: bool = False
    DEPOSIT_AMOUNT_SOARING: bool = False
    GLOBAL_PRICE_DIFFERENCES: bool = False
    CONCENTRATION_OF_SMALL_ACCOUNTS: bool = False


class MarketEvent(BaseModel):
    model_config = ConfigDict(frozen=True)

    warning: bool
    caution: MarketCaution


class TradingPair(BaseModel):
    model_config = ConfigDict(frozen=True)

    market: str
    korean_name: str
    english_name: str
    market_event: MarketEvent | None = None
