"""Entry-point helper to run the Lynch strategy backtest for both markets."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
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


def _save_monthly_chart(result, output_dir: Path | None = None) -> Path:
    """Render the monthly annualized return chart for ``result``."""

    output_dir = output_dir or Path("charts")
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{result.market.lower()}_monthly_annualized.svg"

    dates = [point[0] for point in result.monthly_annualized]
    rates = [point[1] * 100.0 for point in result.monthly_annualized]
    start = dates[0]
    end = dates[-1]

    width, height = 1000, 600
    margin_x, margin_y = 80, 70
    plot_width = width - 2 * margin_x
    plot_height = height - 2 * margin_y

    min_rate = min(rates + [0.0])
    max_rate = max(rates + [0.0])
    if max_rate - min_rate < 1e-6:
        max_rate += 1.0
        min_rate -= 1.0

    def _scale_x(date: datetime) -> float:
        total = (end - start).days or 1
        return margin_x + ((date - start).days / total) * plot_width

    def _scale_y(rate: float) -> float:
        return margin_y + (max_rate - rate) / (max_rate - min_rate) * plot_height

    path_commands = []
    for idx, (date, rate) in enumerate(zip(dates, rates)):
        x = _scale_x(date)
        y = _scale_y(rate)
        command = "M" if idx == 0 else "L"
        path_commands.append(f"{command}{x:.2f},{y:.2f}")

    year_ticks = sorted({date.year for date in dates})
    tick_elements = []
    for year in year_ticks:
        tick_date = datetime(year, 12, 31)
        if tick_date < start:
            tick_date = datetime(year, 1, 1)
        if tick_date > end:
            tick_date = end
        x = _scale_x(tick_date)
        tick_elements.append(
            f'<line x1="{x:.2f}" y1="{height - margin_y}" x2="{x:.2f}" y2="{height - margin_y + 10}" stroke="#444" stroke-width="1" />'
        )
        tick_elements.append(
            f'<text x="{x:.2f}" y="{height - margin_y + 30}" font-size="18" text-anchor="middle" fill="#444">{year}</text>'
        )

    horizontal_ticks = []
    for step in range(5):
        ratio = step / 4
        rate = max_rate - (max_rate - min_rate) * ratio
        y = _scale_y(rate)
        horizontal_ticks.append(
            f'<line x1="{margin_x}" y1="{y:.2f}" x2="{width - margin_x}" y2="{y:.2f}" stroke="#ddd" stroke-width="1" />'
        )
        horizontal_ticks.append(
            f'<text x="{margin_x - 10}" y="{y + 6:.2f}" font-size="18" text-anchor="end" fill="#666">{rate:.1f}%</text>'
        )

    svg_content = f"""
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
  <rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff" />
  <text x="{width/2:.2f}" y="40" font-size="28" text-anchor="middle" fill="#222">
    {result.market} 每月年化收益率
  </text>
  <g>
    {''.join(horizontal_ticks)}
    <line x1="{margin_x}" y1="{margin_y}" x2="{margin_x}" y2="{height - margin_y}" stroke="#444" stroke-width="2" />
    <line x1="{margin_x}" y1="{height - margin_y}" x2="{width - margin_x}" y2="{height - margin_y}" stroke="#444" stroke-width="2" />
    {''.join(tick_elements)}
  </g>
  <path d="{' '.join(path_commands)}" fill="none" stroke="#1f77b4" stroke-width="3" />
  {''.join(
      f'<circle cx="{_scale_x(date):.2f}" cy="{_scale_y(rate):.2f}" r="4" fill="#1f77b4" />'
      for date, rate in zip(dates, rates)
  )}
</svg>
"""

    path.write_text(svg_content, encoding="utf-8")
    return path


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
        chart_path = _save_monthly_chart(result)
        print("Monthly annualized return chart saved to:", chart_path)
        print()


if __name__ == "__main__":
    run_demo()
