# Section Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add lightweight within-tab navigation and cross-tab handoffs so users can move through long tabs more easily without adding heavy navigation chrome.

**Architecture:** Extend `/Users/zhoufuwang/Projects/deposits_channel/src/app.py` with a small navigation layer that reuses the current scholarly-modern visual system: per-tab section navigators, lightweight jump/read-next cues, and cross-tab continuation prompts. Keep the core tab architecture intact and avoid sticky side rails or JS-heavy solutions.

**Tech Stack:** Python, Streamlit, inline helper functions/CSS, pytest, Ruff, Ty

---

## File Map

- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
  - Add section-navigation helpers and within-tab navigator blocks
  - Add localized `Read this next` / `Continue in...` cues
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
  - Add smoke tests for navigation anchors and handoff structure
- Verify: `/Users/zhoufuwang/Projects/deposits_channel/pyproject.toml`
  - Use existing project commands only; no config changes expected

### Task 1: Add Navigation Guardrail Tests

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_section_navigation_anchors_present() -> None:
    content = Path("src/app.py").read_text()

    for marker in [
        "Jump to section",
        "Read this next",
        "Continue in",
    ]:
        assert marker in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_section_navigation_anchors_present -q`
Expected: FAIL because the current app does not yet include the section-navigation anchors.

- [ ] **Step 3: Reserve the expected navigation surface in later implementation**

```python
st.markdown("**Jump to section:** ...")
st.caption("Read this next: ...")
st.caption("Continue in ...")
```

Do not add placeholders in this task; this step exists to define the interface later tasks will implement.

- [ ] **Step 4: Run the targeted test after later tasks add the anchors**

Run: `uv run pytest tests/test_cli.py::test_section_navigation_anchors_present -q`
Expected: PASS after Tasks 2–4.

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli.py src/app.py
git commit -m "Add section navigation guardrail test"
```

### Task 2: Add Per-Tab Section Navigators

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_tabs_include_section_navigators() -> None:
    content = Path("src/app.py").read_text()
    assert content.count("render_section_navigator(") >= 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_tabs_include_section_navigators -q`
Expected: FAIL because the app does not yet define or use a section navigator helper.

- [ ] **Step 3: Add the helper and wire it into all tabs**

```python
def render_section_navigator(title: str, sections: list[str]) -> None:
    items = "".join(f"<li>{html.escape(section)}</li>" for section in sections)
    st.markdown(
        f"""
        <div class="research-module">
          <div class="module-kicker">Jump to section</div>
          <p><strong>{html.escape(title)}</strong></p>
          <ul>{items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
```

Call it near the top of each tab, after the seminar banner and tab-purpose strip, with a compact list of that tab’s major sections.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_section_navigation_anchors_present tests/test_cli.py::test_tabs_include_section_navigators -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Add per-tab section navigators"
```

### Task 3: Add Within-Tab Read-Next and One-Chart Cues

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_app_includes_within_tab_read_next_cues() -> None:
    content = Path("src/app.py").read_text()
    assert content.count("Read this next") >= 3
    assert content.count("If you only look at one chart") >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_app_includes_within_tab_read_next_cues -q`
Expected: FAIL or be incomplete until within-tab navigation cues are in place.

- [ ] **Step 3: Add sparse within-tab movement cues**

```python
st.caption("Read this next: move from the signal board to the event evidence if you want to know whether the regime signal shows up around policy dates.")
st.caption("If you only look at one chart, start with the scorecard in this tab before the scenario detail below.")
```

Add them where they genuinely reduce scrolling uncertainty:
- after the empirical signal board
- near the monitoring scorecard
- where a summary naturally leads into a deeper module

Keep them sparse and useful.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_app_includes_within_tab_read_next_cues -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Add within-tab navigation cues"
```

### Task 4: Add Cross-Tab Continue-In Handoffs

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_app_includes_cross_tab_handoffs() -> None:
    content = Path("src/app.py").read_text()
    assert content.count("Continue in") >= 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_app_includes_cross_tab_handoffs -q`
Expected: FAIL until the cross-tab continuation cues are added.

- [ ] **Step 3: Add short cross-tab continuation prompts**

```python
st.caption("Continue in Empirical Terminal if you want to see whether the theoretical channel is actually visible in the selected sample.")
st.caption("Continue in Macro & Credit if the empirical tab suggests the channel is active and you want to see where the pressure propagates.")
st.caption("Continue in Monitoring & Scenarios if you want to translate the case study lessons into a live watchlist.")
```

Add them only where the narrative handoff is natural.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_app_includes_cross_tab_handoffs -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Add cross-tab navigation handoffs"
```

### Task 5: Final Navigation Consistency Sweep and Verification

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Add the final consistency test**

```python
def test_navigation_layer_is_present_without_heavy_chrome() -> None:
    content = Path("src/app.py").read_text()
    assert "Jump to section" in content
    assert content.count("render_section_navigator(") >= 5
    assert 3 <= content.count("Continue in") <= 5
```

- [ ] **Step 2: Run test to verify it fails or is incomplete**

Run: `uv run pytest tests/test_cli.py::test_navigation_layer_is_present_without_heavy_chrome -q`
Expected: FAIL until the navigation layer is fully in place.

- [ ] **Step 3: Do the final navigation sweep**

In `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`:
- ensure section navigators stay compact on laptop widths
- keep within-tab cues sparse and useful
- make cross-tab handoffs contextual, not repetitive
- avoid adding sticky chrome or turning the page into a control panel
- make sure the navigation layer supports reading rather than competing with it

- [ ] **Step 4: Run full verification**

Run:
- `uv run ruff check .`
- `uv run ty check --extra-search-path src`
- `uv run pytest -q`
- `python3 -m py_compile src/app.py`
- `uv run streamlit run src/app.py --server.headless true --server.port 8517`

Expected:
- lint passes
- type checking passes
- tests pass
- app compiles and starts without startup exceptions

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Complete section navigation pass"
```

## Self-Review

- Spec coverage:
  - within-tab navigation is covered by Tasks 2 and 3
  - cross-tab handoffs are covered by Task 4
  - compactness and non-intrusive navigation are covered by Task 5
- Placeholder scan:
  - no `TODO` / `TBD` placeholders remain
  - all paths and commands are explicit
- Type consistency:
  - navigation labels remain consistent across tasks: `Jump to section`, `Read this next`, `Continue in`
  - all changes stay inside `/Users/zhoufuwang/Projects/deposits_channel/src/app.py` and `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

