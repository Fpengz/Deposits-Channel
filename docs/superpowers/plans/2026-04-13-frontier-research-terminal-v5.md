# Frontier Research Suite v5.0 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement advanced quantitative modules: Impulse Response Functions (VAR), Unrealized Losses (AOCI), Volatility-conditional analysis (VIX), and Synthetic HHI cohorts.

**Architecture:** 
- `data_fetcher.py`: Add VIX fetching.
- `analysis.py`: Implement IRF calculation and duration risk math.
- `app.py`: Expand to 6 specialized sub-sections across reorganized tabs.

**Tech Stack:** Python, Streamlit, Plotly, Pandas, Statsmodels (VAR), Numpy.

---

## Chunk 1: Frontier Backend Logic

### Task 1: Update Data and Statistical Modules

**Files:**
- Modify: `src/data_fetcher.py`
- Modify: `src/analysis.py`

- [ ] **Step 1: Add VIX to data fetcher**
```python
def get_proxy_volatility() -> pd.DataFrame:
    """Returns the CBOE Volatility Index (^VIX)."""
    return fetch_market_data('^VIX')
```

- [ ] **Step 2: Implement Impulse Response Function (IRF) logic**
```python
def calculate_irf(df: pd.DataFrame, response_col: str, shock_col: str, periods: int = 20):
    """Calculates IRF for a response column given a shock in shock_col."""
    data = df[[shock_col, response_col]].dropna()
    from statsmodels.tsa.api import VAR
    model = VAR(data)
    results = model.fit(maxlags=15, ic='aic')
    irf = results.irf(periods)
    # Get the specific response of response_col to shock_col
    # results.irf returns (periods+1, k, k)
    idx_shock = 0 # shock_col is first
    idx_resp = 1  # response_col is second
    return irf.orth_irfs[:, idx_resp, idx_shock]
```

- [ ] **Step 3: Implement Bond Portfolio Loss (AOCI) math**
```python
def calculate_bond_portfolio_loss(base_value: float, rate_change: float, duration: float = 5.0) -> float:
    """Calculates market value loss based on duration risk."""
    # Simplified duration math: dV = -D * dy * V
    loss = -duration * rate_change * base_value
    return loss
```

- [ ] **Step 4: Commit logic updates**
```bash
git add src/data_fetcher.py src/analysis.py
git commit -m "feat: implement IRF and AOCI duration risk logic"
```

---

## Chunk 2: Empirical Frontier

### Task 2: Implement IRF and VIX Analysis in `app.py`

**Files:**
- Modify: `src/app.py`

- [ ] **Step 1: Add VIX-conditional regression**
Calculate Beta when VIX > 20 vs VIX < 20.

- [ ] **Step 2: Add IRF Visualization**
Show the dynamic ripple effect of a rate shock.

- [ ] **Step 3: Commit**
```bash
git add src/app.py
git commit -m "feat: add dynamic shock analysis and VIX-conditional analysis"
```

---

## Chunk 3: Simulation Frontier

### Task 3: Implement AOCI and Synthetic Cohorts

**Files:**
- Modify: `src/app.py`

- [ ] **Step 1: Add AOCI "Dual Squeeze" metric to Theory tab**
Show bond losses + deposit outflows.

- [ ] **Step 2: Implement Synthetic "Monopolist vs Competitor" Dashboard**
Use synthetic data based on paper coefficients.

- [ ] **Step 3: Verify and Finalize UI**
Run `uv run streamlit run src/app.py`.

- [ ] **Step 4: Commit and Finish**
```bash
git add src/app.py
git commit -m "feat: complete Frontier Suite with AOCI and Synthetic HHI analysis"
```
