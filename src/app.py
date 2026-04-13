import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import statsmodels.api as sm
from simulation import calculate_deposit_rate, calculate_deposit_volume
from data_fetcher import get_proxy_fed_funds, get_proxy_deposits, get_proxy_regional_banks, get_proxy_market
from analysis import (
    run_ols_regression, 
    check_stationarity, 
    calculate_rolling_beta, 
    calculate_correlation_matrix,
    calculate_cross_correlation,
    detect_monetary_regimes,
    calculate_recursive_ols,
    run_monte_carlo_simulation
)

st.set_page_config(page_title="Deposits Channel Research Terminal", layout="wide")

st.title("The Deposits Channel: Research Terminal v3.0")
st.markdown("""
This terminal explores the mechanics of **Drechsler, Savov & Schnabl (2017)**. 
Use the tabs below to switch between theoretical modeling, empirical evidence, and risk stress tests.
""")

# Sidebar Navigation & Global Filters
st.sidebar.title("Terminal Controls")
st.sidebar.divider()
st.sidebar.subheader("Global Timeframe")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime('2018-01-01'))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime('today'))

# 3-Tab Structure
tab1, tab2, tab3 = st.tabs(["Theory & Simulation", "Empirical Terminal", "Risk Stress Test"])

with tab1:
    st.header("Theoretical Model")
    
    st.subheader("The Mechanism: From Rates to Lending")
    st.markdown(r"""
    ### 1. Fed Funds Rate ↑  $\longrightarrow$  2. Deposit Spread ↑  $\longrightarrow$  3. Deposit Outflow  $\longrightarrow$  4. Bank Lending ↓
    """)
    
    colA, colB, colC = st.columns(3)
    with colA:
        st.info("**1. Market Power**\n\nBanks in concentrated markets (high HHI) can keep deposit rates low even when the Fed hikes.")
    with colB:
        st.warning("**2. The Spread**\n\nThe 'price of liquidity' widens as banks widen the gap between what they earn and what they pay you.")
    with colC:
        st.success("**3. Transmission**\n\nAs deposits flow to Money Market Funds, banks lose their cheapest source of funding and must cut lending.")

    st.divider()
    
    # Sidebar for simulation controls
    st.sidebar.header("Simulation Parameters")
    fed_funds_rate = st.sidebar.slider("Fed Funds Rate (%)", 0.0, 10.0, 5.0, 0.25) / 100.0
    market_power = st.sidebar.slider("Bank Market Power (0 to 1)", 0.0, 1.0, 0.5, 0.1)
    elasticity = st.sidebar.slider("Depositor Elasticity", 1.0, 20.0, 10.0, 1.0)
    base_volume = 10000.0

    # Calculate theoretical values
    dep_rate = calculate_deposit_rate(fed_funds_rate, market_power)
    spread = fed_funds_rate - dep_rate
    volume = calculate_deposit_volume(base_volume, spread, elasticity)

    col1, col2, col3 = st.columns(3)
    col1.metric("Fed Funds Rate", f"{fed_funds_rate*100:.2f}%")
    col2.metric("Deposit Rate", f"{dep_rate*100:.2f}%", f"-{spread*100:.2f}% spread")
    col3.metric("Total Deposits", f"${volume:,.0f}B")

    # Static plot for simulation
    rates = [r/100.0 for r in range(0, 1000, 25)]
    volumes = [calculate_deposit_volume(base_volume, r - calculate_deposit_rate(r, market_power), elasticity) for r in rates]

    fig = go.Figure(data=go.Scatter(x=[r*100 for r in rates], y=volumes, mode='lines', name='Theoretical Volume', line=dict(color='#1f77b4', width=3)))
    fig.add_vline(x=fed_funds_rate*100, line_dash="dash", line_color="#ff7f0e", annotation_text="Current Rate")
    fig.update_layout(title="Theoretical Deposit Volume vs Fed Funds Rate", xaxis_title="Fed Funds Rate (%)", yaxis_title="Deposit Volume ($B)", template="plotly_white")
    st.plotly_chart(fig, width='stretch')

    st.divider()
    st.subheader("Interactive Heatmap: Deposit Spreads")
    ff_range = np.linspace(0, 0.1, 20)
    mp_range = np.linspace(0, 1.0, 20)
    spreads = np.array([[f * mp * 100 for mp in mp_range] for f in ff_range])
    fig_heat_sim = px.imshow(spreads, x=[f"{mp:.1f}" for mp in mp_range], y=[f"{f*100:.1f}%" for f in ff_range], labels=dict(x="Bank Market Power", y="Fed Funds Rate (%)", color="Spread (%)"), color_continuous_scale='Viridis', aspect="auto")
    fig_heat_sim.update_layout(template="plotly_white")
    st.plotly_chart(fig_heat_sim, width='stretch')

with tab2:
    st.header("Empirical Terminal")
    
    with st.spinner("Fetching terminal data..."):
        ff_proxy = get_proxy_fed_funds()
        kbe_proxy = get_proxy_deposits()
        iat_proxy = get_proxy_regional_banks()
        spy_proxy = get_proxy_market()

    if not ff_proxy.empty and not kbe_proxy.empty and not iat_proxy.empty and not spy_proxy.empty:
        # Merge and Filter
        merged = ff_proxy.join(kbe_proxy, lsuffix='_ff', rsuffix='_kbe').join(iat_proxy, rsuffix='_iat').join(spy_proxy, rsuffix='_spy').dropna()
        merged.columns = ['FF_Proxy', 'KBE', 'IAT', 'SPY']
        data_full = merged[(merged.index >= pd.to_datetime(start_date)) & (merged.index <= pd.to_datetime(end_date))]
        
        if data_full.empty:
            st.warning("Selected timeframe has no data overlap.")
        else:
            data_full['d_ff'] = data_full['FF_Proxy'].diff()
            data_full['r_kbe'] = data_full['KBE'].pct_change()
            data_full['r_iat'] = data_full['IAT'].pct_change()
            data_full['r_spy'] = data_full['SPY'].pct_change()
            data = data_full.dropna()

            # 1. Market Evolution
            st.subheader("1. Time Series: Sector Benchmarking")
            fig_ts = go.Figure()
            fig_ts.add_trace(go.Scatter(x=data.index, y=data['FF_Proxy'], name="FF Proxy (%)", yaxis="y1"))
            fig_ts.add_trace(go.Scatter(x=data.index, y=data['KBE'], name="Broad Banks (KBE)", yaxis="y2"))
            fig_ts.add_trace(go.Scatter(x=data.index, y=data['SPY'], name="Market (SPY)", yaxis="y2", line=dict(dash='dash')))
            # FOMC Events
            fomc_dates = ['2022-03-16', '2023-03-22', '2023-05-03']
            for d in fomc_dates:
                dt = pd.to_datetime(d)
                if dt in data.index:
                    fig_ts.add_vline(x=dt, line_dash="dot", line_color="gray", annotation_text="FOMC")
            fig_ts.update_layout(yaxis=dict(title="Yield (%)", side="left"), yaxis2=dict(title="ETF Price", side="right", overlaying="y", showgrid=False), template="plotly_white")
            st.plotly_chart(fig_ts, width='stretch')

            # 2. Sector Sensitivity Comparison
            st.subheader("2. Sector Benchmarking: Interest Rate Betas")
            res_kbe = run_ols_regression(data, 'r_kbe', 'd_ff')
            res_spy = run_ols_regression(data, 'r_spy', 'd_ff')
            col1, col2 = st.columns(2)
            col1.metric("Bank Beta", f"{res_kbe.params['d_ff']:.4f}")
            col2.metric("Market Beta", f"{res_spy.params['d_ff']:.4f}")
            st.caption("Lower (more negative) Beta means the sector is more sensitive to rate hikes. Banks typically show higher sensitivity.")

            # 3. Recursive Estimation
            st.subheader("3. Advanced: Recursive Beta Evolution")
            betas, se = calculate_recursive_ols(data, 'r_kbe', 'd_ff')
            fig_rec = go.Figure()
            fig_rec.add_trace(go.Scatter(x=data.index, y=betas, name="Recursive Beta", line=dict(color='#1f77b4')))
            fig_rec.add_trace(go.Scatter(x=data.index, y=betas + 1.96*se, line_color='rgba(0,0,0,0)', showlegend=False))
            fig_rec.add_trace(go.Scatter(x=data.index, y=betas - 1.96*se, fill='tonexty', fillcolor='rgba(31, 119, 180, 0.2)', name="95% Confidence Band"))
            fig_rec.update_layout(title="Beta Stability Over Time", xaxis_title="Date", yaxis_title="Beta", template="plotly_white")
            st.plotly_chart(fig_rec, width='stretch')

            # 4. Heatmap
            st.divider()
            st.subheader("4. Correlation Heatmap")
            corr = calculate_correlation_matrix(data[['d_ff', 'r_kbe', 'r_iat', 'r_spy']])
            st.plotly_chart(px.imshow(corr, text_auto=".2f", color_continuous_scale='Viridis', template="plotly_white"), width='stretch')

with tab3:
    st.header("Risk stress Test")
    st.markdown("""
    This section uses **Monte Carlo Simulation** to project potential deposit volume outcomes based on 1,000 random 
    interest rate paths starting from the current level.
    """)
    
    if st.button("🚀 Run 1,000 Trial Stress Test"):
        trials = run_monte_carlo_simulation(fed_funds_rate, market_power, base_volume, elasticity)
        
        fig_hist = px.histogram(trials, nbins=50, title="Distribution of Projected Deposit Volume ($B)", labels={'value': 'Deposit Volume ($B)'}, color_discrete_sequence=['#2ca02c'])
        fig_hist.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig_hist, width='stretch')
        
        # Risk Metrics
        var_95 = np.percentile(trials, 5)
        expected = np.mean(trials)
        contraction = (base_volume - var_95) / base_volume * 100
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Volume", f"${base_volume:,.0f}B")
        col2.metric("95% VaR Volume", f"${var_95:,.0f}B")
        col3.metric("Max Potential Drain", f"{contraction:.1f}%", delta="-Risk Exposure", delta_color="inverse")
        
        st.warning(f"In 5% of simulated scenarios, the Deposits Channel causes a drain of more than ${base_volume - var_95:,.0f}B.")

st.divider()
with st.expander("Reference: Drechsler, Savov & Schnabl (2017)"):
    st.latex(r"Spread_i = f - r^d_i = \alpha_i + \beta_i f + \epsilon_i")
    st.markdown("""
    The "Smoking Gun" evidence in the paper shows that the coefficient $\beta_i$ is significantly larger in markets 
    with high HHI (bank concentration). This dashboard allows you to stress test that assumption.
    """)
