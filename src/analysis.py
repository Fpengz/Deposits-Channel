from typing import TypedDict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller


class TerminalStateSummary(TypedDict):
    overall_terminal_state: str
    action_posture: str
    driver_text: str
    dominant_tabs: list[str]
    confidence_note: str
    tab_states: dict[str, str]


def run_ols_regression(df: pd.DataFrame, y_col: str, x_col: str):
    """Performs OLS regression and returns the model results."""
    y = df[y_col]
    x = sm.add_constant(df[x_col])
    model = sm.OLS(y, x).fit()
    return model


def check_stationarity(series: pd.Series) -> float:
    """Runs ADF test and returns the p-value."""
    result = adfuller(series.dropna())
    return result[1]  # p-value


def calculate_rolling_beta(
    df: pd.DataFrame, y_col: str, x_col: str, window: int = 252
) -> pd.Series:
    """Calculates rolling beta of y relative to x."""
    betas = []
    for i in range(len(df)):
        if i < window:
            betas.append(np.nan)
        else:
            sub = df.iloc[i - window : i]
            if sub[y_col].dropna().empty or sub[x_col].dropna().empty:
                betas.append(np.nan)
                continue
            res = run_ols_regression(sub, y_col, x_col)
            betas.append(res.params[x_col])
    return pd.Series(betas, index=df.index)


def estimate_var_forecast(df: pd.DataFrame, steps: int = 5) -> np.ndarray:
    """Fits a VAR model and forecasts future values."""
    data = df.dropna()
    model = VAR(data)
    # Ensure at least 1 lag is used
    results = model.fit(maxlags=15, ic="aic", trend="c")
    # If k_ar is 0, VAR isn't useful, but statsmodels might return it
    if results.k_ar == 0:
        results = model.fit(1)

    forecast = results.forecast(data.values[-results.k_ar :], steps)
    return forecast


def calculate_correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Returns the correlation matrix of a dataframe."""
    return df.corr()


def calculate_irf(df: pd.DataFrame, response_col: str, shock_col: str, periods: int = 20):
    """Calculates IRF for a response column given a shock in shock_col."""
    data = df[[shock_col, response_col]].dropna()
    # Ensure some variation
    if data.empty or data[shock_col].std() == 0 or data[response_col].std() == 0:
        return None

    model = VAR(data)
    try:
        results = model.fit(maxlags=min(15, len(data) // 10), ic="aic")
        irf = results.irf(periods)
        # Get the specific response of response_col to shock_col
        # results.irf returns (periods+1, k, k)
        idx_shock = 0  # shock_col is first
        idx_resp = 1  # response_col is second
        return irf.orth_irfs[:, idx_resp, idx_shock]
    except Exception:
        return None


def calculate_bond_portfolio_loss(
    base_value: float, rate_change: float, duration: float = 5.0
) -> float:
    """Calculates market value loss based on duration risk."""
    # Simplified duration math: dV = -D * dy * V
    loss = -duration * rate_change * base_value
    return loss


def calculate_liquidity_proxy(
    volume: float,
    base_volume: float,
    current_rate: float,
    baseline_rate: float,
    duration: float = 5.0,
    bond_portfolio_ratio: float = 0.6,
):
    """Returns (bond_loss, liquidity_proxy_percent)."""
    rate_change = current_rate - baseline_rate
    bond_portfolio_value = base_volume * bond_portfolio_ratio
    bond_loss = calculate_bond_portfolio_loss(bond_portfolio_value, rate_change, duration=duration)
    liquidity_proxy = (volume + bond_loss) / base_volume * 100
    return bond_loss, liquidity_proxy


def calculate_returns(series: pd.Series) -> pd.Series:
    """Calculates simple returns."""
    return series.pct_change()


def calculate_drawdown(series: pd.Series) -> pd.Series:
    """Calculates drawdown from rolling peak."""
    rolling_max = series.cummax()
    return (series / rolling_max) - 1.0


def rolling_zscore(series: pd.Series, window: int = 252) -> pd.Series:
    """Calculates rolling z-score."""
    mean = series.rolling(window=window).mean()
    std = series.rolling(window=window).std(ddof=0)
    z = (series - mean) / std
    return z


def build_stress_index(
    d_ff: pd.Series,
    r_vix: pd.Series,
    kbe_price: pd.Series,
    window: int = 252,
    smoothing: int = 5,
) -> pd.Series:
    """Builds an equal-weight stress index from rate changes, VIX returns, and bank drawdown."""
    dd_kbe = calculate_drawdown(kbe_price)
    z_dff = rolling_zscore(d_ff, window=window)
    z_vix = rolling_zscore(r_vix, window=window)
    z_dd = rolling_zscore(dd_kbe, window=window)
    stress = pd.concat([z_dff, z_vix, z_dd], axis=1).mean(axis=1)
    if smoothing and smoothing > 1:
        stress = stress.rolling(window=smoothing).mean()
    return stress


def build_combined_stress_grid(
    outflow_range: np.ndarray,
    aoci_range: np.ndarray,
    threshold: float = 0.25,
) -> pd.DataFrame:
    z = []
    for outflow in outflow_range:
        row = []
        for aoci in aoci_range:
            row.append(int(outflow + aoci >= threshold))
        z.append(row)
    return pd.DataFrame(z, index=outflow_range, columns=aoci_range)


def build_beta_heatmap(beta_df: pd.DataFrame):
    """Builds a heatmap figure for rolling betas."""
    if beta_df.empty:
        return go.Figure()
    max_abs = np.nanmax(np.abs(beta_df.values))
    if max_abs == 0 or np.isnan(max_abs):
        max_abs = 1.0
    fig = go.Figure(
        data=go.Heatmap(
            z=beta_df.T.values,
            x=beta_df.index,
            y=beta_df.columns,
            colorscale="RdBu",
            zmin=-max_abs,
            zmax=max_abs,
        )
    )
    return fig


def event_study_car(
    returns: pd.DataFrame,
    event_dates: list,
    window: int = 5,
    benchmark_col: str = "SPY",
) -> pd.DataFrame:
    """Computes average cumulative abnormal returns around event dates."""
    if benchmark_col not in returns.columns:
        raise ValueError("benchmark_col not found in returns")
    returns = returns.dropna()
    if returns.empty:
        return pd.DataFrame()
    abnormal = returns.sub(returns[benchmark_col], axis=0)
    series_cols = [c for c in abnormal.columns if c != benchmark_col]
    car_frames = []
    for date in event_dates:
        if date not in abnormal.index:
            continue
        loc = abnormal.index.get_loc(date)
        if isinstance(loc, slice):
            loc = loc.start
        start = loc - window
        end = loc + window
        if start < 0 or end >= len(abnormal):
            continue
        windowed = abnormal.iloc[start : end + 1][series_cols]
        car = windowed.cumsum()
        car.index = range(-window, window + 1)
        car_frames.append(car)
    if not car_frames:
        return pd.DataFrame(index=range(-window, window + 1), columns=series_cols)
    return pd.concat(car_frames).groupby(level=0).mean()


def calculate_recursive_ols(df: pd.DataFrame, y_col: str, x_col: str):
    """Calculates recursive OLS coefficients and standard errors."""
    y = df[y_col]
    x = sm.add_constant(df[x_col])
    from statsmodels.regression.recursive_ls import RecursiveLS

    res = RecursiveLS(y, x).fit()
    # statsmodels RecursiveLSResults.recursive_coefficients has 'params' attribute in some versions
    # but more reliably we can use res.filtered_state
    # filtered_state is (k_vars, nobs)
    betas = res.filtered_state[1]
    # standard errors from filtered_state_cov diagonal
    se = np.sqrt(res.filtered_state_cov[1, 1, :])
    return pd.Series(betas, index=df.index), pd.Series(se, index=df.index)


def run_monte_carlo_simulation(
    current_rate: float,
    market_power: float,
    base_volume: float,
    elasticity: float,
    trials: int = 1000,
):
    """Simulates random rate paths and resulting volume contractions."""
    # Assuming daily volatility of 5bps for rate shocks
    vol = 0.0005
    results = []
    np.random.seed(42)
    for _ in range(trials):
        # 1-year random walk (approx 252 days)
        shocks = np.random.normal(0, vol, 252)
        final_rate = max(0.0, current_rate + np.sum(shocks))
        # Calculate resulting volume using our simulation functions
        try:
            from simulation import calculate_deposit_rate, calculate_deposit_volume
        except ImportError:
            from src.simulation import calculate_deposit_rate, calculate_deposit_volume
        dep_rate = calculate_deposit_rate(final_rate, market_power)
        final_vol = calculate_deposit_volume(base_volume, final_rate - dep_rate, elasticity)
        results.append(final_vol)
    return np.array(results)


def calculate_yield_curve_slope(ten_year: pd.Series, three_month: pd.Series) -> pd.Series:
    """Calculates the 10Y - 3M yield curve slope."""
    return ten_year - three_month


def calculate_credit_spread(credit_price: pd.Series, treasury_price: pd.Series) -> pd.Series:
    """Calculates proxy credit spread using relative price performance."""
    # Since we fetch prices for LQD, a simple proxy for spread stress is the ratio
    # or the difference in cumulative returns.
    # Higher spread = lower relative price of credit vs treasury
    return treasury_price / credit_price


def classify_curve_regime(
    slope: pd.Series,
    flat_threshold: float = 0.25,
) -> pd.Series:
    regimes = pd.Series("Normal", index=slope.index)
    regimes[slope.isna()] = "Insufficient data"
    regimes[slope < 0] = "Inverted"
    regimes[(slope >= 0) & (slope <= flat_threshold)] = "Flat"
    return regimes


def calculate_cross_correlation(s1: pd.Series, s2: pd.Series, max_lag: int = 15):
    """Calculates cross-correlation between two series at various lags."""
    lags = range(-max_lag, max_lag + 1)
    if s1.std() == 0 or s2.std() == 0:
        return list(lags), [np.nan] * len(lags)
    # Ensure they are aligned and normalized for better correlation values
    s1_norm = (s1 - s1.mean()) / (s1.std() * len(s1))
    s2_norm = (s2 - s2.mean()) / s2.std()
    coeffs = np.correlate(s1_norm, s2_norm, mode="full")
    # Match the range of lags
    mid = len(coeffs) // 2
    coeffs = coeffs[mid - max_lag : mid + max_lag + 1]
    return list(lags), list(coeffs)


def classify_channel_state(
    stress_value: float,
    bank_beta: float,
    mmf_relative: float,
) -> str:
    if pd.isna(stress_value) or pd.isna(bank_beta) or pd.isna(mmf_relative):
        return "Insufficient data"
    if stress_value >= 1.5 or (bank_beta < -0.5 and mmf_relative < -0.05):
        return "Stressed"
    if stress_value >= 0.75 or bank_beta < -0.2 or mmf_relative < -0.02:
        return "Active"
    return "Dormant"


def classify_theory_state(liquidity_proxy: float, stress_share: float) -> str:
    """Classifies the theory tab into a compact fragility state."""
    if pd.isna(liquidity_proxy) or pd.isna(stress_share):
        return "Insufficient data"
    if liquidity_proxy <= 94 or stress_share >= 0.25:
        return "Fragility elevated"
    return "Fragility contained"


def classify_macro_credit_state(
    curve_regime: str | None,
    mmf_relative: float,
    credit_stress_change: float,
) -> str:
    """Classifies the macro tab into a spillover state."""
    if curve_regime is None or pd.isna(mmf_relative) or pd.isna(credit_stress_change):
        return "Insufficient data"
    if curve_regime == "Inverted" and (mmf_relative <= -0.05 or credit_stress_change > 0.02):
        return "Transmission widening"
    if curve_regime in {"Flat", "Inverted"} or mmf_relative <= -0.02 or credit_stress_change > 0:
        return "Spillover building"
    return "Spillover contained"


def classify_case_study_state(
    deposit_outflow: float,
    aoci_loss: float,
    equity_divergence: float,
) -> str:
    """Classifies how relevant the March 2023 case study looks as an analog."""
    values = [deposit_outflow, aoci_loss, equity_divergence]
    if any(pd.isna(value) for value in values):
        return "Insufficient data"
    total_pressure = deposit_outflow + aoci_loss + equity_divergence
    if total_pressure >= 35:
        return "Analog relevance high"
    if total_pressure >= 15:
        return "Analog relevance moderate"
    return "Analog relevance low"


def classify_monitoring_state(
    stress_value: float,
    bank_beta: float,
    curve_regime: str | None,
    mmf_pressure: str | None,
    credit_stress: str | None,
) -> str:
    """Classifies the monitoring tab into an operational state."""
    if (
        pd.isna(stress_value)
        or pd.isna(bank_beta)
        or curve_regime is None
        or mmf_pressure is None
        or credit_stress is None
    ):
        return "Insufficient data"
    if (
        stress_value >= 1.25
        or bank_beta <= -0.35
        or (curve_regime == "Inverted" and mmf_pressure == "Pressure building")
        or credit_stress == "Stress rising"
    ):
        return "Escalation risk high"
    if (
        stress_value >= 0.6
        or bank_beta <= -0.15
        or curve_regime in {"Flat", "Inverted"}
        or mmf_pressure == "Pressure building"
    ):
        return "Monitoring elevated"
    return "Monitoring stable"


def scenario_expectations(name: str) -> dict[str, str]:
    mapping = {
        "Higher for longer": {
            "spreads": "Wider",
            "deposits": "Weaker",
            "stress": "Higher",
            "banks": "Underperform",
        },
        "Rapid cuts": {
            "spreads": "Narrower",
            "deposits": "Stabilize",
            "stress": "Lower",
            "banks": "Rebound",
        },
        "Volatility shock": {
            "spreads": "Wider",
            "deposits": "Fragile",
            "stress": "Higher",
            "banks": "Sell off",
        },
        "Bank-specific confidence shock": {
            "spreads": "Wider",
            "deposits": "Run risk",
            "stress": "Higher",
            "banks": "Diverge",
        },
    }
    if name not in mapping:
        raise ValueError(f"Unknown scenario: {name}")
    return mapping[name]


def detect_monetary_regimes(ff_series: pd.Series, window: int = 20) -> pd.Series:
    """Detects 'Hiking' vs 'Easing' regimes based on a rolling average of proxy changes."""
    # Smoothed change to avoid noise
    change = ff_series.diff().rolling(window=window).mean()
    regimes = pd.Series("Stable", index=ff_series.index)
    regimes[change > 0.0001] = "Hiking"
    regimes[change < -0.0001] = "Easing"
    return regimes


TAB_STATE_SEVERITY = {
    "Fragility contained": 0,
    "Fragility elevated": 1,
    "Transmission dormant": 0,
    "Transmission active": 1,
    "Transmission broadening": 2,
    "Spillover contained": 0,
    "Spillover building": 1,
    "Transmission widening": 2,
    "Analog relevance low": 0,
    "Analog relevance moderate": 1,
    "Analog relevance high": 2,
    "Monitoring stable": 0,
    "Monitoring elevated": 1,
    "Escalation risk high": 2,
    "Insufficient data": np.nan,
}

TAB_WEIGHTS = {
    "Theory": 0.6,
    "Empirical": 1.0,
    "Macro & Credit": 0.75,
    "Case Study": 0.45,
    "Monitoring": 1.0,
}


def resolve_action_posture(overall_terminal_state: str, disagreement: bool = False) -> str:
    """Maps the rolled-up state into a compact action posture."""
    if overall_terminal_state == "Transmission risk elevated":
        return "Escalate"
    if overall_terminal_state == "Transmission mixed but elevated":
        return "Escalate" if not disagreement else "Watch"
    if overall_terminal_state == "Transmission active but mixed":
        return "Watch"
    if overall_terminal_state == "Transmission dormant":
        return "Routine"
    return "Watch"


def build_terminal_driver_text(
    tab_states: dict[str, str],
    dominant_tabs: list[str],
    disagreement: bool = False,
) -> str:
    """Builds a short summary of the strongest tab-level contributors."""
    if not disagreement:
        dominant_severities = {
            TAB_STATE_SEVERITY.get(tab_states.get(tab, "Insufficient data"), np.nan)
            for tab in dominant_tabs[:2]
        }
        disagreement = len({value for value in dominant_severities if not pd.isna(value)}) > 1
    driver_labels = []
    for tab in dominant_tabs[:2]:
        state = tab_states.get(tab)
        if state and state != "Insufficient data":
            state_label = state.lower()
            tab_label = tab.lower()
            if state_label.startswith(tab_label):
                driver_labels.append(state_label)
            else:
                driver_labels.append(f"{tab_label} {state_label}")
    if not driver_labels:
        base = "Limited overlapping evidence across the live tabs."
    elif len(driver_labels) == 1:
        base = f"{driver_labels[0].capitalize()}."
    else:
        base = f"{driver_labels[0].capitalize()} and {driver_labels[1]}."
    if disagreement:
        return f"{base[:-1]}, with mixed signals across the highest-weight tabs."
    return base


def rollup_terminal_state(tab_states: dict[str, str]) -> TerminalStateSummary:
    """Rolls tab states into one overall terminal state and posture."""
    weighted_scores: dict[str, float] = {}
    available_scores: list[float] = []
    available_weights: list[float] = []
    for tab, state in tab_states.items():
        severity = TAB_STATE_SEVERITY.get(state, np.nan)
        weight = TAB_WEIGHTS.get(tab, 0.0)
        if pd.isna(severity) or weight == 0:
            continue
        weighted_scores[tab] = severity * weight
        available_scores.append(severity)
        available_weights.append(weight)

    if not available_weights:
        overall_terminal_state = "Insufficient data"
        disagreement = False
        dominant_tabs: list[str] = []
        confidence_note = "Limited confidence due to insufficient tab classifications"
    else:
        weighted_average = float(np.average(available_scores, weights=available_weights))
        high_weight_tabs = [tab for tab in ("Empirical", "Monitoring") if tab in weighted_scores]
        remaining_tabs = sorted(
            [tab for tab in weighted_scores if tab not in high_weight_tabs],
            key=lambda tab: (weighted_scores[tab], TAB_WEIGHTS[tab]),
            reverse=True,
        )
        dominant_tabs = high_weight_tabs + remaining_tabs
        high_weight_states = {tab_states[tab] for tab in high_weight_tabs}
        disagreement = len(high_weight_states) > 1 and {
            TAB_STATE_SEVERITY[tab_states[tab]] for tab in high_weight_tabs
        } != {np.nan}
        if weighted_average >= 1.35:
            overall_terminal_state = "Transmission risk elevated"
        elif weighted_average >= 0.95:
            overall_terminal_state = (
                "Transmission mixed but elevated" if disagreement else "Transmission elevated"
            )
        elif weighted_average >= 0.4:
            overall_terminal_state = (
                "Transmission active but mixed" if disagreement else "Transmission active"
            )
        else:
            overall_terminal_state = "Transmission dormant"
        confidence_note = (
            "Mixed signal across high-weight tabs"
            if disagreement
            else "High-weight tabs are broadly aligned"
        )

    action_posture = resolve_action_posture(overall_terminal_state, disagreement=disagreement)
    driver_text = build_terminal_driver_text(
        tab_states,
        dominant_tabs,
        disagreement=disagreement,
    )

    return {
        "overall_terminal_state": overall_terminal_state,
        "action_posture": action_posture,
        "driver_text": driver_text,
        "dominant_tabs": dominant_tabs,
        "confidence_note": confidence_note,
        "tab_states": tab_states,
    }
