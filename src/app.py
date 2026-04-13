import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import statsmodels.api as sm
from simulation import calculate_deposit_rate, calculate_deposit_volume
from data_fetcher import get_proxy_fed_funds, get_proxy_deposits
from analysis import run_ols_regression, check_stationarity, calculate_rolling_beta, calculate_correlation_matrix

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
    st.markdown("""
    ```mermaid
    graph TD
        Fed[Fed Funds Rate ↑] --> Spread[Deposit Spread ↑]
        Power[Bank Market Power] --> Spread
        Spread --> Outflow[Deposit Outflow]
        Outflow --> Lending[Bank Lending ↓]
        style Fed fill:#f96,stroke:#333
        style Lending fill:#69f,stroke:#333
    ```
    """, unsafe_allow_html=True)
    
    colA, colB, colC = st.columns(3)
    with colA:
        st.markdown("**1. Market Power**")
        st.caption("Banks in concentrated markets (high HHI) can keep deposit rates low even when the Fed hikes.")
    with colB:
        st.markdown("**2. The Spread**")
        st.caption("The 'price of liquidity' widens as banks widen the gap between what they earn and what they pay you.")
    with colC:
        st.markdown("**3. Transmission**")
        st.caption("As deposits flow to Money Market Funds, banks lose their cheapest source of funding and must cut lending.")

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

    fig = go.Figure(data=go.Scatter(x=[r*100 for r in rates], y=volumes, mode='lines', name='Theoretical Volume'))
    fig.add_vline(x=fed_funds_rate*100, line_dash="dash", line_color="red", annotation_text="Current Rate")

    fig.update_layout(
        title="Theoretical Deposit Volume vs Fed Funds Rate",
        xaxis_title="Fed Funds Rate (%)",
        yaxis_title="Deposit Volume ($B)",
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Concentration Analysis: How Market Power Amplifies the Channel")

    # Compare High HHI vs Low HHI
    rates_hhi = [r/100.0 for r in range(0, 1001, 25)]
    vol_high = [calculate_deposit_volume(10000, r - calculate_deposit_rate(r, 0.8), 10) for r in rates_hhi]
    vol_low = [calculate_deposit_volume(10000, r - calculate_deposit_rate(r, 0.2), 10) for r in rates_hhi]

    fig_hhi = go.Figure()
    fig_hhi.add_trace(go.Scatter(x=[r*100 for r in rates_hhi], y=vol_high, name="High Concentration (HHI=0.8)"))
    fig_hhi.add_trace(go.Scatter(x=[r*100 for r in rates_hhi], y=vol_low, name="Low Concentration (HHI=0.2)"))
    fig_hhi.update_layout(title="HHI Impact: Deposit Supply Curve", xaxis_title="Fed Funds Rate (%)", yaxis_title="Deposit Volume ($B)")
    st.plotly_chart(fig_hhi, use_container_width=True)
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

    if not ff_proxy.empty and not kbe_proxy.empty:
        # Prepare Data
        merged = ff_proxy.join(kbe_proxy, lsuffix='_ff', rsuffix='_kbe').dropna()
        merged.columns = ['FF_Proxy', 'Bank_ETF']
        
        # Calculate changes/returns
        merged['d_ff'] = merged['FF_Proxy'].diff()
        merged['r_kbe'] = merged['Bank_ETF'].pct_change()
        data = merged.dropna()
        
        # Display raw time series
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(x=merged.index, y=merged['FF_Proxy'], name="FF Proxy Yield (%)", yaxis="y1"))
        fig_ts.add_trace(go.Scatter(x=merged.index, y=merged['Bank_ETF'], name="Bank ETF Price ($)", yaxis="y2"))
        fig_ts.update_layout(
            title="Time Series: Rates vs Bank Stock Price",
            yaxis=dict(title="Yield (%)", side="left"),
            yaxis2=dict(title="Price ($)", side="right", overlaying="y", showgrid=False),
            hovermode="x unified"
        )
        st.plotly_chart(fig_ts, use_container_width=True)
        
        st.divider()

        # Correlation Heatmap
        st.subheader("Correlation Matrix: Market Proxy Interactions")
        corr_matrix = calculate_correlation_matrix(data[['d_ff', 'r_kbe']])
        fig_heat = px.imshow(corr_matrix, text_auto=True, color_continuous_scale='RdBu_r', labels=dict(color="Correlation"))
        st.plotly_chart(fig_heat, use_container_width=True)
        
        st.divider()
        
        # 1. Stationarity Tests
        st.subheader("1. Stationarity Analysis (ADF Test)")
        p_ff = check_stationarity(merged['FF_Proxy'])
        p_kbe = check_stationarity(merged['Bank_ETF'])
        
        col1, col2 = st.columns(2)
        col1.write(f"**FF Proxy ADF p-value:** {p_ff:.4f}")
        col2.write(f"**Bank ETF ADF p-value:** {p_kbe:.4f}")
        if p_ff > 0.05 or p_kbe > 0.05:
            st.warning("Series are non-stationary. We must use differences/returns for regression to avoid spurious results.")

        st.divider()

        # 2. Regression
        st.subheader("2. Regression: Bank Performance vs Rate Changes")
        res = run_ols_regression(data, 'r_kbe', 'd_ff')
        
        st.markdown(f"""
        **Hypothesis:** If the Deposits Channel is active, rate hikes ($\Delta f$) should correlate with lower bank performance.
        - **Coefficient ($\beta$):** {res.params['d_ff']:.4f}
        - **P-Value:** {res.pvalues['d_ff']:.4f}
        - **R-Squared:** {res.rsquared:.4f}
        """)
        
        with st.expander("Show Full Regression Summary"):
            st.text(res.summary())
            
        fig_ols = go.Figure()
        fig_ols.add_trace(go.Scatter(x=data['d_ff'], y=data['r_kbe'], mode='markers', name='Actual Data'))
        # Generate fit line
        x_range = np.linspace(data['d_ff'].min(), data['d_ff'].max(), 100)
        y_fit = res.params['const'] + res.params['d_ff'] * x_range
        fig_ols.add_trace(go.Scatter(x=x_range, y=y_fit, mode='lines', name='Linear Fit', line=dict(color='red')))
        fig_ols.update_layout(title="Regression: Bank Returns vs $\Delta$ Rate Proxy", xaxis_title="$\Delta$ Rate (%)", yaxis_title="Bank ETF Return")
        st.plotly_chart(fig_ols, use_container_width=True)

        st.divider()

        # 3. Rolling Beta
        st.subheader("3. Rolling Interest Rate Sensitivity")
        window = st.slider("Rolling Window (Days)", 60, 500, 252)
        rolling_beta = calculate_rolling_beta(data, 'r_kbe', 'd_ff', window=window)
        
        fig_roll = go.Figure(data=go.Scatter(x=rolling_beta.index, y=rolling_beta, mode='lines', name='Beta'))
        fig_roll.update_layout(title=f"Rolling {window}-Day Beta (Sensitivity to Rates)", xaxis_title="Date", yaxis_title="Beta Coefficient")
        st.plotly_chart(fig_roll, use_container_width=True)
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
