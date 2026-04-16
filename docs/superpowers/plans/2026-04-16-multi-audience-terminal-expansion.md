# Multi-Audience Terminal Expansion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the Streamlit terminal into a complete multi-audience research product with finished story arcs, stronger visual sequencing, deeper analytics, and a new monitoring/scenarios tab.

**Architecture:** Keep the Streamlit UI centered in `src/app.py`, but add only small, testable analytics helpers in `src/analysis.py` and, where needed, focused simulation helpers in `src/simulation.py`. Reuse the current yfinance proxy pipeline and preserve the existing tab-by-tab story flow, while layering each section with signal, mechanism, decision/monitoring, and three audience takeaways.

**Tech Stack:** Streamlit, pandas, numpy, plotly, statsmodels, pytest, ruff, ty, uv

---

## File Map
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/analysis.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/simulation.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_simulation.py`

## Chunk 1: Analytics Helpers

### Task 1: Add signal-board classification helper

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/analysis.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py`

- [ ] **Step 1: Write the failing test**

```python
def test_classify_channel_state():
    state = classify_channel_state(
        stress_value=1.9,
        bank_beta=-0.8,
        mmf_relative=-0.12,
    )

    assert state == "Stressed"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_analysis.py::test_classify_channel_state -v`
Expected: FAIL with `NameError` or import failure for `classify_channel_state`

- [ ] **Step 3: Write minimal implementation**

```python
def classify_channel_state(
    stress_value: float,
    bank_beta: float,
    mmf_relative: float,
) -> str:
    if stress_value >= 1.5 or (bank_beta < -0.5 and mmf_relative < -0.05):
        return "Stressed"
    if stress_value >= 0.75 or bank_beta < -0.2 or mmf_relative < -0.02:
        return "Active"
    return "Dormant"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_analysis.py::test_classify_channel_state -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/analysis.py tests/test_analysis.py
git commit -m "Add channel state classification helper"
```

### Task 2: Add curve-regime classifier

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/analysis.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py`

- [ ] **Step 1: Write the failing test**

```python
def test_classify_curve_regime():
    slope = pd.Series([1.2, 0.1, -0.3], index=["a", "b", "c"])
    regimes = classify_curve_regime(slope)

    assert regimes.tolist() == ["Normal", "Flat", "Inverted"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_analysis.py::test_classify_curve_regime -v`
Expected: FAIL with missing helper

- [ ] **Step 3: Write minimal implementation**

```python
def classify_curve_regime(
    slope: pd.Series,
    flat_threshold: float = 0.25,
) -> pd.Series:
    regimes = pd.Series("Normal", index=slope.index)
    regimes[slope < 0] = "Inverted"
    regimes[(slope >= 0) & (slope <= flat_threshold)] = "Flat"
    return regimes
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_analysis.py::test_classify_curve_regime -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/analysis.py tests/test_analysis.py
git commit -m "Add curve regime classification helper"
```

### Task 3: Add stress-threshold map helper

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/analysis.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py`

- [ ] **Step 1: Write the failing test**

```python
def test_build_combined_stress_grid_shape():
    grid = build_combined_stress_grid(
        outflow_range=np.array([0.0, 0.1]),
        aoci_range=np.array([0.0, 0.2, 0.4]),
        threshold=0.25,
    )

    assert grid.shape == (2, 3)
    assert grid.iloc[-1, -1] == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_analysis.py::test_build_combined_stress_grid_shape -v`
Expected: FAIL with missing helper

- [ ] **Step 3: Write minimal implementation**

```python
def build_combined_stress_grid(
    outflow_range: np.ndarray,
    aoci_range: np.ndarray,
    threshold: float = 0.25,
) -> pd.DataFrame:
    z = []
    for outflow in outflow_range:
        row = []
        for aoci in aoci_range:
            row.append(int(outflow + aoci >= threshold))
        z.append(row)
    return pd.DataFrame(z, index=outflow_range, columns=aoci_range)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_analysis.py::test_build_combined_stress_grid_shape -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/analysis.py tests/test_analysis.py
git commit -m "Add combined stress grid helper"
```

### Task 4: Add scenario expectation mapping helper

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/analysis.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_analysis.py`

- [ ] **Step 1: Write the failing test**

```python
def test_scenario_expectations_higher_for_longer():
    result = scenario_expectations("Higher for longer")

    assert result["spreads"] == "Wider"
    assert result["deposits"] == "Weaker"
    assert result["banks"] == "Underperform"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_analysis.py::test_scenario_expectations_higher_for_longer -v`
Expected: FAIL with missing helper

- [ ] **Step 3: Write minimal implementation**

```python
def scenario_expectations(name: str) -> dict[str, str]:
    mapping = {
        "Higher for longer": {
            "spreads": "Wider",
            "deposits": "Weaker",
            "stress": "Higher",
            "banks": "Underperform",
        },
        "Rapid cuts": {
            "spreads": "Narrower",
            "deposits": "Stabilize",
            "stress": "Lower",
            "banks": "Rebound",
        },
        "Volatility shock": {
            "spreads": "Wider",
            "deposits": "Fragile",
            "stress": "Higher",
            "banks": "Sell off",
        },
        "Bank-specific confidence shock": {
            "spreads": "Wider",
            "deposits": "Run risk",
            "stress": "Higher",
            "banks": "Diverge",
        },
    }
    return mapping[name]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_analysis.py::test_scenario_expectations_higher_for_longer -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/analysis.py tests/test_analysis.py
git commit -m "Add scenario expectation mapping helper"
```

### Task 5: Add crisis counterfactual helper

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/simulation.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_simulation.py`

- [ ] **Step 1: Write the failing test**

```python
def test_counterfactual_impact_reduces_with_lower_duration():
    result = counterfactual_channel_impact(
        deposit_outflow=12.0,
        rate_change=0.02,
        duration=2.0,
        deposit_friction=0.5,
    )

    assert result["aoci_loss"] < 12.0
    assert result["total_impact"] > 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_simulation.py::test_counterfactual_impact_reduces_with_lower_duration -v`
Expected: FAIL with missing helper

- [ ] **Step 3: Write minimal implementation**

```python
def counterfactual_channel_impact(
    deposit_outflow: float,
    rate_change: float,
    duration: float,
    deposit_friction: float,
) -> dict[str, float]:
    adjusted_outflow = deposit_outflow * (1.0 - deposit_friction)
    aoci_loss = abs(duration * rate_change * 100)
    total_impact = adjusted_outflow + aoci_loss
    return {
        "deposit_outflow": adjusted_outflow,
        "aoci_loss": aoci_loss,
        "total_impact": total_impact,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_simulation.py::test_counterfactual_impact_reduces_with_lower_duration -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/simulation.py tests/test_simulation.py
git commit -m "Add counterfactual channel impact helper"
```

## Chunk 2: Theory & Simulation Story Completion

### Task 6: Add threshold and scenario story sections to Theory & Simulation

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Add a failing smoke assertion for the new section labels**

```python
def test_theory_tab_story_labels_present():
    content = Path("src/app.py").read_text()

    assert "Q5: When do outflows and AOCI become destabilizing?" in content
    assert "Research takeaway" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py -k theory_tab_story_labels_present -v`
Expected: FAIL because the test does not exist yet

- [ ] **Step 3: Add the smoke test to `tests/test_cli.py`**

```python
from pathlib import Path

def test_theory_tab_story_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Q5: When do outflows and AOCI become destabilizing?" in content
    assert "Research takeaway" in content
```

- [ ] **Step 4: Run test to verify it fails for the right reason**

Run: `uv run pytest tests/test_cli.py::test_theory_tab_story_labels_present -v`
Expected: FAIL because the new label is missing from `src/app.py`

- [ ] **Step 5: Implement the minimal UI changes**

```python
st.subheader("Q5: When do outflows and AOCI become destabilizing?")
st.markdown("We map the combinations of funding loss and mark-to-market pressure that push the system into a stress zone.")

grid = build_combined_stress_grid(
    outflow_range=np.linspace(0.0, 0.25, 25),
    aoci_range=np.linspace(0.0, 0.25, 25),
    threshold=0.25,
)

fig_threshold = px.imshow(
    grid.values,
    x=[f"{c:.0%}" for c in grid.columns],
    y=[f"{i:.0%}" for i in grid.index],
    labels=dict(x="AOCI proxy", y="Deposit outflow proxy", color="Stress zone"),
    color_continuous_scale="YlOrRd",
    aspect="auto",
)
st.plotly_chart(fig_threshold, width="stretch")

st.markdown("**What to notice:** the stress zone appears only after outflows and AOCI pressure reinforce each other.")
```

- [ ] **Step 6: Add the audience takeaway block**

```python
st.markdown("**Research takeaway:** concentration and stickiness create nonlinear funding pressure.")
st.markdown("**Investor takeaway:** threshold behavior matters more than smooth linear sensitivity once balance sheets are strained.")
st.markdown("**Policy/risk takeaway:** outflows are most dangerous when unrealized losses are already large.")
```

- [ ] **Step 7: Run the test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_theory_tab_story_labels_present -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Complete theory and simulation story sections"
```

## Chunk 3: Empirical Terminal Story Completion

### Task 7: Add signal board and regime framing to Empirical Terminal

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Add the failing smoke test**

```python
def test_empirical_terminal_signal_board_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Signal Board" in content
    assert "Dormant" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_empirical_terminal_signal_board_labels_present -v`
Expected: FAIL

- [ ] **Step 3: Implement the signal board**

```python
signal_state = classify_channel_state(
    stress_value=float(stress.dropna().iloc[-1]),
    bank_beta=float(beta_df["KBE"].dropna().iloc[-1]),
    mmf_relative=float(rel.dropna().iloc[-1] - 1.0) if "rel" in locals() else 0.0,
)

st.subheader("Signal Board")
col1, col2, col3 = st.columns(3)
col1.metric("Channel state", signal_state)
col2.metric("Latest stress", f"{float(stress.dropna().iloc[-1]):.2f}")
col3.metric("Latest bank beta", f"{float(beta_df['KBE'].dropna().iloc[-1]):.2f}")
st.markdown("**What to notice:** the terminal should summarize whether the channel is dormant, active, or stressed before the deep dives begin.")
```

- [ ] **Step 4: Add regime-segmentation framing**

```python
st.subheader("Q8: Which regime are we in?")
st.markdown("We split observations into calm and stressed regimes to see when the channel becomes state dependent.")
```

- [ ] **Step 5: Add audience takeaways**

```python
st.markdown("**Research takeaway:** rate sensitivity is strongest when stress conditions are already elevated.")
st.markdown("**Investor takeaway:** regime shifts matter more than unconditional averages.")
st.markdown("**Policy/risk takeaway:** the same hike can have very different effects depending on system stress.")
```

- [ ] **Step 6: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_empirical_terminal_signal_board_labels_present -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Complete empirical terminal signal framing"
```

## Chunk 4: Macro & Credit Story Completion

### Task 8: Add regime matrix and warning rules to Macro & Credit

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Add the failing smoke test**

```python
def test_macro_regime_matrix_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Regime Matrix" in content
    assert "Crisis" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_macro_regime_matrix_labels_present -v`
Expected: FAIL

- [ ] **Step 3: Implement the regime matrix section**

```python
st.subheader("Q5: Which macro regime are we in?")
st.markdown("We combine the curve regime and stress backdrop into a simple operating map.")

regime_labels = pd.DataFrame(
    [
        ["Normal", "Squeeze"],
        ["Stress", "Crisis"],
    ],
    index=["Calm stress", "High stress"],
    columns=["Normal/flat curve", "Inverted curve"],
)
st.table(regime_labels)
st.markdown("**What to notice:** inversion is not sufficient on its own; crisis requires inversion plus elevated stress.")
```

- [ ] **Step 4: Add warning-rule bullets**

```python
st.markdown("**Warning rules:**")
st.markdown("- Inverted curve + rising stress index + bank underperformance")
st.markdown("- MMF relative outperformance + negative bank beta")
st.markdown("- Credit stress widening while bank returns stay weak")
```

- [ ] **Step 5: Add audience takeaways**

```python
st.markdown("**Research takeaway:** funding pressure and credit pressure interact through macro regime shifts.")
st.markdown("**Investor takeaway:** bank underperformance means something different in a liquidity-migration regime than in a credit-stress regime.")
st.markdown("**Policy/risk takeaway:** surveillance should escalate when multiple warning rules trigger together.")
```

- [ ] **Step 6: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_macro_regime_matrix_labels_present -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Complete macro and credit regime story"
```

## Chunk 5: March 2023 Case Study Completion

### Task 9: Add timeline, waterfall framing, and counterfactuals

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Add the failing smoke test**

```python
def test_case_study_counterfactual_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Q4: What would have reduced the damage?" in content
    assert "Lower duration" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_case_study_counterfactual_labels_present -v`
Expected: FAIL

- [ ] **Step 3: Implement the counterfactual section**

```python
st.subheader("Q4: What would have reduced the damage?")
st.markdown("We run simple counterfactuals to show which balance-sheet characteristics would have softened the crisis.")

counterfactuals = {
    "Lower duration": counterfactual_channel_impact(deposit_outflow=12.0, rate_change=0.02, duration=2.0, deposit_friction=0.2),
    "Higher stickiness": counterfactual_channel_impact(deposit_outflow=12.0, rate_change=0.02, duration=5.0, deposit_friction=0.6),
    "Less concentrated system": counterfactual_channel_impact(deposit_outflow=8.0, rate_change=0.02, duration=5.0, deposit_friction=0.3),
}
st.dataframe(pd.DataFrame(counterfactuals).T)
st.markdown("**What to notice:** duration and deposit stickiness each change the shape of crisis transmission, not just its size.")
```

- [ ] **Step 4: Add audience takeaways**

```python
st.markdown("**Research takeaway:** March 2023 exposed where the canonical channel became nonlinear.")
st.markdown("**Investor takeaway:** large-bank resilience and regional fragility reflected different funding narratives.")
st.markdown("**Policy/risk takeaway:** reducing duration and stabilizing deposits are both crisis-mitigation levers.")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_case_study_counterfactual_labels_present -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Complete March 2023 case study story"
```

## Chunk 6: Monitoring & Scenarios Tab

### Task 10: Add the Monitoring & Scenarios tab scaffold

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Add the failing smoke test**

```python
def test_monitoring_tab_present() -> None:
    content = Path("src/app.py").read_text()
    assert "Monitoring & Scenarios" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_monitoring_tab_present -v`
Expected: FAIL

- [ ] **Step 3: Add the new tab to the tab list**

```python
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Theory & Simulation", "Empirical Terminal", "Macro & Credit", "Case Study", "Monitoring & Scenarios"]
)
```

- [ ] **Step 4: Add the monitoring tab shell**

```python
with tab5:
    st.header("Monitoring & Scenarios")
    st.markdown("Turn the terminal into a practical monitoring board for research, markets, and policy.")
```

- [ ] **Step 5: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_monitoring_tab_present -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Add monitoring and scenarios tab scaffold"
```

### Task 11: Add scorecard and scenario cards to the Monitoring & Scenarios tab

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

- [ ] **Step 1: Add the failing smoke test**

```python
def test_monitoring_playbook_labels_present() -> None:
    content = Path("src/app.py").read_text()
    assert "If this, then that playbook" in content
    assert "Higher for longer" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_monitoring_playbook_labels_present -v`
Expected: FAIL

- [ ] **Step 3: Implement the scorecard**

```python
st.subheader("Signal Scorecard")
score_cols = st.columns(5)
score_cols[0].metric("Stress composite", f"{latest_stress:.2f}")
score_cols[1].metric("Bank beta regime", signal_state)
score_cols[2].metric("Curve regime", latest_curve_regime)
score_cols[3].metric("MMF pressure", f"{latest_mmf_relative:.2%}")
score_cols[4].metric("Credit stress trend", f"{latest_credit_change:.2f}")
st.markdown("**What to notice:** the terminal should summarize conditions before the user reads a single deep-dive chart.")
```

- [ ] **Step 4: Implement scenario cards**

```python
st.subheader("Scenario Cards")
for scenario_name in [
    "Higher for longer",
    "Rapid cuts",
    "Volatility shock",
    "Bank-specific confidence shock",
]:
    scenario = scenario_expectations(scenario_name)
    st.markdown(f"**{scenario_name}**")
    st.markdown(
        f"Spreads: {scenario['spreads']} | Deposits: {scenario['deposits']} | Stress: {scenario['stress']} | Banks: {scenario['banks']}"
    )
```

- [ ] **Step 5: Implement the playbook**

```python
st.subheader("If this, then that playbook")
st.markdown("- If rates rise while VIX stays low: expect orderly spread widening before panic.")
st.markdown("- If rates are stable but VIX spikes: expect fear to dominate rate mechanics.")
st.markdown("- If the curve steepens through cuts: expect temporary relief in funding stress.")
st.markdown("- If MMFs outperform while bank betas stay negative: treat that as an active-channel warning.")
```

- [ ] **Step 6: Add audience takeaways**

```python
st.markdown("**Research takeaway:** use the scorecard to identify which hypothesis deserves the next deep test.")
st.markdown("**Investor takeaway:** scenario cards convert macro states into positioning narratives.")
st.markdown("**Policy/risk takeaway:** the playbook identifies when surveillance should escalate.")
```

- [ ] **Step 7: Run test to verify it passes**

Run: `uv run pytest tests/test_cli.py::test_monitoring_playbook_labels_present -v`
Expected: PASS

- [ ] **Step 8: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Add monitoring scorecard and scenarios"
```

## Chunk 7: Final Validation

### Task 12: Run formatting, type checks, and tests

- [ ] Run: `uv run fix`
- [ ] Run: `uv run typecheck`
- [ ] Run: `uv run test`
- [ ] Run: `uv run check`
- [ ] Manual run: `uv run app`

### Task 13: Final commit

```bash
git add src/app.py src/analysis.py src/simulation.py tests/test_analysis.py tests/test_simulation.py tests/test_cli.py
git commit -m "Expand terminal stories and monitoring workflows"
```

## Plan Self-Review
- Spec coverage: the plan covers all five target tabs, adds the new monitoring/scenarios tab, finishes unfinished story arcs, and includes the audience takeaway structure.
- Placeholder scan: every task includes explicit file paths, test code, commands, and commit steps.
- Type consistency: helper names are defined once and reused consistently across analytics, simulation, and app tasks.
