import numpy as np
import pandas as pd
import pytest
from src.analysis import (
    build_beta_heatmap,
    build_stress_index,
    calculate_bond_portfolio_loss,
    calculate_correlation_matrix,
    calculate_cross_correlation,
    calculate_drawdown,
    calculate_irf,
    calculate_liquidity_proxy,
    calculate_recursive_ols,
    calculate_returns,
    calculate_rolling_beta,
    check_stationarity,
    classify_channel_state,
    detect_monetary_regimes,
    estimate_var_forecast,
    event_study_car,
    rolling_zscore,
    run_monte_carlo_simulation,
    run_ols_regression,
)

...


def test_calculate_recursive_ols():
    x = np.linspace(0, 10, 100)
    y = 2 * x + np.random.normal(0, 0.1, 100)
    df = pd.DataFrame({"y": y, "x": x})
    betas, se = calculate_recursive_ols(df, "y", "x")
    assert len(betas) == 100
    assert betas.iloc[-1] == pytest.approx(2, rel=0.1)


def test_run_monte_carlo_simulation():
    res = run_monte_carlo_simulation(0.05, 0.5, 10000, 10, trials=100)
    assert len(res) == 100
    assert np.all(res >= 0)


def test_run_ols_regression():
    # Generate dummy data
    x = np.linspace(0, 10, 100)
    y = 2 * x + np.random.normal(0, 1, 100)
    df = pd.DataFrame({"y": y, "x": x})

    results = run_ols_regression(df, "y", "x")
    assert results.params["x"] == pytest.approx(2, rel=0.1)
    assert results.rsquared > 0.8


def test_check_stationarity():
    # Linear trend is non-stationary
    np.random.seed(42)
    t = np.linspace(0, 1, 1000)
    series = 5 * t + np.random.normal(0, 0.1, 1000)
    p_value = check_stationarity(pd.Series(series))
    assert p_value > 0.05


def test_calculate_rolling_beta():
    # Dummy returns
    np.random.seed(42)
    x = np.random.normal(0.001, 0.02, 500)
    y = 0.5 * x + np.random.normal(0, 0.005, 500)
    df = pd.DataFrame({"y": y, "x": x})

    rolling = calculate_rolling_beta(df, "y", "x", window=100)
    assert len(rolling) == 500
    assert rolling.iloc[-1] == pytest.approx(0.5, rel=0.2)


def test_estimate_var_forecast():
    # Generate 2 correlated AR(1) processes
    np.random.seed(42)
    n = 100
    x = np.zeros(n)
    y = np.zeros(n)
    for t in range(1, n):
        x[t] = 0.5 * x[t - 1] + np.random.normal(0, 0.1)
        y[t] = 0.3 * y[t - 1] + 0.2 * x[t - 1] + np.random.normal(0, 0.1)

    df = pd.DataFrame({"A": x, "B": y})

    forecast = estimate_var_forecast(df, steps=5)
    assert forecast.shape == (5, 2)


def test_calculate_correlation_matrix():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [3, 2, 1]})
    corr = calculate_correlation_matrix(df)
    assert corr.loc["A", "B"] == pytest.approx(-1.0)


def test_calculate_cross_correlation():
    s1 = pd.Series([1, 2, 3, 2, 1])
    s2 = pd.Series([0, 1, 2, 3, 2])
    lags, coeffs = calculate_cross_correlation(s1, s2, max_lag=2)
    assert lags[np.argmax(coeffs)] == -1


def test_calculate_cross_correlation_invalid_series():
    s1 = pd.Series([1, 1, 1, 1])
    s2 = pd.Series([0, 0, 0, 0])
    lags, coeffs = calculate_cross_correlation(s1, s2, max_lag=2)
    assert len(lags) == len(coeffs)
    assert np.all(np.isnan(coeffs))


def test_detect_monetary_regimes():
    # Trending up then down
    ff = pd.Series([1.0, 1.1, 1.2, 1.3, 1.2, 1.1, 1.0])
    regimes = detect_monetary_regimes(ff, window=2)
    assert "Hiking" in regimes.values
    assert "Easing" in regimes.values


def test_calculate_irf_returns_none_for_constant_series():
    df = pd.DataFrame({"shock": [0.0] * 50, "resp": [0.0] * 50})
    irf = calculate_irf(df, "resp", "shock", periods=5)
    assert irf is None


def test_calculate_irf_returns_series_for_valid_data():
    np.random.seed(0)
    shock = np.random.normal(0, 1, 200)
    resp = 0.3 * np.roll(shock, 1) + np.random.normal(0, 1, 200)
    df = pd.DataFrame({"shock": shock, "resp": resp})
    irf = calculate_irf(df, "resp", "shock", periods=5)
    assert irf is not None
    assert len(irf) == 6


def test_calculate_bond_portfolio_loss():
    loss = calculate_bond_portfolio_loss(base_value=1000, rate_change=0.01, duration=5.0)
    assert loss == pytest.approx(-50.0)


def test_calculate_liquidity_proxy():
    bond_loss, liquidity_proxy = calculate_liquidity_proxy(
        volume=9000,
        base_volume=10000,
        current_rate=0.05,
        baseline_rate=0.02,
        duration=5.0,
        bond_portfolio_ratio=0.6,
    )
    # rate_change = 0.03, portfolio = 6000, loss = -900
    assert bond_loss == pytest.approx(-900.0)
    assert liquidity_proxy == pytest.approx((9000 - 900) / 10000 * 100)


def test_calculate_returns():
    s = pd.Series([100.0, 110.0, 99.0])
    r = calculate_returns(s)
    assert r.iloc[1] == pytest.approx(0.10)
    assert r.iloc[2] == pytest.approx(-0.1)


def test_calculate_drawdown():
    s = pd.Series([1.0, 1.2, 1.1, 1.3, 1.0])
    dd = calculate_drawdown(s)
    assert dd.iloc[0] == pytest.approx(0.0)
    assert dd.iloc[2] == pytest.approx((1.1 / 1.2) - 1.0)
    assert dd.iloc[3] == pytest.approx(0.0)


def test_rolling_zscore():
    s = pd.Series([1, 2, 3, 4, 5, 6])
    z = rolling_zscore(s, window=3)
    assert np.isnan(z.iloc[1])
    assert z.iloc[-1] == pytest.approx((6 - 5) / np.std([4, 5, 6], ddof=0))


def test_build_stress_index():
    idx = pd.date_range("2023-01-01", periods=10, freq="D")
    d_ff = pd.Series(np.linspace(0, 0.01, 10), index=idx)
    r_vix = pd.Series(np.linspace(0, 0.02, 10), index=idx)
    kbe = pd.Series(np.linspace(100, 90, 10), index=idx)
    stress = build_stress_index(d_ff, r_vix, kbe, window=5, smoothing=3)
    assert stress.index.equals(idx)
    assert not stress.dropna().empty


def test_event_study_car():
    idx = pd.date_range("2023-01-01", periods=21, freq="D")
    kbe = pd.Series(0.01, index=idx)
    spy = pd.Series(0.0, index=idx)
    iat = pd.Series(0.02, index=idx)
    returns = pd.DataFrame({"KBE": kbe, "SPY": spy, "IAT": iat})
    event_dates = [idx[10]]
    car = event_study_car(returns, event_dates, window=5, benchmark_col="SPY")
    assert car.index.min() == -5
    assert car.index.max() == 5
    assert car.loc[5, "KBE"] == pytest.approx(0.11, rel=1e-2)


def test_build_beta_heatmap_returns_figure():
    import plotly.graph_objects as go

    idx = pd.date_range("2023-01-01", periods=3, freq="D")
    beta_df = pd.DataFrame({"KBE": [0.1, -0.2, 0.05], "IAT": [0.0, 0.3, -0.1]}, index=idx)
    fig = build_beta_heatmap(beta_df)
    assert isinstance(fig, go.Figure)


def test_classify_channel_state():
    state = classify_channel_state(
        stress_value=1.9,
        bank_beta=-0.8,
        mmf_relative=-0.12,
    )
    assert state == "Stressed"
