import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import statsmodels.api as sm
import warnings
# Suppress statsmodels frequency warnings
warnings.filterwarnings("ignore", category=UserWarning, module="statsmodels")
from simulation import calculate_deposit_rate, calculate_deposit_volume, generate_rate_paths, generate_deposit_paths
from data_fetcher import get_proxy_fed_funds, get_proxy_deposits, get_proxy_regional_banks, get_proxy_market, get_proxy_mmf, get_proxy_10y_yield, get_proxy_credit_ig, get_proxy_volatility
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
    calculate_credit_spread,
    calculate_liquidity_proxy,
    calculate_returns,
    calculate_drawdown,
    build_stress_index,
    event_study_car,
    calculate_bond_portfolio_loss
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
    col1.metric("Fed Funds Rate", f"{fed_funds_rate*100:.2f}%")
    col2.metric("Deposit Rate", f"{dep_rate*100:.2f}%", f"-{spread*100:.2f}% spread")
    col3.metric("Total Deposits", f"${volume:,.0f}B")
    col4.metric("Capital Buffer (Proxy)", f"{liquidity_proxy:.1f}%", f"${bond_loss:,.0f}B Unrealized Loss", delta_color="inverse")

    st.info("The **Capital Buffer Proxy** shows the dual squeeze: Deposit outflows + bond portfolio losses (AOCI).")

    # Sub-tabs within Theory
    theory_tab1, theory_tab2, theory_tab3 = st.tabs(["Mechanism Simulation", "Synthetic Cross-Section", "Scenario Paths"])
    
    with theory_tab1:
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

        st.divider()
        st.subheader("Sensitivity Surfaces: Elasticity")
        elasticity_levels = [5, 10, 15]
        surface_cols = st.columns(3)
        ff_grid = np.linspace(0, 0.1, 30)
        mp_grid = np.linspace(0, 1.0, 30)
        for col, e in zip(surface_cols, elasticity_levels):
            z = [
                [calculate_deposit_volume(base_volume, f - calculate_deposit_rate(f, mp), e) for mp in mp_grid]
                for f in ff_grid
            ]
            fig_surface = go.Figure(
                data=go.Contour(
                    z=z,
                    x=[f"{mp:.2f}" for mp in mp_grid],
                    y=[f"{f*100:.1f}%" for f in ff_grid],
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
            col.plotly_chart(fig_surface, width='stretch')

        st.divider()
        st.subheader("AOCI Sensitivity: Rate Change → Bond Loss")
        rate_changes = np.linspace(-0.05, 0.05, 51)
        bond_portfolio_value = base_volume * 0.6
        losses = [calculate_bond_portfolio_loss(bond_portfolio_value, rc, duration=duration) for rc in rate_changes]
        fig_aoci = go.Figure(data=go.Scatter(x=rate_changes * 100, y=losses, mode='lines'))
        fig_aoci.add_hline(y=0, line_dash="dash", line_color="gray")
        fig_aoci.update_layout(
            title="Bond Portfolio Loss vs Rate Change",
            xaxis_title="Rate Change (%)",
            yaxis_title="Loss ($B)",
            template="plotly_white",
        )
        st.plotly_chart(fig_aoci, width='stretch')

    with theory_tab2:
        st.subheader("Synthetic HHI Cohorts: Monopolist vs Competitor")
        st.markdown("Replicating zip-code level heterogeneity using paper coefficients.")
        
        # High HHI vs Low HHI
        # DSS (2017) result: High HHI areas have much higher deposit betas
        hhi_high = 0.8
        hhi_low = 0.2
        
        rates_syn = np.linspace(0, 0.08, 50)
        # Using the model: deposit_rate = f * (1 - HHI)
        dr_high = rates_syn * (1 - hhi_high)
        dr_low = rates_syn * (1 - hhi_low)
        
        fig_syn = go.Figure()
        fig_syn.add_trace(go.Scatter(x=rates_syn*100, y=dr_high*100, name="Concentrated Bank (HHI=0.8)", line=dict(dash='dot')))
        fig_syn.add_trace(go.Scatter(x=rates_syn*100, y=dr_low*100, name="Competitive Bank (HHI=0.2)"))
        fig_syn.add_trace(go.Scatter(x=rates_syn*100, y=rates_syn*100, name="Fed Funds (Full Pass-through)", line=dict(color='black', dash='dash')))
        fig_syn.update_layout(title="Synthetic Deposit Rates vs Fed Funds", xaxis_title="Fed Funds Rate (%)", yaxis_title="Deposit Rate (%)", template="plotly_white")
        st.plotly_chart(fig_syn, width='stretch')
        
        st.markdown("""
        **Observations:**
        - **The Monopolist:** Widens the spread aggressively as Fed hikes, maximizing profit at the cost of deposit volume.
        - **The Competitor:** Forced to pass through most of the rate hike to keep depositors, protecting volume but squeezing margin.
        """)

    with theory_tab3:
        st.subheader("Scenario Small Multiples: Rate Paths → Deposits")
        st.markdown("Nine simulated paths (3×3) showing how rate uncertainty maps to deposit volume outcomes.")
        rate_paths = generate_rate_paths(current_rate=fed_funds_rate, paths=9, days=252, seed=42)
        deposit_paths = generate_deposit_paths(rate_paths, market_power, base_volume, elasticity)
        for row in range(3):
            cols = st.columns(3)
            for col_idx in range(3):
                idx = row * 3 + col_idx
                path_rate = rate_paths[idx]
                path_dep = deposit_paths[idx]
                fig_path = go.Figure()
                fig_path.add_trace(go.Scatter(y=path_rate * 100, name="Rate (%)", line=dict(color="#1f77b4")))
                fig_path.add_trace(go.Scatter(y=path_dep, name="Deposits ($B)", line=dict(color="#ff7f0e"), yaxis="y2"))
                fig_path.update_layout(
                    template="plotly_white",
                    height=250,
                    margin=dict(l=30, r=30, t=25, b=25),
                    yaxis=dict(title="Rate (%)"),
                    yaxis2=dict(title="Deposits", overlaying="y", side="right", showgrid=False),
                    showlegend=False,
                )
                cols[col_idx].plotly_chart(fig_path, width='stretch')

with tab2:
    st.header("Empirical Terminal")
    
    with st.spinner("Fetching terminal data..."):
        ff_proxy = get_proxy_fed_funds()
        kbe_proxy = get_proxy_deposits()
        iat_proxy = get_proxy_regional_banks()
        spy_proxy = get_proxy_market()
        vix_proxy = get_proxy_volatility()

    merged = pd.DataFrame()
    if not ff_proxy.empty and not kbe_proxy.empty and not iat_proxy.empty and not spy_proxy.empty and not vix_proxy.empty:
        # Merge and Filter
        merged = ff_proxy.join(kbe_proxy, lsuffix='_ff', rsuffix='_kbe').join(iat_proxy, rsuffix='_iat').join(spy_proxy, rsuffix='_spy').join(vix_proxy, rsuffix='_vix').dropna()
        merged.columns = ['FF_Proxy', 'KBE', 'IAT', 'SPY', 'VIX']
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

            # 4. Stress Composite Index
            st.subheader("4. Stress Composite Index")
            data['r_vix'] = calculate_returns(data['VIX'])
            stress = build_stress_index(data['d_ff'], data['r_vix'], data['KBE'], window=252, smoothing=5)
            if stress.dropna().empty:
                st.warning("Not enough data to compute the Stress Composite Index.")
            else:
                threshold = stress.quantile(0.95)
                fig_stress = go.Figure()
                fig_stress.add_trace(go.Scatter(x=stress.index, y=stress, name="Stress Index"))
                fig_stress.add_hline(y=threshold, line_dash="dash", line_color="red")
                fig_stress.update_layout(title="Composite Stress Index (Rates + VIX + KBE Drawdown)", xaxis_title="Date", yaxis_title="Z-Score", template="plotly_white")
                st.plotly_chart(fig_stress, width='stretch')

            # 5. Event Study: FOMC Abnormal Returns
            st.subheader("5. Event Study: FOMC Abnormal Returns")
            event_dates = [pd.to_datetime(d) for d in ['2022-03-16', '2022-06-15', '2022-09-21', '2023-03-22', '2023-05-03']]
            returns_df = data[['r_kbe', 'r_iat', 'r_spy']].rename(columns={'r_kbe': 'KBE', 'r_iat': 'IAT', 'r_spy': 'SPY'})
            car = event_study_car(returns_df, event_dates, window=5, benchmark_col='SPY')
            if car.empty:
                st.warning("Not enough data to compute event study CARs for the selected period.")
            else:
                fig_car = go.Figure()
                fig_car.add_trace(go.Scatter(x=car.index, y=car['KBE'], name="KBE CAR"))
                fig_car.add_trace(go.Scatter(x=car.index, y=car['IAT'], name="IAT CAR", line=dict(color="red")))
                fig_car.add_hline(y=0, line_dash="dash", line_color="gray")
                fig_car.update_layout(title="Average Cumulative Abnormal Returns (±5 days)", xaxis_title="Event Day", yaxis_title="CAR", template="plotly_white")
                st.plotly_chart(fig_car, width='stretch')

            # 6. Rolling Beta Heatmap
            st.subheader("6. Rolling Beta Heatmap")
            beta_kbe = calculate_rolling_beta(data, 'r_kbe', 'd_ff', window=252)
            beta_iat = calculate_rolling_beta(data, 'r_iat', 'd_ff', window=252)
            beta_spy = calculate_rolling_beta(data, 'r_spy', 'd_ff', window=252)
            beta_df = pd.DataFrame({'KBE': beta_kbe, 'IAT': beta_iat, 'SPY': beta_spy}).dropna()
            if beta_df.empty:
                st.warning("Not enough data to compute rolling betas.")
            else:
                fig_beta = px.imshow(beta_df.T, aspect='auto', color_continuous_scale='RdBu', zmid=0, template="plotly_white")
                fig_beta.update_layout(title="Rolling 1Y Beta vs FF Proxy", xaxis_title="Date", yaxis_title="Series")
                st.plotly_chart(fig_beta, width='stretch')

            # 7. Advanced: Crisis-Conditional Sensitivity (VIX)
            st.subheader("7. Advanced: Crisis-Conditional Sensitivity (VIX)")
            st.markdown("Does the Deposits Channel amplify when market fear is high?")
            high_vix = data[data['VIX'] > 20]
            low_vix = data[data['VIX'] <= 20]
            
            if not high_vix.empty and not low_vix.empty:
                res_high = run_ols_regression(high_vix, 'r_kbe', 'd_ff')
                res_low = run_ols_regression(low_vix, 'r_kbe', 'd_ff')
                
                col1, col2 = st.columns(2)
                col1.metric("Beta (VIX > 20)", f"{res_high.params['d_ff']:.4f}")
                col2.metric("Beta (VIX <= 20)", f"{res_low.params['d_ff']:.4f}")
                st.caption("A more negative Beta during high VIX confirms that Deposits Channel risks are amplified during market stress.")

            # 8. Dynamic Analysis: Impulse Response Functions
            st.subheader("8. Dynamic Analysis: The Shock Ripple (IRF)")
            st.markdown("If the Fed hikes rates by 100bp today, how do bank valuations respond over the next 20 days?")
            from analysis import calculate_irf
            irf_kbe = calculate_irf(data, 'r_kbe', 'd_ff', periods=20)
            irf_iat = calculate_irf(data, 'r_iat', 'd_ff', periods=20)
            
            if irf_kbe is None or irf_iat is None:
                st.warning("IRF model failed to fit for the selected data window. Try a longer timeframe.")
            else:
                fig_irf = go.Figure()
                fig_irf.add_trace(go.Scatter(x=list(range(21)), y=irf_kbe, name="Response of Broad Banks (KBE)"))
                fig_irf.add_trace(go.Scatter(x=list(range(21)), y=irf_iat, name="Response of Regional Banks (IAT)", line=dict(color='red')))
                fig_irf.add_hline(y=0, line_dash="dash", line_color="gray")
                fig_irf.update_layout(title="Impulse Response to 1-Unit Rate Shock", xaxis_title="Days since Shock", yaxis_title="Response (Returns)", template="plotly_white")
                st.plotly_chart(fig_irf, width='stretch')

            # 9. Heatmap
            st.divider()
            st.subheader("9. Correlation Heatmap")
            corr = calculate_correlation_matrix(data[['d_ff', 'r_kbe', 'r_iat', 'r_spy', 'r_vix']].dropna())
            st.plotly_chart(px.imshow(corr, text_auto=".2f", color_continuous_scale='Viridis', template="plotly_white"), width='stretch')

with tab3:
    st.header("Macro Interactions: MMFs & Yield Curve")
    with st.spinner("Analyzing macro interactions..."):
        mmf_proxy = get_proxy_mmf()
        tnx_proxy = get_proxy_10y_yield()
        
    if not mmf_proxy.empty and not tnx_proxy.empty and not kbe_proxy.empty:
        macro_merged = ff_proxy.join(mmf_proxy, lsuffix='_ff', rsuffix='_mmf').join(tnx_proxy, rsuffix='_tnx').join(kbe_proxy, rsuffix='_kbe').dropna()
        macro_merged.columns = ['FF_Proxy', 'MMF_Price', 'Ten_Year', 'KBE']
        macro_data = macro_merged[(macro_merged.index >= pd.to_datetime(start_date)) & (macro_merged.index <= pd.to_datetime(end_date))]
        
        # 1. MMF Destination
        st.subheader("1. Deposits Destination: Money Market Funds")
        st.markdown("As bank spreads widen, deposits flow into MMFs. We proxy this with the price/performance of VMFXX.")
        fig_mmf = go.Figure()
        fig_mmf.add_trace(go.Scatter(x=macro_data.index, y=macro_data['FF_Proxy'], name="Fed Funds Proxy (%)", yaxis="y1"))
        fig_mmf.add_trace(go.Scatter(x=macro_data.index, y=macro_data['MMF_Price'], name="MMF Price (VMFXX)", yaxis="y2"))
        fig_mmf.update_layout(yaxis=dict(title="Yield (%)"), yaxis2=dict(title="Price ($)", overlaying="y", side="right", showgrid=False), template="plotly_white")
        st.plotly_chart(fig_mmf, width='stretch')

        st.subheader("2. Banks vs MMFs: Relative Performance")
        rel = (macro_data['KBE'] / macro_data['MMF_Price'])
        rel = rel / rel.iloc[0]
        fig_rel = go.Figure()
        fig_rel.add_trace(go.Scatter(x=macro_data.index, y=rel, name="KBE / VMFXX (Normalized)"))
        fig_rel.add_hline(y=1, line_dash="dash", line_color="gray")
        fig_rel.update_layout(title="Bank Equity vs MMF Proxy (Relative)", yaxis_title="Ratio (Start = 1.0)", template="plotly_white")
        st.plotly_chart(fig_rel, width='stretch')
        
        # 3. Yield Curve Slope
        st.subheader("3. Yield Curve & The Deposits Channel")
        st.markdown("The paper argues the channel is more strained when the curve is flat or inverted (low slope).")
        macro_data['Slope'] = calculate_yield_curve_slope(macro_data['Ten_Year'], macro_data['FF_Proxy'])
        fig_slope = go.Figure(data=go.Scatter(x=macro_data.index, y=macro_data['Slope'], name="10Y-3M Slope", fill='tozeroy'))
        fig_slope.add_hrect(y0=-10, y1=0, fillcolor="rgba(255,0,0,0.1)", line_width=0)
        fig_slope.add_hrect(y0=0, y1=0.5, fillcolor="rgba(255,165,0,0.1)", line_width=0)
        fig_slope.add_hrect(y0=0.5, y1=10, fillcolor="rgba(0,128,0,0.1)", line_width=0)
        fig_slope.add_hline(y=0, line_dash="dash", line_color="red")
        fig_slope.update_layout(title="Yield Curve Slope (Ten Year - Fed Funds Proxy)", yaxis_title="Spread (%)", template="plotly_white")
        st.plotly_chart(fig_slope, width='stretch')

with tab4:
    st.header("Credit & Lending: Transmission to Real Economy")
    with st.spinner("Calculating credit spreads..."):
        lqd_proxy = get_proxy_credit_ig()
        
    if not lqd_proxy.empty and not kbe_proxy.empty and not iat_proxy.empty:
        credit_merged = ff_proxy.join(lqd_proxy, rsuffix='_lqd').join(spy_proxy, rsuffix='_spy').join(kbe_proxy, rsuffix='_kbe').join(iat_proxy, rsuffix='_iat').dropna()
        credit_merged.columns = ['FF_Proxy', 'Credit_Price', 'SPY', 'KBE', 'IAT']
        credit_data = credit_merged[(credit_merged.index >= pd.to_datetime(start_date)) & (credit_merged.index <= pd.to_datetime(end_date))]
        
        # Calculate proxy spread stress
        # Higher index = higher cost of credit relative to risk-free
        credit_data['Spread_Stress'] = calculate_credit_spread(credit_data['Credit_Price'], credit_data['FF_Proxy'] / 100 + 1) # Normalizing
        
        st.subheader("1. Lending Conditions Proxy")
        st.markdown("Widening credit 'stress' indicates a contraction in bank lending supply as deposits leave the system.")
        fig_credit = px.line(credit_data, y='Credit_Price', title="Investment Grade Credit Price (LQD)", labels={'Credit_Price': 'Price ($)'}, template="plotly_white")
        st.plotly_chart(fig_credit, width='stretch')
        
        st.info("When rates rise and deposits exit, banks must contract their balance sheets, leading to lower credit availability and higher spreads.")

        st.subheader("2. Credit Stress vs Bank Returns")
        credit_data['r_kbe'] = credit_data['KBE'].pct_change()
        credit_data['r_iat'] = credit_data['IAT'].pct_change()
        credit_scatter = credit_data.dropna()
        if credit_scatter.empty:
            st.warning("Not enough data to compute credit stress scatter.")
        else:
            fig_scatter = go.Figure()
            fig_scatter.add_trace(go.Scatter(x=credit_scatter['Spread_Stress'].diff(), y=credit_scatter['r_kbe'], mode='markers', name="KBE"))
            fig_scatter.add_trace(go.Scatter(x=credit_scatter['Spread_Stress'].diff(), y=credit_scatter['r_iat'], mode='markers', name="IAT", marker=dict(color="red")))
            fig_scatter.update_layout(title="Credit Stress vs Bank Returns", xaxis_title="Δ Credit Stress", yaxis_title="Return", template="plotly_white")
            st.plotly_chart(fig_scatter, width='stretch')

        st.subheader("3. Lead/Lag: Rates → Credit Stress")
        d_ff = credit_data['FF_Proxy'].diff().dropna()
        spread_change = credit_data['Spread_Stress'].diff().dropna()
        aligned_ff, aligned_spread = d_ff.align(spread_change, join="inner")
        lags, coeffs = calculate_cross_correlation(aligned_ff, aligned_spread, max_lag=15)
        if np.all(np.isnan(coeffs)):
            st.warning("Lead/lag correlation not available (insufficient variation).")
        else:
            fig_lag = go.Figure()
            fig_lag.add_trace(go.Bar(x=lags, y=coeffs))
            fig_lag.add_hline(y=0, line_dash="dash", line_color="gray")
            fig_lag.update_layout(title="Cross-Correlation (Rates vs Credit Stress)", xaxis_title="Lag (days)", yaxis_title="Correlation", template="plotly_white")
            st.plotly_chart(fig_lag, width='stretch')

with tab5:
    st.header("Case Study: March 2023 Banking Stress")
    st.markdown("""
    March 2023 represented a 'nonlinear' shock where the Deposits Channel mechanism reached a breaking point 
    for regional banks like SVB.
    """)
    
    # Zoom in on 2023
    crisis_start = pd.to_datetime('2023-02-01')
    crisis_end = pd.to_datetime('2023-05-01')
    if merged.empty:
        st.warning("Crisis period data not available in current fetch.")
    else:
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

            st.subheader("Cumulative Divergence (KBE vs IAT)")
            kbe_norm = crisis_data['KBE'] / crisis_data['KBE'].iloc[0]
            iat_norm = crisis_data['IAT'] / crisis_data['IAT'].iloc[0]
            fig_div = go.Figure()
            fig_div.add_trace(go.Scatter(x=crisis_data.index, y=kbe_norm, name="KBE (Normalized)"))
            fig_div.add_trace(go.Scatter(x=crisis_data.index, y=iat_norm, name="IAT (Normalized)", line=dict(color="red")))
            fig_div.update_layout(title="Cumulative Performance Divergence", yaxis_title="Normalized Price", template="plotly_white")
            st.plotly_chart(fig_div, width='stretch')

            st.subheader("Illustrative Waterfall: Deposits + AOCI + Equity")
            deposit_outflow = max(0.0, (1.0 - kbe_norm.min()) * 100)
            rate_change = (crisis_data['FF_Proxy'].iloc[-1] - crisis_data['FF_Proxy'].iloc[0]) / 100.0
            bond_loss = calculate_bond_portfolio_loss(base_value=60.0, rate_change=rate_change, duration=duration)
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
            fig_waterfall.update_layout(title="Illustrative Impact Decomposition", yaxis_title="Impact (pts)", template="plotly_white")
            st.plotly_chart(fig_waterfall, width='stretch')
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
