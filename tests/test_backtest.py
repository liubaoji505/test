from datetime import datetime

import pytest

from lynch_strategy.backtest import BacktestError, run_backtest_for_market


@pytest.fixture(scope="module")
def period():
    return datetime(2020, 1, 2), datetime(2024, 12, 31)


def test_us_backtest_selection_and_returns(period):
    start, end = period
    result = run_backtest_for_market("US", start, end)
    assert result.selected == ["DLTR", "NVR"]
    assert pytest.approx(result.final_value, rel=1e-9) == 1_832_539.6825396826
    assert pytest.approx(result.total_return, rel=1e-9) == 0.8325396825396826
    assert pytest.approx(result.annualized_return, rel=1e-9) == 0.12887722758928866


def test_cn_backtest_selection_and_returns(period):
    start, end = period
    result = run_backtest_for_market("CN", start, end)
    assert result.selected == ["000333.SZ", "002594.SZ", "600519.SS"]
    assert pytest.approx(result.final_value, rel=1e-9) == 2_220_536.7539203675
    assert pytest.approx(result.total_return, rel=1e-9) == 1.2205367539203675
    assert pytest.approx(result.annualized_return, rel=1e-9) == 0.17311085437996887


def test_backtest_requires_candidates(period):
    start, end = period
    with pytest.raises(BacktestError):
        run_backtest_for_market("JP", start, end)
