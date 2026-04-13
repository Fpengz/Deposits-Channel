# Macro-Finance Terminal v4.0 Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the dashboard into a full macro-finance research terminal with MMF flows, yield curve interactions, credit spreads, and a 2023 crisis case study.

**Architecture:** 
- `data_fetcher.py`: Add 4 new macro tickers.
- `analysis.py`: Add slope and spread calculation logic.
- `app.py`: Expand to 5 tabs with multi-asset visualizations.

**Tech Stack:** Python, Streamlit, Plotly, Pandas, Statsmodels.

---

## Chunk 1: Data and Analysis Foundation

### Task 1: Add Macro Proxies to `data_fetcher.py`

**Files:**
- Modify: `src/data_fetcher.py`

- [ ] **Step 1: Add MMF, 10Y, and Credit ETF tickers**
```python
def get_proxy_mmf() -> pd.DataFrame:
    """Returns Vanguard Federal MMF (VMFXX) as a proxy."""
    return fetch_market_data('VMFXX')

def get_proxy_10y_yield() -> pd.DataFrame:
    """Returns 10-Year Treasury Note Yield (^TNX)."""
    return fetch_market_data('^TNX')

def get_proxy_credit_ig() -> pd.DataFrame:
    """Returns iShares Investment Grade Corporate Bond ETF (LQD)."""
    return fetch_market_data('LQD')
```

- [ ] **Step 2: Commit**
```bash
git add src/data_fetcher.py
git commit -m "feat: add macro proxies (MMF, 10Y, Credit) to data fetcher"
```

### Task 2: Implement Macro Analysis Helpers

**Files:**
- Modify: `src/analysis.py`

- [ ] **Step 1: Add yield curve and spread logic**
```python
def calculate_yield_curve_slope(ten_year: pd.Series, three_month: pd.Series) -> pd.Series:
    """Calculates the 10Y - 3M yield curve slope."""
    return ten_year - three_month

def calculate_credit_spread(credit_yield: pd.Series, treasury_yield: pd.Series) -> pd.Series:
    """Calculates proxy credit spread."""
    # Simplified proxy: we use changes in price as a proxy for spread stress if yield is unavailable
    # or calculate directly if yields are fetched.
    return credit_yield - treasury_yield
```

- [ ] **Step 2: Commit**
```bash
git add src/analysis.py
git commit -m "feat: add yield curve and credit spread analysis helpers"
```

---

## Chunk 2: Dashboard Multi-Asset Expansion

### Task 3: Implement Macro & Credit Tabs in `app.py`

**Files:**
- Modify: `src/app.py`

- [ ] **Step 1: Add Tab 3: Macro Interactions**
Show FFR vs MMF Assets and Yield Curve Slope interaction.

- [ ] **Step 2: Add Tab 4: Credit & Lending**
Show transmission to real economy via LQD spreads.

- [ ] **Step 3: Commit**
```bash
git add src/app.py
git commit -m "feat: implement macro and credit tabs in the terminal"
```

---

## Chunk 3: Crisis Case Study

### Task 4: Implement Tab 5: 2023 Case Study

**Files:**
- Modify: `src/app.py`

- [ ] **Step 1: Add high-res zoom-in for March 2023**
Filter data specifically for 2023-03 and overlay Regional Bank stress.

- [ ] **Step 2: Add explanatory educational text**
Connect the "unrealized losses" mentioned in the report to the "Deposits Channel" mechanism.

- [ ] **Step 3: Verify and Finalize**
Run `uv run streamlit run src/app.py`.

- [ ] **Step 4: Commit**
```bash
git add src/app.py
git commit -m "feat: add dedicated 2023 crisis case study tab"
```
