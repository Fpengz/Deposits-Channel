# Macro-Finance Deep Dive: Deposits Channel Terminal v4.0

## Goal
Transform the dashboard into a full-scale macro-finance research terminal by incorporating multiple asset classes (Money Market Funds, Treasuries, Credit) and replicating the deeper cross-sectional and term-structure analysis found in the original DSS (2017) paper, with a focus on recent crises (2023).

## Architecture
- **`src/data_fetcher.py`**: Add new tickers for MMFs (`VMFXX`), Long-term yields (`^TNX`), and Credit spreads (`LQD`, `HYG`).
- **`src/analysis.py`**: Implement helper functions for **Yield Curve Slope** calculation and **Credit Spread** derivation.
- **`src/app.py`**: Reorganize into a 5-tab research suite:
    1.  **Theory & Simulation**: core mathematical model.
    2.  **Empirical Terminal**: Bank beta and recursive OLS.
    3.  **Macro Interactions**: Yield curve and MMF flows.
    4.  **Credit & Lending**: Transmission to the real economy.
    5.  **2023 Case Study**: High-resolution analysis of the March 2023 banking stress.

## Components & Data Flow
1.  **MMF Flow Proxy**: Visualize the "Destination" of deposits.
2.  **Term Structure**: Show the interaction between `(10Y - 3M)` spread and bank performance.
3.  **Lending Proxy**: Use Investment Grade (`LQD`) minus Treasury spreads to show lending conditions.
4.  **Event Markers**: High-resolution zoom into March 2023.

## Success Criteria
- Dashboard fetches and merges data from at least 6 different asset proxies.
- Visualizations clearly show the correlation between rate hikes, yield curve inversion, and credit spread widening.
- Dedicated section for the 2023 crisis is interactive and educational.
