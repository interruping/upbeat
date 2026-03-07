from decimal import ROUND_DOWN, Decimal
from enum import StrEnum

API_BASE_URL = "https://api.upbit.com"

# ── KRW tick size table ──────────────────────────────────────────────────

_KRW_TICK_TABLE: list[tuple[Decimal, Decimal]] = [
    (Decimal("2_000_000"), Decimal("1000")),
    (Decimal("1_000_000"), Decimal("500")),
    (Decimal("500_000"), Decimal("100")),
    (Decimal("100_000"), Decimal("50")),
    (Decimal("10_000"), Decimal("10")),
    (Decimal("1_000"), Decimal("5")),
    (Decimal("100"), Decimal("1")),
    (Decimal("10"), Decimal("0.1")),
    (Decimal("1"), Decimal("0.01")),
]

_KRW_TICK_DEFAULT = Decimal("0.001")


def get_krw_tick_size(price: Decimal) -> Decimal:
    for threshold, tick_size in _KRW_TICK_TABLE:
        if price >= threshold:
            return tick_size
    return _KRW_TICK_DEFAULT


def round_to_tick(price: Decimal) -> Decimal:
    tick = get_krw_tick_size(price)
    return (price / tick).to_integral_value(rounding=ROUND_DOWN) * tick


# ── StrEnum constants ────────────────────────────────────────────────────


class OrderSide(StrEnum):
    BID = "bid"
    ASK = "ask"


class OrderType(StrEnum):
    LIMIT = "limit"
    PRICE = "price"
    MARKET = "market"
    BEST = "best"


class OrderState(StrEnum):
    WAIT = "wait"
    WATCH = "watch"
    DONE = "done"
    CANCEL = "cancel"


class TimeInForce(StrEnum):
    IOC = "ioc"
    FOK = "fok"


class MarketState(StrEnum):
    ACTIVE = "active"


class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"
