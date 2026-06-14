# Archetype: Special Situation

A situation where a **structural, legal, or transactional fact** — not the ongoing business —
drives the outcome: a spin-off, post-bankruptcy equity, a merger/arb spread, a seniority
waterfall, a put/call formula, a squeeze-out or minority-protection statute, a recapitalization.
The edge is *forensic*: you read the actual document, compute the formula yourself, and rebuild
the capital structure — and you reach a conclusion that nearly *has* to resolve a certain way.
(Lou's richest value-investing shape — see Quilmes, MCI, NII Holdings, Telemig in the
`pitch-like-lou` corpus.)

## Tell it by
The thesis hinges on an event or a legal/structural mechanism rather than earnings growth:
corporate actions (spin, merger, tender, reorg), unusual securities (pink-sheet preferreds,
stubs, post-reorg equity), or a binding formula/statute that forces value to a class of
holders.

## Where the value hides
- **In the document itself.** The put/call formula in an exhibit, the seniority of a security
  in the waterfall, the squeeze-out price mechanism in foreign company law. The market prices
  the *headline*; the edge is reading the *fine print* and computing the consequence.
- **In forced/neglected selling.** Spin-offs dumped by index funds, post-bankruptcy equity
  held by creditors who want out, complex securities no analyst covers — structural sellers
  create mispricing unrelated to value.
- **In the binding-ness.** The whole thesis rests on whether the legal fact *actually binds*.
  That is the one thing you must verify yourself, not relay second-hand.

## Pull these (drive sec-edgar)
- **The primary document** — the merger agreement, indenture, plan of reorganization, 13D
  exhibit, Form 10 spin filing, or the foreign-law statute. Read the *exhibit*, not the
  summary. `sec-edgar-skill` can pull attachments/exhibits directly.
- 8-Ks for the triggering event (Item 1.01, 1.03, 2.01, 5.01) and the timeline.
- 13D/G for the activist or controlling holder and — critically —
  `item4_purpose_of_transaction` (the *why*).
- For foreign private issuers: 20-F and 6-K, and the local regulator's filings; reconcile to a
  comparable basis.
- Capital-structure detail to rebuild the **post-event** balance sheet and the waterfall.

## Key metrics / objects
The payoff under each outcome (deal closes / breaks; put exercised / not), the **probability
and timing** of each, the position in the capital structure, the spread vs. downside, the
sum-of-the-parts value, the formula output you computed yourself.

## Normalize / adjust
- **Compute the formula yourself** from the document — do not trust a summary or a third-hand
  characterization (the MCI lesson: ~$24B of intercompany claims surfaced *after* a "books are
  clean" was relayed second-hand).
- Rebuild the **pro-forma** capital structure as it exists *after* the event.
- For foreign issuers, reconcile foreign-GAAP/IFRS to a comparable basis before valuing.

## Valuation lens
**Event payoff / sum-of-the-parts**, probability-weighted across outcomes, with the spread
measured against a hard downside. For spins, value the pieces separately on **multiples**; for
arb, it's payoff × probability vs. break risk; for structural/legal, it's the formula output
discounted for time and the (small) chance the fact doesn't bind.

## Disqualifiers — kill it (or mark it down) if…
- **The legal/structural fact doesn't actually bind** — the formula has an out, the statute
  doesn't apply, the seniority is subordinated by a clause you missed.
- **Minorities have no protection** — a controller can take the value without sharing it
  (no fair-price statute, no independent committee, coercive terms).
- **The timeline is open-ended** — no forcing event or date; "eventually" is not a catalyst and
  time decay eats arb returns.
- **You're relying on something you didn't verify** — any load-bearing claim taken second-hand
  is an unpriced risk; check it or mark the conviction down hard.
- **The downside isn't bounded** — if the deal breaks or the put isn't exercised, the residual
  business is worth far less than the spread implies.
