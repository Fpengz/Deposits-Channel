# Multi-Audience Terminal Expansion Design

## Summary
Expand the deposits-channel terminal so each tab tells a complete story for three audiences at once: research, investor, and policy/risk. Finish previously planned visuals and analyses, add a new monitoring/scenarios tab, and standardize every tab around the same narrative pattern: **Question -> Signal -> Mechanism -> Decision / Monitoring -> Audience Takeaways**.

## Goals
- Finish the previously planned but only partially implemented stories, visuals, and analytics.
- Make each tab understandable as a standalone narrative.
- Serve three audiences without duplicating the whole dashboard into persona-specific tabs.
- Increase decision usefulness with clearer monitoring signals, scenario framing, and annotated takeaways.

## Non-Goals
- No new external data sources beyond yfinance proxies.
- No broad design-system rewrite or major visual branding overhaul.
- No attempt to make every chart exhaustive; headline visuals should stay primary.
- No new backend or multi-page app structure.

## Design Decision
Use a **layered narrative inside each tab** instead of audience-specific tabs or UI toggles.

Why this approach:
- It preserves the current story-first structure.
- It allows one tab to answer three audience lenses in sequence.
- It avoids duplicated charts and reduces maintenance cost.

## Global Story Pattern
Every tab should follow this order:

1. **Question**
   - One framing question that states the purpose of the tab.
2. **Signal**
   - One headline chart that shows the phenomenon quickly.
3. **Mechanism**
   - One or more charts that explain what is driving the signal.
4. **Decision / Monitoring**
   - A scenario, threshold, scorecard, or regime panel that makes the analysis actionable.
5. **Audience Takeaways**
   - `Research takeaway`
   - `Investor takeaway`
   - `Policy/risk takeaway`

## Target Tab Architecture
1. **Theory & Simulation**
2. **Empirical Terminal**
3. **Macro & Credit**
4. **Case Study: March 2023**
5. **Monitoring & Scenarios**

This keeps the current top-level flow mostly intact while adding one explicit operational tab.

## Tab-Level Design

### Tab 1: Theory & Simulation
**Core question:** How do rate hikes translate into funding stress and lending pressure?

#### Signal
- KPI strip for fed funds, deposit rate, spread, deposits, and capital buffer proxy.
- Clean mechanism diagram showing rates -> spreads -> outflows -> lending.

#### Mechanism
- Rate x market-power heatmap for spread amplification.
- Elasticity contour panels to show how assumptions reshape deposit loss.
- Digital friction / stickiness chart to show when sticky deposits break.

#### Decision / Monitoring
- Threshold map for combined outflow and AOCI stress.
- Scenario tree: rate path -> deposit spread -> deposit volume -> lending response.
- Counterfactual widgets for market power, elasticity, friction, baseline rate, and duration.

#### Audience takeaways
- Research: clarify the nonlinear role of concentration and depositor inelasticity.
- Investor: show where rate sensitivity should appear first in bank funding proxies.
- Policy/risk: highlight the combinations that produce destabilizing balance-sheet pressure.

### Tab 2: Empirical Terminal
**Core question:** When does the deposits channel show up in market data?

#### Signal
- Headline chart with rates, bank ETF, regional bank ETF, and market benchmark.
- Signal board summarizing current state: `Dormant`, `Active`, or `Stressed`.

#### Mechanism
- Beta comparison for KBE, IAT, and SPY versus rate changes.
- Recursive beta and rolling beta heatmap to show stability or regime drift.
- Stress composite index combining rate shocks, VIX returns, and KBE drawdown.
- High-VIX versus low-VIX beta comparison to test amplification.

#### Decision / Monitoring
- Event study around hardcoded FOMC dates.
- IRF panel for rate shock propagation into bank returns and volatility.
- Regime segmentation panel using stress or volatility buckets.

#### Audience takeaways
- Research: whether estimated sensitivity is stable, state dependent, or clustered around policy events.
- Investor: whether the channel is currently priced and whether fear amplifies bank sensitivity.
- Policy/risk: whether rate transmission is intensifying into system-wide stress.

### Tab 3: Macro & Credit
**Core question:** How does deposit stress propagate into the wider funding and credit system?

#### Signal
- Banks versus MMF relative-performance chart as a simple destination-of-flows proxy.
- Yield-curve slope panel with regime bands: `Normal`, `Flat`, `Inverted`.

#### Mechanism
- Liquidity-versus-risk dominance panel using MMF proxy versus credit stress.
- Credit stress versus bank returns scatter with fitted line.
- Lead-lag correlation chart for rates and credit stress.
- Lending conditions proxy showing the path from funding pressure to credit tightening.

#### Decision / Monitoring
- Regime matrix with four cells: `Normal`, `Squeeze`, `Stress`, `Crisis`.
- Simple warning rules, for example: inverted curve + rising stress index + bank underperformance.

#### Audience takeaways
- Research: connect deposit reallocation to wider credit tightening.
- Investor: identify when bank weakness reflects liquidity migration versus macro credit deterioration.
- Policy/risk: isolate conditions where deposit stress is feeding into credit availability.

### Tab 4: Case Study: March 2023
**Core question:** What broke in March 2023, how fast, and through which channels?

#### Signal
- Event timeline with annotated dates across February to May 2023.
- KBE versus IAT divergence chart with crisis markers.

#### Mechanism
- Cumulative divergence chart using normalized price paths.
- Propagation-speed chart using time-to-threshold framing.
- Waterfall decomposition for deposit outflow proxy, AOCI proxy, and equity divergence.
- Pre-event versus post-event normalization band to show whether the system returned to baseline.

#### Decision / Monitoring
- Counterfactual mini-scenarios:
  - lower duration
  - higher deposit stickiness
  - less concentrated banking structure
- “What would have reduced damage?” cards for policy/risk interpretation.

#### Audience takeaways
- Research: identify which assumptions from the baseline deposits-channel framework failed under stress.
- Investor: distinguish large-bank recovery from regional-bank fragility.
- Policy/risk: show how quickly liquidity and mark-to-market losses can compound.

### Tab 5: Monitoring & Scenarios
**Core question:** What should we monitor now, and what happens under the next policy path?

#### Signal
- Compact scorecard of the terminal's main indicators:
  - stress composite
  - beta regime
  - curve regime
  - MMF relative pressure
  - credit stress trend

#### Mechanism
- Scenario cards for:
  - `Higher for longer`
  - `Rapid cuts`
  - `Volatility shock`
  - `Bank-specific confidence shock`
- Each scenario should map to expected movements in spreads, deposits, funding stress, and bank equities.

#### Decision / Monitoring
- “If this, then that” playbook:
  - if rates rise while VIX stays low
  - if rates are stable but VIX spikes
  - if curve steepens through cuts
  - if MMFs outperform while bank betas stay negative
- Provide explicit watch items per audience.

#### Audience takeaways
- Research: open hypotheses worth testing next.
- Investor: which signals imply relative-value or risk-reduction positioning.
- Policy/risk: which combinations imply surveillance escalation.

## Cross-Tab Visual Rules
- Every major chart needs one sentence telling the user what to notice.
- Headline charts come before deep dives.
- Use annotations, thresholds, and regime bands where possible.
- Avoid stacking more than two dense charts back to back without interpretation text.
- Prefer one strong chart plus one supporting chart over multiple similarly shaped charts.

## Required Analytics to Finish or Add
- Finish the stress composite and signal-board framing.
- Finish rolling beta and recursive sensitivity storytelling.
- Finish event-study and IRF interpretation sections.
- Finish credit feedback and lead-lag sections with clearer framing.
- Finish the 2023 decomposition with waterfall and normalization logic.
- Add scenario-to-outcome mapping for the new monitoring tab.

## Data and Computation Constraints
- Keep all market data from yfinance-based proxies.
- Keep event dates hardcoded in code.
- Use daily frequency unless a helper explicitly needs another frequency.
- Treat all balance-sheet decompositions and scenario outputs as illustrative proxies, not accounting identities.

## Implementation Notes
- Reuse existing helper functions where possible.
- Add only small helpers that are directly needed for a chart or scorecard.
- Keep empty-data guards around every section that depends on fetched market data.
- Keep the UI in Streamlit, but extract new analytics into testable helpers as needed.

## Validation
- Add or extend tests for any new analytics helpers.
- Verify the scripted workflow remains green through `uv run check`.
- Manually verify that each tab reads as a complete story from top to bottom.

## Spec Self-Review
- Placeholder scan: no `TODO`, `TBD`, or undefined audience behavior remains.
- Consistency check: all tabs follow the same narrative pattern and stay within yfinance-only constraints.
- Scope check: this is one implementation plan with one new tab, not a multi-phase redesign.
- Ambiguity check: the audience model is fixed as layered takeaways within each tab, not separate tabs or toggles.
