import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from simulation import calculate_deposit_rate, calculate_deposit_volume
from data_fetcher import get_proxy_fed_funds, get_proxy_deposits

st.set_page_config(page_title="Deposits Channel", layout="wide")

st.title("The Deposits Channel of Monetary Policy")
st.markdown("""
Interactive simulation of bank market power and deposit flows. This dashboard replicates the core logic of 
**Drechsler, Savov & Schnabl (2017)**: *\"The Deposits Channel of Monetary Policy\"*.
""")

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
# Add a vertical line for the current Fed Funds Rate
fig.add_vline(x=fed_funds_rate*100, line_dash="dash", line_color="red", annotation_text="Current Rate")

fig.update_layout(
    title="Theoretical Deposit Volume vs Fed Funds Rate",
    xaxis_title="Fed Funds Rate (%)",
    yaxis_title="Deposit Volume ($B)",
    hovermode="x unified"
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Empirical Market Proxy Data")
st.markdown("""
Using **Yahoo Finance** data as a proxy for the Fed Funds Rate (13-week T-Bill Yield) and the banking sector (KBE Bank ETF).
""")

# Load and Plot Market Proxy Data
with st.spinner("Fetching market data..."):
    ff_proxy = get_proxy_fed_funds()
    kbe_proxy = get_proxy_deposits()

    if not ff_proxy.empty and not kbe_proxy.empty:
        # Merge on index (date)
        merged = ff_proxy.join(kbe_proxy, lsuffix='_ff', rsuffix='_kbe')
        merged.columns = ['FF Rate Proxy', 'Bank ETF Price']
        
        fig_emp = go.Figure()
        fig_emp.add_trace(go.Scatter(x=merged.index, y=merged['FF Rate Proxy'], name="Fed Funds Rate Proxy (%)", yaxis="y1"))
        fig_emp.add_trace(go.Scatter(x=merged.index, y=merged['Bank ETF Price'], name="Bank ETF Price ($)", yaxis="y2"))

        fig_emp.update_layout(
            title="Fed Funds Proxy vs Bank Stock Performance",
            xaxis_title="Date",
            yaxis=dict(title="Yield (%)", side="left"),
            yaxis2=dict(title="ETF Price ($)", side="right", overlaying="y", showgrid=False),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_emp, use_container_width=True)
    else:
        st.error("Could not retrieve market data. Please check your internet connection.")

st.info("The paper argues that when rates rise (blue line), bank profitability/deposits contract (as reflected in the stock performance).")
