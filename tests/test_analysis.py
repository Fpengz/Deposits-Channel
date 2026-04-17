import numpy as np
import pandas as pd
import pytest
from src.analysis import (
    build_beta_heatmap,
    build_combined_stress_grid,
    build_stress_index,
    build_terminal_driver_text,
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
    classify_case_study_state,
    classify_channel_state,
    classify_curve_regime,
    classify_macro_credit_state,
    classify_monitoring_state,
    classify_theory_state,
    detect_monetary_regimes,
    estimate_var_forecast,
    event_study_car,
    resolve_action_posture,
    rolling_zscore,
    rollup_terminal_state,
    run_monte_carlo_simulation,
    run_ols_regression,
    scenario_expectations,
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


def test_classify_curve_regime():
    slope = pd.Series([1.2, 0.1, -0.3], index=["a", "b", "c"])
    regimes = classify_curve_regime(slope)
    assert regimes.tolist() == ["Normal", "Flat", "Inverted"]


def test_classify_curve_regime_handles_missing_data():
    slope = pd.Series([1.2, np.nan, -0.3], index=["a", "b", "c"])
    regimes = classify_curve_regime(slope)
    assert regimes.tolist() == ["Normal", "Insufficient data", "Inverted"]


def test_classify_curve_regime_threshold_boundaries():
    slope = pd.Series([0.0, 0.25, 0.251, -0.01], index=["a", "b", "c", "d"])
    regimes = classify_curve_regime(slope)
    assert regimes.tolist() == ["Flat", "Flat", "Normal", "Inverted"]


def test_classify_curve_regime_custom_flat_threshold():
    slope = pd.Series([0.05, 0.15, -0.02], index=["a", "b", "c"])
    regimes = classify_curve_regime(slope, flat_threshold=0.1)
    assert regimes.tolist() == ["Flat", "Normal", "Inverted"]


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


def test_build_combined_stress_grid_shape():
    grid = build_combined_stress_grid(
        outflow_range=np.array([0.0, 0.1]),
        aoci_range=np.array([0.0, 0.2, 0.4]),
        threshold=0.25,
    )
    assert grid.shape == (2, 3)
    assert grid.iloc[-1, -1] == 1


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


@pytest.mark.parametrize(
    "stress_value, bank_beta, mmf_relative, expected",
    [
        (1.9, -0.8, -0.12, "Stressed"),
        (0.8, -0.1, -0.01, "Active"),
        (0.2, -0.1, -0.01, "Dormant"),
    ],
)
def test_classify_channel_state(stress_value, bank_beta, mmf_relative, expected):
    state = classify_channel_state(
        stress_value=stress_value,
        bank_beta=bank_beta,
        mmf_relative=mmf_relative,
    )
    assert state == expected


def test_classify_channel_state_thresholds():
    assert classify_channel_state(1.5, 0.0, 0.0) == "Stressed"
    assert classify_channel_state(0.75, 0.0, 0.0) == "Active"
    assert classify_channel_state(0.74, -0.2, -0.02) == "Dormant"


def test_classify_channel_state_missing_data():
    assert (
        classify_channel_state(
            stress_value=np.nan,
            bank_beta=-0.1,
            mmf_relative=-0.01,
        )
        == "Insufficient data"
    )
    assert (
        classify_channel_state(
            stress_value=0.2,
            bank_beta=np.nan,
            mmf_relative=-0.01,
        )
        == "Insufficient data"
    )


def test_scenario_expectations_higher_for_longer():
    result = scenario_expectations("Higher for longer")

    assert result["spreads"] == "Wider"
    assert result["deposits"] == "Weaker"
    assert result["banks"] == "Underperform"


def test_scenario_expectations_unknown_name():
    with pytest.raises(ValueError, match="Unknown scenario: Not a scenario"):
        scenario_expectations("Not a scenario")


def test_classify_theory_state_thresholds():
    assert classify_theory_state(liquidity_proxy=91.0, stress_share=0.35) == "Fragility elevated"
    assert classify_theory_state(liquidity_proxy=97.5, stress_share=0.10) == "Fragility contained"


def test_classify_theory_state_handles_missing_inputs():
    assert classify_theory_state(liquidity_proxy=np.nan, stress_share=0.15) == "Insufficient data"


def test_classify_macro_credit_state_thresholds():
    assert (
        classify_macro_credit_state(
            curve_regime="Inverted",
            mmf_relative=-0.08,
            credit_stress_change=0.04,
        )
        == "Transmission widening"
    )
    assert (
        classify_macro_credit_state(
            curve_regime="Flat",
            mmf_relative=-0.03,
            credit_stress_change=0.01,
        )
        == "Spillover building"
    )
    assert (
        classify_macro_credit_state(
            curve_regime="Normal",
            mmf_relative=0.02,
            credit_stress_change=-0.01,
        )
        == "Spillover contained"
    )


def test_classify_case_study_state_thresholds():
    assert (
        classify_case_study_state(
            deposit_outflow=18.0,
            aoci_loss=12.0,
            equity_divergence=15.0,
        )
        == "Analog relevance high"
    )
    assert (
        classify_case_study_state(
            deposit_outflow=8.0,
            aoci_loss=6.0,
            equity_divergence=5.0,
        )
        == "Analog relevance moderate"
    )
    assert (
        classify_case_study_state(
            deposit_outflow=2.0,
            aoci_loss=1.0,
            equity_divergence=1.5,
        )
        == "Analog relevance low"
    )


def test_classify_monitoring_state_thresholds():
    assert (
        classify_monitoring_state(
            stress_value=1.4,
            bank_beta=-0.45,
            curve_regime="Inverted",
            mmf_pressure="Pressure building",
            credit_stress="Stress rising",
        )
        == "Escalation risk high"
    )
    assert (
        classify_monitoring_state(
            stress_value=0.8,
            bank_beta=-0.15,
            curve_regime="Flat",
            mmf_pressure="Pressure easing",
            credit_stress="Stress easing",
        )
        == "Monitoring elevated"
    )
    assert (
        classify_monitoring_state(
            stress_value=0.2,
            bank_beta=-0.02,
            curve_regime="Normal",
            mmf_pressure="Pressure easing",
            credit_stress="Stress easing",
        )
        == "Monitoring stable"
    )


def test_rollup_terminal_state_escalates_when_live_tabs_align():
    summary = rollup_terminal_state(
        {
            "Theory": "Fragility elevated",
            "Empirical": "Transmission broadening",
            "Macro & Credit": "Transmission widening",
            "Case Study": "Analog relevance high",
            "Monitoring": "Escalation risk high",
        }
    )

    assert summary["overall_terminal_state"] == "Transmission risk elevated"
    assert summary["action_posture"] == "Escalate"
    assert summary["dominant_tabs"][:2] == ["Empirical", "Monitoring"]


def test_rollup_terminal_state_maps_watch_posture_for_mixed_signals():
    summary = rollup_terminal_state(
        {
            "Theory": "Fragility elevated",
            "Empirical": "Transmission active",
            "Macro & Credit": "Spillover contained",
            "Case Study": "Analog relevance moderate",
            "Monitoring": "Monitoring stable",
        }
    )

    assert summary["overall_terminal_state"] == "Transmission active but mixed"
    assert summary["action_posture"] == "Watch"


def test_rollup_terminal_state_handles_low_pressure():
    summary = rollup_terminal_state(
        {
            "Theory": "Fragility contained",
            "Empirical": "Transmission dormant",
            "Macro & Credit": "Spillover contained",
            "Case Study": "Analog relevance low",
            "Monitoring": "Monitoring stable",
        }
    )

    assert summary["overall_terminal_state"] == "Transmission dormant"
    assert summary["action_posture"] == "Routine"


def test_rollup_terminal_state_surfaces_conflicting_high_weight_tabs():
    summary = rollup_terminal_state(
        {
            "Theory": "Fragility elevated",
            "Empirical": "Transmission broadening",
            "Macro & Credit": "Spillover building",
            "Case Study": "Analog relevance moderate",
            "Monitoring": "Monitoring stable",
        }
    )

    assert summary["overall_terminal_state"] == "Transmission mixed but elevated"
    assert summary["confidence_note"] == "Mixed signal across high-weight tabs"


def test_build_terminal_driver_text_references_dominant_tabs_and_disagreement():
    summary = rollup_terminal_state(
        {
            "Theory": "Fragility elevated",
            "Empirical": "Transmission broadening",
            "Macro & Credit": "Spillover contained",
            "Case Study": "Analog relevance moderate",
            "Monitoring": "Monitoring stable",
        }
    )

    driver_text = build_terminal_driver_text(summary["tab_states"], summary["dominant_tabs"])

    assert "the live read is being pulled" in driver_text.lower()
    assert "empirical transmission broadening" in driver_text.lower()
    assert "monitoring stable" in driver_text.lower()
    assert "highest-weight tabs are still mixed" in driver_text.lower()


@pytest.mark.parametrize(
    ("overall_state", "expected_posture"),
    [
        ("Transmission dormant", "Routine"),
        ("Transmission active but mixed", "Watch"),
        ("Transmission risk elevated", "Escalate"),
    ],
)
def test_resolve_action_posture_maps_expected_ranges(overall_state, expected_posture):
    assert resolve_action_posture(overall_state, disagreement=False) == expected_posture
