# Session 824 report: what a lab's power trader reads here

23 October 2026, 08:17 to about 08:40 UTC, unattended, on portable-laptop (the code machine), from the main checkout (a document; no build). Chain `queue/done/080-night-23-october-portable-landing-deals-.md`, session 824. Model Fable 5.1. Precheck 0. Model spend USD 0. No warehouse data written; no request.

## Read these first

- **`docs/reviews/deals-gaps-2026-10-23.md`**: the fields a power trading lead or an infrastructure-finance lead reads in a deal (from AG's section 4 and TL;DR, and DR's roles), each against the column of `energy_deals` that holds it, how many rows state it, how many of the 16 shown rows, and the source that would fill it where the tracker is blank.
- **The tracker holds the counterparties, the type, the size, the status, the value and a stated price or term**; it holds no price structure, settlement index, delivery point, product shape, start or end date, credit terms or docket. 27 of 505 rows state MW, 0 state a price in USD per MWh, 45 name a state.
- **No shown row's evidence is a public filing**: all 16 are World Nuclear News articles, so no field was drawn from a filing; the path stays empty until the data machine adds a filing source. The sources, in order: FERC's EQR (in the warehouse, internal; session 825's join), the companies' own announcements and 8-K exhibits, the ISOs' and utilities' filings, DOE's Loan Programs Office.

## What to review

- The review's table, and its two ruling items.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 824"` | 0 | on duty (the other session had restored this chain's mark after its queue step) |
| the stated-field counts, from `warehouse/output/energy_deals.csv` (505 rows) | | mw 27, dollars 269, state 45, term 17, mwh 2, price 0, price in another unit 2, status 419, AI flag true 194; the shown rows: state 5, term 1, AI true 0 |

## The landing

A document, pushed to main.

## Decisions made without you

1. The fields are the two reports' words and the roles' postings, not an industry template; the credit terms are listed because the Power Trading Lead's posting names risk management.
2. The "drawn from a public filing" path was tested on the evidence table and found empty; nothing was drawn.

## For Samuel's ruling

- The EQR tables' flag (internal today), the one source for the filed price structure, settlement point and dates.
- Whether a press-release feed for the deals' parties is a pull the data machine may make, each newsroom's terms read first.

## Files

- New: `docs/reviews/deals-gaps-2026-10-23.md`, this report.
