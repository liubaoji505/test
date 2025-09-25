"""Utilities for quantifying Peter Lynch's investment strategy."""

from .criteria import LynchCriteria
from .strategy import evaluate_company
from .backtest import BacktestResult, run_backtest_for_market

__all__ = [
    "LynchCriteria",
    "evaluate_company",
    "BacktestResult",
    "run_backtest_for_market",
]
