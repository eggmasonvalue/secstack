# Reading the ownership signal — 13F and insider data

Phase 6 support. Pull the data via `sec-edgar-skill` (institutional 13F holders and Form 4
insider transactions), then read it against the thesis. This guide is *how to interpret*
each pattern; the fetch mechanics and flags live in `sec-edgar-skill` (`--help` is
authoritative).

13F output reports **share counts**, not dollar values (13F values are stale quarter-end
prices). Convert to ownership percentages by dividing by shares outstanding from the
`market-scout` snapshot or the latest 10-Q.

## Institutional ownership (13F)

Who is positioned and how the holder base has shifted — signals that feed the risk and
catalyst assessment:

- **Concentration risk:** if 3–5 holders own >30% of the float, a single redemption cycle
  can crater the stock independent of fundamentals.
- **Smart-money conviction:** are high-conviction value managers (Royce, Needham, Baupost)
  building or trimming? A rising share count from a known deep-diver is a confirming signal;
  a quiet exit is a warning.
- **Activist presence:** a 13D/13G filer in the holder list may signal an upcoming catalyst
  (board fight, strategic review, buyback demand).
- **Passive vs. active mix:** a stock dominated by index funds (Vanguard, BlackRock, State
  Street) has different liquidity and governance dynamics than one held by concentrated
  active managers.
- **Ownership trend vs. price:** rising institutional ownership into a falling price
  suggests accumulation; the reverse suggests distribution. Cross-reference with the holder
  history.

## Insider activity (Form 4)

Insider transactions are a direct, auditable read on whether the people running the business
are aligned with outside shareholders — or quietly heading for the exits. Read them for
adverse-selection risk:

- **Open-market purchases by officers/directors** are the strongest signal — voluntary, with
  the insider's own capital, filed publicly. A CEO or CFO buying $500K+ at current prices is
  putting money where their mouth is; multiple insiders buying in the same window (a "cluster
  buy") is stronger still.
- **Selling context matters.** Discretionary sales by senior officers outside a pre-announced
  10b5-1 plan — especially into strength or ahead of a known risk — are a red flag; routine
  10b5-1, diversification, and tax-driven exercises are not. Read the pattern: clockwork
  quarterly selling is a plan; three executives dumping the week after an earnings beat is
  discretionary.
- **Ownership level vs. compensation.** Cross-reference insider holdings (the "Remaining
  Shares" column) against the proxy's compensation tables. Holdings 10x+ annual salary is
  real skin in the game; holdings that round to zero against cash comp are not.
- **Buy/sell ratio and trend.** A ratio well above 1x (net buying) over the past 6–12 months
  is confirming; well below 1x (net selling) into a long you are building is a direct
  adverse-selection warning — the best-informed people are reducing exposure.
- **Activity at inflection points.** The most informative trades cluster around events. An
  insider buying after a 40% drawdown thinks the market overreacted; an insider selling ahead
  of a product launch they have been hyping is telling you the opposite.
- **Foreign private issuers (FPIs):** FPIs are exempt from Section 16 and do not file Forms
  3/4/5 on EDGAR. Insider data will be unavailable — note the gap in the memo, and check the
  home-jurisdiction regulator (e.g. SEDAR+ for Canadian filers) if the thesis depends on
  insider alignment.
