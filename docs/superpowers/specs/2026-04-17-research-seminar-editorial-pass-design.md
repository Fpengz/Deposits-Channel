# Research Seminar Editorial Pass

## Goal

Refine the merged Streamlit terminal so it reads like a coherent research seminar rather than a collection of strong but independently-written dashboard sections. This pass prioritizes editorial clarity over new analytics.

## Scope

The pass applies to `/Users/zhoufuwang/Projects/deposits_channel/src/app.py` on `main` and focuses on:

- section ordering within tabs
- header and subheader consistency
- explanatory copy around figures and metrics
- repeated framing patterns (`Question`, `Short answer`, `Evidence`, `Mechanism`, `What to notice`, `Takeaway`)
- reducing redundant wording across tabs
- making each tab understandable as a self-contained seminar segment

This pass does **not** primarily add new charts or new data sources. Visual redesign and deeper methodological enhancements are intentionally deferred to later phases.

## Editorial Direction

The voice should feel like a research seminar:

- rigorous but readable
- interpretive rather than merely descriptive
- explicit about what the reader should conclude from a chart
- comfortable naming uncertainty, assumptions, and limits
- less like a dashboard tooltip wall and less like an institutional compliance memo

The terminal should feel like it is guiding the reader through an argument.

## Design Principles

1. Every tab should answer a clear motivating question.
2. The reader should get the conclusion before the full detail.
3. Deeper analytics should appear after orientation, not before it.
4. Repeated structural cues should make the app easier to scan.
5. Copy should interpret visuals, not merely restate titles.
6. Takeaways should distinguish evidence from implication.

## Narrative Structure

Each tab should be refactored toward the same spine where practical:

1. `Question`
2. `Short answer`
3. `Evidence`
4. `Mechanism`
5. `What to notice`
6. `Takeaway`

This structure should be used consistently, but not mechanically. If a section is very short, the labels can be implied rather than repeated verbatim. The point is predictable narrative flow, not templated monotony.

## Tab-Level Design

### Theory & Simulation

Purpose:
Introduce the economic logic of the deposits channel and show how model assumptions translate into funding stress.

Editorial changes:
- sharpen the opening explanation so the mechanism is understandable before any controls are touched
- make simulation sections feel cumulative instead of separate widgets
- ensure every model panel explains what parameter change matters and why
- tighten the bridge from spread mechanics to AOCI/liquidity stress

Desired reader experience:
By the end of this tab, the reader should understand the channel conceptually and know what parameters make the system fragile.

### Empirical Terminal

Purpose:
Show when the deposits channel appears in market data and how that signal changes across regimes and events.

Editorial changes:
- foreground the signal board as the opening empirical summary
- make the sequence move from regime identification to event evidence to propagation
- improve transitions between rolling beta, event study, fear amplification, and IRF sections
- make warnings and insufficient-data messages sound intentional and analytical, not merely defensive

Desired reader experience:
The reader should leave knowing whether the channel is dormant, active, or stressed in the selected sample and why.

### Macro & Credit

Purpose:
Trace how deposit pressure connects to MMFs, the curve, and credit conditions.

Editorial changes:
- make the “flow of funds” logic explicit before showing relative-performance or curve material
- reduce repetition between regime language and chart titles
- clarify what is proxy-based and what is interpretive
- make the credit feedback section read as a consequence of prior sections rather than a separate module

Desired reader experience:
The reader should understand how deposit stress propagates beyond bank equity into funding competition and credit tightening.

### Case Study

Purpose:
Tell the March 2023 episode as a compact narrative with decomposition and counterfactual interpretation.

Editorial changes:
- make the timeline feel like a sequence of breakpoints rather than a loose collection of visuals
- frame the waterfall and divergence charts as explanatory evidence
- sharpen the counterfactual section so it answers “what would have changed the outcome?” directly

Desired reader experience:
The reader should be able to retell the March 2023 story in a few sentences after reading this tab.

### Monitoring & Scenarios

Purpose:
Turn the research into a practical decision panel without losing rigor.

Editorial changes:
- make the scorecard feel like an opening diagnostic, not just five metrics
- keep scenario cards compact and interpretable
- ensure the playbook reads like seminar guidance on state recognition, not trading slogans
- keep audience takeaways, but make them feel like consequences of the preceding analysis

Desired reader experience:
The reader should understand what to watch now and how to interpret combinations of signals.

## Copy Rules

- Prefer short paragraphs over dense markdown blocks.
- Avoid repeating the same phrase in consecutive sections.
- Use “What to notice” only when there is a concrete visual inference.
- Use “Takeaway” for synthesis, not for introducing new facts.
- Use “Short answer” near the top of major tab sections when the conclusion can be stated clearly.
- Avoid overusing “deep dive” as a label; use it only when the section truly narrows into a method or mechanism.

## Implementation Boundaries

This pass may:
- reorder sections within tabs
- rewrite markdown text and labels
- rename section headers/subheaders
- add small helper text blocks or captions
- lightly regroup content for better flow

This pass should not:
- add substantial new analytics
- change core formulas unless needed for wording accuracy
- introduce new dependencies
- redesign the whole visual theme yet

## Verification

Verification for this pass should include:

- `uv run ruff check .`
- `uv run ty check --extra-search-path src`
- `uv run pytest -q`
- a Streamlit startup sanity check
- manual scan of key tab headings/copy order in `/Users/zhoufuwang/Projects/deposits_channel/src/app.py`

## Follow-On Work

After this editorial pass:

1. `Research depth pass`
   - method notes
   - caveats and assumptions
   - sharper discussion of proxies and identification limits

2. `Terminal personality pass`
   - stronger visual system
   - more distinctive section styling
   - improved scorecard and tab identity

