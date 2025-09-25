"""Backtesting helpers for the Lynch-inspired quantitative screen."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Sequence, Tuple

from .criteria import LynchCriteria
from .data import FundamentalRecord, PriceRecord, load_fundamentals, load_prices
from .strategy import Evaluation, evaluate_company


@dataclass
class BacktestResult:
    market: str
    selected: List[str]
    initial_capital: float
    final_value: float
    total_return: float
    annualized_return: float
    timeline: List[Tuple[datetime, float]]
    evaluations: Dict[str, Evaluation]
    criteria: LynchCriteria


class BacktestError(RuntimeError):
    """Raised when a backtest cannot be executed because of missing data."""


def _select_companies(
    market: str,
    fundamentals: Dict[Tuple[str, str], FundamentalRecord],
    criteria: LynchCriteria,
) -> Dict[str, Evaluation]:
    evaluations: Dict[str, Evaluation] = {}
    for (market_key, ticker), record in fundamentals.items():
        if market_key != market.upper():
            continue
        evaluation = evaluate_company(record, criteria)
        if evaluation.passed:
            evaluations[ticker] = evaluation
    return evaluations


def _find_entry_exit(
    prices: Sequence[PriceRecord], start: datetime, end: datetime
) -> Tuple[PriceRecord, PriceRecord]:
    entries = [price for price in prices if price.date >= start]
    exits = [price for price in prices if price.date <= end]
    if not entries or not exits:
        raise BacktestError("Insufficient price data for the requested window.")
    return entries[0], exits[-1]


def _build_timeline(
    price_map: Dict[str, Sequence[PriceRecord]],
    holdings: Dict[str, float],
    start: datetime,
    end: datetime,
) -> List[Tuple[datetime, float]]:
    dates: List[datetime] = sorted(
        {
            price.date
            for ticker in holdings
            for price in price_map[ticker]
            if start <= price.date <= end
        }
    )
    timeline: List[Tuple[datetime, float]] = []
    for date in dates:
        value = 0.0
        for ticker, shares in holdings.items():
            prices = [record for record in price_map[ticker] if record.date == date]
            if prices:
                value += shares * prices[0].close
        timeline.append((date, value))
    return timeline


def run_backtest_for_market(
    market: str,
    start: datetime,
    end: datetime,
    initial_capital: float = 1_000_000.0,
    criteria: LynchCriteria | None = None,
) -> BacktestResult:
    """Run the Lynch screen on the provided market and compute performance."""

    criteria = criteria or LynchCriteria()
    fundamentals = load_fundamentals()
    prices = load_prices()

    evaluations = _select_companies(market, fundamentals, criteria)
    if not evaluations:
        raise BacktestError(f"No companies satisfied the criteria for market {market}.")

    price_map: Dict[str, Sequence[PriceRecord]] = {}
    for ticker in evaluations:
        key = (market.upper(), ticker)
        series = prices.get(key)
        if not series:
            raise BacktestError(f"Missing price data for {ticker} in market {market}.")
        price_map[ticker] = [record for record in series if start <= record.date <= end]
        if len(price_map[ticker]) < 2:
            raise BacktestError(
                f"Not enough price snapshots for {ticker} between {start:%Y-%m-%d} and {end:%Y-%m-%d}."
            )

    equal_allocation = initial_capital / len(evaluations)
    holdings: Dict[str, float] = {}
    final_value = 0.0
    max_end_date = start
    for ticker, series in price_map.items():
        entry, exit_ = _find_entry_exit(series, start, end)
        shares = equal_allocation / entry.close
        holdings[ticker] = shares
        position_final = shares * exit_.close
        final_value += position_final
        if exit_.date > max_end_date:
            max_end_date = exit_.date

    total_return = (final_value - initial_capital) / initial_capital
    years = (max_end_date - start).days / 365.25
    annualized_return = (1.0 + total_return) ** (1.0 / years) - 1.0 if years > 0 else 0.0

    timeline = _build_timeline(price_map, holdings, start, end)

    return BacktestResult(
        market=market.upper(),
        selected=sorted(evaluations),
        initial_capital=initial_capital,
        final_value=final_value,
        total_return=total_return,
        annualized_return=annualized_return,
        timeline=timeline,
        evaluations=evaluations,
        criteria=criteria,
    )
