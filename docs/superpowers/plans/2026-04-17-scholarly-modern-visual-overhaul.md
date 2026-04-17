# Scholarly Modern Visual Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redesign the Streamlit terminal into a polished, scholarly-modern research product with stronger module hierarchy, more intentional scorecards, and laptop-friendly visual rhythm.

**Architecture:** Keep the current analytics and seminar-style content in `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`, but layer a coherent visual system on top using Streamlit-friendly structure and custom CSS. The redesign should focus on reusable visual grammar for seminar banners, diagnostic bands, research modules, and takeaway blocks, while preserving the current tab architecture and avoiding fragile over-customization.

**Tech Stack:** Python, Streamlit, inline CSS, pytest, Ruff, Ty

---

## File Map

- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
  - Add visual-system CSS and reusable rendering helpers
  - Refactor tab openings, scorecards, module framing, and takeaway blocks
  - Preserve analytical logic and tab sequencing
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
  - Add smoke tests for the new visual-system anchors and helper usage
- Verify: `/Users/zhoufuwang/Projects/deposits_channel/pyproject.toml`
  - Use existing project commands; no config changes expected

### Task 1: Add Visual-System Guardrails and CSS Anchor Tests

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_visual_overhaul_css_anchors_present() -> None:
    content = Path("src/app.py").read_text()

    for marker in [
        "seminar-banner",
        "diagnostic-band",
        "research-module",
        "takeaway-block",
    ]:
        assert marker in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_visual_overhaul_css_anchors_present -q`
Expected: FAIL because the current app does not yet include the visual-system class anchors.

- [ ] **Step 3: Reserve the expected CSS/helper surface in app implementation**

```python
VISUAL_SYSTEM_CSS = """
<style>
.seminar-banner { }
.diagnostic-band { }
.research-module { }
.takeaway-block { }
</style>
"""
```

Do not implement placeholders only; this step exists to define the expected surface for later tasks.

- [ ] **Step 4: Run the targeted test after later tasks add the actual anchors**

Run: `uv run pytest tests/test_cli.py::test_visual_overhaul_css_anchors_present -q`
Expected: PASS after Tasks 2–6.

- [ ] **Step 5: Commit**

```bash
git add tests/test_cli.py src/app.py
git commit -m "Add visual system guardrail tests"
```

### Task 2: Introduce the Global Visual System and Reusable Module Helpers

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_app_defines_visual_system_helpers() -> None:
    content = Path("src/app.py").read_text()
    assert "def render_seminar_banner(" in content
    assert "def render_research_module_intro(" in content
    assert "def render_takeaway_block(" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_app_defines_visual_system_helpers -q`
Expected: FAIL because the helpers do not yet exist.

- [ ] **Step 3: Add the CSS system and helper functions**

```python
VISUAL_SYSTEM_CSS = """
<style>
:root {
  --page-bg: #f6f3ee;
  --panel-bg: #fbfaf7;
  --panel-border: #d8d2c6;
  --ink: #1f1f1c;
  --muted: #5d5a55;
  --accent: #2f5d50;
  --accent-soft: #dce8e1;
}
.seminar-banner { padding: 1.25rem 1.5rem; border: 1px solid var(--panel-border); background: linear-gradient(180deg, #fcfbf8 0%, #f2eee6 100%); border-radius: 18px; margin-bottom: 1.2rem; }
.diagnostic-band { padding: 1rem 1.1rem; border: 1px solid var(--panel-border); background: var(--panel-bg); border-radius: 16px; margin: 1rem 0 1.4rem; }
.research-module { padding: 1rem 1.1rem; border-left: 4px solid var(--accent); background: #fcfbf8; border-radius: 14px; margin: 1rem 0 1.25rem; }
.takeaway-block { padding: 1rem 1.1rem; background: var(--accent-soft); border-radius: 14px; border: 1px solid #bfd0c7; margin-top: 1rem; }
.module-kicker { color: var(--muted); font-size: 0.92rem; margin-bottom: 0.35rem; }
.short-answer { font-weight: 600; color: var(--ink); }
</style>
"""
st.markdown(VISUAL_SYSTEM_CSS, unsafe_allow_html=True)


def render_seminar_banner(title: str, framing: str, short_answer: str) -> None:
    st.markdown(
        f"""
        <div class="seminar-banner">
          <div class="module-kicker">Research Seminar Module</div>
          <h2>{title}</h2>
          <p>{framing}</p>
          <p class="short-answer"><strong>Short answer:</strong> {short_answer}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_research_module_intro(title: str, why_it_matters: str) -> None:
    st.markdown(
        f"""
        <div class="research-module">
          <div class="module-kicker">Why this matters</div>
          <h3>{title}</h3>
          <p>{why_it_matters}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_takeaway_block(text: str) -> None:
    st.markdown(
        f'<div class="takeaway-block"><strong>Takeaway:</strong> {text}</div>',
        unsafe_allow_html=True,
    )
```

Keep helper output simple and Streamlit-safe; do not add JS or custom components.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_visual_overhaul_css_anchors_present tests/test_cli.py::test_app_defines_visual_system_helpers -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Add scholarly visual system helpers"
```

### Task 3: Redesign Seminar Banners and Diagnostic Bands Across Tabs

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_tabs_use_seminar_banners_and_diagnostic_band() -> None:
    content = Path("src/app.py").read_text()
    assert content.count("render_seminar_banner(") >= 5
    assert "diagnostic-band" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_tabs_use_seminar_banners_and_diagnostic_band -q`
Expected: FAIL until the tab headers and scorecard wrappers are updated.

- [ ] **Step 3: Apply banners and diagnostic bands to each tab**

```python
with tab2:
    render_seminar_banner(
        "Empirical Terminal",
        "Start with the live diagnostic, then move from regime classification into event and propagation evidence.",
        "Treat the signal board as the first read on whether the deposits channel is dormant, active, or stressed in the selected sample.",
    )
    st.markdown('<div class="diagnostic-band">', unsafe_allow_html=True)
    # existing Signal Board or metric block
    st.markdown('</div>', unsafe_allow_html=True)
```

Do this for all tabs where there is a banner-equivalent header, and wrap scorecards / metric bands in a consistent diagnostic treatment.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_tabs_use_seminar_banners_and_diagnostic_band -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Apply seminar banners and diagnostic bands"
```

### Task 4: Convert Major Sections Into Research Modules

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_app_uses_research_module_intro_for_major_sections() -> None:
    content = Path("src/app.py").read_text()
    assert content.count("render_research_module_intro(") >= 8
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_app_uses_research_module_intro_for_major_sections -q`
Expected: FAIL until the major section intros are migrated.

- [ ] **Step 3: Add module intros before major evidence blocks**

```python
render_research_module_intro(
    "Q3: Do policy events create abnormal returns?",
    "This module tests whether policy dates leave return patterns that are unusual relative to the broader market benchmark.",
)
# existing chart/table logic follows
st.markdown("**What to notice:** ...")
```

Apply this pattern to the major chart/table sections across tabs, especially where the current flow still feels visually flat.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_app_uses_research_module_intro_for_major_sections -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Wrap major sections in research modules"
```

### Task 5: Redesign Takeaway and Audience-Takeaway Closures

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

```python
def test_takeaways_use_visual_blocks() -> None:
    content = Path("src/app.py").read_text()
    assert content.count("render_takeaway_block(") >= 5
    assert "Audience Takeaways" in content
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli.py::test_takeaways_use_visual_blocks -q`
Expected: FAIL until the current plain-text takeaway endings are upgraded.

- [ ] **Step 3: Replace plain takeaway endings with styled blocks**

```python
render_takeaway_block(
    "The deposits channel matters most when rate sensitivity becomes a regime signal rather than a one-off market reaction."
)
st.markdown("**Audience Takeaways**")
st.markdown("- Research: ...")
st.markdown("- Investor: ...")
st.markdown("- Policy/risk: ...")
```

Keep the audience-takeaway content, but group it visually beneath the main synthesized takeaway.

- [ ] **Step 4: Run focused tests**

Run: `uv run pytest tests/test_cli.py::test_takeaways_use_visual_blocks -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Redesign takeaway closures"
```

### Task 6: Laptop-Focused Rhythm and Final Visual Consistency Sweep

**Files:**
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`
- Modify: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`
- Test: `/Users/zhoufuwang/Projects/deposits_channel/tests/test_cli.py`

- [ ] **Step 1: Add a final consistency test**

```python
def test_visual_overhaul_keeps_modular_seminar_rhythm() -> None:
    content = Path("src/app.py").read_text()
    assert "seminar-banner" in content
    assert "diagnostic-band" in content
    assert "research-module" in content
    assert "takeaway-block" in content
```

- [ ] **Step 2: Run test to verify it fails or is incomplete**

Run: `uv run pytest tests/test_cli.py::test_visual_overhaul_keeps_modular_seminar_rhythm -q`
Expected: FAIL until the full styling pass is complete.

- [ ] **Step 3: Perform the final visual sweep**

In `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`:
- ensure vertical spacing between modules is consistent
- reduce visually noisy default markdown transitions
- keep 3-column layouts limited to compact diagnostics/controls
- ensure banners and scorecards still read at laptop width
- keep chart context above charts and `What to notice` below charts where practical
- avoid decorative clutter or heavy visual density

- [ ] **Step 4: Run full verification**

Run:
- `uv run ruff check .`
- `uv run ty check --extra-search-path src`
- `uv run pytest -q`
- `python3 -m py_compile src/app.py`
- `uv run streamlit run src/app.py --server.headless true --server.port 8515`

Expected:
- lint passes
- type checking passes
- tests pass
- app compiles and starts without startup exceptions

- [ ] **Step 5: Commit**

```bash
git add src/app.py tests/test_cli.py
git commit -m "Complete scholarly modern visual overhaul"
```

## Self-Review

- Spec coverage:
  - seminar banners, diagnostic bands, research modules, and takeaway blocks are covered by Tasks 2–5
  - laptop-oriented layout rhythm and consistency are covered by Task 6
  - no interaction-model redesign or new analytics are included, matching the spec boundary
- Placeholder scan:
  - no `TODO` / `TBD` placeholders remain
  - every task includes explicit file paths, code examples, and verification commands
- Type consistency:
  - helper names are consistent across tasks: `render_seminar_banner`, `render_research_module_intro`, `render_takeaway_block`
  - CSS anchors are consistent across tasks: `seminar-banner`, `diagnostic-band`, `research-module`, `takeaway-block`

