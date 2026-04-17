# Decision Layer Design

## Goal

Add a decision layer to the terminal so it can answer not just what the data say, but what state the system appears to be in and what posture the user should take next. The design should preserve analytical honesty while making the app more decision-useful.

## Product Direction

The app should not jump straight from raw evidence to action language. It should work in two layers:

1. **Research state**
   What state does each tab imply?

2. **Action posture**
   Given those states, what posture should the user take?

This keeps the terminal rigorous enough for research-oriented users while making it more practical for investor and policy/risk users.

## Chosen Model

### Two-Layer State Model

#### Layer 1: Tab-Specific Research States

Each major tab should surface its own state.

Examples:
- Theory / Simulation: `Fragility low`, `Fragility elevated`
- Empirical: `Dormant`, `Active`, `Stress building`
- Macro & Credit: `Contained`, `Spillover building`, `Transmission widening`
- Case Study: `Low analog relevance`, `Moderate analog relevance`, `High analog relevance`
- Monitoring: `Stable`, `Elevated`, `Escalate`

The exact wording can be refined, but the structure should remain tab-specific.

#### Layer 2: Overall Terminal State + Action Posture

The terminal should also show:
- one overall terminal state
- one action posture

This should be a roll-up, not a replacement for the tab states.

## Roll-Up Strategy

### Weighted Rollup

Use a weighted rollup from tab states rather than consensus-only or no-summary.

Reasoning:
- some tabs carry more weight for live decision support than others
- a single overall state is useful, but only if it remains visibly derived

Recommended weighting logic:
- `Empirical` and `Monitoring` carry the most weight
- `Macro & Credit` is secondary but important
- `Case Study` is contextual rather than dominant
- `Theory` helps explain fragility but should not dominate live state labeling

The summary should still show disagreement rather than hiding it.

## Primary UX Surface

### Top Summary Panel

The first decision-layer surface should live near the top of the app.

It should show:
- `Overall terminal state`
- `Action posture`
- `What is driving this`
- `Where to read next`

This should not be a giant dashboard control center. It should feel like a concise decision summary for the current sample.

## Decision Semantics

### Research State

Research state should stay analytical and descriptive.

Examples of tone:
- `Dormant`
- `Active`
- `Stress building`
- `Propagation widening`
- `Analog relevance high`

### Action Posture

Action posture should be simpler and more user-facing.

Recommended default set:
- `Routine`
- `Watch`
- `Escalate`

These are broad enough to work across research, investor, and policy/risk users without implying overly specific instructions.

## Transparency Rules

The decision layer must remain visibly derived from the underlying tabs.

That means:
- the app should show which tab states are driving the rollup
- disagreement between tabs should remain visible
- the summary should avoid sounding more certain than the underlying evidence

If the tabs diverge materially, the overall panel should communicate that rather than forcing a false single story.

## UI Design

### 1. Terminal Summary Band

Add a compact summary band near the top of the app with:
- overall state
- action posture
- 1-2 lines of explanation
- optional “read next” pointer

This should reuse the existing scholarly-modern visual system.

### 2. Tab State Chips or Labels

Each major tab should expose a small state label near the top.

These labels should be readable and compact, not full paragraphs.

### 3. Driver Summary

The top panel should include a short explanation such as:
- `Driven by empirical stress and elevated monitoring pressure`
- `Driven by active empirical regime but limited macro spillover`

This is important because it makes the rollup legible.

## Boundaries

This pass may:
- add state-classification helpers
- add a top summary panel
- add tab-level state labels
- add light driver explanations and read-next pointers

This pass should not:
- make specific trading or policy recommendations
- pretend the model is more precise than it is
- replace the underlying analysis with a single score
- add major new analytics unless absolutely needed to classify state safely

## Verification

Verification should include:
- `uv run ruff check .`
- `uv run ty check --extra-search-path src`
- `uv run pytest -q`
- Streamlit startup sanity check
- manual check that the summary panel remains interpretable and not overconfident

## Follow-On Work

After this pass:
- action-layer refinement
- audience-specific interpretation improvements
- stronger longitudinal change tracking (e.g. “what changed since last state”)
