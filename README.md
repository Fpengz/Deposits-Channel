# The Deposits Channel of Monetary Policy

A critical review and analysis of the seminal paper by **Drechsler, Savov & Schnabl (2017)**: *"The Deposits Channel of Monetary Policy"*, published in the *Quarterly Journal of Economics*.

This repository contains a comprehensive report, a presentation outline, and the underlying LaTeX source code evaluating the mechanism through which bank market power over deposit markets transmits monetary policy to the real economy.

## Overview

The "Deposits Channel" proposes that when the Federal Reserve raises interest rates, banks use their market power to keep deposit rates low, widening "deposit spreads." This causes deposits to flow out of the banking system into alternative assets like money market funds, forcing banks to contract their lending. This mechanism provides a modern alternative to the traditional "bank lending channel" which relied on reserve requirements that are no longer binding in the current financial system.

## Repository Structure

- `paper.md`: A detailed critical review of the DSS (2017) paper, covering the theoretical framework, empirical strategy, findings, and a discussion of recent events (e.g., the 2022–2023 rate hiking cycle and the Silicon Valley Bank collapse).
- `report.tex`: The LaTeX source code for the formal review report.
- `slides_outline.md`: A structured outline for a 10-minute presentation on the deposits channel, including slide-by-slide transitions and key talking points.
- `.gitignore`: Configured to ignore LaTeX build artifacts and generated PDFs.

## Key Themes Explored

1.  **Market Power & Sticky Deposits**: How banks exploit depositor inelasticity to widen spreads.
2.  **Transmission Mechanism**: The three-step process from Fed Funds Rate hikes to lending contraction.
3.  **Endogenous Market Power**: Why the channel is more potent in concentrated banking markets.
4.  **Modern Context**: Evaluating the theory's relevance during the 2023 banking stress and the "higher-for-longer" interest rate environment.

## Usage

### Reading the Review
For a quick read of the analysis, refer to `paper.md`. For the presentation structure, see `slides_outline.md`.

### Building the LaTeX Report
To generate the PDF version of the report from `report.tex`, use a LaTeX distribution (e.g., TeX Live, MiKTeX) with `pdflatex` or `latexmk`:

```bash
latexmk -pdf report.tex
```

## References
*   Drechsler, I., Savov, A., & Schnabl, P. (2017). The deposits channel of monetary policy. *The Quarterly Journal of Economics*, 132(4), 1819-1876.
