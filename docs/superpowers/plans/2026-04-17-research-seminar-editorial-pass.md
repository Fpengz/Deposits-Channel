# Research Seminar Editorial Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refine the Streamlit research terminal so every tab reads like a coherent research seminar with clearer narrative flow, stronger interpretation, and more consistent editorial structure.

**Architecture:** Keep the current analytical structure and charts mostly intact, but rewrite and reorder the copy in `/Users/zhoufuwang/Projects/deposits_channel/src/app.py` so each tab follows a predictable argument: motivating question, short answer, evidence, mechanism, what to notice, and takeaway. Protect the new editorial structure with focused string-presence tests in `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`.

**Tech Stack:** Python, Streamlit, pytest, Ruff, Ty

---

## File Map

- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
  - Reorder section copy within tabs
  - Rewrite tab intros, section headers, captions, “what to notice,” and takeaways
  - Keep existing analytics/helpers intact unless wording accuracy requires tiny adjustments
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
  - Add/adjust smoke tests that assert the editorial structure exists in the app source
- Verify: `/Users/zhoufuwang/Projects/deposits_channel/pyproject.toml`
  - Use existing project commands; no config changes expected

### Task 1: Add Seminar Structure Guardrails

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_tabs_follow_research_seminar_spine() -> None:
    content = Path("src/app.py").read_text()

    for label in [
        "Short answer",
        "What to notice",
        "Takeaway",
    ]:
        assert label in content

    for heading in [
        "Theory & Simulation",
        "Empirical Terminal",
        "Macro & Credit",
        "Case Study",
        "Monitoring & Scenarios",
    ]:
        assert heading in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_tabs_follow_research_seminar_spine -q`
Expected: FAIL because the merged app does not yet contain the standardized seminar labels consistently.

- [ ] **Step 3: Write minimal implementation placeholder in app copy**

```python
st.markdown("**Short answer:** ...")
st.markdown("**What to notice:** ...")
st.markdown("**Takeaway:** ...")
```

Add these only where needed in later tasks; do not commit placeholder ellipses. This step exists to lock the expected editorial surface before broader rewrites.

- [ ] **Step 4: Run targeted test to verify it passes after later editorial edits**

Run: `uv run pytest tests/test_cli.py::test_tabs_follow_research_seminar_spine -q`
Expected: PASS after Tasks 2–6 complete.

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli.py src/app.py
git commit -m "Add seminar editorial structure guards"
```

### Task 2: Rewrite Theory & Simulation as an Opening Seminar Segment

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_theory_tab_uses_question_short_answer_takeaway() -> None:
    content = Path("src/app.py").read_text()
    assert "Q1: What is the deposits channel mechanism?" in content
    assert "**Short answer:**" in content
    assert "By the end of this section" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_theory_tab_uses_question_short_answer_takeaway -q`
Expected: FAIL because the current theory tab lacks the new seminar framing sentence.

- [ ] **Step 3: Rewrite the theory tab intro and transitions**

```python
st.header("Theory & Simulation")
st.markdown(
    "This opening segment introduces the economic logic first, then shows how parameter choices turn a benign tightening cycle into funding stress."
)

st.subheader("Q1: What is the deposits channel mechanism?")
st.markdown(
    "**Short answer:** policy tightening matters when banks can keep deposit rates sticky while alternative cash vehicles become more attractive."
)
st.markdown(
    "By the end of this section, the reader should know which assumptions make the system fragile and why."
)
```

Also rewrite later theory subsections so they read cumulatively: mechanism -> pass-through -> deposit sensitivity -> scenarios -> destabilization threshold.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_theory_tab_uses_question_short_answer_takeaway -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Rewrite theory tab as seminar opening"
```

### Task 3: Restructure Empirical Terminal Around Signal, Regime, and Propagation

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_empirical_tab_opens_with_signal_and_short_answer() -> None:
    content = Path("src/app.py").read_text()
    assert "Signal Board" in content
    assert "**Short answer:**" in content
    assert "The selected sample" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_empirical_tab_opens_with_signal_and_short_answer -q`
Expected: FAIL because the empirical tab has the board but not the new seminar opening sentence.

- [ ] **Step 3: Rewrite empirical framing and transitions**

```python
st.header("Empirical Terminal")
st.markdown(
    "This tab asks whether the deposits channel is visible in market data for the selected sample, and if so, which regime is doing the work."
)
st.markdown(
    "**Short answer:** use the signal board to classify the current sample first, then read event, beta, and propagation evidence as explanations of that state."
)
```

Then tighten transitions around:
- Signal Board
- regime identification
- event study
- fear amplification
- IRF / propagation

Warnings should read analytically, e.g.:

```python
st.warning(
    "This sample is too thin for stable empirical inference after return and rate filters are applied. Try widening the timeframe."
)
```

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_empirical_tab_opens_with_signal_and_short_answer -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Refactor empirical tab into seminar narrative"
```

### Task 4: Reframe Macro & Credit as a Flow-of-Funds Story

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_macro_tab_explains_flow_of_funds() -> None:
    content = Path("src/app.py").read_text()
    assert "Follow the funding flow" in content
    assert "**Short answer:**" in content
    assert "proxy-based" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_macro_tab_explains_flow_of_funds -q`
Expected: FAIL because the macro tab does not yet explicitly explain proxy-based inference in seminar language.

- [ ] **Step 3: Rewrite macro and credit copy**

```python
st.header("Macro & Credit")
st.markdown(
    "This segment follows the flow of funds from deposits into money funds, the yield curve, and finally credit conditions."
)
st.markdown(
    "**Short answer:** when deposits become expensive, the signal rarely stays inside bank equity; it spills into funding competition and then into credit conditions."
)
st.caption(
    "This tab is intentionally proxy-based: the point is not to measure deposits directly, but to trace where the pressure shows up next."
)
```

Rewrite the credit feedback section so it reads as a downstream consequence of the earlier MMF/curve story.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_macro_tab_explains_flow_of_funds -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Reframe macro and credit as flow story"
```

### Task 5: Turn the Case Study Into a Compact Narrative Arc

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_case_study_reads_as_narrative() -> None:
    content = Path("src/app.py").read_text()
    assert "March 2023" in content
    assert "**Short answer:**" in content
    assert "What changed the outcome" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_case_study_reads_as_narrative -q`
Expected: FAIL because the case study lacks the new narrative cue phrase.

- [ ] **Step 3: Rewrite the case study framing**

```python
st.header("Case Study")
st.markdown(
    "This segment treats March 2023 as a sequence: preconditions, break, market interpretation, and counterfactual repair."
)
st.markdown(
    "**Short answer:** the episode was not just about higher rates; it was about duration losses, deposit fragility, and confidence moving at once."
)
st.markdown("What changed the outcome is not a single variable, but how quickly multiple stresses aligned.")
```

Then align the timeline, waterfall, divergence, and counterfactual blocks to that story order.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_case_study_reads_as_narrative -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Rewrite case study as narrative arc"
```

### Task 6: Tighten Monitoring & Scenarios Into a Practical Seminar Close

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_monitoring_tab_opens_as_diagnostic() -> None:
    content = Path("src/app.py").read_text()
    assert "Signal Scorecard" in content
    assert "opening diagnostic" in content
    assert "If this, then that playbook" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_monitoring_tab_opens_as_diagnostic -q`
Expected: FAIL because the current monitoring tab does not use the new framing language.

- [ ] **Step 3: Rewrite monitoring copy while preserving structure**

```python
st.header("Monitoring & Scenarios")
st.markdown(
    "This closing segment turns the research into a practical diagnostic without dropping the analytical framing."
)
st.markdown(
    "**Short answer:** read the scorecard as an opening diagnostic, then use the scenarios and playbook to interpret combinations of signals rather than any single metric in isolation."
)
```

Keep:
- 5-metric scorecard
- scenario cards
- exact four playbook rules
- audience takeaways

But rewrite transitions and captions so the tab feels like the seminar close.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_monitoring_tab_opens_as_diagnostic -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Rewrite monitoring tab as seminar close"
```

### Task 7: Final Copy Consistency and Verification Pass

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Add a final consistency test**

```python
def test_editorial_pass_uses_consistent_seminar_language() -> None:
    content = Path("src/app.py").read_text()
    assert content.count("**Short answer:**") >= 5
    assert content.count("**What to notice:**") >= 5
    assert content.count("**Takeaway:**") >= 5
```

- [ ] **Step 2: Run test to verify it fails or is incomplete**

Run: `uv run pytest tests/test_cli.py::test_editorial_pass_uses_consistent_seminar_language -q`
Expected: FAIL until all prior rewrites are complete.

- [ ] **Step 3: Do the final editorial sweep**

Apply a final consistency pass in `/Users/zhoufuwang/Projects/deposits_channel/src/app.py` to:
- remove repeated “deep dive” phrasing where unnecessary
- standardize heading case and narrative cues
- keep “What to notice” tied to actual chart inference
- keep “Takeaway” for synthesis rather than new information
- ensure short paragraphs instead of dense markdown walls

- [ ] **Step 4: Run full verification**

Run:
- `uv run ruff check .`
- `uv run ty check --extra-search-path src`
- `uv run pytest -q`
- `python3 -m py_compile src/app.py`
- `uv run streamlit run src/app.py --server.headless true --server.port 8512`

Expected:
- lint passes
- type checking passes
- tests pass
- app compiles and starts without startup exceptions

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Complete research seminar editorial pass"
```

## Self-Review

- Spec coverage:
  - editorial clarity across all five tabs is covered by Tasks 2–6
  - standard seminar spine is covered by Tasks 1 and 7
  - no visual redesign or new analytics are planned, matching the spec boundary
- Placeholder scan:
  - no `TODO`/`TBD` placeholders remain
  - every test and command uses exact file paths and commands
- Type consistency:
  - all paths reference `/Users/zhoufuwang/Projects/deposits_channel/src/app.py` and `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
  - shared seminar labels are consistent: `Short answer`, `What to notice`, `Takeaway`

