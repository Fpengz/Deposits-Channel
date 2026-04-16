import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from analysis import (
    build_beta_heatmap,
    build_combined_stress_grid,
    build_stress_index,
    calculate_bond_portfolio_loss,
    calculate_correlation_matrix,
    calculate_cross_correlation,
    calculate_liquidity_proxy,
    calculate_recursive_ols,
    calculate_returns,
    calculate_rolling_beta,
    calculate_yield_curve_slope,
    classify_channel_state,
    classify_curve_regime,
    event_study_car,
    run_monte_carlo_simulation,
    run_ols_regression,
    scenario_expectations,
)
from data_fetcher import (
    get_proxy_10y_yield,
    get_proxy_credit_ig,
    get_proxy_deposits,
    get_proxy_fed_funds,
    get_proxy_market,
    get_proxy_mmf,
    get_proxy_regional_banks,
    get_proxy_volatility,
)
from simulation import (
    calculate_deposit_rate,
    calculate_deposit_volume,
    counterfactual_channel_impact,
    generate_deposit_paths,
    generate_rate_paths,
)

# Suppress statsmodels frequency warnings
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")
st.set_page_config(page_title="Deposits Channel Research Terminal", layout="wide")

st.title("The Deposits Channel: Macro-Finance Terminal v4.0")
st.markdown("""
This terminal explores the mechanics of **Drechsler, Savov & Schnabl (2017)** across multiple asset classes. 
Use the tabs below to explore the "Flow of Funds", Yield Curve interactions, and recent banking stress.
""")

# Sidebar Navigation & Global Filters
st.sidebar.title("Terminal Controls")
st.sidebar.divider()
st.sidebar.subheader("Global Timeframe")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2018-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

# Global data fetch (shared across tabs)
with st.spinner("Fetching market data..."):
    ff_proxy = get_proxy_fed_funds()
    kbe_proxy = get_proxy_deposits()
    iat_proxy = get_proxy_regional_banks()
    spy_proxy = get_proxy_market()
    vix_proxy = get_proxy_volatility()
    mmf_proxy = get_proxy_mmf()
    tnx_proxy = get_proxy_10y_yield()
    lqd_proxy = get_proxy_credit_ig()

# 5-Tab Structure (Question-Driven)
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    [
        "Theory & Simulation",
        "Empirical Terminal",
        "Macro & Credit",
        "Case Study",
        "Monitoring & Scenarios",
    ]
)


def _build_recent_stress_series(frame: pd.DataFrame) -> pd.Series:
    for lookback in (252, 126, 63, 21, 10, 5):
        recent = frame.tail(lookback + 4).copy()
        if len(recent) < 2:
            continue
        stress_series = build_stress_index(
            recent["d_ff"],
            recent["r_vix"],
            recent["KBE"],
            window=min(lookback, len(recent)),
            smoothing=min(5, len(recent)),
        ).dropna()
        if not stress_series.empty:
            return stress_series
    return pd.Series(dtype=float)


def _recent_beta_regime(frame: pd.DataFrame) -> tuple[float | None, str | None]:
    for lookback in (252, 126, 63, 21, 10, 5):
        recent = frame.tail(lookback).dropna()
        if len(recent) < 5:
            continue
        if recent["d_ff"].std() == 0 or recent["r_kbe"].std() == 0:
            continue
        beta_model = run_ols_regression(recent, "r_kbe", "d_ff")
        latest_bank_beta = beta_model.params["d_ff"]
        if latest_bank_beta <= -0.2:
            return latest_bank_beta, "Amplifying"
        if latest_bank_beta <= -0.05:
            return latest_bank_beta, "Leaning negative"
        return latest_bank_beta, "Contained"
    return None, None


def _recent_change(series: pd.Series) -> tuple[float, int]:
    for lookback in (252, 126, 63, 21, 10, 5):
        recent = series.dropna().tail(lookback)
        if len(recent) < 2:
            continue
        first = recent.iloc[0]
        last = recent.iloc[-1]
        if pd.notna(first) and pd.notna(last) and first != 0:
            return last / first - 1, len(recent)
    return np.nan, 0


with tab1:
    st.header("Theory & Simulation")
    st.markdown("Each section answers a core question, then pushes deeper into the mechanics.")

    st.subheader("Q1: What is the deposits channel mechanism?")
    st.markdown("The channel transmits policy rates into bank funding costs and lending supply.")
    st.markdown(r"""
    **Fed Funds Rate ↑ → Deposit Spread ↑ → Deposit Outflow → Bank Lending ↓**
    """)

    colA, colB, colC = st.columns(3)
    with colA:
        st.info(
            "**Market Power**\n\nBanks in concentrated markets (high HHI) can keep deposit rates low even when the Fed hikes."
        )
    with colB:
        st.warning(
            "**The Spread**\n\nThe 'price of liquidity' widens as banks widen the gap between what they earn and what they pay you."
        )
    with colC:
        st.success(
            "**Transmission**\n\nAs deposits flow to Money Market Funds, banks lose their cheapest source of funding and must cut lending."
        )

    st.divider()

    # Sidebar for simulation controls
    st.sidebar.header("Simulation Parameters")
    fed_funds_rate = st.sidebar.slider("Fed Funds Rate (%)", 0.0, 10.0, 5.0, 0.25) / 100.0
    market_power = st.sidebar.slider("Bank Market Power (0 to 1)", 0.0, 1.0, 0.5, 0.1)
    elasticity = st.sidebar.slider("Depositor Elasticity", 1.0, 20.0, 10.0, 1.0)
    baseline_rate = st.sidebar.slider("Baseline Rate (%)", 0.0, 10.0, 2.0, 0.25) / 100.0
    duration = st.sidebar.slider("Bond Portfolio Duration (yrs)", 1.0, 10.0, 5.0, 0.5)
    base_volume = 10000.0

    # Calculate theoretical values
    dep_rate = calculate_deposit_rate(fed_funds_rate, market_power)
    spread = fed_funds_rate - dep_rate
    volume = calculate_deposit_volume(base_volume, spread, elasticity)

    # AOCI Calculation
    bond_loss, liquidity_proxy = calculate_liquidity_proxy(
        volume=volume,
        base_volume=base_volume,
        current_rate=fed_funds_rate,
        baseline_rate=baseline_rate,
        duration=duration,
        bond_portfolio_ratio=0.6,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fed Funds Rate", f"{fed_funds_rate * 100:.2f}%")
    col2.metric("Deposit Rate", f"{dep_rate * 100:.2f}%", f"-{spread * 100:.2f}% spread")
    col3.metric("Total Deposits", f"${volume:,.0f}B")
    col4.metric(
        "Capital Buffer (Proxy)",
        f"{liquidity_proxy:.1f}%",
        f"${bond_loss:,.0f}B Unrealized Loss",
        delta_color="inverse",
    )

    st.info(
        "The **Capital Buffer Proxy** shows the dual squeeze: Deposit outflows + bond portfolio losses (AOCI)."
    )

    st.subheader("Q2: How sensitive is the mechanism to assumptions?")
    st.markdown("We vary market power and depositor elasticity to see where spreads bite most.")

    rates = [r / 100.0 for r in range(0, 1000, 25)]
    volumes = [
        calculate_deposit_volume(
            base_volume, r - calculate_deposit_rate(r, market_power), elasticity
        )
        for r in rates
    ]

    fig = go.Figure(
        data=go.Scatter(
            x=[r * 100 for r in rates],
            y=volumes,
            mode="lines",
            name="Theoretical Volume",
            line=dict(color="#1f77b4", width=3),
        )
    )
    fig.add_vline(x=fed_funds_rate * 100, line_dash="dash", line_color="#ff7f0e")
    fig.add_annotation(
        x=fed_funds_rate * 100,
        text="Current Rate",
        showarrow=False,
        y=1,
        yref="paper",
        textangle=-90,
        yanchor="bottom",
    )
    fig.update_layout(
        title="Theoretical Deposit Volume vs Fed Funds Rate",
        xaxis_title="Fed Funds Rate (%)",
        yaxis_title="Deposit Volume ($B)",
        template="plotly_white",
    )
    st.plotly_chart(fig, width="stretch")

    st.markdown("**Deposit spread heatmap** — where market power amplifies spread pressure.")
    ff_range = np.linspace(0, 0.1, 20)
    mp_range = np.linspace(0, 1.0, 20)
    spreads = np.array([[f * mp * 100 for mp in mp_range] for f in ff_range])
    fig_heat_sim = px.imshow(
        spreads,
        x=[f"{mp:.1f}" for mp in mp_range],
        y=[f"{f * 100:.1f}%" for f in ff_range],
        labels=dict(x="Bank Market Power", y="Fed Funds Rate (%)", color="Spread (%)"),
        color_continuous_scale="Viridis",
        aspect="auto",
    )
    fig_heat_sim.update_layout(template="plotly_white")
    st.plotly_chart(fig_heat_sim, width="stretch")

    st.markdown(
        "**Elasticity sensitivity** — surfaces reveal how quickly deposits evaporate as pass-through weakens."
    )
    elasticity_levels = [5, 10, 15]
    surface_cols = st.columns(3)
    ff_grid = np.linspace(0, 0.1, 30)
    mp_grid = np.linspace(0, 1.0, 30)
    for col, e in zip(surface_cols, elasticity_levels, strict=False):
        z = [
            [
                calculate_deposit_volume(base_volume, f - calculate_deposit_rate(f, mp), e)
                for mp in mp_grid
            ]
            for f in ff_grid
        ]
        fig_surface = go.Figure(
            data=go.Contour(
                z=z,
                x=[f"{mp:.2f}" for mp in mp_grid],
                y=[f"{f * 100:.1f}%" for f in ff_grid],
                colorscale="Viridis",
                contours=dict(showlabels=False),
            )
        )
        fig_surface.update_layout(
            title=f"Elasticity = {e}",
            xaxis_title="Market Power",
            yaxis_title="Fed Funds Rate (%)",
            template="plotly_white",
            height=300,
        )
        col.plotly_chart(fig_surface, width="stretch")

    st.markdown(
        "**Cross‑section intuition** — concentrated markets widen spreads more aggressively."
    )
    hhi_high = 0.8
    hhi_low = 0.2
    rates_syn = np.linspace(0, 0.08, 50)
    dr_high = rates_syn * (1 - hhi_high)
    dr_low = rates_syn * (1 - hhi_low)
    fig_syn = go.Figure()
    fig_syn.add_trace(
        go.Scatter(
            x=rates_syn * 100,
            y=dr_high * 100,
            name="Concentrated Bank (HHI=0.8)",
            line=dict(dash="dot"),
        )
    )
    fig_syn.add_trace(
        go.Scatter(x=rates_syn * 100, y=dr_low * 100, name="Competitive Bank (HHI=0.2)")
    )
    fig_syn.add_trace(
        go.Scatter(
            x=rates_syn * 100,
            y=rates_syn * 100,
            name="Fed Funds (Full Pass-through)",
            line=dict(color="black", dash="dash"),
        )
    )
    fig_syn.update_layout(
        title="Synthetic Deposit Rates vs Fed Funds",
        xaxis_title="Fed Funds Rate (%)",
        yaxis_title="Deposit Rate (%)",
        template="plotly_white",
    )
    st.plotly_chart(fig_syn, width="stretch")

    st.subheader("Q3: What happens under plausible rate paths?")
    st.markdown("Nine simulated paths map policy uncertainty into funding outcomes.")
    rate_paths = generate_rate_paths(current_rate=fed_funds_rate, paths=9, days=252, seed=42)
    deposit_paths = generate_deposit_paths(rate_paths, market_power, base_volume, elasticity)
    for row in range(3):
        cols = st.columns(3)
        for col_idx in range(3):
            idx = row * 3 + col_idx
            path_rate = rate_paths[idx]
            path_dep = deposit_paths[idx]
            fig_path = go.Figure()
            fig_path.add_trace(
                go.Scatter(y=path_rate * 100, name="Rate (%)", line=dict(color="#1f77b4"))
            )
            fig_path.add_trace(
                go.Scatter(y=path_dep, name="Deposits ($B)", line=dict(color="#ff7f0e"), yaxis="y2")
            )
            fig_path.update_layout(
                template="plotly_white",
                height=250,
                margin=dict(l=30, r=30, t=25, b=25),
                yaxis=dict(title="Rate (%)"),
                yaxis2=dict(title="Deposits", overlaying="y", side="right", showgrid=False),
                showlegend=False,
            )
            cols[col_idx].plotly_chart(fig_path, width="stretch")

    st.subheader("Q4: How do rate changes impact AOCI?")
    st.markdown(
        "Duration risk translates rate changes into unrealized losses on bank bond portfolios."
    )
    rate_changes = np.linspace(-0.05, 0.05, 51)
    bond_portfolio_value = base_volume * 0.6
    losses = [
        calculate_bond_portfolio_loss(bond_portfolio_value, rc, duration=duration)
        for rc in rate_changes
    ]
    fig_aoci = go.Figure(data=go.Scatter(x=rate_changes * 100, y=losses, mode="lines"))
    fig_aoci.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_aoci.update_layout(
        title="Bond Portfolio Loss vs Rate Change",
        xaxis_title="Rate Change (%)",
        yaxis_title="Loss ($B)",
        template="plotly_white",
    )
    st.plotly_chart(fig_aoci, width="stretch")

    st.subheader("Q5: When do outflows and AOCI become destabilizing?")
    st.markdown(
        "Outflow pressure becomes more dangerous when unrealized bond losses are already eating into capital. "
        "This simple grid marks the zone where deposit runoff and AOCI losses combine into a destabilizing stress pocket."
    )
    outflow_range = np.linspace(0.0, 0.2, 5)
    aoci_range = np.linspace(0.0, 0.15, 4)
    combined_stress_grid = build_combined_stress_grid(
        outflow_range=outflow_range,
        aoci_range=aoci_range,
        threshold=0.25,
    )
    fig_combined_stress = px.imshow(
        combined_stress_grid,
        x=[f"{value * 100:.0f}%" for value in combined_stress_grid.columns],
        y=[f"{value * 100:.0f}%" for value in combined_stress_grid.index],
        labels=dict(x="AOCI loss share", y="Deposit outflow share", color="Stress zone"),
        color_continuous_scale=[[0, "#dfe7f2"], [1, "#b42318"]],
        aspect="auto",
    )
    fig_combined_stress.update_layout(template="plotly_white")
    st.plotly_chart(fig_combined_stress, width="stretch")
    st.markdown(
        "**What to notice:** Once both pressures build together, the safe region disappears quickly."
    )
    st.markdown(
        "**Research takeaway:** The joint threshold matters more than either margin in isolation."
    )
    st.markdown(
        "**Investor takeaway:** Watch for banks with both deposit flight and hidden bond losses."
    )
    st.markdown(
        "**Policy/risk takeaway:** Liquidity backstops matter most when AOCI has already weakened buffers."
    )

    st.subheader("Takeaway")
    st.markdown(
        "**Rising rates + market power = widening spreads, faster outflows, and thinner capital buffers.**"
    )

with tab2:
    st.header("Empirical Terminal")
    st.markdown("Each section asks a market question, then answers it with data.")

    merged = pd.DataFrame()
    if (
        not ff_proxy.empty
        and not kbe_proxy.empty
        and not iat_proxy.empty
        and not spy_proxy.empty
        and not vix_proxy.empty
    ):
        # Merge and Filter
        merged = (
            ff_proxy.join(kbe_proxy, lsuffix="_ff", rsuffix="_kbe")
            .join(iat_proxy, rsuffix="_iat")
            .join(spy_proxy, rsuffix="_spy")
            .join(vix_proxy, rsuffix="_vix")
            .dropna()
        )
        merged.columns = ["FF_Proxy", "KBE", "IAT", "SPY", "VIX"]
        data_full = merged[
            (merged.index >= pd.to_datetime(start_date))
            & (merged.index <= pd.to_datetime(end_date))
        ]

        if data_full.empty:
            st.warning("Selected timeframe has no data overlap.")
        else:
            core_empirical_cols = ["FF_Proxy", "KBE", "IAT", "SPY", "VIX"]
            required_empirical_factors = ["d_ff", "r_kbe", "r_iat", "r_spy"]
            data_full["d_ff"] = data_full["FF_Proxy"].diff()
            data_full["r_kbe"] = data_full["KBE"].pct_change()
            data_full["r_iat"] = data_full["IAT"].pct_change()
            data_full["r_spy"] = data_full["SPY"].pct_change()
            data = data_full[core_empirical_cols].dropna().copy()
            data["d_ff"] = data_full.loc[data.index, "d_ff"]
            data["r_kbe"] = data_full.loc[data.index, "r_kbe"]
            data["r_iat"] = data_full.loc[data.index, "r_iat"]
            data["r_spy"] = data_full.loc[data.index, "r_spy"]
            data = data.dropna(subset=required_empirical_factors)
            if data.empty:
                st.warning(
                    "Selected timeframe does not have enough return/rate observations for empirical analysis."
                )
            else:
                # Q1. Market Evolution
                st.subheader("Q1: Are banks sensitive to rate shocks?")
                st.markdown("We compare rate changes to bank and market performance.")
                fig_ts = go.Figure()
                fig_ts.add_trace(
                    go.Scatter(x=data.index, y=data["FF_Proxy"], name="FF Proxy (%)", yaxis="y1")
                )
                fig_ts.add_trace(
                    go.Scatter(x=data.index, y=data["KBE"], name="Broad Banks (KBE)", yaxis="y2")
                )
                fig_ts.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data["SPY"],
                        name="Market (SPY)",
                        yaxis="y2",
                        line=dict(dash="dash"),
                    )
                )
                # FOMC Events
                fomc_dates = ["2022-03-16", "2023-03-22", "2023-05-03"]
                for d in fomc_dates:
                    dt = pd.to_datetime(d)
                    if dt in data.index:
                        fig_ts.add_vline(x=dt, line_dash="dot", line_color="gray")
                        fig_ts.add_annotation(
                            x=dt,
                            text="FOMC",
                            showarrow=False,
                            y=1,
                            yref="paper",
                            textangle=-90,
                            yanchor="bottom",
                        )
                fig_ts.update_layout(
                    yaxis=dict(title="Yield (%)", side="left"),
                    yaxis2=dict(title="ETF Price", side="right", overlaying="y", showgrid=False),
                    template="plotly_white",
                )
                st.plotly_chart(fig_ts, width="stretch")

                # Q1 continued: Sector Sensitivity
                st.subheader("Q1 Deep Dive: Interest Rate Betas")
                res_kbe = run_ols_regression(data, "r_kbe", "d_ff")
                res_spy = run_ols_regression(data, "r_spy", "d_ff")
                col1, col2 = st.columns(2)
                col1.metric("Bank Beta", f"{res_kbe.params['d_ff']:.4f}")
                col2.metric("Market Beta", f"{res_spy.params['d_ff']:.4f}")
                st.caption(
                    "Lower (more negative) Beta means the sector is more sensitive to rate hikes. Banks typically show higher sensitivity."
                )

                # Q4. Sensitivity Stability
                st.subheader("Q4: Is sensitivity stable over time?")
                st.markdown("Recursive betas show whether rate exposure drifts through regimes.")
                betas, se = calculate_recursive_ols(data, "r_kbe", "d_ff")
                fig_rec = go.Figure()
                fig_rec.add_trace(
                    go.Scatter(
                        x=data.index, y=betas, name="Recursive Beta", line=dict(color="#1f77b4")
                    )
                )
                fig_rec.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=betas + 1.96 * se,
                        line_color="rgba(0,0,0,0)",
                        showlegend=False,
                    )
                )
                fig_rec.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=betas - 1.96 * se,
                        fill="tonexty",
                        fillcolor="rgba(31, 119, 180, 0.2)",
                        name="95% Confidence Band",
                    )
                )
                fig_rec.update_layout(
                    title="Beta Stability Over Time",
                    xaxis_title="Date",
                    yaxis_title="Beta",
                    template="plotly_white",
                )
                st.plotly_chart(fig_rec, width="stretch")

                # Q2. Stress Signal
                st.subheader("Q2: Is stress building in the system?")
                st.markdown(
                    "We combine rate shocks, volatility, and bank drawdowns into one signal."
                )
                data["r_vix"] = calculate_returns(data["VIX"])
                stress = build_stress_index(
                    data["d_ff"], data["r_vix"], data["KBE"], window=252, smoothing=5
                )
                if stress.dropna().empty:
                    st.warning("Not enough data to compute the Stress Composite Index.")
                else:
                    threshold = stress.quantile(0.95)
                    fig_stress = go.Figure()
                    fig_stress.add_trace(go.Scatter(x=stress.index, y=stress, name="Stress Index"))
                    fig_stress.add_hline(y=threshold, line_dash="dash", line_color="red")
                    fig_stress.update_layout(
                        title="Composite Stress Index (Rates + VIX + KBE Drawdown)",
                        xaxis_title="Date",
                        yaxis_title="Z-Score",
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_stress, width="stretch")

                    latest_bank_beta = res_kbe.params["d_ff"]
                    latest_stress = stress.dropna().iloc[-1]
                    if not mmf_proxy.empty:
                        signal_frame = data[["KBE"]].copy()
                        signal_frame["MMF"] = np.asarray(mmf_proxy.reindex(data.index)).reshape(-1)
                        mmf_relative_series = (signal_frame["KBE"] / signal_frame["MMF"]).dropna()
                    else:
                        mmf_relative_series = pd.Series(dtype=float)
                    if not mmf_relative_series.empty:
                        mmf_relative = (
                            mmf_relative_series.iloc[-1] / mmf_relative_series.iloc[0] - 1
                        )
                    else:
                        mmf_relative = np.nan
                    channel_state = classify_channel_state(
                        latest_stress,
                        latest_bank_beta,
                        mmf_relative,
                    )

                    st.subheader("Signal Board")
                    board_col1, board_col2, board_col3 = st.columns(3)
                    board_col1.metric("Channel State", channel_state)
                    board_col2.metric("Latest Stress", f"{latest_stress:.2f}")
                    board_col3.metric("Latest Bank Beta", f"{latest_bank_beta:.4f}")
                    st.caption(
                        "What to notice: a move from Dormant to Active or Stressed means rate sensitivity is broadening into a regime signal."
                    )

                # Q3. Policy Event Impact
                st.subheader("Q3: Do policy events create abnormal returns?")
                st.markdown("We average cumulative abnormal returns around FOMC dates.")
                event_dates = [
                    pd.to_datetime(d)
                    for d in ["2022-03-16", "2022-06-15", "2022-09-21", "2023-03-22", "2023-05-03"]
                ]
                returns_df = data[["r_kbe", "r_iat", "r_spy"]].rename(
                    columns={"r_kbe": "KBE", "r_iat": "IAT", "r_spy": "SPY"}
                )
                car = event_study_car(returns_df, event_dates, window=5, benchmark_col="SPY")
                if car.empty:
                    st.warning(
                        "Not enough data to compute event study CARs for the selected period."
                    )
                else:
                    fig_car = go.Figure()
                    fig_car.add_trace(go.Scatter(x=car.index, y=car["KBE"], name="KBE CAR"))
                    fig_car.add_trace(
                        go.Scatter(
                            x=car.index, y=car["IAT"], name="IAT CAR", line=dict(color="red")
                        )
                    )
                    fig_car.add_hline(y=0, line_dash="dash", line_color="gray")
                    fig_car.update_layout(
                        title="Average Cumulative Abnormal Returns (±5 days)",
                        xaxis_title="Event Day",
                        yaxis_title="CAR",
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_car, width="stretch")

                # Q4 Deep Dive
                st.subheader("Q4 Deep Dive: Rolling Beta Heatmap")
                beta_kbe = calculate_rolling_beta(data, "r_kbe", "d_ff", window=252)
                beta_iat = calculate_rolling_beta(data, "r_iat", "d_ff", window=252)
                beta_spy = calculate_rolling_beta(data, "r_spy", "d_ff", window=252)
                beta_df = pd.DataFrame({"KBE": beta_kbe, "IAT": beta_iat, "SPY": beta_spy}).dropna()
                if beta_df.empty:
                    st.warning("Not enough data to compute rolling betas.")
                else:
                    fig_beta = build_beta_heatmap(beta_df)
                    fig_beta.update_layout(
                        title="Rolling 1Y Beta vs FF Proxy",
                        xaxis_title="Date",
                        yaxis_title="Series",
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_beta, width="stretch")

                # Q5. Fear Amplification
                st.subheader("Q5: Does fear amplify the channel?")
                st.markdown("We split betas by high vs low VIX to test amplification.")
                high_vix = data[data["VIX"] > 20]
                low_vix = data[data["VIX"] <= 20]

                if not high_vix.empty and not low_vix.empty:
                    res_high = run_ols_regression(high_vix, "r_kbe", "d_ff")
                    res_low = run_ols_regression(low_vix, "r_kbe", "d_ff")

                    col1, col2 = st.columns(2)
                    col1.metric("Beta (VIX > 20)", f"{res_high.params['d_ff']:.4f}")
                    col2.metric("Beta (VIX <= 20)", f"{res_low.params['d_ff']:.4f}")
                    st.caption(
                        "A more negative Beta during high VIX confirms that Deposits Channel risks are amplified during market stress."
                    )

                # Q6. Shock Propagation
                st.subheader("Q6: How do shocks propagate over time?")
                st.markdown(
                    "Impulse responses trace the shock ripple over the next 20 trading days."
                )
                from analysis import calculate_irf

                irf_kbe = calculate_irf(data, "r_kbe", "d_ff", periods=20)
                irf_iat = calculate_irf(data, "r_iat", "d_ff", periods=20)

                if irf_kbe is None or irf_iat is None:
                    st.warning(
                        "IRF model failed to fit for the selected data window. Try a longer timeframe."
                    )
                else:
                    fig_irf = go.Figure()
                    fig_irf.add_trace(
                        go.Scatter(
                            x=list(range(21)), y=irf_kbe, name="Response of Broad Banks (KBE)"
                        )
                    )
                    fig_irf.add_trace(
                        go.Scatter(
                            x=list(range(21)),
                            y=irf_iat,
                            name="Response of Regional Banks (IAT)",
                            line=dict(color="red"),
                        )
                    )
                    fig_irf.add_hline(y=0, line_dash="dash", line_color="gray")
                    fig_irf.update_layout(
                        title="Impulse Response to 1-Unit Rate Shock",
                        xaxis_title="Days since Shock",
                        yaxis_title="Response (Returns)",
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_irf, width="stretch")

                # Q7. Co-movement
                st.divider()
                st.subheader("Q7: How do the variables co-move?")
                corr = calculate_correlation_matrix(
                    data[["d_ff", "r_kbe", "r_iat", "r_spy", "r_vix"]].dropna()
                )
                st.plotly_chart(
                    px.imshow(
                        corr,
                        text_auto=".2f",
                        color_continuous_scale="Viridis",
                        template="plotly_white",
                    ),
                    width="stretch",
                )

                st.subheader("Q8: Which regime are we in?")
                if stress.dropna().empty:
                    st.warning("Not enough data to frame the current regime.")
                else:
                    if channel_state == "Stressed":
                        regime_label = "Stress regime"
                    elif channel_state == "Active":
                        regime_label = "Transmission regime"
                    elif channel_state == "Dormant":
                        regime_label = "Dormant regime"
                    else:
                        regime_label = "Data-building regime"
                    st.markdown(
                        f"**Current regime:** {regime_label}. The signal board blends stress, bank beta, and bank-vs-MMF relative performance."
                    )
                    st.markdown(
                        "**Research takeaway:** Regime framing helps separate a live deposits-channel signal from routine market noise."
                    )
                    st.markdown(
                        "**Investor takeaway:** When the board turns more active, bank equity sensitivity deserves tighter monitoring."
                    )
                    st.markdown(
                        "**Policy/risk takeaway:** A stressed board suggests liquidity and confidence risks may be reinforcing each other."
                    )

                st.subheader("Takeaway")
                st.markdown(
                    "**Empirically, bank sensitivity to rates spikes in stress regimes and clusters around policy events.**"
                )

with tab3:
    st.header("Macro & Credit")
    st.markdown("Follow the funding flow from deposits into the broader macro and credit system.")

    if not mmf_proxy.empty and not tnx_proxy.empty and not kbe_proxy.empty:
        macro_merged = (
            ff_proxy.join(mmf_proxy, lsuffix="_ff", rsuffix="_mmf")
            .join(tnx_proxy, rsuffix="_tnx")
            .join(kbe_proxy, rsuffix="_kbe")
            .dropna()
        )
        macro_merged.columns = ["FF_Proxy", "MMF_Price", "Ten_Year", "KBE"]
        macro_data = macro_merged[
            (macro_merged.index >= pd.to_datetime(start_date))
            & (macro_merged.index <= pd.to_datetime(end_date))
        ]

        # Q1. Deposit Destination
        st.subheader("Q1: Where do deposits go when spreads widen?")
        st.markdown("We proxy flows by comparing bank equities to money market funds.")
        fig_mmf = go.Figure()
        fig_mmf.add_trace(
            go.Scatter(
                x=macro_data.index, y=macro_data["FF_Proxy"], name="Fed Funds Proxy (%)", yaxis="y1"
            )
        )
        fig_mmf.add_trace(
            go.Scatter(
                x=macro_data.index, y=macro_data["MMF_Price"], name="MMF Price (VMFXX)", yaxis="y2"
            )
        )
        fig_mmf.update_layout(
            yaxis=dict(title="Yield (%)"),
            yaxis2=dict(title="Price ($)", overlaying="y", side="right", showgrid=False),
            template="plotly_white",
        )
        st.plotly_chart(fig_mmf, width="stretch")

        st.subheader("Q1 Deep Dive: Banks vs MMFs (Relative Performance)")
        rel = macro_data["KBE"] / macro_data["MMF_Price"]
        rel = rel / rel.iloc[0]
        fig_rel = go.Figure()
        fig_rel.add_trace(go.Scatter(x=macro_data.index, y=rel, name="KBE / VMFXX (Normalized)"))
        fig_rel.add_hline(y=1, line_dash="dash", line_color="gray")
        fig_rel.update_layout(
            title="Bank Equity vs MMF Proxy (Relative)",
            yaxis_title="Ratio (Start = 1.0)",
            template="plotly_white",
        )
        st.plotly_chart(fig_rel, width="stretch")

        # Q2. Macro Regime
        st.subheader("Q2: What macro regime are we in?")
        st.markdown("The channel strains when the curve is flat or inverted.")
        macro_data["Slope"] = calculate_yield_curve_slope(
            macro_data["Ten_Year"], macro_data["FF_Proxy"]
        )
        fig_slope = go.Figure(
            data=go.Scatter(
                x=macro_data.index, y=macro_data["Slope"], name="10Y-3M Slope", fill="tozeroy"
            )
        )
        fig_slope.add_hrect(y0=-10, y1=0, fillcolor="rgba(255,0,0,0.1)", line_width=0)
        fig_slope.add_hrect(y0=0, y1=0.5, fillcolor="rgba(255,165,0,0.1)", line_width=0)
        fig_slope.add_hrect(y0=0.5, y1=10, fillcolor="rgba(0,128,0,0.1)", line_width=0)
        fig_slope.add_hline(y=0, line_dash="dash", line_color="red")
        fig_slope.update_layout(
            title="Yield Curve Slope (Ten Year - Fed Funds Proxy)",
            yaxis_title="Spread (%)",
            template="plotly_white",
        )
        st.plotly_chart(fig_slope, width="stretch")

        st.subheader("Q5: Which macro regime are we in?")
        regime_matrix = pd.DataFrame(
            [
                ("Normal", "Positive slope", "Benign", "Routine monitoring"),
                ("Squeeze", "Flat curve", "Rising", "Watch funding competition"),
                ("Stress", "Inverted curve", "Elevated", "Prepare for balance-sheet pressure"),
                (
                    "Crisis",
                    "Inverted + disorderly moves",
                    "Acute",
                    "Treat liquidity as a binding constraint",
                ),
            ],
            columns=["Regime", "Curve", "Credit", "Read-through"],
        )
        st.markdown("**Regime Matrix**")
        st.table(regime_matrix)
        st.markdown("Warning rules")
        st.markdown(
            "- Flat curve plus weaker bank-vs-MMF relative performance signals a squeeze.\n"
            "- Inverted curve plus widening credit stress raises the odds that deposit pressure feeds back into lending.\n"
            "- If both conditions persist, treat the setup as a crisis-style funding regime."
        )
        st.markdown(
            "What to notice: the regime turns dangerous when curve compression and credit deterioration happen together."
        )
        st.markdown(
            "**Research takeaway:** The regime matrix links rates, flows, and credit into one narrative state."
        )
        st.markdown(
            "**Investor takeaway:** The move from Squeeze to Stress is where bank equity downside typically accelerates."
        )
        st.markdown(
            "**Policy/risk takeaway:** Crisis conditions call for tighter liquidity surveillance and faster confidence backstops."
        )

with tab3:
    st.divider()
    st.subheader("Q3: Is credit stress feeding back into banks?")
    st.markdown("We compare daily credit stress moves to bank returns.")

    if not lqd_proxy.empty and not kbe_proxy.empty and not iat_proxy.empty:
        credit_merged = (
            ff_proxy.join(lqd_proxy, rsuffix="_lqd")
            .join(spy_proxy, rsuffix="_spy")
            .join(kbe_proxy, rsuffix="_kbe")
            .join(iat_proxy, rsuffix="_iat")
            .dropna()
        )
        credit_merged.columns = ["FF_Proxy", "Credit_Price", "SPY", "KBE", "IAT"]
        credit_data = credit_merged[
            (credit_merged.index >= pd.to_datetime(start_date))
            & (credit_merged.index <= pd.to_datetime(end_date))
        ]

        # Use the recent LQD price trend as a direct credit stress proxy.
        credit_data["Credit_Stress_Trend"] = -credit_data["Credit_Price"].pct_change()

        st.subheader("1. Lending Conditions Proxy")
        st.markdown(
            "Widening credit 'stress' indicates a contraction in bank lending supply as deposits leave the system."
        )
        fig_credit = px.line(
            credit_data,
            y="Credit_Price",
            title="Investment Grade Credit Price (LQD)",
            labels={"Credit_Price": "Price ($)"},
            template="plotly_white",
        )
        st.plotly_chart(fig_credit, width="stretch")

        st.info(
            "When rates rise and deposits exit, banks must contract their balance sheets, leading to lower credit availability and higher spreads."
        )

        st.subheader("Q3 Deep Dive: Credit Stress vs Bank Returns")
        credit_data["r_kbe"] = credit_data["KBE"].pct_change()
        credit_data["r_iat"] = credit_data["IAT"].pct_change()
        credit_scatter = credit_data.dropna()
        if credit_scatter.empty:
            st.warning("Not enough data to compute credit stress scatter.")
        else:
            fig_scatter = go.Figure()
            fig_scatter.add_trace(
                go.Scatter(
                    x=credit_scatter["Credit_Stress_Trend"].diff(),
                    y=credit_scatter["r_kbe"],
                    mode="markers",
                    name="KBE",
                )
            )
            fig_scatter.add_trace(
                go.Scatter(
                    x=credit_scatter["Credit_Stress_Trend"].diff(),
                    y=credit_scatter["r_iat"],
                    mode="markers",
                    name="IAT",
                    marker=dict(color="red"),
                )
            )
            fig_scatter.update_layout(
                title="Credit Stress vs Bank Returns",
                xaxis_title="Δ Credit Stress",
                yaxis_title="Return",
                template="plotly_white",
            )
            st.plotly_chart(fig_scatter, width="stretch")

        st.subheader("Q4: Do rates lead credit stress?")
        d_ff = credit_data["FF_Proxy"].diff().dropna()
        spread_change = credit_data["Credit_Stress_Trend"].diff().dropna()
        aligned_ff, aligned_spread = d_ff.align(spread_change, join="inner")
        lags, coeffs = calculate_cross_correlation(aligned_ff, aligned_spread, max_lag=15)
        if np.all(np.isnan(coeffs)):
            st.warning("Lead/lag correlation not available (insufficient variation).")
        else:
            fig_lag = go.Figure()
            fig_lag.add_trace(go.Bar(x=lags, y=coeffs))
            fig_lag.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_lag.update_layout(
                title="Cross-Correlation (Rates vs Credit Stress)",
                xaxis_title="Lag (days)",
                yaxis_title="Correlation",
                template="plotly_white",
            )
            st.plotly_chart(fig_lag, width="stretch")

        st.subheader("Takeaway")
        st.markdown(
            "**When rates rise, deposits shift toward MMFs, the curve compresses, and credit stress feeds back into bank equity.**"
        )

with tab4:
    st.header("Case Study: March 2023 Banking Stress")
    st.markdown("A nonlinear shock reveals how quickly the deposits channel can break.")
    st.markdown("""
    March 2023 represented a 'nonlinear' shock where the Deposits Channel mechanism reached a breaking point 
    for regional banks like SVB.
    """)

    # Zoom in on 2023
    crisis_start = pd.to_datetime("2023-02-01")
    crisis_end = pd.to_datetime("2023-05-01")
    if merged.empty:
        st.warning("Crisis period data not available in current fetch.")
    else:
        crisis_data = merged[(merged.index >= crisis_start) & (merged.index <= crisis_end)]

        if not crisis_data.empty:
            st.subheader("Q1: What broke in March 2023?")
            st.markdown("Regional banks diverged as deposit outflows and AOCI losses accelerated.")
            st.markdown(
                "**Timeline:** February rate pressure hit bond values, March 10 marked the SVB collapse, and the following days became a system-wide confidence test."
            )
            fig_svb = go.Figure()
            fig_svb.add_trace(
                go.Scatter(x=crisis_data.index, y=crisis_data["KBE"], name="Broad Banks (KBE)")
            )
            fig_svb.add_trace(
                go.Scatter(
                    x=crisis_data.index,
                    y=crisis_data["IAT"],
                    name="Regional Banks (IAT)",
                    line=dict(width=4, color="red"),
                )
            )
            fig_svb.add_vline(x=pd.to_datetime("2023-03-10"), line_dash="dash", line_color="black")
            fig_svb.add_annotation(
                x=pd.to_datetime("2023-03-10"),
                text="SVB Collapse",
                showarrow=False,
                y=1,
                yref="paper",
                textangle=-90,
                yanchor="bottom",
            )
            fig_svb.update_layout(
                title="KBE vs IAT: The Regional Divergence",
                yaxis_title="Price ($)",
                template="plotly_white",
            )
            st.plotly_chart(fig_svb, width="stretch")

            st.markdown("""
            **Implications:**
            - **Sticky no more:** The assumption of deposit stickiness failed as digital banking allowed instant outflows.
            - **Unrealized Losses:** High interest rates (the X-axis of our model) caused the value of bank-held bonds to drop, 
              creating the 'hole' that deposit outflows exposed.
            - **Endogenous Power:** Large banks (KBE) recovered faster as they benefited from a 'flight to safety', 
              further increasing their market power.
            """)

            st.subheader("Q2: How big was the divergence?")
            st.markdown("Normalize KBE and IAT to visualize cumulative separation.")
            kbe_norm = crisis_data["KBE"] / crisis_data["KBE"].iloc[0]
            iat_norm = crisis_data["IAT"] / crisis_data["IAT"].iloc[0]
            fig_div = go.Figure()
            fig_div.add_trace(go.Scatter(x=crisis_data.index, y=kbe_norm, name="KBE (Normalized)"))
            fig_div.add_trace(
                go.Scatter(
                    x=crisis_data.index, y=iat_norm, name="IAT (Normalized)", line=dict(color="red")
                )
            )
            fig_div.update_layout(
                title="Cumulative Performance Divergence",
                yaxis_title="Normalized Price",
                template="plotly_white",
            )
            st.plotly_chart(fig_div, width="stretch")

            st.subheader("Q3: What were the channels of damage?")
            st.markdown(
                "An illustrative waterfall decomposes the impact into deposits, AOCI, and equity divergence."
            )
            deposit_outflow = max(0.0, (1.0 - kbe_norm.min()) * 100)
            rate_change = (
                crisis_data["FF_Proxy"].iloc[-1] - crisis_data["FF_Proxy"].iloc[0]
            ) / 100.0
            bond_loss = calculate_bond_portfolio_loss(
                base_value=60.0, rate_change=rate_change, duration=duration
            )
            aoci_loss = abs(bond_loss)
            equity_divergence = max(0.0, (kbe_norm.iloc[-1] - iat_norm.iloc[-1]) * 100)
            total_impact = deposit_outflow + aoci_loss + equity_divergence
            fig_waterfall = go.Figure(
                go.Waterfall(
                    orientation="v",
                    measure=["relative", "relative", "relative", "total"],
                    x=["Deposit Outflow", "AOCI Loss", "Equity Divergence", "Total Impact"],
                    y=[deposit_outflow, aoci_loss, equity_divergence, total_impact],
                )
            )
            fig_waterfall.update_layout(
                title="Illustrative Impact Decomposition",
                yaxis_title="Impact (pts)",
                template="plotly_white",
            )
            st.plotly_chart(fig_waterfall, width="stretch")
            st.markdown(
                "**Waterfall framing:** the damage compounded in sequence as deposit flight exposed bond losses and then widened the equity penalty for regionals."
            )

            st.subheader("Q4: What would have reduced the damage?")
            st.markdown(
                "We run simple counterfactuals to show which balance-sheet choices would have softened the shock."
            )
            counterfactuals = {
                "Lower duration": counterfactual_channel_impact(
                    deposit_outflow=deposit_outflow,
                    rate_change=rate_change,
                    duration=2.0,
                    deposit_friction=0.2,
                ),
                "Higher stickiness": counterfactual_channel_impact(
                    deposit_outflow=deposit_outflow,
                    rate_change=rate_change,
                    duration=duration,
                    deposit_friction=0.6,
                ),
                "Less concentrated system": counterfactual_channel_impact(
                    deposit_outflow=max(deposit_outflow * 0.7, 0.0),
                    rate_change=rate_change,
                    duration=duration,
                    deposit_friction=0.3,
                ),
            }
            st.dataframe(pd.DataFrame(counterfactuals).T, width="stretch")
            st.markdown(
                "**What to notice:** lower duration and stickier deposits shrink the crisis path before equity divergence spirals."
            )

            st.subheader("Takeaway")
            st.markdown(
                "**The 2023 episode shows how fast liquidity outflows and AOCI losses can propagate into equity stress.**"
            )
            st.markdown(
                "**Research takeaway:** March 2023 exposed where the canonical channel became nonlinear."
            )
            st.markdown(
                "**Investor takeaway:** Large-bank resilience and regional fragility reflected very different funding narratives."
            )
            st.markdown(
                "**Policy/risk takeaway:** Lower duration and more stable deposits are complementary crisis-mitigation levers."
            )
        else:
            st.warning("Crisis period data not available in current fetch.")

    # Re-add the Risk Test here or as an expander
    st.divider()
    st.subheader("Stress Test Simulation")
    if st.button("🚀 Run 1,000 Trial Stress Test"):
        trials = run_monte_carlo_simulation(fed_funds_rate, market_power, base_volume, elasticity)
        fig_hist = px.histogram(
            trials,
            nbins=50,
            title="Distribution of Projected Deposit Volume ($B)",
            labels={"value": "Deposit Volume ($B)"},
            color_discrete_sequence=["#2ca02c"],
        )
        fig_hist.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig_hist, width="stretch")
        var_95 = np.percentile(trials, 5)
        st.metric(
            "95% VaR Volume",
            f"${var_95:,.0f}B",
            delta=f"-{(base_volume - var_95) / base_volume * 100:.1f}% Risk",
        )

with tab5:
    st.header("Monitoring & Scenarios")
    st.markdown("Use this section to track live signals and frame forward-looking stress cases.")
    monitoring_frame = pd.DataFrame()
    if not merged.empty:
        monitoring_frame = merged[
            (merged.index >= pd.to_datetime(start_date))
            & (merged.index <= pd.to_datetime(end_date))
        ].copy()

    st.subheader("Signal Scorecard")
    scorecard_col1, scorecard_col2, scorecard_col3, scorecard_col4, scorecard_col5 = st.columns(5)
    stress_value = "N/A"
    stress_delta = None
    beta_value = "N/A"
    beta_delta = None
    curve_value = "N/A"
    curve_delta = None
    mmf_value = "N/A"
    mmf_delta = None
    credit_value = "N/A"
    credit_delta = None

    if monitoring_frame.empty:
        scorecard_col1.metric("Stress composite", "N/A")
        scorecard_col2.metric("Bank beta regime", "N/A")
        scorecard_col3.metric("Curve regime", "N/A")
        scorecard_col4.metric("MMF pressure", "N/A")
        scorecard_col5.metric("Credit stress trend", "N/A")
        st.caption("Scorecard updates when the selected timeframe has overlapping market data.")
    else:
        scorecard_frame = monitoring_frame.copy()
        scorecard_frame["d_ff"] = scorecard_frame["FF_Proxy"].diff()
        scorecard_frame["r_vix"] = calculate_returns(scorecard_frame["VIX"])

        stress_latest = _build_recent_stress_series(scorecard_frame)
        if not stress_latest.empty:
            latest_stress = stress_latest.iloc[-1]
            stress_value = f"{latest_stress:.2f}"
            stress_delta = "Elevated" if latest_stress >= 0.75 else "Normal"

        beta_frame = scorecard_frame[["FF_Proxy", "KBE"]].copy()
        beta_frame["r_kbe"] = beta_frame["KBE"].pct_change()
        beta_frame["d_ff"] = beta_frame["FF_Proxy"].diff()
        beta_frame = beta_frame.dropna()
        latest_bank_beta, bank_beta_regime = _recent_beta_regime(beta_frame)
        if latest_bank_beta is not None and bank_beta_regime is not None:
            beta_value = bank_beta_regime
            beta_delta = f"β={latest_bank_beta:.2f}"

        curve_frame = pd.DataFrame()
        if not ff_proxy.empty and not tnx_proxy.empty:
            curve_frame = ff_proxy.join(tnx_proxy, lsuffix="_ff", rsuffix="_tnx").dropna()
            curve_frame.columns = ["FF_Proxy", "Ten_Year"]
            curve_frame = curve_frame[
                (curve_frame.index >= pd.to_datetime(start_date))
                & (curve_frame.index <= pd.to_datetime(end_date))
            ].copy()
            if not curve_frame.empty:
                curve_slope = calculate_yield_curve_slope(
                    curve_frame["Ten_Year"], curve_frame["FF_Proxy"]
                )
                curve_regimes = classify_curve_regime(curve_slope).dropna()
                if not curve_regimes.empty:
                    curve_value = curve_regimes.iloc[-1]
                    curve_delta = f"10Y-3M={curve_slope.dropna().iloc[-1]:.2f}"

        mmf_frame = pd.DataFrame()
        if not ff_proxy.empty and not mmf_proxy.empty:
            mmf_frame = ff_proxy.join(mmf_proxy, lsuffix="_ff", rsuffix="_mmf").dropna()
            mmf_frame.columns = ["FF_Proxy", "MMF_Price"]
            mmf_frame = mmf_frame[
                (mmf_frame.index >= pd.to_datetime(start_date))
                & (mmf_frame.index <= pd.to_datetime(end_date))
            ].copy()
            mmf_trend, mmf_horizon = _recent_change(mmf_frame["MMF_Price"])
            if not np.isnan(mmf_trend):
                mmf_value = "Pressure building" if mmf_trend > 0 else "Pressure easing"
                mmf_delta = f"{mmf_horizon}d={mmf_trend:+.1%}"

        credit_frame = pd.DataFrame()
        if not ff_proxy.empty and not lqd_proxy.empty:
            credit_frame = ff_proxy.join(lqd_proxy, lsuffix="_ff", rsuffix="_lqd").dropna()
            credit_frame.columns = ["FF_Proxy", "Credit_Price"]
            credit_frame = credit_frame[
                (credit_frame.index >= pd.to_datetime(start_date))
                & (credit_frame.index <= pd.to_datetime(end_date))
            ].copy()
            credit_trend, credit_horizon = _recent_change(credit_frame["Credit_Price"])
            credit_trend = -credit_trend
            if not np.isnan(credit_trend):
                credit_value = "Stress rising" if credit_trend > 0 else "Stress easing"
                credit_delta = f"{credit_horizon}d={credit_trend:+.1%}"

        scorecard_col1.metric("Stress composite", stress_value, delta=stress_delta)
        scorecard_col2.metric("Bank beta regime", beta_value, delta=beta_delta)
        scorecard_col3.metric("Curve regime", curve_value, delta=curve_delta)
        scorecard_col4.metric("MMF pressure", mmf_value, delta=mmf_delta)
        scorecard_col5.metric("Credit stress trend", credit_value, delta=credit_delta)
        st.caption(
            "Read left to right: stress, bank beta, curve, MMFs, and credit should align before the regime turns persistent."
        )

    st.subheader("Scenario Cards")

    def render_scenario_card(
        title: str,
        research_takeaway: str,
        investor_takeaway: str,
        policy_takeaway: str,
    ) -> None:
        expectations = scenario_expectations(title)
        st.markdown(f"#### {title}")
        st.markdown(
            f"**Spreads | Deposits | Stress | Banks**\n\n{expectations['spreads']} | {expectations['deposits']} | {expectations['stress']} | {expectations['banks']}"
        )
        st.markdown(f"**Research takeaway:** {research_takeaway}")
        st.markdown(f"**Investor takeaway:** {investor_takeaway}")
        st.markdown(f"**Policy/risk takeaway:** {policy_takeaway}")

    scenario_col1, scenario_col2 = st.columns(2)
    scenario_specs = [
        (
            "Higher for longer",
            "Watch whether spread widening persists even after growth slows.",
            "Favor banks with stickier deposits and shorter-duration securities books.",
            "Prepare for liquidity fatigue rather than a one-day event shock.",
        ),
        (
            "Volatility shock",
            "Separate flow-driven stress from a pure repricing episode.",
            "Expect regional-bank beta to gap wider than broad-bank beta.",
            "Tighten surveillance when volatility spills into deposit behavior.",
        ),
        (
            "Rapid cuts",
            "Test whether easing repairs funding faster than it repairs earnings.",
            "Relief rallies are strongest where unrealized losses were the main overhang.",
            "Rate relief helps most when paired with clear liquidity signaling.",
        ),
        (
            "Bank-specific confidence shock",
            "Treat confidence breaks as nonlinear jumps, not smooth beta moves.",
            "Underwrite name-specific funding resilience, not just sector averages.",
            "Response speed matters more than broad easing when trust is the trigger.",
        ),
    ]

    with scenario_col1:
        for title, research_takeaway, investor_takeaway, policy_takeaway in scenario_specs[:2]:
            render_scenario_card(title, research_takeaway, investor_takeaway, policy_takeaway)

    with scenario_col2:
        for title, research_takeaway, investor_takeaway, policy_takeaway in scenario_specs[2:]:
            render_scenario_card(title, research_takeaway, investor_takeaway, policy_takeaway)

    st.subheader("If this, then that playbook")

    def render_playbook_rule(
        rule: str, research_takeaway: str, investor_takeaway: str, policy_takeaway: str
    ) -> None:
        st.markdown(
            f"**{rule}**\n\n"
            f"**Research takeaway:** {research_takeaway}\n"
            f"**Investor takeaway:** {investor_takeaway}\n"
            f"**Policy/risk takeaway:** {policy_takeaway}"
        )

    render_playbook_rule(
        "If rates rise while VIX stays low: expect orderly spread widening before panic.",
        "Orderly widening usually appears before fear is visible in volatility.",
        "Prefer names that can reprice deposits without losing franchise stability.",
        "Use calm volatility as a signal to watch spreads before stress is obvious.",
    )
    render_playbook_rule(
        "If rates are stable but VIX spikes: expect fear to dominate rate mechanics.",
        "Volatility shocks can overwhelm an otherwise stable rate backdrop.",
        "Reduce exposure where sentiment can outrun fundamentals.",
        "Treat elevated volatility as a funding-confidence issue even without a rate move.",
    )
    render_playbook_rule(
        "If the curve steepens through cuts: expect temporary relief in funding stress.",
        "Curve steepening from easing can buy time for balance sheets that were under pressure.",
        "Look for relief, but do not mistake it for a fully repaired franchise.",
        "Use easing windows to reinforce liquidity backstops before stress returns.",
    )
    render_playbook_rule(
        "If MMFs outperform while bank betas stay negative: treat that as an active-channel warning.",
        "MMF outperformance alongside negative bank beta says the deposit trade is still live.",
        "Favor banks with stickier funding and less reliance on hot money.",
        "Treat the combination as an active migration signal, not a benign rotation.",
    )

st.divider()
with st.expander("Reference: Drechsler, Savov & Schnabl (2017)"):
    st.latex(r"Spread_i = f - r^d_i = \alpha_i + \beta_i f + \epsilon_i")
    st.markdown("""
    The "Smoking Gun" evidence in the paper shows that the coefficient $\beta_i$ is significantly larger in markets 
    with high HHI (bank concentration). This dashboard allows you to stress test that assumption.
    """)
