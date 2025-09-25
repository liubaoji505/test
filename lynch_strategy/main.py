"""Entry-point helper to run the Lynch strategy backtest for both markets."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .backtest import BacktestError, run_backtest_for_market
from .criteria import LynchCriteria


def _format_currency(value: float) -> str:
    return f"${value:,.2f}"


def _describe_selection(result) -> str:
    details = []
    for ticker in result.selected:
        evaluation = result.evaluations[ticker]
        details.append(
            f"  - {ticker}: PEG={evaluation.reasons['peg']:.2f}, "
            f"PE={evaluation.reasons['pe']:.2f}, Debt/Equity={evaluation.reasons['debt_to_equity']:.2f}, "
            f"Revenue growth={evaluation.reasons['revenue_growth']:.2%}, "
            f"EPS growth={evaluation.reasons['eps_growth']:.2%}"
        )
    return "\n".join(details)


def run_demo(markets: Iterable[str] | None = None) -> None:
    markets = markets or ("US", "CN")
    criteria = LynchCriteria()
    start = datetime(2020, 1, 2)
    end = datetime(2024, 12, 31)

    for market in markets:
        print(f"=== Market: {market} ===")
        try:
            result = run_backtest_for_market(market, start, end, 1_000_000.0, criteria)
        except BacktestError as exc:
            print(f"Backtest failed: {exc}")
            continue

        print(f"Selected tickers ({len(result.selected)}): {', '.join(result.selected)}")
        print(_describe_selection(result))
        print(
            "Final value:",
            _format_currency(result.final_value),
            "Total return:",
            f"{result.total_return:.2%}",
        )
        print(
            "Annualized return:",
            f"{result.annualized_return:.2%}",
            "over",
            f"{len(result.timeline)} valuation points",
        )
        print()


if __name__ == "__main__":
    run_demo()
