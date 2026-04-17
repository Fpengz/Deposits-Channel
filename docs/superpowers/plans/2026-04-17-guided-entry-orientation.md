# Guided Entry Orientation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a lightweight guided-entry layer so users understand where to start, what each tab is for, and how to interpret the selected sample without adding tutorial friction.

**Architecture:** Extend `/Users/zhoufuwang/Projects/deposits_channel/src/app.py` with a small orientation system built from reusable helpers and the existing scholarly-modern visual language. The implementation should add an app-level orientation panel, a sample-context block, tab-purpose strips, and sparse reading cues while preserving the current tab/content structure.

**Tech Stack:** Python, Streamlit, inline CSS/helpers, pytest, Ruff, Ty

---

## File Map

- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
  - Add orientation helpers and render guided-entry panels
  - Add app-level reading preface, sample-context framing, and tab-level cues
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
  - Add smoke tests for orientation anchors and cue structure
- Verify: `/Users/zhoufuwang/Projects/deposits_channel/pyproject.toml`
  - Use existing commands only; no config changes expected

### Task 1: Add Orientation Guardrail Tests

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_guided_entry_orientation_anchors_present() -> None:
    content = Path("src/app.py").read_text()

    for marker in [
        "How to read this terminal",
        "Question:",
        "Use this when:",
        "Start here:",
    ]:
        assert marker in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_guided_entry_orientation_anchors_present -q`
Expected: FAIL because the current app does not yet include the guided-entry orientation anchors.

- [ ] **Step 3: Reserve the expected orientation surface in later implementation**

```python
st.markdown("## How to read this terminal")
st.markdown("**Question:** ...")
st.markdown("**Use this when:** ...")
st.markdown("**Start here:** ...")
```

Do not add placeholders in this task; this step exists to define the expected interface for later tasks.

- [ ] **Step 4: Run the targeted test after later tasks add the orientation blocks**

Run: `uv run pytest tests/test_cli.py::test_guided_entry_orientation_anchors_present -q`
Expected: PASS after Tasks 2–4.

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli.py src/app.py
git commit -m "Add guided-entry orientation guardrail test"
```

### Task 2: Add App-Level Orientation and Sample Context

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_app_includes_reading_preface_and_sample_context() -> None:
    content = Path("src/app.py").read_text()
    assert "How to read this terminal" in content
    assert "Start with Theory" in content
    assert "Selected sample" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_app_includes_reading_preface_and_sample_context -q`
Expected: FAIL because the app does not yet include an app-level reading preface or sample-context panel.

- [ ] **Step 3: Add the app-level orientation blocks**

```python
st.markdown(
    """
    <div class="research-module">
      <div class="module-kicker">How to read this terminal</div>
      <p><strong>Start with Theory</strong> if you are new to the deposits channel. Start with Empirical if you want to know what the current sample is signaling. Use Macro, Case Study, and Monitoring once you know which question you are asking.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="diagnostic-band">
      <strong>Selected sample</strong><br>
      {pd.to_datetime(start_date).date()} to {pd.to_datetime(end_date).date()}<br>
      Interpret every chart as evidence conditional on this sample window rather than as a universal statement.
    </div>
    """,
    unsafe_allow_html=True,
)
```

If needed, factor this into a tiny helper function, but keep it lightweight and local.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_guided_entry_orientation_anchors_present tests/test_cli.py::test_app_includes_reading_preface_and_sample_context -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Add app-level guided entry orientation"
```

### Task 3: Add Tab-Purpose Strips and Start-Here Cues

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_tabs_include_question_use_case_and_start_here_cues() -> None:
    content = Path("src/app.py").read_text()
    assert content.count("**Question:**") >= 5
    assert content.count("**Use this when:**") >= 5
    assert content.count("**Start here:**") >= 5
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_tabs_include_question_use_case_and_start_here_cues -q`
Expected: FAIL until each tab gets a tab-purpose strip.

- [ ] **Step 3: Add tab-purpose orientation blocks**

```python
st.markdown(
    """
    <div class="research-module">
      <p><strong>Question:</strong> What question this tab answers.</p>
      <p><strong>Use this when:</strong> Why a reader would come here.</p>
      <p><strong>Start here:</strong> Which module or scorecard to read first.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
```

Apply a tailored version of this block to all five tabs near the top, directly below the seminar banner.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_tabs_include_question_use_case_and_start_here_cues -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Add tab-level purpose and start-here cues"
```

### Task 4: Add Read-This-Next Guidance and Cross-Tab Orientation

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_app_includes_read_this_next_guidance() -> None:
    content = Path("src/app.py").read_text()
    assert "Read this next" in content
    assert "If you only look at one chart" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_app_includes_read_this_next_guidance -q`
Expected: FAIL because the app does not yet include explicit reading-order cues.

- [ ] **Step 3: Add sparse reading cues**

```python
st.caption("Start here: read the signal board before the deeper event and propagation sections.")
st.caption("Read this next: use Macro & Credit if the empirical tab suggests the channel is active.")
st.caption("If you only look at one chart, start with the scorecard or board in this tab.")
```

Add these sparingly in the places where they reduce uncertainty:
- after app-level preface
- near empirical signal board
- near monitoring scorecard
- where Theory / Case Study should point users forward

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_app_includes_read_this_next_guidance -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Add reading-order guidance cues"
```

### Task 5: Final Guided-Entry Consistency Sweep and Verification

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Add the final consistency test**

```python
def test_guided_entry_orientation_is_present_without_becoming_tutorial_heavy() -> None:
    content = Path("src/app.py").read_text()
    assert "How to read this terminal" in content
    assert content.count("**Start here:**") >= 5
    assert content.count("Read this next") >= 2
```

- [ ] **Step 2: Run test to verify it fails or is incomplete**

Run: `uv run pytest tests/test_cli.py::test_guided_entry_orientation_is_present_without_becoming_tutorial_heavy -q`
Expected: FAIL until the orientation cues are fully in place.

- [ ] **Step 3: Do the final orientation sweep**

In `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`:
- ensure orientation blocks are easy to scan on laptop widths
- keep guidance light and non-repetitive
- avoid turning every section into an instruction panel
- make sure each tab’s top framing clearly answers what it is for
- make sure the sample-context block is visible but not visually louder than the seminar banner

- [ ] **Step 4: Run full verification**

Run:
- `uv run ruff check .`
- `uv run ty check --extra-search-path src`
- `uv run pytest -q`
- `python3 -m py_compile src/app.py`
- `uv run streamlit run src/app.py --server.headless true --server.port 8516`

Expected:
- lint passes
- type checking passes
- tests pass
- app compiles and starts without startup exceptions

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Complete guided entry orientation pass"
```

## Self-Review

- Spec coverage:
  - app-level orientation is covered by Task 2
  - tab-purpose strips are covered by Task 3
  - reading-order cues and cross-tab guidance are covered by Task 4
  - final scanability and non-intrusive guidance are covered by Task 5
- Placeholder scan:
  - no `TODO` / `TBD` placeholders remain
  - all paths and commands are explicit
- Type consistency:
  - orientation labels are consistent across tasks: `Question`, `Use this when`, `Start here`, `Read this next`
  - all changes stay inside `/Users/zhoufuwang/Projects/deposits_channel/src/app.py` and `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

