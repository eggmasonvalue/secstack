# Full due-diligence memo

Use this skeleton for a requested deep dive. It is not a questionnaire: combine, reorder, or omit
sections when that improves the argument, and add a section when the company's economics demand
it. A special situation, cyclical, and compounder should not produce identical memos.

## Evidence notation

Use the notation consistently on load-bearing factual and model claims:

- **[V]** checked against a cited authoritative primary record;
- **[E]** calculated or modeled, with inputs and units;
- **[A]** unresolved assumption, with its decision impact; and
- **[W]** external, trade, channel, expert, or secondary evidence, named and dated.

The tag does not replace a citation. Do not label an analytical inference `[V]` merely because
its inputs are verified; state that it is an inference. Ordinary connective prose does not need
a tag.

## Header

```markdown
# [Company] ([Ticker / share class]) — investment memo
**As of:** [date, time zone where relevant]
**Question:** [decision being evaluated]
**Decision:** [Long / Watch / Pass]
**Conviction:** [plain-language level and why]
```

## Decision snapshot

Select the small set of current metrics that orient this specific case. Do not reproduce a
fixed stat block inherited from another pitch or fill irrelevant cells. Possibilities include:
price and market value, enterprise value, diluted shares, net debt, normalized FCFF, valuation
range, cycle position, unit metric, asset value, liquidity runway, or event spread. Label dates,
periods, currencies, and adjustments.

Then state in a few sentences:

- what the market price appears to require;
- the variant view, if one exists;
- the decisive evidence;
- what could make the view wrong; and
- why the current price does or does not compensate for that uncertainty.

If no differentiated view is established, say so. A clear pass is better than an invented
variant perception.

## Business and economic model

Explain in plain language:

- product or service, customer, payer, and unit of sale;
- segments and where gross profit and cash flow arise;
- pricing, volume, retention, cyclicality, and capital needs; and
- the few operating variables that govern value.

Name the analytical lens or lenses only if they sharpen the decision. Do not force the company
into an archetype.

## Reported-to-normalized economics

Reconcile reported results to the cash-flow basis used in valuation. Include the periods and
metrics that reveal the economics rather than a mandatory table. Show:

- recurring versus non-recurring items;
- organic versus acquired growth;
- maintenance and growth investment;
- working-capital and deferred-revenue timing;
- stock compensation and diluted shares;
- lease treatment; and
- capital allocation and return on incremental capital where meaningful.

Use `guide_normalization.md`. If a new stream or future margin structure carries material value,
include a driver bridge from volume and price through costs, reinvestment, and FCFF.

## Competitive and industry underwriting

Define the relevant market and profit pool, identify economically comparable peers, and explain
the company's position through mechanisms and evidence. Connect material advantages and threats
to an operating assumption, scenario, or monitorable.

Quantify where evidence supports it. Where it does not, use a range, break-even calculation,
leading indicator, or explicit `[A]` gap rather than invented precision. Use
`guide_competitive.md`.

## Management, ownership, and governance

Include this section when control, incentives, dilution, capital allocation, insider activity,
or holder concentration can affect the outcome. Distinguish:

- beneficial ownership and voting control from 13F positions;
- voluntary Form 4 purchases and sales from grants, exercises, tax withholding, and gifts;
- reported quarter-end 13F changes from inferred trading intent; and
- compensation design from demonstrated capital-allocation behavior.

Use `guide_ownership_signals.md`. Keep immaterial holder lists out of the memo.

## Valuation and expectations

Use methods that fit the business and reconcile each to common equity. State:

- valuation date, currency, and current price;
- reported-to-normalized cash-flow bridge;
- enterprise-to-equity bridge and diluted shares;
- explicit operating scenarios and their evidence;
- discount-rate and terminal assumptions;
- value per share or payoff under relevant outcomes; and
- price discount/premium, downside, and required return.

A reverse DCF is useful only if its positive-FCFF model describes the company. EPV is a no-growth
case, not a hard floor. Growth sensitivity alone is not a bear/base/bull analysis when margins,
capital needs, dilution, or financing also change. Use `guide_valuation.md`.

Summarize the assumptions that dominate the result and show the sensitivity that matters. Do
not require a ceremonial peer-beta table if another discount-rate method is better supported.

## Countercase and pre-mortem

Make the strongest good-faith case against owning the security. Run the relevant archetype
disqualifiers, then answer:

- Which fact, inference, or assumption is most likely wrong?
- What permanent impairment path exists?
- What financing, dilution, control, or liquidity event could intervene?
- Which downside estimate is genuinely anchored, and which is not?
- If the thesis has failed one year from now, what probably happened?

Size material effects when the evidence supports it. For discontinuous or poorly disclosed
risks, describe the mechanism, exposure, leading indicator, and decision impact instead of
inventing a probability.

## Catalysts, falsifiers, and monitorables

List observable developments that change probability or value. For each, state the expected
time window, source to check, and what outcome confirms or weakens the thesis. A catalyst needs a
mechanism; “re-rating” alone is an outcome.

Separate a catalyst from a falsifier. The latter is the evidence that should make the investor
exit or revisit the work even if price has not cooperated.

## Verdict

Conclude **Long**, **Watch**, or **Pass** at the confidence supported by the research. Tie the
verdict to valuation, the variant view, and the countercase. State unresolved work and the price
or evidence that would change the decision.

## Sources and calculation notes

Provide an audit trail for material claims:

- SEC form, filing date, accession, and item or section;
- issuer, regulator, court, or industry document title and date;
- external URL, publisher, publication date, and access date where relevant; and
- calculation inputs, units, periods, and formulas.

Do not dump every document opened. Include the sources on which the argument actually relies and
preserve conflicting evidence.
