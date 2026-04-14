# Story-Driven Terminal Reorg Design

## Summary
Reorganize the Streamlit terminal into story-complete tabs with question-driven sections, guiding copy, deep analysis visuals, and a short takeaway per tab. Add new story questions across theory, sensitivity, empirical signals, shock attribution, macro/credit transmission, and the 2023 case study. Keep data sources as yfinance proxies; reuse existing analytics where possible and add only minimal new helpers where required.

## Goals
- Deliver a clean narrative flow per tab: **Question → Deep Analysis → Takeaway**.
- Cover all new story questions requested by the user.
- Keep visuals coherent and readable without overloading a single tab.
- Preserve existing analytics and expand where necessary.

## Non-Goals
- No new external data sources (e.g., FRED).
- No UI redesign beyond section flow, headings, and guiding copy.
- No aggressive performance optimization beyond reasonable chart grouping and reuse.

## New Tab Architecture
1. **Mechanism & Market Power**
2. **Sensitivity & Scenarios**
3. **Empirical Signals**
4. **Shock Attribution**
5. **Macro & Credit Transmission**
6. **2023 Case Study**

Each tab ends with a concise **Takeaway** section summarizing the story.

## Section-Level Design

### Tab 1 — Mechanism & Market Power
- **Q1: What is the deposits channel mechanism?**
  - Visuals: Mechanism schematic, KPI strip (rate, spread, deposits).
  - Takeaway: Market power widens spreads and amplifies outflows.
- **Q2: Where does market power matter most?**
  - Visuals: 2D heatmap (rate × market power) + contour overlay.
- **Q3: What breaks the sticky-deposits assumption?**
  - Visuals: “friction/digital ease” slider → outflow curve shift.

### Tab 2 — Sensitivity & Scenarios
- **Q1: How sensitive is the mechanism to assumptions?**
  - Visuals: Elasticity surfaces (3 panels) + deposit volume vs rate line.
- **Q2: What happens under plausible rate paths?**
  - Visuals: 3×3 small multiples (rate paths → deposit paths).
- **Q3: How quickly does lending contract after outflows?**
  - Visuals: stylized lag response curve (outflow → lending contraction) with lag slider.

### Tab 3 — Empirical Signals
- **Q1: Are banks sensitive to rate shocks?**
  - Visuals: time series + beta comparison (KBE vs SPY).
- **Q2: Is stress building in the system?**
  - Visuals: composite stress index with 95th percentile threshold.
- **Q3: Is sensitivity stable over time?**
  - Visuals: recursive beta plot + rolling beta heatmap.
- **Q4: Do shocks cluster in policy cycles?**
  - Visuals: FOMC event-study CAR chart (±5 days).

### Tab 4 — Shock Attribution
- **Q1: Are rate shocks or volatility shocks more important?**
  - Visuals: partial correlation/variance decomposition (dFF vs VIX).
- **Q2: Do deposit channels differ by bank size proxy?**
  - Visuals: KBE vs IAT vs SPY betas across regimes.
- **Q3: Are banks or credit more rate-sensitive right now?**
  - Visuals: rolling beta spread (bank vs credit) + KPI snapshot.

### Tab 5 — Macro & Credit Transmission
- **Q1: Where do deposits go when spreads widen?**
  - Visuals: KBE/VMFXX ratio + MMF overlay.
- **Q2: Is the system liquidity- or risk-constrained?**
  - Visuals: MMF flow proxy vs credit spreads dominance chart.
- **Q3: Does curve inversion coincide with outflows?**
  - Visuals: yield-curve regime bands + KBE drawdown overlay.
- **Q4: Does credit stress feed back into banks?**
  - Visuals: credit stress vs bank returns scatter + lead/lag correlation.

### Tab 6 — 2023 Case Study
- **Q1: What broke in March 2023?**
  - Visuals: KBE vs IAT divergence chart + event markers.
- **Q2: How fast did stress propagate?**
  - Visuals: cumulative change vs days-since-event.
- **Q3: Which channel dominated the damage?**
  - Visuals: stacked contribution over time (deposits + AOCI + equity).
- **Q4: Did the system normalize after?**
  - Visuals: post-event mean reversion vs baseline band.

## Data & Computation Notes
- All series remain yfinance-based proxies.
- Stress index uses 1-year rolling z-scores; equal weights.
- Event study uses hardcoded FOMC dates.
- New charts should reuse existing helper functions when possible; add minimal new helpers for new analytics.

## UX Copy & Flow
- Each section starts with a concise guiding sentence (1–2 lines).
- Use consistent “Q#: …” headings per tab.
- End each tab with a 1–2 sentence takeaway.

## Testing & Validation
- Unit tests for any new helper functions added for new visuals.
- Light sanity checks: ensure empty data guards prevent runtime errors.

