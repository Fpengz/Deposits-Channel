# Scholarly Modern Visual Overhaul

## Goal

Redesign the Streamlit terminal so it feels like a polished research product rather than a default dashboard, while staying equally strong on laptop-sized screens. The overhaul should preserve the seminar-style narrative structure already added and give it a visual system that is clearer, more intentional, and easier to scan.

## Product Direction

The interface should feel:

- scholarly
- modern
- calm
- high-signal
- visually structured without becoming busy

This is not a market-terminal imitation and not a glossy editorial magazine. It should feel like a well-designed research seminar environment.

## Target Device Constraint

The design must be equally strong on laptop screens from the start.

Implications:
- avoid relying on wide multi-column compositions as the primary experience
- prioritize stacked modules with strong vertical rhythm
- use side-by-side layouts only where they remain legible on laptop widths
- ensure scorecards and takeaways still feel prominent when reduced to 2- or 1-column arrangements

## Chosen Approach

### Modular Seminar Layout

Keep the tab model, but redesign each tab as a sequence of content modules that repeat a coherent visual grammar:

1. Seminar banner
2. Diagnostic band or opening orientation
3. Evidence modules
4. Interpretation module
5. Takeaway close

The point is not to make every tab identical, but to give the reader a consistent sense of where they are in the argument.

## Visual System

### 1. Seminar Banner

Each tab should open with a stronger top section containing:
- tab title
- one-sentence framing
- visually distinct `Short answer`

This banner should feel more like a seminar slide opener than a standard markdown header.

### 2. Diagnostic Band

Scorecards and headline metrics should become a distinct visual band with:
- stronger spacing
- clearer visual grouping
- less “default `st.metric` grid” feeling
- compact supporting context beneath the numbers when needed

This band should be the first thing the user can scan after the banner.

### 3. Research Modules

Major sections should be wrapped in visually consistent modules containing:
- section title
- short framing sentence (`why this matters`)
- chart or table
- `What to notice`

These modules should create a predictable rhythm down the page.

### 4. Takeaway Blocks

`Takeaway` sections should become clearly distinct closing elements with more visual presence than plain markdown.

They should read as synthesis, not as another paragraph in the flow.

### 5. Audience Takeaways

Where audience-specific takeaways remain useful, they should be grouped and visually tidied so they read as a considered close rather than a loose appendix.

## Layout Rules

- Prefer 1-column and 2-column compositions that survive laptop widths.
- Use 3+ columns only for compact metrics or tightly bounded controls.
- Avoid over-fragmenting content into too many cards.
- Preserve generous spacing between modules.
- Keep charts wide enough to read comfortably without horizontal strain.

## Typography and Tone

Typography should communicate seriousness and clarity.

Guidelines:
- stronger hierarchy between page title, section title, framing sentence, and helper text
- use muted supporting text for framing/captions
- use high-contrast text for analytical conclusions
- avoid decorative excess
- make `Short answer`, `What to notice`, and `Takeaway` visually distinct and immediately scannable

## Color and Styling Direction

The palette should be restrained and academic rather than flashy.

Suggested direction:
- warm off-white or very light neutral background treatment where appropriate
- deep charcoal / near-black text for primary hierarchy
- one restrained accent family for state and emphasis
- light panel fills or borders to separate modules
- minimal saturated color use outside actual data visuals and state cues

The app should feel designed, but never loud.

## Interaction and Information Hierarchy

This pass should not redesign the interaction model yet, but it should improve perceived usability through visual hierarchy:
- users should know where to start on each tab
- primary signals should stand out before details
- charts should feel contextualized, not dropped into the page
- modules should feel like a guided reading sequence

## Implementation Boundaries

This pass may:
- add custom CSS in `src/app.py`
- wrap sections in styled containers
- redesign metric/scorecard presentation
- redesign headings, captions, takeaway blocks, and section rhythm
- slightly reorganize visual groupings within tabs

This pass should not:
- introduce major new analytics
- rewrite the entire interaction model
- add heavy custom component dependencies
- compromise readability for visual flair

## Expected Outcomes by Tab

### Theory & Simulation
- cleaner seminar opener
- stronger model/control framing
- clearer separation between conceptual mechanism and simulation evidence

### Empirical Terminal
- stronger signal-board prominence
- clearer sequencing from summary to evidence to propagation
- less visual sameness between empirical subsections

### Macro & Credit
- clearer flow-of-funds progression
- better visual distinction between MMF/curve/credit modules

### Case Study
- more narrative pacing
- sharper visual transitions across timeline, divergence, waterfall, and counterfactuals

### Monitoring & Scenarios
- scorecard should feel like a true opening diagnostic band
- scenarios and playbook should feel like a designed closing instrument panel

## Verification

Verification should include:
- `uv run ruff check .`
- `uv run ty check --extra-search-path src`
- `uv run pytest -q`
- Streamlit startup sanity check
- manual laptop-oriented review of spacing, module rhythm, and scorecard legibility

## Follow-On Work

After this pass:

1. Interaction-model pass
- progressive disclosure
- improved cross-tab navigation and summary flow
- stronger orientation for first-time users

2. Decision-layer pass
- better “what matters now” framing
- clearer action or monitoring implications
- more explicit state-change interpretation
