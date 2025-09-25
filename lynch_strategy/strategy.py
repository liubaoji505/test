"""Implementation of a quantitative interpretation of Peter Lynch's rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from .criteria import LynchCriteria
from .data import FundamentalRecord


@dataclass
class Evaluation:
    ticker: str
    market: str
    passed: bool
    reasons: Dict[str, float]
    category: str


def evaluate_company(
    record: FundamentalRecord, criteria: LynchCriteria | None = None
) -> Evaluation:
    """Evaluate whether a company satisfies the quantitative Lynch filters."""

    criteria = criteria or LynchCriteria()
    metrics = {
        "peg": record.peg,
        "pe": record.pe,
        "debt_to_equity": record.debt_to_equity,
        "revenue_growth": record.revenue_growth,
        "eps_growth": record.eps_growth,
        "current_ratio": record.current_ratio,
        "gross_margin": record.gross_margin,
    }

    checks = {
        "peg": record.peg <= criteria.max_peg,
        "pe": criteria.min_pe <= record.pe <= criteria.max_pe,
        "debt_to_equity": record.debt_to_equity <= criteria.max_debt_to_equity,
        "revenue_growth": record.revenue_growth >= criteria.min_revenue_growth,
        "eps_growth": record.eps_growth >= criteria.min_eps_growth,
        "current_ratio": record.current_ratio >= criteria.min_current_ratio,
        "gross_margin": record.gross_margin >= criteria.min_gross_margin,
    }

    passed = all(checks.values())
    return Evaluation(
        ticker=record.ticker,
        market=record.market,
        passed=passed,
        reasons=metrics,
        category=record.category,
    )


def summarize_evaluations(
    evaluations: Dict[Tuple[str, str], Evaluation]
) -> Dict[str, Dict[str, float]]:
    """Utility helper for debugging and reporting."""

    summary: Dict[str, Dict[str, float]] = {}
    for (_market, ticker), evaluation in evaluations.items():
        summary[ticker] = evaluation.reasons
        summary[ticker]["passed"] = float(evaluation.passed)
    return summary
