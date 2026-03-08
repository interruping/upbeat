from __future__ import annotations

from upbeat.strategies._base import (
    AsyncClientProtocol,
    PortfolioItem,
    SyncClientProtocol,
)


def get_portfolio_value(client: SyncClientProtocol) -> float:
    accounts = client.accounts.list()

    krw_total = 0.0
    non_krw = []

    for account in accounts:
        balance = float(account.balance) + float(account.locked)
        if account.currency == "KRW":
            krw_total += balance
        elif balance > 0:
            non_krw.append(account)

    if non_krw:
        markets = ",".join(f"KRW-{a.currency}" for a in non_krw)
        tickers = client.quotation.get_tickers(markets)
        price_map = {t.market: t.trade_price for t in tickers}

        for account in non_krw:
            market = f"KRW-{account.currency}"
            balance = float(account.balance) + float(account.locked)
            price = price_map.get(market, 0.0)
            krw_total += balance * price

    return krw_total


def get_portfolio(client: SyncClientProtocol) -> list[PortfolioItem]:
    accounts = client.accounts.list()

    non_krw = []
    items: list[PortfolioItem] = []

    for account in accounts:
        balance = float(account.balance)
        locked = float(account.locked)
        if account.currency == "KRW":
            items.append(
                PortfolioItem(
                    currency="KRW",
                    balance=balance,
                    locked=locked,
                    current_price=1.0,
                    market="KRW",
                    estimated_value_krw=balance + locked,
                )
            )
        elif balance + locked > 0:
            non_krw.append(account)

    if non_krw:
        markets = ",".join(f"KRW-{a.currency}" for a in non_krw)
        tickers = client.quotation.get_tickers(markets)
        price_map = {t.market: t.trade_price for t in tickers}

        for account in non_krw:
            market = f"KRW-{account.currency}"
            balance = float(account.balance)
            locked = float(account.locked)
            price = price_map.get(market, 0.0)
            items.append(
                PortfolioItem(
                    currency=account.currency,
                    balance=balance,
                    locked=locked,
                    current_price=price,
                    market=market,
                    estimated_value_krw=(balance + locked) * price,
                )
            )

    return items


async def async_get_portfolio_value(client: AsyncClientProtocol) -> float:
    accounts = await client.accounts.list()

    krw_total = 0.0
    non_krw = []

    for account in accounts:
        balance = float(account.balance) + float(account.locked)
        if account.currency == "KRW":
            krw_total += balance
        elif balance > 0:
            non_krw.append(account)

    if non_krw:
        markets = ",".join(f"KRW-{a.currency}" for a in non_krw)
        tickers = await client.quotation.get_tickers(markets)
        price_map = {t.market: t.trade_price for t in tickers}

        for account in non_krw:
            market = f"KRW-{account.currency}"
            balance = float(account.balance) + float(account.locked)
            price = price_map.get(market, 0.0)
            krw_total += balance * price

    return krw_total


async def async_get_portfolio(client: AsyncClientProtocol) -> list[PortfolioItem]:
    accounts = await client.accounts.list()

    non_krw = []
    items: list[PortfolioItem] = []

    for account in accounts:
        balance = float(account.balance)
        locked = float(account.locked)
        if account.currency == "KRW":
            items.append(
                PortfolioItem(
                    currency="KRW",
                    balance=balance,
                    locked=locked,
                    current_price=1.0,
                    market="KRW",
                    estimated_value_krw=balance + locked,
                )
            )
        elif balance + locked > 0:
            non_krw.append(account)

    if non_krw:
        markets = ",".join(f"KRW-{a.currency}" for a in non_krw)
        tickers = await client.quotation.get_tickers(markets)
        price_map = {t.market: t.trade_price for t in tickers}

        for account in non_krw:
            market = f"KRW-{account.currency}"
            balance = float(account.balance)
            locked = float(account.locked)
            price = price_map.get(market, 0.0)
            items.append(
                PortfolioItem(
                    currency=account.currency,
                    balance=balance,
                    locked=locked,
                    current_price=price,
                    market=market,
                    estimated_value_krw=(balance + locked) * price,
                )
            )

    return items
