import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import statsmodels.api as sm
import warnings
# Suppress statsmodels frequency warnings
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")
from simulation import calculate_deposit_rate, calculate_deposit_volume
from data_fetcher import get_proxy_fed_funds, get_proxy_deposits, get_proxy_regional_banks, get_proxy_market, get_proxy_mmf, get_proxy_10y_yield, get_proxy_credit_ig
from analysis import (
    run_ols_regression, 
    check_stationarity, 
    calculate_rolling_beta, 
    calculate_correlation_matrix,
    calculate_cross_correlation,
    detect_monetary_regimes,
    calculate_recursive_ols,
    run_monte_carlo_simulation,
    calculate_yield_curve_slope,
    calculate_credit_spread
)

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
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime('2018-01-01'))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime('today'))

# 5-Tab Structure
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Theory & Simulation", 
    "Empirical Terminal", 
    "Macro Interactions", 
    "Credit & Lending", 
    "2023 Case Study"
])


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
    fig.add_vline(x=fed_funds_rate*100, line_dash="dash", line_color="#ff7f0e")
    fig.add_annotation(x=fed_funds_rate*100, text="Current Rate", showarrow=False, y=1, yref="paper", textangle=-90, yanchor="bottom")
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
                    fig_ts.add_vline(x=dt, line_dash="dot", line_color="gray")
                    fig_ts.add_annotation(x=dt, text="FOMC", showarrow=False, y=1, yref="paper", textangle=-90, yanchor="bottom")
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
    st.header("Macro Interactions: MMFs & Yield Curve")
    with st.spinner("Analyzing macro interactions..."):
        mmf_proxy = get_proxy_mmf()
        tnx_proxy = get_proxy_10y_yield()
        
    if not mmf_proxy.empty and not tnx_proxy.empty:
        macro_merged = ff_proxy.join(mmf_proxy, lsuffix='_ff', rsuffix='_mmf').join(tnx_proxy, rsuffix='_tnx').dropna()
        macro_merged.columns = ['FF_Proxy', 'MMF_Price', 'Ten_Year']
        macro_data = macro_merged[(macro_merged.index >= pd.to_datetime(start_date)) & (macro_merged.index <= pd.to_datetime(end_date))]
        
        # 1. MMF Destination
        st.subheader("1. Deposits Destination: Money Market Funds")
        st.markdown("As bank spreads widen, deposits flow into MMFs. We proxy this with the price/performance of VMFXX.")
        fig_mmf = go.Figure()
        fig_mmf.add_trace(go.Scatter(x=macro_data.index, y=macro_data['FF_Proxy'], name="Fed Funds Proxy (%)", yaxis="y1"))
        fig_mmf.add_trace(go.Scatter(x=macro_data.index, y=macro_data['MMF_Price'], name="MMF Price (VMFXX)", yaxis="y2"))
        fig_mmf.update_layout(yaxis=dict(title="Yield (%)"), yaxis2=dict(title="Price ($)", overlaying="y", side="right", showgrid=False), template="plotly_white")
        st.plotly_chart(fig_mmf, width='stretch')
        
        # 2. Yield Curve Slope
        st.subheader("2. Yield Curve & The Deposits Channel")
        st.markdown("The paper argues the channel is more strained when the curve is flat or inverted (low slope).")
        macro_data['Slope'] = calculate_yield_curve_slope(macro_data['Ten_Year'], macro_data['FF_Proxy'])
        fig_slope = go.Figure(data=go.Scatter(x=macro_data.index, y=macro_data['Slope'], name="10Y-3M Slope", fill='tozeroy'))
        fig_slope.add_hline(y=0, line_dash="dash", line_color="red")
        fig_slope.update_layout(title="Yield Curve Slope (Ten Year - Fed Funds Proxy)", yaxis_title="Spread (%)", template="plotly_white")
        st.plotly_chart(fig_slope, width='stretch')

with tab4:
    st.header("Credit & Lending: Transmission to Real Economy")
    with st.spinner("Calculating credit spreads..."):
        lqd_proxy = get_proxy_credit_ig()
        
    if not lqd_proxy.empty:
        credit_merged = ff_proxy.join(lqd_proxy, rsuffix='_lqd').join(spy_proxy, rsuffix='_spy').dropna()
        credit_merged.columns = ['FF_Proxy', 'Credit_Price', 'SPY']
        credit_data = credit_merged[(credit_merged.index >= pd.to_datetime(start_date)) & (credit_merged.index <= pd.to_datetime(end_date))]
        
        # Calculate proxy spread stress
        # Higher index = higher cost of credit relative to risk-free
        credit_data['Spread_Stress'] = calculate_credit_spread(credit_data['Credit_Price'], credit_data['FF_Proxy'] / 100 + 1) # Normalizing
        
        st.subheader("1. Lending Conditions Proxy")
        st.markdown("Widening credit 'stress' indicates a contraction in bank lending supply as deposits leave the system.")
        fig_credit = px.line(credit_data, y='Credit_Price', title="Investment Grade Credit Price (LQD)", labels={'Credit_Price': 'Price ($)'}, template="plotly_white")
        st.plotly_chart(fig_credit, width='stretch')
        
        st.info("When rates rise and deposits exit, banks must contract their balance sheets, leading to lower credit availability and higher spreads.")

with tab5:
    st.header("Case Study: March 2023 Banking Stress")
    st.markdown("""
    March 2023 represented a 'nonlinear' shock where the Deposits Channel mechanism reached a breaking point 
    for regional banks like SVB.
    """)
    
    # Zoom in on 2023
    crisis_start = pd.to_datetime('2023-02-01')
    crisis_end = pd.to_datetime('2023-05-01')
    crisis_data = merged[(merged.index >= crisis_start) & (merged.index <= crisis_end)]
    
    if not crisis_data.empty:
        st.subheader("The Regional Bank Breaking Point")
        fig_svb = go.Figure()
        fig_svb.add_trace(go.Scatter(x=crisis_data.index, y=crisis_data['KBE'], name="Broad Banks (KBE)"))
        fig_svb.add_trace(go.Scatter(x=crisis_data.index, y=crisis_data['IAT'], name="Regional Banks (IAT)", line=dict(width=4, color='red')))
        fig_svb.add_vline(x=pd.to_datetime('2023-03-10'), line_dash="dash", line_color="black")
        fig_svb.add_annotation(x=pd.to_datetime('2023-03-10'), text="SVB Collapse", showarrow=False, y=1, yref="paper", textangle=-90, yanchor="bottom")
        fig_svb.update_layout(title="KBE vs IAT: The Regional Divergence", yaxis_title="Price ($)", template="plotly_white")
        st.plotly_chart(fig_svb, width='stretch')
        
        st.markdown("""
        **Implications:**
        - **Sticky no more:** The assumption of deposit stickiness failed as digital banking allowed instant outflows.
        - **Unrealized Losses:** High interest rates (the X-axis of our model) caused the value of bank-held bonds to drop, 
          creating the 'hole' that deposit outflows exposed.
        - **Endogenous Power:** Large banks (KBE) recovered faster as they benefited from a 'flight to safety', 
          further increasing their market power.
        """)
    else:
        st.warning("Crisis period data not available in current fetch.")

    # Re-add the Risk Test here or as an expander
    st.divider()
    st.subheader("Stress Test Simulation")
    if st.button("🚀 Run 1,000 Trial Stress Test"):
        trials = run_monte_carlo_simulation(fed_funds_rate, market_power, base_volume, elasticity)
        fig_hist = px.histogram(trials, nbins=50, title="Distribution of Projected Deposit Volume ($B)", labels={'value': 'Deposit Volume ($B)'}, color_discrete_sequence=['#2ca02c'])
        fig_hist.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig_hist, width='stretch')
        var_95 = np.percentile(trials, 5)
        st.metric("95% VaR Volume", f"${var_95:,.0f}B", delta=f"-{(base_volume-var_95)/base_volume*100:.1f}% Risk")

st.divider()
with st.expander("Reference: Drechsler, Savov & Schnabl (2017)"):
    st.latex(r"Spread_i = f - r^d_i = \alpha_i + \beta_i f + \epsilon_i")
    st.markdown("""
    The "Smoking Gun" evidence in the paper shows that the coefficient $\beta_i$ is significantly larger in markets 
    with high HHI (bank concentration). This dashboard allows you to stress test that assumption.
    """)
