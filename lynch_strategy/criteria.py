"""Definitions of the quantitative filters inspired by Peter Lynch."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LynchCriteria:
    """Container describing the filtering thresholds.

    The defaults reflect a conservative interpretation of Lynch's preferences for
    profitable companies with sustainable growth at reasonable prices.
    """

    max_peg: float = 1.5
    max_debt_to_equity: float = 0.5
    max_pe: float = 35.0
    min_pe: float = 5.0
    min_revenue_growth: float = 0.08
    min_eps_growth: float = 0.10
    min_current_ratio: float = 1.2
    min_gross_margin: float = 0.25

    def as_dict(self) -> dict[str, float]:
        """Return the criteria as a dictionary for serialization/reporting."""

        return {
            "max_peg": self.max_peg,
            "max_debt_to_equity": self.max_debt_to_equity,
            "max_pe": self.max_pe,
            "min_pe": self.min_pe,
            "min_revenue_growth": self.min_revenue_growth,
            "min_eps_growth": self.min_eps_growth,
            "min_current_ratio": self.min_current_ratio,
            "min_gross_margin": self.min_gross_margin,
        }
