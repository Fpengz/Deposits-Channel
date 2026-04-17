import html
import warnings
from collections.abc import Callable
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

try:
    from src.analysis import (
        build_beta_heatmap,
        build_combined_stress_grid,
        build_stress_index,
        calculate_bond_portfolio_loss,
        calculate_correlation_matrix,
        calculate_cross_correlation,
        calculate_irf,
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
    from src.data_fetcher import (
        get_proxy_10y_yield,
        get_proxy_credit_ig,
        get_proxy_deposits,
        get_proxy_fed_funds,
        get_proxy_market,
        get_proxy_mmf,
        get_proxy_regional_banks,
        get_proxy_volatility,
    )
    from src.simulation import (
        calculate_deposit_rate,
        calculate_deposit_volume,
        counterfactual_channel_impact,
        generate_deposit_paths,
        generate_rate_paths,
    )
except ImportError:
    from analysis import (
        build_beta_heatmap,
        build_combined_stress_grid,
        build_stress_index,
        calculate_bond_portfolio_loss,
        calculate_correlation_matrix,
        calculate_cross_correlation,
        calculate_irf,
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

VISUAL_SYSTEM_CSS = """
<style>
:root {
    --page-bg: #f6f3ee;
    --panel-bg: #fbfaf7;
    --panel-border: #d8d2c6;
    --ink: #1f1f1c;
    --muted: #5d5a55;
    --accent: #2f5d50;
    --accent-soft: #dce8e1;
}

.seminar-banner {
    padding: 1.25rem 1.5rem;
    border: 1px solid var(--panel-border);
    background: linear-gradient(180deg, #fcfbf8 0%, #f2eee6 100%);
    border-radius: 18px;
    margin-bottom: 1.2rem;
}

.diagnostic-band {
    padding: 1rem 1.1rem;
    border: 1px solid var(--panel-border);
    background: var(--panel-bg);
    border-radius: 16px;
    margin: 1rem 0 1.4rem;
}

.research-module {
    padding: 1rem 1.1rem;
    border-left: 4px solid var(--accent);
    background: #fcfbf8;
    border-radius: 14px;
    margin: 1rem 0 1.25rem;
}

.tab-purpose-strip {
    padding: 0.95rem 1.05rem;
    border: 1px solid var(--panel-border);
    border-left: 4px solid var(--accent);
    background: var(--panel-bg);
    border-radius: 14px;
    margin: 0.85rem 0 1.1rem;
}

.takeaway-block {
    padding: 1rem 1.1rem;
    background: var(--accent-soft);
    border-radius: 14px;
    border: 1px solid #bfd0c7;
    margin-top: 1rem;
}

.module-kicker {
    color: var(--muted);
    font-size: 0.92rem;
    margin-bottom: 0.35rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.short-answer {
    font-weight: 600;
    color: var(--ink);
}
</style>
"""

st.markdown(VISUAL_SYSTEM_CSS, unsafe_allow_html=True)


def render_seminar_banner(title: str, framing: str, short_answer: str) -> None:
    st.markdown(
        f"""
        <div class="seminar-banner">
          <div class="module-kicker">Research Seminar Module</div>
          <h2>{html.escape(title)}</h2>
          <p>{html.escape(framing)}</p>
          <p class="short-answer"><strong>Short answer:</strong> {html.escape(short_answer)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_diagnostic_band(
    title: str,
    summary: str,
    note: str | None = None,
    body: Callable[[], None] | None = None,
) -> None:
    note_html = (
        f'<p class="short-answer"><strong>Diagnostic note:</strong> {html.escape(note)}</p>'
        if note
        else ""
    )
    with st.container(border=True):
        st.markdown(
            f"""
            <div class="diagnostic-band">
              <div class="module-kicker">Diagnostic Band</div>
              <h3>{html.escape(title)}</h3>
              <p>{html.escape(summary)}</p>
              {note_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
        if body is not None:
            body()


def render_research_module_intro(title: str, why_it_matters: str) -> None:
    st.markdown(
        f"""
        <div class="research-module">
          <div class="module-kicker">Why this matters</div>
          <h3>{html.escape(title)}</h3>
          <p>{html.escape(why_it_matters)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_tab_purpose_strip(question: str, use_this_when: str, start_here: str) -> None:
    st.markdown(
        f"""
        <div class="tab-purpose-strip">
          <div class="module-kicker">Tab purpose</div>
          <p><strong>Question:</strong> {html.escape(question)}</p>
          <p><strong>Use this when:</strong> {html.escape(use_this_when)}</p>
          <p><strong>Start here:</strong> {html.escape(start_here)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_takeaway_block(text: str) -> None:
    st.markdown(
        f"""
        <div class="takeaway-block">
          <strong>Takeaway:</strong> {html.escape(text)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reading_preface(
    sample_start: date | pd.Timestamp, sample_end: date | pd.Timestamp
) -> None:
    sample_start_label = pd.to_datetime(sample_start).strftime("%b %d, %Y")
    sample_end_label = pd.to_datetime(sample_end).strftime("%b %d, %Y")
    st.markdown(
        f"""
        <div class="seminar-banner">
          <div class="module-kicker">How to read this terminal</div>
          <h2>How to read this terminal</h2>
          <p>Start here: read the opening mechanism, then use the selected sample in the sidebar as the common frame for the evidence below.</p>
          <p>Sample context: the current sample runs from {html.escape(sample_start_label)} to {html.escape(sample_end_label)}. If a panel says the data are unavailable, treat that as a coverage note for this sample rather than a change in the underlying story.</p>
          <p class="short-answer"><strong>Question:</strong> Which part of the deposits channel is under pressure in the selected sample?</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.title("The Deposits Channel: Macro-Finance Terminal v4.0")

# Sidebar Navigation & Global Filters
st.sidebar.title("Terminal Controls")
st.sidebar.divider()
st.sidebar.subheader("Global Timeframe")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2018-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

render_reading_preface(start_date, end_date)
st.markdown("""
This terminal explores the mechanics of **Drechsler, Savov & Schnabl (2017)** across multiple asset classes.
Use the tabs below to explore the "Flow of Funds", Yield Curve interactions, and recent banking stress.
""")

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
            window=min(5, len(recent)),
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
            if isinstance(recent.index, pd.DatetimeIndex):
                horizon = (recent.index[-1] - recent.index[0]).days
            else:
                horizon = len(recent)
            return last / first - 1, horizon
    return np.nan, 0


with tab1:
    render_seminar_banner(
        "Theory & Simulation",
        "Start with the mechanism, then move through pass-through, deposit sensitivity, scenarios, and the destabilization threshold.",
        "Policy tightening matters when banks can keep deposit rates sticky while alternatives become more attractive.",
    )
    render_tab_purpose_strip(
        "How does the deposits channel work in theory?",
        "You want the mechanism before the empirical evidence or scenario close.",
        "Start with the opening diagnostic, then read Q1 before the simulation panels.",
    )
    st.markdown(
        "We begin with the mechanism, then move through pass-through, deposit sensitivity, scenarios, and the destabilization threshold."
    )

    render_diagnostic_band(
        "Opening diagnostic",
        "The first read is the gap between rates, deposit pricing, and volume before the scenario surface expands.",
        "The core metric band later in the tab turns that framing into live funding-pressure numbers.",
    )
    render_research_module_intro(
        "Q1: What is the deposits channel mechanism?",
        "This opening module states the mechanism clearly before the simulation turns it into visible pass-through and balance-sheet pressure.",
    )
    st.markdown(
        "By the end of this section, the reader should know which assumptions make the system fragile and why."
    )
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

    st.markdown(
        "The next step is pass-through: how much of a policy move reaches deposit pricing before the volume response begins."
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

    render_research_module_intro(
        "Q2: How sensitive is the mechanism to assumptions?",
        "This module tests whether market power and depositor elasticity make the same rate shock bite harder or softer.",
    )

    def render_core_metric_surface() -> None:
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

    render_diagnostic_band(
        "Core metric band",
        "This row condenses the live simulation into a quick read on policy, deposits, and the balance-sheet buffer.",
        "Use it as the opening diagnostic before the scenario charts deepen the evidence.",
        body=render_core_metric_surface,
    )
    st.markdown(
        "This pass-through step varies market power and depositor elasticity to see where spreads bite most."
    )

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
    st.markdown(
        "**What to notice:** concentrated banks sit farther below full pass-through, so the policy shock is absorbed by depositors unevenly."
    )

    render_research_module_intro(
        "Q3: What happens under plausible rate paths?",
        "The path simulation shows that identical starting conditions can diverge quickly once rates and elasticity move together.",
    )
    st.markdown(
        "Now we move to deposit sensitivity: nine simulated paths map policy uncertainty into funding outcomes."
    )
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
    st.markdown(
        "**What to notice:** the same rate path can produce very different deposit trajectories once elasticity shifts the curve's steepness."
    )

    render_research_module_intro(
        "Q4: How do rate changes impact AOCI?",
        "Duration losses are the bridge between rates and capital; this module shows when mark-to-market pain arrives before deposits visibly run.",
    )
    st.markdown(
        "The scenario step adds duration risk, translating rate changes into unrealized losses on bank bond portfolios."
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
    st.markdown(
        "**What to notice:** rate-path scenarios matter because bond losses can arrive even before deposit outflows fully show up."
    )

    render_research_module_intro(
        "Q5: When do outflows and AOCI become destabilizing?",
        "This threshold view shows how the channel tips from friction into stress once runoff and duration losses compound.",
    )
    st.markdown(
        "This is the destabilization threshold: outflow pressure becomes more dangerous when unrealized bond losses are already eating into capital. "
        "The grid marks the zone where deposit runoff and AOCI losses combine into a stress pocket."
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
    render_takeaway_block(
        "The channel becomes dangerous when partial pass-through, high elasticity, and duration losses line up at the same time."
    )

with tab2:
    render_seminar_banner(
        "Empirical Terminal",
        "Open with the signal board, then move from regime identification into event evidence, fear amplification, and propagation.",
        "The deposits channel is clearest when rate shocks, volatility, and bank drawdowns line up.",
    )
    render_tab_purpose_strip(
        "What does the selected sample say about deposits-channel stress?",
        "You want the live evidence board before jumping back to theory or forward to scenarios.",
        "Start with the signal board, then use the regime summary to anchor the sample.",
    )
    render_diagnostic_band(
        "Empirical opening",
        "This tab starts with the live diagnostic question: are rate sensitivity and stress lining up into a channel regime?",
        "The signal board below is the first synthesis point before the empirical tests fan out.",
    )
    st.markdown(
        "We open the empirical tab as a research seminar: first the signal board, then regime identification, event evidence, fear amplification, and propagation."
    )
    st.markdown(
        "Each section asks a market question, then answers it with data, with transitions that follow the evidence from the signal board to the downstream tests."
    )

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
            st.warning(
                "The selected timeframe leaves no overlapping observations, so the empirical board cannot be assembled."
            )
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
                    "The selected timeframe does not leave enough aligned return and rate observations to estimate the empirical panel cleanly."
                )
            else:
                # Q1. Market Evolution
                render_research_module_intro(
                    "Q1: Are banks sensitive to rate shocks?",
                    "The first empirical module checks whether bank returns actually move with rate shocks before we interpret any regime story.",
                )
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
                st.subheader("Q1: Interest Rate Betas")
                res_kbe = run_ols_regression(data, "r_kbe", "d_ff")
                res_spy = run_ols_regression(data, "r_spy", "d_ff")

                def render_rate_beta_surface() -> None:
                    col1, col2 = st.columns(2)
                    col1.metric("Bank Beta", f"{res_kbe.params['d_ff']:.4f}")
                    col2.metric("Market Beta", f"{res_spy.params['d_ff']:.4f}")
                    st.caption(
                        "Lower (more negative) Beta means the sector is more sensitive to rate hikes. Banks typically show higher sensitivity."
                    )

                render_diagnostic_band(
                    "Interest rate betas",
                    "This live read compares the bank and market response to rate shocks before the regime test zooms in.",
                    "The beta pair is the empirical surface, not just a lead-in sentence.",
                    body=render_rate_beta_surface,
                )

                # Q4. Sensitivity Stability
                render_research_module_intro(
                    "Q4: Is sensitivity stable over time?",
                    "Recursive betas check whether rate exposure drifts as the market moves between calmer and more stressed periods.",
                )
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
                render_research_module_intro(
                    "Q2: Is stress building in the system?",
                    "This module tests whether rates, volatility, and bank drawdowns are already accumulating into a channel-wide signal.",
                )
                st.markdown(
                    "We combine rate shocks, volatility, and bank drawdowns into one signal, then use that signal to anchor the rest of the seminar."
                )
                data["r_vix"] = calculate_returns(data["VIX"])
                stress = build_stress_index(
                    data["d_ff"], data["r_vix"], data["KBE"], window=252, smoothing=5
                )
                if stress.dropna().empty:
                    st.warning(
                        "The empirical board and stress composite could not be assembled for this sample, so the signal board and regime summary are unavailable."
                    )
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

                    def render_signal_board_surface() -> None:
                        st.subheader("Signal Board")
                        st.markdown(
                            "With the board in hand, the next question is whether the channel is merely active or fully in a transmission regime."
                        )
                        board_col1, board_col2, board_col3 = st.columns(3)
                        board_col1.metric("Channel State", channel_state)
                        board_col2.metric("Latest Stress", f"{latest_stress:.2f}")
                        board_col3.metric("Latest Bank Beta", f"{latest_bank_beta:.4f}")
                        st.caption(
                            "What to notice: a move from Dormant to Active or Stressed means rate sensitivity is broadening into a regime signal."
                        )

                    render_diagnostic_band(
                        "Signal board",
                        "The latest stress, beta, and relative performance summary gives the first regime read before the event tests continue.",
                        "When the board turns more active, the seminar shifts from description to transmission evidence.",
                        body=render_signal_board_surface,
                    )
                    render_research_module_intro(
                        "Q8: Which regime are we in?",
                        "This summary translates the signal board into a regime label before the downstream event and propagation evidence continue.",
                    )
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
                    st.markdown(
                        "Once the regime is visible, the next check is whether policy events leave abnormal footprints in bank and market returns."
                    )

                # Q3. Policy Event Impact
                render_research_module_intro(
                    "Q3: Do policy events create abnormal returns?",
                    "Event studies test whether FOMC dates produce footprints that are different from ordinary market noise.",
                )
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
                        "The event window does not contain enough aligned observations to estimate average CARs for the selected period."
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

                # Q4 continued: Rolling Beta Heatmap
                st.subheader("Q4: Rolling Beta Heatmap")
                beta_kbe = calculate_rolling_beta(data, "r_kbe", "d_ff", window=252)
                beta_iat = calculate_rolling_beta(data, "r_iat", "d_ff", window=252)
                beta_spy = calculate_rolling_beta(data, "r_spy", "d_ff", window=252)
                beta_df = pd.DataFrame({"KBE": beta_kbe, "IAT": beta_iat, "SPY": beta_spy}).dropna()
                if beta_df.empty:
                    st.warning(
                        "The rolling window is too sparse to support a stable beta surface in this period."
                    )
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
                render_research_module_intro(
                    "Q5: Does fear amplify the channel?",
                    "This split asks whether volatility makes the same rate shock more potent for bank returns.",
                )
                st.markdown(
                    "We split betas by high vs low VIX to test whether market fear makes the channel materially stronger."
                )
                high_vix = data[data["VIX"] > 20]
                low_vix = data[data["VIX"] <= 20]

                if not high_vix.empty and not low_vix.empty:
                    res_high = run_ols_regression(high_vix, "r_kbe", "d_ff")
                    res_low = run_ols_regression(low_vix, "r_kbe", "d_ff")

                    def render_fear_split_surface() -> None:
                        col1, col2 = st.columns(2)
                        col1.metric("Beta (VIX > 20)", f"{res_high.params['d_ff']:.4f}")
                        col2.metric("Beta (VIX <= 20)", f"{res_low.params['d_ff']:.4f}")
                        st.caption(
                            "A more negative Beta during high VIX confirms that Deposits Channel risks are amplified during market stress."
                        )

                    render_diagnostic_band(
                        "Fear split",
                        "This surface compares high- and low-volatility beta estimates before the propagation test takes over.",
                        "The split is the diagnostic surface, not just a transition sentence.",
                        body=render_fear_split_surface,
                    )
                    st.markdown(
                        "The fear split closes the event test by showing whether stress changes the strength of the same rate response."
                    )

                # Q6. Shock Propagation
                render_research_module_intro(
                    "Q6: How do shocks propagate over time?",
                    "Impulse responses show whether the channel diffuses quickly or keeps working through the system over multiple days.",
                )
                st.markdown(
                    "Impulse responses trace the shock ripple over the next 20 trading days, letting us see how quickly the channel travels through the system."
                )
                irf_kbe = calculate_irf(data, "r_kbe", "d_ff", periods=20)
                irf_iat = calculate_irf(data, "r_iat", "d_ff", periods=20)

                if irf_kbe is None or irf_iat is None:
                    st.warning(
                        "The impulse-response model cannot be fit cleanly in this window, so the propagation path remains underidentified."
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
                render_research_module_intro(
                    "Q7: How do the variables co-move?",
                    "The correlation surface checks whether the system behaves as a connected channel or as a set of unrelated indicators.",
                )
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

                render_takeaway_block(
                    "Bank sensitivity to rates spikes in stress regimes and clusters around policy events."
                )

with tab3:
    render_seminar_banner(
        "Macro & Credit",
        "Trace proxy evidence from deposits into the broader macro and credit system, then interpret the downstream pressure through the curve and credit lens.",
        "The deposit and MMF comparisons are proxy-based, while the curve and credit read-throughs are interpretive.",
    )
    render_tab_purpose_strip(
        "How do macro and credit proxies map back to the channel?",
        "You want a cross-market interpretation after the empirical tab identifies pressure.",
        "Begin with the proxy comparison, then read the curve and credit blocks.",
    )
    render_diagnostic_band(
        "Macro opening",
        "This tab opens by comparing deposit migration proxies before translating them into curve and credit read-throughs.",
        "Use the regime matrix as the compact macro summary once the opening comparison lands.",
    )
    st.markdown(
        "Trace proxy evidence from deposits into the broader macro and credit system: the opening comparison looks at bank-vs-MMF behavior, then the curve and credit sections interpret the downstream pressure."
    )

    if not ff_proxy.empty and not mmf_proxy.empty and not tnx_proxy.empty and not kbe_proxy.empty:
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
        render_research_module_intro(
            "Q1: Where do deposits go when spreads widen?",
            "The first macro module asks whether deposit migration is visible in the bank-versus-MMF proxy relationship.",
        )
        st.markdown(
            "We proxy flows by comparing bank equities to money market funds; this is the observable stand-in for deposit migration, not a literal flow measure."
        )
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

        st.subheader("Q1: Banks vs MMFs (Relative Performance)")
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
        render_research_module_intro(
            "Q2: What macro regime are we in?",
            "The curve regime anchors the macro story by showing whether the funding backdrop is normal, squeezed, or under stress.",
        )
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

        render_diagnostic_band(
            "Macro regime band",
            "The matrix translates curve slope and credit stress into one compact read on whether the system is normal, squeezed, stressed, or in crisis.",
            "Use this as the macro summary before the downstream credit section.",
        )
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
        render_takeaway_block(
            "The regime matrix links rates, flows, and credit into one narrative state."
        )
        st.subheader("Audience Takeaways")
        st.markdown(
            "- Investors: the move from Squeeze to Stress is where bank equity downside typically accelerates.\n"
            "- Policy/risk users: crisis conditions call for tighter liquidity surveillance and faster confidence backstops."
        )
        st.markdown(
            "The credit section below is a downstream consequence of this earlier flow-of-funds story: once deposits leak toward MMFs and the curve compresses, credit conditions usually tighten afterward."
        )

with tab3:
    st.divider()
    render_research_module_intro(
        "Q3: Is credit stress feeding back into banks?",
        "Credit stress closes the loop by testing whether downstream pressure is showing up in bank returns.",
    )
    st.markdown("We compare daily credit stress moves to bank returns.")

    if (
        not ff_proxy.empty
        and not lqd_proxy.empty
        and not spy_proxy.empty
        and not kbe_proxy.empty
        and not iat_proxy.empty
    ):
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

        st.subheader("Q3: Credit Stress vs Bank Returns")
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

        render_takeaway_block(
            "When rates rise, deposits shift toward MMFs, the curve compresses, and credit stress feeds back into bank equity."
        )

with tab4:
    render_seminar_banner(
        "Case Study: March 2023 Banking Stress",
        "Work through preconditions, break, market interpretation, and counterfactual repair as a compact narrative arc.",
        "March 2023 broke when rate-sensitive funding met unrealized losses and the market treated the move as a confidence event.",
    )
    render_tab_purpose_strip(
        "What changed in the break, and what would have changed the outcome?",
        "You want a narrative comparison between the observed episode and the counterfactual path.",
        "Start with the break chronology, then use the counterfactual controls to test the story.",
    )
    render_diagnostic_band(
        "Case opening",
        "The crisis narrative is organized as evidence, not just chronology: preconditions, break, market interpretation, then repair.",
        "The counterfactuals below test which balance-sheet choices would have changed the outcome.",
    )
    st.markdown(
        "We open this case as a compact narrative arc: preconditions, break, market interpretation, and counterfactual repair."
    )
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
            render_research_module_intro(
                "Q1: What conditions preceded the break?",
                "This opening module frames the crisis as a balance-sheet setup, not a one-day surprise.",
            )
            st.markdown(
                "The preconditions were rate pressure, large unrealized bond losses, and a funding base that could not absorb fast deposit outflows."
            )
            st.markdown(
                "The break came when regional banks diverged as deposit outflows and AOCI losses accelerated."
            )
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

            render_research_module_intro(
                "Q2: How did the market interpret the break?",
                "This module shows how the selloff and divergence turned a balance-sheet event into a confidence story.",
            )
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

            render_research_module_intro(
                "Q3: How does market interpretation map back to channel mechanics?",
                "The waterfall turns the narrative back into mechanics by decomposing the visible damage into deposits, AOCI, and equity divergence.",
            )
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

            render_research_module_intro(
                "Q4: What would have changed the outcome?",
                "The counterfactuals test whether the crisis was mostly about duration, stickiness, or concentration.",
            )
            st.markdown(
                "We run simple counterfactuals to show which balance-sheet choices would have changed the outcome, not just softened the optics after the fact."
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
                "**What to notice:** lower duration would have reduced mark-to-market losses, stickier deposits would have slowed the run, and a less concentrated system would have weakened the feedback loop."
            )

            render_takeaway_block(
                "The 2023 episode shows how fast liquidity outflows and AOCI losses can propagate into equity stress."
            )
            st.subheader("Audience Takeaways")
            st.markdown(
                "- Researchers: March 2023 exposed where the canonical channel became nonlinear.\n"
                "- Investors: large-bank resilience and regional fragility reflected very different funding narratives.\n"
                "- Policy/risk users: lower duration and more stable deposits are complementary crisis-mitigation levers."
            )
        else:
            st.warning("Crisis period data not available in current fetch.")

    # Re-add the Risk Test here or as an expander
    st.divider()
    render_research_module_intro(
        "Stress Test Simulation",
        "The final check turns the crisis lesson into a Monte Carlo distribution of possible deposit outcomes.",
    )
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
    render_seminar_banner(
        "Monitoring & Scenarios",
        "Close the seminar by turning live signals into a practical reading order: scorecard first, scenarios second, playbook last.",
        "The five-metric scorecard is an opening diagnostic, not a verdict.",
    )
    render_tab_purpose_strip(
        "Which stress conditions should you monitor now?",
        "You want a compact watchlist and scenario playbook at the end of the terminal.",
        "Start with the scorecard, then read the playbook beneath the stress surfaces.",
    )
    render_diagnostic_band(
        "Monitoring opening",
        "The scorecard compresses stress, beta, curve, MMF pressure, and credit stress into one live reading before the scenarios and playbook.",
        "Treat it as the first triage layer for the seminar close.",
    )
    st.markdown(
        "We close the seminar by turning live signals into a practical reading order: scorecard first, scenarios second, playbook last."
    )
    monitoring_frame = pd.DataFrame()
    if not merged.empty:
        monitoring_frame = merged[
            (merged.index >= pd.to_datetime(start_date))
            & (merged.index <= pd.to_datetime(end_date))
        ].copy()

    def render_scorecard_surface() -> None:
        st.subheader("Signal Scorecard")
        scorecard_col1, scorecard_col2, scorecard_col3, scorecard_col4, scorecard_col5 = st.columns(
            5
        )
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
            st.markdown(
                "**What to notice:** without overlapping market data, the scorecard cannot support a regime read, so the seminar close stays at the diagnostic stage."
            )
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
            st.markdown(
                "**What to notice:** the board matters most when stress, bank beta, curve, MMFs, and credit all point the same way; any split says the channel is still forming rather than fully settled."
            )

    render_diagnostic_band(
        "Monitoring opening",
        "The scorecard compresses stress, beta, curve, MMF pressure, and credit stress into one live reading before the scenarios and playbook.",
        "Treat it as the first triage layer for the seminar close.",
        body=render_scorecard_surface,
    )

    render_research_module_intro(
        "Scenario Cards",
        "The scenario module translates the scorecard into forward-looking checks on how the channel could behave next.",
    )
    st.markdown(
        "These scenarios are the seminar close in compact form: each card turns the scorecard into a forward-looking check on how the channel could behave next."
    )

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

    render_research_module_intro(
        "If this, then that playbook",
        "The playbook turns the seminar close into a small set of decision rules that can be applied when the channel starts moving again.",
    )

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

    render_takeaway_block(
        "Researchers should use the scorecard to classify the regime, investors should use the scenarios to pressure-test exposures, and policy users should use the playbook to decide when monitoring needs to tighten."
    )
    st.subheader("Audience Takeaways")
    st.markdown(
        "- Researchers: use the scorecard to classify the regime.\n"
        "- Investors: use the scenarios to pressure-test exposures.\n"
        "- Policy users: use the playbook to decide when monitoring needs to tighten."
    )

st.divider()
with st.expander("Reference: Drechsler, Savov & Schnabl (2017)"):
    st.latex(r"Spread_i = f - r^d_i = \alpha_i + \beta_i f + \epsilon_i")
    st.markdown("""
    The "Smoking Gun" evidence in the paper shows that the coefficient $\beta_i$ is significantly larger in markets 
    with high HHI (bank concentration). This dashboard allows you to stress test that assumption.
    """)
