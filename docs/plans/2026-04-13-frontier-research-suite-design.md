# Frontier Research Suite: Deposits Channel Terminal v5.0

## Goal
Elevate the terminal to professional quantitative research standards by adding dynamic shock modeling (VAR), asset-liability duration risk simulation (AOCI), and volatility-conditional analysis (VIX), while explicitly visualizing the paper's cross-sectional HHI findings via synthetic cohorts.

## Architecture
- **`src/data_fetcher.py`**: Add VIX (`^VIX`) ticker.
- **`src/analysis.py`**: 
    - Implement `calculate_irf()` for Impulse Response Functions from VAR.
    - Implement `calculate_bond_portfolio_loss()` for duration risk.
    - Implement `run_vix_conditional_regression()` for volatility-adjusted betas.
- **`src/app.py`**: 
    - Add sub-tabs for "Dynamic Analysis" and "Cross-Sectional Simulation".
    - Integrate AOCI metrics into the core simulation.

## Components
1. **The Dynamic Shock Engine**: Uses `statsmodels.tsa.api.VAR` to show lead-lag shocks.
2. **Bond Portfolio Simulator**: Simple duration math ($-\Delta y \times Duration$) to show unrealized losses.
3. **Volatility Controller**: Analyzes if rate sensitivity increases when VIX > 20.
4. **Synthetic HHI Dashboard**: Side-by-side comparison of "The Monopolist" (HHI=0.8) vs "The Competitor" (HHI=0.2) based on DSS (2017) coefficients.

## Success Criteria
- IRF charts render correctly showing the ripple effect of rate shocks.
- The dual-squeeze metric (Deposits Outflow + Bond Losses) is interactive.
- Conditional regression proves the "Crisis Sensitivity" of bank stocks.
