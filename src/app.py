import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import statsmodels.api as sm
from simulation import calculate_deposit_rate, calculate_deposit_volume
from data_fetcher import get_proxy_fed_funds, get_proxy_deposits, get_proxy_regional_banks
from analysis import (
    run_ols_regression, 
    check_stationarity, 
    calculate_rolling_beta, 
    calculate_correlation_matrix,
    calculate_cross_correlation,
    detect_monetary_regimes
)

st.set_page_config(page_title="Deposits Channel", layout="wide")

st.title("The Deposits Channel of Monetary Policy")
st.markdown("""
This dashboard explores the core logic of **Drechsler, Savov & Schnabl (2017)**: *\"The Deposits Channel of Monetary Policy\"*.
""")

# Sidebar Navigation
st.sidebar.title("Navigation")
mode = st.sidebar.radio("Select View", ["Theory & Simulation", "Empirical Analysis"])

if mode == "Theory & Simulation":
    st.header("Theoretical Model")
    
    st.subheader("The Mechanism: From Rates to Lending")
    # Fixed Mermaid rendering using st.tabs or just clean st.markdown if supported, 
    # but st.components.v1.html or a dedicated Mermaid component is more reliable.
    # For simplicity and reliability in standard Streamlit, we use st.code or a clear step-by-step UI.
    # However, st.markdown with a mermaid block is supported in modern Streamlit.
    # Let's use a more robust layout.
    
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
    st.markdown("Use the sliders to see how Fed Rate hikes transmit through sticky deposits.")
    
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

    fig.update_layout(
        title="Theoretical Deposit Volume vs Fed Funds Rate",
        xaxis_title="Fed Funds Rate (%)",
        yaxis_title="Deposit Volume ($B)",
        hovermode="x unified",
        template="plotly_white"
    )
    st.plotly_chart(fig, width='stretch')

    st.divider()
    st.subheader("Interactive Heatmap: Deposit Spreads")
    st.markdown("This heatmap shows the **Deposit Spread** (Fed Rate - Deposit Rate) across different levels of market power and interest rates.")

    # Grid for heatmap
    ff_range = np.linspace(0, 0.1, 20)
    mp_range = np.linspace(0, 1.0, 20)
    # Spread = f - f*(1-mp) = f*mp
    spreads = np.array([[f * mp * 100 for mp in mp_range] for f in ff_range])

    fig_heat_sim = px.imshow(
        spreads,
        x=[f"{mp:.1f}" for mp in mp_range],
        y=[f"{f*100:.1f}%" for f in ff_range],
        labels=dict(x="Bank Market Power", y="Fed Funds Rate (%)", color="Spread (%)"),
        color_continuous_scale='Viridis',
        aspect="auto"
    )
    fig_heat_sim.update_layout(template="plotly_white")
    st.plotly_chart(fig_heat_sim, width='stretch')

    st.divider()
    st.subheader("Concentration Analysis: How Market Power Amplifies the Channel")

    # Compare High HHI vs Low HHI
    rates_hhi = [r/100.0 for r in range(0, 1001, 25)]
    vol_high = [calculate_deposit_volume(10000, r - calculate_deposit_rate(r, 0.8), 10) for r in rates_hhi]
    vol_low = [calculate_deposit_volume(10000, r - calculate_deposit_rate(r, 0.2), 10) for r in rates_hhi]

    fig_hhi = go.Figure()
    fig_hhi.add_trace(go.Scatter(x=[r*100 for r in rates_hhi], y=vol_high, name="High Concentration (HHI=0.8)", line=dict(color='#d62728', dash='dot')))
    fig_hhi.add_trace(go.Scatter(x=[r*100 for r in rates_hhi], y=vol_low, name="Low Concentration (HHI=0.2)", line=dict(color='#2ca02c')))
    fig_hhi.update_layout(title="HHI Impact: Deposit Supply Curve", xaxis_title="Fed Funds Rate (%)", yaxis_title="Deposit Volume ($B)", template="plotly_white")
    st.plotly_chart(fig_hhi, width='stretch')
    st.info("The Deposits Channel is more potent in concentrated markets. Higher HHI = Steeper deposit supply curve.")

else:
    st.header("Empirical Analysis")
    st.markdown("""
    Replicating the paper's empirical strategy using market proxies. 
    The paper regresses deposit growth on rate changes to find **Deposit Betas**.
    """)
    
    # Load Market Data
    with st.spinner("Fetching market data..."):
        ff_proxy = get_proxy_fed_funds()
        kbe_proxy = get_proxy_deposits()
        iat_proxy = get_proxy_regional_banks()

    if not ff_proxy.empty and not kbe_proxy.empty and not iat_proxy.empty:
        # Prepare Data
        merged = ff_proxy.join(kbe_proxy, lsuffix='_ff', rsuffix='_kbe')
        merged = merged.join(iat_proxy, rsuffix='_iat').dropna()
        merged.columns = ['FF_Proxy', 'KBE', 'IAT']
        
        # Calculate changes/returns
        merged['d_ff'] = merged['FF_Proxy'].diff()
        merged['r_kbe'] = merged['KBE'].pct_change()
        merged['r_iat'] = merged['IAT'].pct_change()
        data = merged.dropna()
        
        # Display raw time series
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=merged.index, y=merged['FF_Proxy'], name="FF Proxy Yield (%)", yaxis="y1", line=dict(color='#1f77b4')))
        fig_ts.add_trace(go.Scatter(x=merged.index, y=merged['KBE'], name="Bank ETF Price ($)", yaxis="y2", line=dict(color='#ff7f0e')))
        fig_ts.update_layout(
            title="Time Series: Rates vs Bank Stock Price",
            yaxis=dict(title=dict(text="Yield (%)", font=dict(color="#1f77b4")), side="left", tickfont=dict(color="#1f77b4")),
            yaxis2=dict(title=dict(text="Price ($)", font=dict(color="#ff7f0e")), side="right", overlaying="y", showgrid=False, tickfont=dict(color="#ff7f0e")),
            hovermode="x unified",
            template="plotly_white"
        )
        st.plotly_chart(fig_ts, width='stretch')
        
        st.divider()

        # 4. Monetary Policy Regime Performance
        st.subheader("4. Monetary Policy Regime Performance")
        regimes = detect_monetary_regimes(data['FF_Proxy'])
        data['Regime'] = regimes

        regime_perf = data.groupby('Regime')['r_kbe'].mean() * 100 * 252 # Annualized
        fig_regime = px.bar(regime_perf, title="Annualized Broad Bank Returns (KBE) by Regime", labels=dict(value="Annualized Return (%)", Regime="Policy Regime"), color=regime_perf.index)
        st.plotly_chart(fig_regime, width='stretch')

        # Cumulative returns during the most recent hiking cycle
        hiking_cycle = data[data.index > '2022-01-01']
        if not hiking_cycle.empty:
            hiking_cycle['cum_kbe'] = (1 + hiking_cycle['r_kbe']).cumprod()
            hiking_cycle['cum_iat'] = (1 + hiking_cycle['r_iat']).cumprod()
            fig_cum = go.Figure()
            fig_cum.add_trace(go.Scatter(x=hiking_cycle.index, y=hiking_cycle['cum_kbe'], name='Broad Banks (KBE)'))
            fig_cum.add_trace(go.Scatter(x=hiking_cycle.index, y=hiking_cycle['cum_iat'], name='Regional Banks (IAT)'))
            fig_cum.update_layout(title="Bank Performance during 2022-2024 Hike Cycle", xaxis_title="Date", yaxis_title="Cumulative Return", template="plotly_white")
            st.plotly_chart(fig_cum, width='stretch')

        st.divider()

        # 5. Lead/Lag (Cross-Correlation) Analysis
        st.subheader("5. Lead/Lag (Cross-Correlation) Analysis")
        lags, coeffs = calculate_cross_correlation(data['r_kbe'], data['d_ff'])
        fig_lag = go.Figure(data=go.Scatter(x=lags, y=coeffs, mode='lines+markers', marker=dict(size=8, color='#1f77b4')))
        fig_lag.add_vline(x=0, line_dash="dash", line_color="gray")
        fig_lag.update_layout(title="Correlation: Rate Changes vs Bank Returns (Various Lags)", xaxis_title="Lag (Days)", yaxis_title="Correlation Coefficient", template="plotly_white")
        st.plotly_chart(fig_lag, width='stretch')
        st.caption("Lag > 0: Rate changes lead bank returns. Lag < 0: Bank returns lead rate changes.")

        st.divider()

        # Correlation Heatmap
        st.subheader("Correlation Matrix: Market Proxy Interactions")
        # Customizing labels for the heatmap
        heatmap_data = data[['d_ff', 'r_kbe']].rename(columns={'d_ff': 'Rate Change', 'r_kbe': 'Bank Return'})
        corr_matrix = calculate_correlation_matrix(heatmap_data)
        
        # Using a more professional color scale (Viridis or Plasma often fit modern dark/light UIs better than RdBu)
        fig_heat = px.imshow(
            corr_matrix, 
            text_auto=".2f", 
            color_continuous_scale='Viridis', 
            labels=dict(color="Correlation"),
            aspect="auto"
        )
        fig_heat.update_layout(template="plotly_white")
        st.plotly_chart(fig_heat, width='stretch')
        
        st.divider()
        
        # 1. Stationarity Tests
        st.subheader("1. Stationarity Analysis (ADF Test)")
        p_ff = check_stationarity(merged['FF_Proxy'])
        p_kbe = check_stationarity(merged['KBE'])
        
        col1, col2 = st.columns(2)
        col1.write(f"**FF Proxy ADF p-value:** {p_ff:.4f}")
        col2.write(f"**Bank ETF ADF p-value:** {p_kbe:.4f}")
        if p_ff > 0.05 or p_kbe > 0.05:
            st.warning("Series are non-stationary. We must use differences/returns for regression to avoid spurious results.")

        st.divider()

        # 2. Regression
        st.subheader("2. Regression: Regional vs. Broad Banks")
        res_kbe = run_ols_regression(data, 'r_kbe', 'd_ff')
        res_iat = run_ols_regression(data, 'r_iat', 'd_ff')
        
        st.markdown(rf"""
        Comparing how sensitive different bank types are to interest rate changes.
        - **Broad Banks (KBE) $\beta$:** `{res_kbe.params['d_ff']:.4f}` (p-val: `{res_kbe.pvalues['d_ff']:.4f}`)
        - **Regional Banks (IAT) $\beta$:** `{res_iat.params['d_ff']:.4f}` (p-val: `{res_iat.pvalues['d_ff']:.4f}`)
        """)
        
        with st.expander("Show Regression Summaries"):
            st.text("Broad Banks (KBE):")
            st.text(res_kbe.summary())
            st.text("---")
            st.text("Regional Banks (IAT):")
            st.text(res_iat.summary())
            
        fig_ols = go.Figure()
        fig_ols.add_trace(go.Scatter(x=data['d_ff'], y=data['r_kbe'], mode='markers', name='KBE Data', marker=dict(color='rgba(31, 119, 180, 0.3)')))
        fig_ols.add_trace(go.Scatter(x=data['d_ff'], y=data['r_iat'], mode='markers', name='IAT Data', marker=dict(color='rgba(255, 127, 14, 0.3)')))
        
        x_range = np.linspace(data['d_ff'].min(), data['d_ff'].max(), 100)
        y_kbe = res_kbe.params['const'] + res_kbe.params['d_ff'] * x_range
        y_iat = res_iat.params['const'] + res_iat.params['d_ff'] * x_range
        
        fig_ols.add_trace(go.Scatter(x=x_range, y=y_kbe, mode='lines', name='KBE Fit', line=dict(color='#1f77b4', width=3)))
        fig_ols.add_trace(go.Scatter(x=x_range, y=y_iat, mode='lines', name='IAT Fit', line=dict(color='#ff7f0e', width=3)))
        
        fig_ols.update_layout(title=r"Regression: Bank Returns vs $\Delta$ Rate Proxy", xaxis_title=r"$\Delta$ Rate (%)", yaxis_title="Return", template="plotly_white")
        st.plotly_chart(fig_ols, width='stretch')

        st.divider()

        # 3. Rolling Beta
        st.subheader("3. Rolling Interest Rate Sensitivity")
        window = st.slider("Rolling Window (Days)", 60, 500, 252)
        rolling_beta = calculate_rolling_beta(data, 'r_kbe', 'd_ff', window=window)
        
        fig_roll = go.Figure(data=go.Scatter(x=rolling_beta.index, y=rolling_beta, mode='lines', name='Beta', line=dict(color='#9467bd')))
        fig_roll.update_layout(title=f"Rolling {window}-Day Beta (Sensitivity to Rates)", xaxis_title="Date", yaxis_title="Beta Coefficient", template="plotly_white")
        st.plotly_chart(fig_roll, width='stretch')
        st.info("A negative beta means the bank sector tends to underperform when rates rise, consistent with the Deposits Channel.")

    else:
        st.error("Market data unavailable. Please check your connection.")

st.divider()
with st.expander("Academic Deep Dive: Equations & Results from DSS (2017)"):
    st.latex(r"Spread_i = f - r^d_i = \alpha_i + \beta_i f + \epsilon_i")
    st.markdown("""
    **Core Findings from the Paper:**
    1. **Deposit Betas:** Banks pass through only a fraction of rate hikes to depositors.
    2. **Smoking Gun:** This effect is significantly stronger in zip codes with high bank concentration (HHI).
    3. **Lending Impact:** A 100bp hike leads to a roughly 0.5% drop in total bank assets via this channel.
    """)
