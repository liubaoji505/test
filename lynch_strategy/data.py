"""Data loading helpers for the local sample data set."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass(frozen=True)
class FundamentalRecord:
    market: str
    ticker: str
    peg: float
    pe: float
    debt_to_equity: float
    revenue_growth: float
    eps_growth: float
    current_ratio: float
    gross_margin: float
    category: str


@dataclass(frozen=True)
class PriceRecord:
    market: str
    ticker: str
    date: datetime
    close: float


def load_fundamentals() -> Dict[Tuple[str, str], FundamentalRecord]:
    """Load the static fundamental data from ``data/fundamentals.csv``."""

    path = DATA_DIR / "fundamentals.csv"
    fundamentals: Dict[Tuple[str, str], FundamentalRecord] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            record = FundamentalRecord(
                market=row["market"],
                ticker=row["ticker"],
                peg=float(row["peg"]),
                pe=float(row["pe"]),
                debt_to_equity=float(row["debt_to_equity"]),
                revenue_growth=float(row["revenue_growth"]),
                eps_growth=float(row["eps_growth"]),
                current_ratio=float(row["current_ratio"]),
                gross_margin=float(row["gross_margin"]),
                category=row["category"],
            )
            fundamentals[(record.market.upper(), record.ticker)] = record
    return fundamentals


def load_prices() -> Dict[Tuple[str, str], List[PriceRecord]]:
    """Load the price snapshots from ``data/prices.csv``."""

    path = DATA_DIR / "prices.csv"
    prices: Dict[Tuple[str, str], List[PriceRecord]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            record = PriceRecord(
                market=row["market"],
                ticker=row["ticker"],
                date=datetime.strptime(row["date"], "%Y-%m-%d"),
                close=float(row["close"]),
            )
            prices.setdefault((record.market.upper(), record.ticker), []).append(record)

    for key in prices:
        prices[key].sort(key=lambda record: record.date)
    return prices


def list_tickers(prices: Dict[Tuple[str, str], List[PriceRecord]], market: str) -> Iterable[str]:
    """Return the tickers for the requested market contained in ``prices``."""

    market = market.upper()
    for (market_key, ticker), _records in prices.items():
        if market_key == market:
            yield ticker
