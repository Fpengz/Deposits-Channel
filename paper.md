# The Deposits Channel of Monetary Policy: A Critical Review

**Drechsler, Savov & Schnabl (2017), _Quarterly Journal of Economics_, 132(4), pp. 1819–1876**

---

## Abstract

This report critically reviews Drechsler, Savov and Schnabl's (2017) seminal paper on the deposits channel of monetary policy. The paper proposes and empirically validates a new mechanism through which monetary policy transmits to the real economy — one grounded in banks' market power over deposit markets rather than the reserve requirements that underpinned prior theories. This review assesses the paper's research question, theoretical framework, empirical strategy, and findings, before evaluating its strengths and limitations, proposing extensions, and situating the mechanism in the context of recent economic events including the 2022–2023 rate hiking cycle and the collapse of Silicon Valley Bank.

---

## 1. Introduction and Research Question

The question of how monetary policy transmits through the banking system to the broader economy has occupied macroeconomists for decades. The prevailing framework — the bank lending channel — held that the Federal Reserve controlled bank balance sheets by setting the supply of required reserves, thereby influencing how much banks could lend. As Bernanke and Blinder (1988) formalised, this reserve mechanism was thought to be the primary conduit between the Fed funds rate and credit supply.

However, a long-recognised problem plagued this theory. By the 1980s, required reserves had become far too small relative to total banking system assets to exert any meaningful influence. Since 2008, the Federal Reserve has maintained a large balance sheet funded by interest-paying excess reserves, rendering reserve requirements entirely slack as a policy tool. As Romer and Romer (1990), Bernanke and Gertler (1995), and Woodford (2010) all noted, this left the bank lending channel theoretically unmoored — the empirical relationships were observed, but the mechanism was implausible.

Drechsler, Savov and Schnabl (2017) — hereafter DSS — fill this gap by proposing and rigorously testing a new channel: **the deposits channel of monetary policy**. Their central research question is whether, and through what mechanism, changes in the Fed funds rate affect the supply of bank deposits and, in turn, bank lending and real economic activity.

Their answer is built on a deceptively simple insight: banks have **market power** over local deposit markets. When the Fed funds rate rises, the opportunity cost of holding cash increases, which reduces depositors' sensitivity to deposit rates. Banks exploit this reduced sensitivity by widening deposit spreads — keeping deposit rates low while market rates rise. Deposits consequently flow out of the banking system into bonds and money market instruments. Since deposits are a uniquely stable and cheap source of bank funding, their contraction induces a contraction in lending. DSS argue, both theoretically and empirically, that this mechanism is large enough to account for the entire transmission of monetary policy through bank balance sheets — without requiring any role for reserve requirements.

---

## 2. Economic Intuition and Theoretical Framework

### 2.1 The Core Mechanism

The deposits channel operates through a three-step transmission process. First, when the Fed raises the funds rate, the opportunity cost of holding cash rises. This makes depositors less inclined to substitute away from deposits into cash, effectively rendering deposit demand more inelastic. Second, banks exploit this inelasticity by widening deposit spreads — charging more for the liquidity services that deposits provide. Third, even though depositors are less likely to substitute into cash, they do shift funds toward bonds and money market instruments, causing aggregate deposit outflows. Since deposits are a special, stable funding source that cannot be costlessly replaced by wholesale borrowing, banks respond by contracting lending.

A critical and elegant aspect of DSS's theory is that bank market power is **endogenous to the level of the Fed funds rate**. At low rates, cash is cheap to hold, so it represents a meaningful competitive alternative to deposits. Banks must keep spreads low to avoid losing depositors to cash. At high rates, cash becomes expensive, shifting competition away from cash and toward other banks. In concentrated markets, interbank competition is also limited, so banks face relatively inelastic demand and can charge high spreads. The implication is that the deposits channel is inherently non-linear and more powerful in concentrated markets and at higher rate levels.

The deposit spread — defined as the difference between the Fed funds rate and the deposit rate — is the central price variable. Empirically, DSS document that for every 100 basis points (bps) increase in the Fed funds rate, the aggregate deposit spread widens by approximately 54 bps, reflecting substantial and pervasive market power across the U.S. banking system.

### 2.2 The Theoretical Model

DSS formalise this intuition through a CES utility model. The representative household maximises utility over final wealth $W$ and liquidity services $l$:

$$u(W_0) = \max \left[ W^{\frac{\rho-1}{\rho}} + \lambda l^{\frac{\rho-1}{\rho}} \right]^{\frac{\rho}{\rho-1}}$$

where $\rho < 1$ ensures wealth and liquidity are complements — households value liquidity in addition to returns. Liquidity services are in turn derived from cash $M$ and deposits $D$ via a CES aggregator with elasticity of substitution $\epsilon > 1$, capturing the fact that cash and deposits are substitutes in liquidity provision.

Banks, which have market power parametrised by $\mathcal{M} = 1 - (\eta-1)(N-1)$ where $N$ is the number of banks and $\eta$ is the cross-bank substitution elasticity, optimally set the deposit spread to satisfy:

$$s = \delta^{\frac{1}{\epsilon-1}} \cdot \frac{\mathcal{M} - \rho}{\epsilon - \mathcal{M}} \cdot f$$

The key theoretical predictions are: (i) the deposit spread rises proportionally with the Fed funds rate $f$; (ii) the deposit spread beta $\frac{\partial s}{\partial f}$ is increasing in market power $\mathcal{M}$; and (iii) deposit quantities fall as spreads rise, triggering the lending contraction via the balance sheet identity.

When the model is extended to include costly wholesale funding and profitable lending opportunities (Proposition 3), the qualitative results are unchanged: higher rates induce deposit contraction, partial wholesale funding substitution, and a net reduction in lending. This extension makes the model's lending predictions directly testable.

### 2.3 Financial Sophistication as an Additional Source of Market Power

Beyond geographic concentration, DSS extend the model to incorporate depositor financial sophistication (Proposition 2). Households that are inattentive to interest rate differentials, do not participate in bond markets, or face high perceived switching costs give banks additional market power independently of market structure. The deposit spread beta becomes a function of both concentration and the share of unsophisticated depositors — meaning banks can maintain market power even in structurally competitive markets if their depositor base is sufficiently inattentive.

This extension is important because it broadens the channel's scope and makes the deposit spread beta a **sufficient statistic** for market power from all sources — not just concentration. DSS use county-level proxies for financial sophistication (age, income, and education) to validate this extension empirically.

---

## 3. Empirical Strategy

### 3.1 Data

DSS construct their empirical analysis from five main datasets spanning 1994 to 2013:

- **FDIC branch-level deposit data:** Annual branch-level deposit quantities for the universe of U.S. bank branches.
- **Ratewatch:** Weekly branch-level deposit rates by product (January 1997–December 2013), covering 54% of all U.S. branches.
- **U.S. Call Reports:** Quarterly bank-level income statements and balance sheets.
- **NCRC Small Business Lending data:** Annual bank-county-level new small business loan originations.
- **FRED and Datastream:** Fed funds rate, T-bill rates, and Fed funds futures for expected rate change decomposition.

Market concentration is measured using the Herfindahl-Hirschman Index (HHI) computed from county-level deposit market shares, averaged over the sample period. This yields substantial cross-sectional variation, from HHI = 0.06 in the most competitive urban markets to HHI = 1.0 in monopolistic rural markets.

### 3.2 The Identification Challenge

The core identification problem is that deposit supply and banks' lending opportunities may be correlated. If the Fed raises rates during an economic downturn, loan demand falls simultaneously with deposit supply. A naive regression of deposit growth on rate changes would conflate the monetary transmission effect with the demand effect, potentially overstating or understating the true deposit channel.

### 3.3 Within-Bank, Across-Branch Estimation

DSS's primary identification strategy is an elegant within-bank design. The key insight is that because banks can move deposits between branches — raising funds at a branch in one county and lending them in another — the deposit decision at a given branch is separable from the local lending decision. By comparing branches of the **same bank** located in counties with **different HHI levels**, DSS can control for bank-specific lending opportunities entirely.

The baseline regression is:

$$\Delta y_{it} = \alpha_i + \zeta_{c(i)} + \lambda_{s(i)t} + \delta_{j(i)t} + \gamma \cdot \Delta FF_t \times \text{Branch-HHI}_i + \varepsilon_{it}$$

where $y_{it}$ is either the change in the deposit spread or log deposit growth at branch $i$, $\delta_{j(i)t}$ are bank $\times$ time fixed effects that absorb all time-varying bank-level factors, and $\gamma$ captures the differential sensitivity of deposit supply to monetary policy by concentration level. Standard errors are clustered at the county level.

The identifying assumption is that banks equalise marginal lending returns across branches — an assumption supported by results in Section 7 showing that local deposit concentration has no independent effect on local lending, which is consistent only with internal capital market allocation.

### 3.4 Event Study

To sharpen causal inference, DSS exploit the weekly frequency of Ratewatch data to conduct an event study around FOMC announcements. By examining a $\pm5$ week window around Fed funds rate changes, they show that the differential spread response at high- versus low-concentration branches occurs essentially within one week of the announcement, with no pre-announcement drift. This precise timing rules out anticipation effects and slow-moving confounds, strongly supporting a direct causal interpretation.

### 3.5 Expected versus Unexpected Rate Changes

A further robustness test separates the total Fed funds rate change into expected and unexpected components using Fed funds futures prices. Since savings deposits have zero maturity, their rates should respond to a rate change when it occurs regardless of whether it was anticipated — unlike stocks and bonds, which incorporate expectations in advance. DSS find that both expected and unexpected components have similar effects on deposit spreads, confirming that monetary policy affects deposit pricing through the funds rate itself rather than through information conveyed by the rate change.

---

## 4. Key Findings

### 4.1 Aggregate Evidence

At the aggregate level, the deposit spread increases by 54 bps per 100 bps rise in the Fed funds rate over the 1986–2013 period. The spread increase is strongest for the most liquid deposit categories: savings and checking deposit spreads rose by 340 bps and 470 bps respectively during the mid-2000s hiking cycle, compared to 105 bps for time deposits. Aggregate core deposit growth is negatively correlated with rate changes at −49%, confirming that prices (spreads) and quantities (deposit growth) move in opposite directions — the hallmark of a supply curve shift.

_[FIGURE PLACEHOLDER — Figure I from DSS (2017): Panel A plots the average deposit rate against the Fed funds rate (1986–2013). Panel B plots deposit rates by product type. Caption: Deposit rates track the Fed funds rate with incomplete pass-through (beta = 0.54 on average). The spread increase is largest for liquid deposit categories, consistent with the liquidity-preference mechanism.]_

_[FIGURE PLACEHOLDER — Figure II from DSS (2017): Panels A–D plot year-over-year deposit growth against the change in the Fed funds rate for core, savings, checking, and time deposits. Caption: Deposit quantities are strongly negatively correlated with rate increases for liquid categories (savings: −59%, checking: −33%) but positively for time deposits (+23%), reflecting substitution within deposit categories as liquid deposits become relatively more expensive.]_

### 4.2 Within-Bank Results on Deposit Spreads and Flows

The within-bank estimation results are presented in Tables II and III of DSS. Following a 100 bps increase in the Fed funds rate, branches of the same bank located in high-concentration counties raise savings deposit spreads by **14 bps more** and experience deposit outflows **66 bps greater** than branches in low-concentration counties. These results are robust across all specification variants and hold for both savings and time deposits.

The implied semi-elasticity of deposits to deposit spreads is −5.3, meaning a 100 bps increase in the deposit spread is associated with a 530 bps contraction in deposits. Since a 100 bps rate hike generates on average a 61 bps spread increase among large banks, the expected deposit contraction per 100 bps hike is approximately 323 bps.

_[FIGURE PLACEHOLDER — Figure IV from DSS (2017): Panels A–C plot spread betas (savings, time) and flow betas against county HHI percentile bins. Caption: Both spread betas and flow betas increase monotonically with market concentration, consistent with the market power mechanism. The relationship is approximately linear across all 20 HHI bins.]_

### 4.3 Event Study Results

_[FIGURE PLACEHOLDER — Figure V from DSS (2017): Cumulative differential deposit spread response (high vs. low concentration) in the ±5 week window around FOMC announcements. Caption: The differential spread response is zero in the weeks prior to the announcement, rises sharply within one week of the FOMC decision, and stabilises at approximately 11 bps after two weeks. The permanent magnitude is consistent with quarterly regression estimates.]_

### 4.4 Results on Lending and Real Activity

Using small business lending data and within-county estimation, DSS find that a one standard deviation increase in bank-level concentration (Bank-HHI) reduces new small business lending by **291 bps** per 100 bps increase in the Fed funds rate. At the county level, a one standard deviation increase in County-HHI reduces employment growth by **9 bps** and total wage growth by **11 bps** per 100 bps rate hike. These effects are statistically significant and economically meaningful.

Bank-level Call Reports regressions confirm these findings: banks in more concentrated deposit markets increase deposit spreads, experience greater deposit outflows, partially offset by increasing wholesale funding, and ultimately contract total lending, securities, and assets.

### 4.5 Deposit Spread Beta and Aggregate Implications

The deposit spread beta — the sensitivity of a bank's deposit spread to the Fed funds rate — averages 0.54 across all banks and 0.61 for the largest 5% of banks. DSS use this measure as a sufficient statistic for bank-level exposure to monetary policy, demonstrating that it predicts the sensitivity of deposits, assets, securities, and loans to rate changes.

For a typical 400 bps hiking cycle, DSS estimate a 1,458 bps reduction in deposits and a 995 bps reduction in lending relative to keeping rates unchanged. Based on 2014 balance sheet figures, this translates to a **$1.35 trillion** reduction in deposits and a **$763 billion** reduction in lending — magnitudes that account for the entire bank lending channel effect documented by Bernanke and Blinder (1992).

### 4.6 The Liquidity Premium

_[FIGURE PLACEHOLDER — Figure VIII from DSS (2017): Time series of the aggregate deposit spread and the T-bill liquidity premium (Fed funds rate minus 3-month T-bill rate), 1986–2013. Caption: The two series co-move with a correlation of 90%, both cyclically and in long-run trends, suggesting that the deposits channel is a primary driver of the liquidity premium in financial markets.]_

Since deposits are the main source of liquid assets for households, the contraction in deposit supply reduces aggregate liquidity and pushes up the liquidity premium on all safe assets including Treasuries. The 90% correlation between the aggregate deposit spread and the T-bill liquidity premium provides striking macro-level validation and explains the puzzling relationship documented by Nagel (2016).

---

## 5. Critical Evaluation

### 5.1 Strengths

**Identification strategy.** The within-bank, across-branch design is one of the most credible natural experiments in the empirical banking literature. By exploiting within-bank variation in local market concentration while absorbing bank-time fixed effects, DSS cleanly separate the deposit supply effect from lending opportunity effects. The event study's one-week response window further closes off virtually all alternative explanations. These two identification approaches are mutually reinforcing: the panel regression establishes the cross-sectional mechanism, while the event study establishes precise timing.

**Empirical breadth and consistency.** Results are consistent across five levels of analysis — aggregate time series, branch-level regressions, bank-level Call Reports, county-level employment outcomes, and the event study — using three independent datasets. This convergence across methodologies and datasets greatly strengthens confidence in the mechanism.

**The deposit spread beta as a policy instrument.** The deposit spread beta is a theoretically grounded, easily observable, bank-level measure of monetary policy exposure. It aggregates all sources of market power — concentration, depositor inattention, switching costs, financial sophistication — into a single sufficient statistic. This has genuine practical value for regulators seeking to assess which banks are most exposed to rate cycles in stress testing exercises.

**Theoretical resolution of a long-standing puzzle.** By providing a market power foundation for the bank lending channel, DSS resolve a decades-old problem in monetary economics. The mechanism does not require reserves, does not depend on banks being liquidity-constrained, and is consistent with the modern institutional structure of banking.

### 5.2 Weaknesses and Limitations

**The representative household assumption.** The CES framework assumes a representative depositor with constant elasticity preferences. In reality, deposit markets are deeply heterogeneous. Sophisticated depositors — corporate treasurers, institutional investors, and high-net-worth individuals — have near-zero switching costs and highly elastic demand. Retail depositors have high inertia. Aggregating these populations into a single representative agent masks the heterogeneity that drives tail risks such as bank runs, as the Silicon Valley Bank episode illustrated. A model with a distribution of depositor types would yield richer predictions and better account for the concentration of outflows at specific institutions.

**Sample period and the pre-fintech limitation.** The empirical analysis covers 1994–2013, predating the structural disruption of digital banking. Online high-yield savings accounts, mobile banking apps, and fintech platforms have fundamentally reduced geographic switching frictions. A depositor in 2024 can open a high-yield account in minutes on a smartphone, rendering county-level HHI a less meaningful proxy for competitive pressure. The model's market power parameters — and therefore its quantitative predictions — likely require re-estimation for the post-2015 era.

**Wholesale funding cost is assumed, not estimated.** The parameter $h$ governing the cost of wholesale funding is treated as exogenous and constant. In practice, wholesale funding costs vary with market conditions, a bank's credit rating, and regulatory requirements such as the Liquidity Coverage Ratio and Net Stable Funding Ratio introduced by Basel III. The lending contraction results are sensitive to this parameter, and treating it as a fixed structural constant limits the model's applicability in different regulatory environments.

**Static concentration measure.** The HHI is computed as a time-averaged, county-level measure, abstracting away from dynamic competitive entry, the growing role of non-bank competitors (money market funds, fintechs), and cross-market competition from internet banks that operate across geographic boundaries. In the modern era, a bank's competitive environment is increasingly defined by product and digital competition rather than geographic proximity.

**General equilibrium endogeneity.** DSS acknowledge that the Fed tends to raise rates during economic expansions when loan demand is high. While cross-sectional identification controls for this at the bank and county level, the aggregate estimates necessarily reflect the net of deposit contraction and demand-side expansion effects. The $763 billion lending reduction estimate is therefore best interpreted as an upper bound on the net contractionary effect of monetary tightening, since it assumes lending would have remained at pre-hike levels in the counterfactual.

---

## 6. Evaluation of Key Assumptions

| Assumption                                         | Role                                     | Assessment                                                                         |
| -------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------- |
| Banks freely allocate deposits across branches     | Enables within-bank identification       | Indirectly validated; may be weaker for small single-market banks                  |
| Wealth and liquidity are complements ($\rho < 1$)  | Drives demand inelasticity at high rates | Well-grounded theoretically; validated by liquid vs. illiquid deposit differential |
| Market power is stable over time                   | Justifies static HHI                     | Increasingly questionable post-2015 due to digital banking                         |
| Wholesale funding imperfectly substitutes deposits | Generates lending contraction            | Theoretically standard; not directly estimated                                     |
| Representative household                           | Simplifies aggregation                   | Problematic for heterogeneous depositor dynamics and tail risk                     |

---

## 7. Engagement with the Broader Literature

DSS's paper sits at the intersection of three major literatures, making meaningful contributions to each.

**Bank lending channel.** Relative to Bernanke and Blinder (1988, 1992) and Kashyap and Stein (2000), DSS provide the micro-foundation that prior work lacked. Their aggregate estimates closely replicate Bernanke and Blinder's VAR results — deposit outflows of 113 bps, securities reductions of 154 bps, and loan contractions of 77 bps per 31 bps rate increase — demonstrating quantitative equivalence while offering a theoretically coherent mechanism.

**Balance sheet channel.** A key distinguishing prediction separates the deposits channel from Bernanke and Gertler (1989) and the broader balance sheet channel literature. Under balance sheet amplification, banks should cut all funding symmetrically as net worth declines. DSS find instead that banks _increase_ wholesale funding to partially offset deposit outflows — a pattern consistent only with the deposits channel, where banks are responding to a funding composition shock rather than a net worth shock.

**Liquidity premium literature.** By connecting the deposit spread to the T-bill liquidity premium at 90% correlation, DSS provide the most compelling supply-side explanation for the puzzling relationship documented by Nagel (2016). The mechanism is intuitive: deposits are the marginal supplier of household liquidity, so their contraction mechanically tightens liquidity conditions across all markets. This bridges monetary economics and asset pricing in a novel way, suggesting that monetary tightening has financial market effects that operate independently of the traditional interest rate channel emphasised in New Keynesian models.

---

## 8. Extensions and Creative Thinking

### 8.1 Digital Banking and the Erosion of Market Power

The structural rise of internet banking represents perhaps the most important challenge to the deposits channel as described by DSS. The reduction in switching costs since approximately 2015 has been substantial and continues to accelerate. A natural extension would re-estimate deposit spread betas across pre- and post-fintech periods, exploiting the staggered geographic rollout of high-yield online savings products as an exogenous shock to competitive pressure in local deposit markets. The hypothesis is that spread betas have declined structurally as switching costs fell, implying that the deposits channel has weakened as a monetary transmission mechanism precisely as central banks have come to rely on rate-based policy more heavily. This has potentially important implications for the design of monetary policy in a digitally enabled financial system.

### 8.2 Central Bank Digital Currency

A retail CBDC paying a rate mechanically linked to monetary policy would constitute a direct government-backed competitor to bank deposits. This creates a fundamental tension. On one hand, a CBDC would accelerate and deepen pass-through of rate changes to household liquidity costs, amplifying the deposits channel's transmission intensity. On the other hand, it would eliminate banks' market power in deposit markets entirely, destroying the deposit franchise value that is the source of the spread differential. A model extension incorporating a CBDC as a fourth asset class — alongside cash, deposits, and bonds — would quantify this tradeoff. For a 400 bps hiking cycle with a CBDC replacing even 20% of deposit market share, the predicted deposit outflows could far exceed DSS's baseline estimates, potentially destabilising bank funding systemically and creating a new form of liquidity risk.

### 8.3 Heterogeneous Depositor Model

Replacing the representative household with a distribution of depositor types — varying in financial sophistication, inattention, switching costs, and wealth — would generate substantially richer predictions. Such a model would yield: first, a distributional account of which depositor segments drive aggregate dynamics; second, welfare implications of monetary tightening that vary across income and wealth groups; and third, a framework to account for tail events such as bank runs, where the composition of the deposit base (rather than its average characteristics) determines stability. Linking administrative bank account data with household financial records, where available through central bank supervisory datasets in Europe and Canada, could enable structural estimation of the switching cost distribution and a proper test of the heterogeneous depositor extension.

### 8.4 International Evidence

**Thought Experiment:** Consider two stylised banking systems: System A, with moderate deposit market concentration, privately owned banks, and competitive deposit markets (approximating the United States); and System B, with state-owned banks, administered deposit rates, and implicit deposit guarantees (approximating China or some European banking systems). In System B, the deposits channel should be muted or absent — state banks do not maximise deposit rents and do not face the same market power dynamic. Cross-country panel data combining BIS banking statistics with central bank policy rates and bank ownership structures could test whether the deposits channel's strength correlates with private bank ownership, deposit market concentration, and the degree of depositor protection. Such evidence would determine whether DSS's findings are specific to the U.S. institutional context or represent a general feature of market-based banking systems.

---

## 9. Real-World Relevance and Contemporary Application

### 9.1 The 2022–2023 Hiking Cycle

The Federal Reserve's 2022–2023 tightening cycle — the fastest in 40 years, raising rates from near-zero to over 5% in 18 months — provides a partial out-of-sample test of DSS's framework. The deposits channel's predictions were broadly borne out: aggregate U.S. bank deposits fell by approximately $1 trillion between early 2022 and mid-2023, broadly consistent with DSS's predicted $1.35 trillion outflow for a 400 bps cycle. Money market fund assets surged by approximately $1.2 trillion over the same period, consistent with DSS's model of substitution from deposits into bonds and near-money instruments.

However, one significant deviation from the DSS framework was observed: the speed and concentration of deposit outflows was faster than historical patterns suggested. Digital banking had reduced switching frictions substantially, and sophisticated depositors responded more quickly and decisively than the 1994–2013 model parameters would predict. This suggests that while the directional predictions of the deposits channel remain valid, its quantitative calibration requires updating to reflect the post-fintech competitive landscape.

### 9.2 The Silicon Valley Bank Collapse

The March 2023 collapse of Silicon Valley Bank (SVB) is a striking real-world illustration of the deposits channel's fragility dimension. SVB's depositor base was the polar opposite of the DSS high-market-power profile: concentrated, highly financially sophisticated, deeply networked, and almost entirely above FDIC insurance limits. When the Fed raised rates and SVB's mark-to-market losses on its long-duration asset portfolio became publicly known, the elasticity of deposit demand was essentially infinite. An information-triggered run unfolded in hours rather than quarters.

This episode illuminates a critical heterogeneity that the DSS representative agent model cannot capture. Banks with high measured market power in DSS's framework — those whose depositors are unsophisticated, inattentive, and geographically captive — are stable in a rate tightening cycle but may be vulnerable to slow-moving erosion of franchise value. Banks like SVB, which appear to have a stable, relationship-based deposit base in normal times, can experience catastrophic run dynamics when information shocks interact with depositor sophistication and network effects. The deposits channel, as modelled by DSS, is fundamentally a story about gradual adjustment; SVB is a story about discontinuous adjustment — a regime that requires an extension of the framework to model properly.

### 9.3 Policy Implications

**For central banks**, the deposits channel implies that monetary tightening is more powerful than New Keynesian models suggest, operating through a supply contraction in liquidity in addition to the standard demand suppression via interest rates. The level of the short rate matters independently of its deviation from neutral, providing a theoretical basis for the gradualism in rate adjustment documented by Bernanke (2004) and Stein and Sunderam (2015). In a world of declining bank market power due to fintech disruption and potential CBDC introduction, however, the potency of this channel may weaken structurally, increasing the relative importance of balance sheet tools.

**For bank regulators**, deposit spread betas should be incorporated into stress testing frameworks as a measure of rate sensitivity that complements traditional asset duration analysis. Crucially, bank mergers that increase deposit market concentration amplify both the profit upside in normal times and the funding fragility during tightening cycles — a dual effect that antitrust analysis focused solely on consumer welfare in product markets may miss. The 90% correlation between deposit spreads and the T-bill liquidity premium suggests that monitoring deposit market conditions provides a leading indicator of broader financial market liquidity stress, ahead of observable distress in credit markets.

**For CBDC policy**, the deposits channel analysis suggests that a retail CBDC paying a policy-linked rate would fundamentally alter the transmission of monetary policy by eliminating the market power friction that the channel depends upon. While this would improve the efficiency and speed of pass-through, it would simultaneously threaten bank disintermediation at a scale that could destabilise financial system stability — particularly during rate tightening cycles when deposit outflows would be both faster and larger than in the status quo.

---

## 10. Conclusion

Drechsler, Savov and Schnabl (2017) make a landmark contribution to monetary economics. By grounding the bank lending channel in banks' market power over deposit markets — rather than the long-implausible reserve requirements mechanism — they solve a decades-old theoretical problem and provide a quantitatively credible, empirically validated account of how monetary policy propagates through bank balance sheets to the real economy.

The paper's primary strengths lie in its identification strategy, the breadth and consistency of its empirical evidence, and the practical utility of the deposit spread beta as a policy instrument. Its primary limitations are the pre-fintech sample period, the representative household assumption, and the treatment of wholesale funding cost as a fixed structural parameter.

The 2022–2023 hiking cycle and the SVB collapse have provided a rich set of out-of-sample data that partially validates the channel's directional predictions while exposing its sensitivity to changes in depositor composition and switching costs. These events underscore the need for extensions that incorporate depositor heterogeneity, dynamic market power, and the structural shifts introduced by digital banking and potential CBDC deployment.

The deposits channel reframes our understanding of how central banks move the real economy. The friction that makes it work — depositor inertia and bank market power — is real, measurable, and historically consequential. Whether it remains so in an era of instant digital account switching, abundant money market alternatives, and potentially a government-backed digital currency is one of the most important open questions at the frontier of monetary economics and banking research.

---

## References

Bernanke, B.S. (1983). Nonmonetary Effects of the Financial Crisis in the Propagation of the Great Depression. _American Economic Review_, 73, 257–276.

Bernanke, B.S. & Blinder, A.S. (1988). Credit, Money, and Aggregate Demand. _American Economic Review_, 78, 435–439.

Bernanke, B.S. & Blinder, A.S. (1992). The Federal Funds Rate and the Channels of Monetary Transmission. _American Economic Review_, 82, 901–921.

Bernanke, B.S. & Gertler, M. (1989). Agency Costs, Net Worth, and Business Fluctuations. _American Economic Review_, 79, 14–31.

Bernanke, B.S. & Gertler, M. (1995). Inside the Black Box: The Credit Channel of Monetary Policy. _Journal of Economic Perspectives_, 9, 27–48.

Bernanke, B.S. (2004). Gradualism. Remarks at the Federal Reserve Bank of San Francisco, Seattle Branch.

Drechsler, I., Savov, A. & Schnabl, P. (2017). The Deposits Channel of Monetary Policy. _Quarterly Journal of Economics_, 132(4), 1819–1876.

Gilje, E.P., Loutskina, E. & Strahan, P.E. (2016). Exporting Liquidity: Branch Banking and Financial Integration. _Journal of Finance_, 71, 1159–1184.

Kashyap, A.K. & Stein, J.C. (2000). What Do a Million Observations on Banks Say about the Transmission of Monetary Policy? _American Economic Review_, 90, 407–428.

Krishnamurthy, A. & Vissing-Jørgensen, A. (2012). The Aggregate Demand for Treasury Debt. _Journal of Political Economy_, 120, 233–267.

Nagel, S. (2016). The Liquidity Premium of Near-Money Assets. _Quarterly Journal of Economics_, 131, 1927–1971.

Romer, C.D. & Romer, D.H. (1990). New Evidence on the Monetary Transmission Mechanism. _Brookings Papers on Economic Activity_, 1, 149–213.

Stein, J.C. (1998). An Adverse-Selection Model of Bank Asset and Liability Management with Implications for the Transmission of Monetary Policy. _RAND Journal of Economics_, 29, 466–486.

Stein, J.C. & Sunderam, A. (2015). The Fed, the Bond Market, and Gradualism in Monetary Policy. Working Paper, Harvard University.

Woodford, M. (2010). Financial Intermediation and Macroeconomic Analysis. _Journal of Economic Perspectives_, 24, 21–44.

