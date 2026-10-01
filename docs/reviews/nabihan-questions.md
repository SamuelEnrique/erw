# Ten questions for Nabihan (cost of power v2, the seller's side)

Energy Research Warehouse (ERW), session 51. For an investment director at a private credit fund reviewing "What a generator earns" (`/cost-of-power/seller`): can a power asset service its debt?

Each question is tied to one part of the tab (`site/lib/merchant.ts`, `warehouse/derived/merchant_revenue.py`, `docs/methods/cost_of_power.md`). His answer decides v3, written next to it.

1. **The bad month (the median, the 10th-percentile month and the worst three, over the months held).**
   - Is the 10th percentile the right downside statistic, or do you size on the P90 of annual revenue, the P99, or a named stress year?
   - *Decides:* which statistic the summary leads with.
2. **Monthly against trailing-twelve-month coverage (both shown; flags at 1.0x and 1.25x).**
   - Which do your covenants test, and at what threshold: is 1.25x your lock-up, your default, or neither?
   - Should a six-month lookback be shown too?
   - *Decides:* the coverage tests and their lines.
3. **Cash flow available for debt service (revenue less fixed O&M only).**
   - What else do you take out before coverage: property tax, insurance, land, major maintenance reserves, a debt service reserve?
   - Should the tab take a single "other operating costs" input?
   - *Decides:* the CFADS formula.
4. **The default debt service (Lazard 2025 midpoint capital cost, 60 percent debt at 8 percent, amortized over the asset's life).**
   - Is a levelized mortgage over the full life how merchant or semi-merchant debt is structured today, or is it a shorter tenor with a sculpted or cash-sweep profile?
   - *Decides:* the debt service default and whether to model sculpting.
5. **Merchant only (no PPA, hedge, capacity payment or ancillary service).**
   - Which contract would you layer in first: a fixed-price PPA share, a hub-settled hedge (proxy revenue swap), or capacity revenue?
   - What share of a typical financed asset is contracted?
   - *Decides:* v3's first contract input.
6. **Hub price, not node price.**
   - How large a basis haircut do you apply for solar and wind in ERCOT West or SPP?
   - Should the tab take a basis input in USD/MWh or as a percent of the hub price?
   - *Decides:* a basis input.
7. **Fleet-average solar and wind shapes (EIA-930 output over EIA-860M nameplate in the balancing authority).**
   - Is a fleet shape good enough for screening, or do you need a site's P50/P90 shape before reading anything here?
   - *Decides:* whether to accept an uploaded hourly shape.
8. **The battery as a perfect-foresight upper bound.**
   - What share of perfect foresight do you credit a merchant battery's operator with: 60, 70, 80 percent?
   - Does that share change in the stress days?
   - *Decides:* a capture-of-perfect-foresight haircut input.
9. **The stress days (Uri, Elliott, the 2023 heat) against a normal week.**
   - Is upside in a storm worth anything to a lender, or only the downside of being unavailable then (Uri's frozen plants)?
   - Should the tab show the loss from an outage on those days?
   - *Decides:* whether stress days show an availability haircut.
10. **The short window outside ERCOT (thirteen months from September 2025).**
    - Would you read any coverage figure built on one year, or should the tab refuse to show coverage below some number of years?
    - *Decides:* a minimum history before the coverage section shows.

**Answers:** write each answer under its question with the date. The design change follows in the next session, with the method citing "Nabihan, review of 2026-10" where his answer sets a default.
