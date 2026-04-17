# Section Navigation Design

## Goal

Improve how users move through the terminal by making it easier to navigate within each tab first, then across tabs. This pass should reduce friction in long pages without introducing heavy navigation chrome or changing the core tab structure.

## Why This Pass

The terminal now has stronger content, visual hierarchy, and guided-entry framing, but long tabs still depend too much on scrolling and memory. Users may understand what a tab is for yet still lose track of where to go inside it or what to open next.

The navigation problem is therefore:
- inside a tab, sections are not easy to revisit or skip between
- across tabs, natural handoffs exist but are not surfaced clearly enough

## Scope

This pass should focus on:
- within-tab navigation first
- cross-tab handoffs second

This pass should **not** build a full decision engine or redesign the tab architecture.

## Chosen Approach

### Section Navigator + Next-Step Links

Use lightweight navigation aids that feel integrated into the research experience:

1. **Per-tab section navigator**
   A compact list near the top of each tab showing the major sections.

2. **Within-tab movement cues**
   `Jump to section`, `Start here`, and `Read this next` pointers.

3. **Cross-tab handoffs**
   Short “continue in…” guidance where a user naturally wants the next answer.

This should feel quiet and helpful, not like a separate control surface.

## Interaction Design

### 1. Per-Tab Section Navigator

Near the top of each tab, add a compact navigator listing the major sections in that tab.

This can be implemented as:
- a compact visual outline
- a selectbox/radio/jump list
- anchor-style cues if Streamlit supports them cleanly in the current structure

The design should be laptop-friendly and compact.

The navigator should answer:
- what sections are in this tab?
- where should I jump if I already know what I want?

### 2. Jump-To Controls

Within the tab, the user should be able to jump or quickly orient to a target section.

This does not need to be a full sticky navigator.
A lightweight top-of-tab section chooser is enough if it is well integrated.

### 3. Start-Here and Read-Next Cues

Build on the guided-entry pass by making section progression more actionable:
- `Start here` for first important module
- `Read this next` after summary/diagnostic sections
- `Continue in Macro & Credit` / `Continue in Monitoring` where the narrative naturally leaves one tab and enters another

These should be sparse and placed where the user’s next question is obvious.

### 4. Cross-Tab Handoffs

Where one tab naturally leads into another, surface that transition explicitly.

Examples:
- Theory -> Empirical
- Empirical -> Macro & Credit
- Case Study -> Monitoring

These should remain short and contextual rather than becoming a breadcrumb system.

## UX Principles

- Optimize first for orientation inside long tabs.
- Keep navigation aids secondary to the content itself.
- Use the scholarly-modern visual system, not separate chrome.
- Avoid sticky side rails or dense navigation bars on laptop widths.
- Navigation should reduce effort without making the app feel like an enterprise dashboard.

## UI Elements to Add

Likely components for this pass:
- per-tab section navigator block
- section-jump chooser or quick-outline
- localized `Read this next` handoffs
- cross-tab “continue in…” cues

These should all reuse the current visual language.

## Boundaries

This pass may:
- add helper functions for section navigation and handoff cues
- slightly reorder top-of-tab framing to integrate the navigator
- add lightweight jump controls and section labels
- add contextual cross-tab pointers

This pass should not:
- replace tabs with a new navigation model
- add sticky navigation rails unless absolutely necessary
- add heavyweight interaction state or custom JS
- build decision-support logic

## Verification

Verification should include:
- `uv run ruff check .`
- `uv run ty check --extra-search-path src`
- `uv run pytest -q`
- Streamlit startup sanity check
- manual check that section navigation is clear and compact on laptop widths

## Follow-On Work

After this pass:

1. `Decision-layer pass`
- stronger “what matters now” interpretation
- state prioritization
- clearer implications and next actions
