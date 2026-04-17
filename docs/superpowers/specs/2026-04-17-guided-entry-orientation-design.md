# Guided Entry Orientation Design

## Goal

Improve the interaction model of the terminal by making it easier for a user to understand where to start, what each tab is for, and how to read the current sample. This pass focuses on orientation rather than navigation mechanics or decision support.

## Why This Pass

The app now has strong content and a stronger visual system, but a first-time user still has to infer the reading strategy from the page itself. The interaction-model problem is not “too few tabs”; it is that the user is not explicitly told how to approach them.

This pass should make the app feel easier to enter and easier to interpret without adding onboarding friction.

## Scope

This pass should focus on guided entry:
- app-level orientation
- tab purpose framing
- start-here cues
- next-read cues
- clearer sample context framing

This pass should **not** yet redesign broader navigation systems or add a separate decision engine.

## Product Direction

The terminal should behave like a well-led seminar:
- the reader knows where to begin
- each tab clearly states its job
- the current sample context is obvious
- the app gently guides reading order without forcing a wizard-like flow

The guidance should feel calm and useful, not tutorial-heavy.

## Chosen Approach

### Guided Entry

Add a lightweight orientation layer at two levels:

1. **App-level orientation**
   A short “How to read this terminal” section near the top of the app.

2. **Tab-level orientation**
   Each tab should include:
   - what question this tab answers
   - when to use it
   - what to look at first
   - where to go next, when appropriate

This should create a usable reading path without introducing new navigation chrome.

## Interaction Design

### 1. App-Level Orientation Strip

Add a compact orientation block near the top of the app that explains:
- what the terminal is
- the recommended reading order
- how to think about the tabs

This should answer, in a few lines:
- start with theory if you are new
- start with empirical if you want to know the current signal
- use macro/case-study/monitoring once you know what question you are asking

This is not a tutorial modal. It should feel like a research preface.

### 2. Sample Context Block

Make the current sample and interpretation frame more explicit:
- selected date range
- what those dates imply for interpretation
- reminder that conclusions depend on the chosen sample

This block should help the user avoid reading the app as if it were always a universal statement.

### 3. Tab Purpose Block

At the top of each tab, add a concise orientation row or block answering:
- `Question:` what this tab is trying to answer
- `Use this when:` what kind of user need or reasoning step it serves
- `Start here:` what module or scorecard to read first

This should sit above the deeper seminar content and be easier to scan than ordinary prose.

### 4. Reading Cues Inside Tabs

Add light guidance within tabs, such as:
- `Start here` for the first important module
- `Read this next` after summary/diagnostic sections
- `If you only look at one chart...` where appropriate

These cues should be sparse and intentional. They are meant to reduce uncertainty, not narrate every move.

### 5. Cross-Tab Guidance

Where helpful, add one-line pointers such as:
- from Theory -> Empirical
- from Empirical -> Macro or Monitoring
- from Case Study -> Monitoring

These should be short and contextual, not global breadcrumbs.

## Design Principles

- Guidance should reduce ambiguity, not add visual clutter.
- Orientation should be more explicit for new users and minimally intrusive for returning users.
- The user should always know what the current tab contributes to the larger story.
- The app should feel like it is inviting a reading path, not forcing a workflow.

## UI Elements to Add

Likely components for this pass:
- app-level orientation panel
- sample-context panel
- tab-purpose strip or info row
- `Start here` cue treatment
- `Read this next` cue treatment

These can reuse the existing scholarly-modern visual system rather than inventing a separate style language.

## Boundaries

This pass may:
- add lightweight orientation panels and cue blocks
- add small helper functions for tab-purpose and reading-order cues
- slightly reorder top-of-tab framing to make guidance clearer
- reuse the current visual system for orientation components

This pass should not:
- add major new analytics
- build a full navigation rail
- add collapsible onboarding overlays or forced tours
- redesign the tab architecture itself

## Verification

Verification should include:
- `uv run ruff check .`
- `uv run ty check --extra-search-path src`
- `uv run pytest -q`
- Streamlit startup sanity check
- manual check that the app-level orientation and tab-level cues are easy to scan on laptop widths

## Follow-On Work

After this pass:

1. `Navigation pass`
- stronger in-page movement
- jump links / section progression
- cross-tab movement aids

2. `Decision-layer pass`
- clearer state interpretation
- stronger “what matters now” framing
- better action/monitoring implications
