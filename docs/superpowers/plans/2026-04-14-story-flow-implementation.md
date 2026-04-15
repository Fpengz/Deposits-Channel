# Story-Driven Terminal Reorg Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the Streamlit terminal into six story-complete tabs with question-driven sections, guiding copy, deeper analytics, and per-tab takeaways.

**Architecture:** Keep Streamlit as the single UI file while adding small, testable analytics helpers in `src/analysis.py` and `src/simulation.py`. Reuse yfinance proxies and existing calculations; add minimal new helpers for new story questions.

**Tech Stack:** Streamlit, pandas, numpy, plotly, statsmodels, pytest, ruff, ty

---

## File Map (Planned)
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/analysis.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/simulation.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_simulation.py`

## Chunk 1: Analytics Helpers & Tests

### Task 1: Add helper for friction-adjusted outflow curve
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/analysis.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py`

- [ ] **Step 1: Write failing test**
```python
def test_adjust_outflow_for_friction():
    spread = pd.Series([0.0, 0.01, 0.02])
    adjusted = adjust_outflow_for_friction(spread, friction=0.5)
    assert adjusted.iloc[0] == pytest.approx(0.0)
    assert adjusted.iloc[-1] < spread.iloc[-1]
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest /Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py::test_adjust_outflow_for_friction -v`
Expected: FAIL (function missing)

- [ ] **Step 3: Implement helper**
```python
def adjust_outflow_for_friction(spread: pd.Series, friction: float = 0.5) -> pd.Series:
    friction = max(0.0, min(1.0, friction))
    return spread * (1.0 - friction)
```

- [ ] **Step 4: Re-run test**
Run: same test; Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/analysis.py /Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py
git commit -m "Add friction-adjusted outflow helper"
```

### Task 2: Add lending contraction response helper
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/analysis.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py`

- [ ] **Step 1: Write failing test**
```python
def test_lending_response_lagged():
    outflow = pd.Series([0, 1, 2, 3, 4])
    response = simulate_lending_response(outflow, lag_days=2, decay=0.5)
    assert response.iloc[0] == pytest.approx(0.0)
    assert response.iloc[2] > 0
```

- [ ] **Step 2: Run test**
Run: `pytest /Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py::test_lending_response_lagged -v`
Expected: FAIL

- [ ] **Step 3: Implement helper**
```python
def simulate_lending_response(outflow: pd.Series, lag_days: int = 5, decay: float = 0.8) -> pd.Series:
    response = outflow.shift(lag_days).fillna(0) * (1.0 - decay)
    return response.cumsum()
```

- [ ] **Step 4: Re-run test**
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/analysis.py /Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py
git commit -m "Add lending response lag helper"
```

### Task 3: Add shock attribution helper (rate vs VIX)
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/analysis.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py`

- [ ] **Step 1: Write failing test**
```python
def test_multivariate_shock_importance():
    df = pd.DataFrame({"y": [0.1, 0.0, 0.2], "d_ff": [0.01, 0.0, -0.01], "r_vix": [0.02, -0.01, 0.03]})
    res = multivariate_shock_importance(df, "y", ["d_ff", "r_vix"])
    assert "d_ff" in res
    assert "r_vix" in res
```

- [ ] **Step 2: Run test**
Run: `pytest /Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py::test_multivariate_shock_importance -v`
Expected: FAIL

- [ ] **Step 3: Implement helper**
```python
def multivariate_shock_importance(df: pd.DataFrame, y_col: str, x_cols: list[str]) -> dict:
    y = df[y_col]
    x = sm.add_constant(df[x_cols])
    res = sm.OLS(y, x).fit()
    return {col: res.params[col] for col in x_cols}
```

- [ ] **Step 4: Re-run test**
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/analysis.py /Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py
git commit -m "Add multivariate shock attribution helper"
```

### Task 4: Add propagation speed + normalization helpers
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/analysis.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py`

- [ ] **Step 1: Write failing test**
```python
def test_time_to_threshold():
    s = pd.Series([0, 1, 2, 3, 4])
    assert time_to_threshold(s, 3) == 3

def test_post_event_normalization():
    pre = pd.Series([1, 1, 1])
    post = pd.Series([0.9, 1.0, 1.1])
    band = normalization_band(pre)
    assert band[0] < post.mean() < band[1]
```

- [ ] **Step 2: Run tests**
Expected: FAIL

- [ ] **Step 3: Implement helpers**
```python
def time_to_threshold(series: pd.Series, threshold: float) -> int | None:
    hits = series[series >= threshold]
    return None if hits.empty else int(hits.index[0])

def normalization_band(pre_event: pd.Series, n_std: float = 1.0) -> tuple[float, float]:
    mean = pre_event.mean()
    std = pre_event.std(ddof=0)
    return mean - n_std * std, mean + n_std * std
```

- [ ] **Step 4: Re-run tests**
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/analysis.py /Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py
git commit -m "Add propagation and normalization helpers"
```

---

## Chunk 2: Reorganize Tabs & Section Flow

### Task 5: Rebuild tab structure into six story tabs
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Write a failing UI check (optional)**
If no UI test framework exists, skip.

- [ ] **Step 2: Implement tab scaffold**
Update tab list to:
- Mechanism & Market Power
- Sensitivity & Scenarios
- Empirical Signals
- Shock Attribution
- Macro & Credit Transmission
- 2023 Case Study

- [ ] **Step 3: Move existing sections into their new tabs**
Preserve code blocks, adjust headers, insert guiding copy.

- [ ] **Step 4: Manual run**
Run: `streamlit run /Users/zhoufuwang/Projects/deposits_channel/src/app.py`
Expected: 6 tabs show, no exceptions.

- [ ] **Step 5: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/app.py
git commit -m "Reorganize tabs into story-driven flow"
```

---

## Chunk 3: Add New Story Sections per Tab

### Task 6: Tab 1 (Mechanism & Market Power)
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Insert Q1, Q2, Q3 blocks with guiding copy**
- Q1: mechanism schematic + KPI strip (reuse existing)
- Q2: heatmap/contours (reuse existing)
- Q3: friction slider + outflow curve (new helper)

- [ ] **Step 2: Manual run**
Check layout order, copy, and charts.

- [ ] **Step 3: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/app.py
git commit -m "Add market power story sections"
```

### Task 7: Tab 2 (Sensitivity & Scenarios)
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Insert Q1–Q3 blocks**
- Q1: elasticity surfaces + deposit line
- Q2: scenario small multiples
- Q3: lending response curve (new helper)

- [ ] **Step 2: Manual run**

- [ ] **Step 3: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/app.py
git commit -m "Add sensitivity and scenario story sections"
```

### Task 8: Tab 3 (Empirical Signals)
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Insert Q1–Q4 blocks**
- Q1: rates sensitivity + betas
- Q2: stress composite index
- Q3: stability (recursive/rolling)
- Q4: policy cycle clustering (event study)

- [ ] **Step 2: Manual run**

- [ ] **Step 3: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/app.py
git commit -m "Add empirical signal story sections"
```

### Task 9: Tab 4 (Shock Attribution)
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Insert Q1–Q3 blocks**
- Q1: rate vs VIX importance (new helper)
- Q2: size proxy differences (KBE/IAT/SPY)
- Q3: bank vs credit rate sensitivity

- [ ] **Step 2: Manual run**

- [ ] **Step 3: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/app.py
git commit -m "Add shock attribution story sections"
```

### Task 10: Tab 5 (Macro & Credit Transmission)
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Insert Q1–Q4 blocks**
- Q1: deposit destination (KBE/VMFXX)
- Q2: liquidity vs risk dominance
- Q3: curve inversion overlap with drawdowns
- Q4: credit feedback (scatter + lead/lag)

- [ ] **Step 2: Manual run**

- [ ] **Step 3: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/app.py
git commit -m "Add macro and credit transmission story sections"
```

### Task 11: Tab 6 (2023 Case Study)
**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Insert Q1–Q4 blocks**
- Q1: divergence chart
- Q2: propagation speed
- Q3: stacked contributions
- Q4: normalization vs baseline band

- [ ] **Step 2: Manual run**

- [ ] **Step 3: Commit**
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/app.py
git commit -m "Add 2023 case study story sections"
```

---

## Chunk 4: Validation & Cleanup

### Task 12: Run tests and lint
- [ ] Run: `uv run ruff check .`
- [ ] Run: `uv run ruff format .`
- [ ] Run: `uv run ty check --extra-search-path src`
- [ ] Run: `pytest -q`

### Task 13: Final commit
```bash
git add /Users/zhoufuwang/Projects/deposits_channel/src/app.py /Users/zhoufuwang/Projects/deposits_channel/src/analysis.py /Users/zhoufuwang/Projects/deposits_channel/src/simulation.py /Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py /Users/zhoufuwang/Projects/deposits_channel/tests/test_simulation.py
git commit -m "Implement story-driven terminal flow"
```

---

## Plan Review Loop
Subagent review is required by the skill, but the current environment disallows spawning subagents. Proceed without automated plan review and request human review instead.
