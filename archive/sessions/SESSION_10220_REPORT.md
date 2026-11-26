# Session 10220 report: the congestion page audited as a hostile expert would

Chain 710, part D (one more tool, in the form of part B), the old laptop, 26 November 2026. Worktree `C:\Users\lossa\Documents\erw-c710-c`, branch `wip/audit-congestion-doc`.

## What was done

- `docs/reviews/congestion-model-audit-2026-11-26.md` and its evidence folder `docs/reviews/congestion-model-audit-2026-11-26/` (every script and printout).
- `/congestion` drawn with the site's own code in five views. Every figure of the default view was restated independently from the page file: 245 of 245 to the digit. The places' mean day-ahead LMP was checked against the warehouse's hub tables: 105 of 106 whole months to the cent.
- Seven findings: two Major, three Moderate, two Minor. Four words branches and their merge `wip/audit-congestion-words`; three ruling lines; four data requests.
- No table written, no lock, no model call, no request to any service, no site build, no default moved.

## Branches

- `wip/audit-congestion-1` `9bb3a6d57`: words (a congestion part is measured from its own operator's reference).
- `wip/audit-congestion-2` `e268ba266`: words (one element on several rows; "no contingency named").
- `wip/audit-congestion-3` `6a134c972`: words (the newest day held, each place's days, UTC days named).
- `wip/audit-congestion-4` `e3033c44a`: words (SPP's western area from 1 April 2026; the ERCOT decision's API).
- `wip/audit-congestion-words` `45e118e40`: the four merged, 45 tests and the reader render pass, drawn and read.

## Decisions made without you

- The page's "constraint" was audited as the operator's element under one contingency, and the label "(no contingency named)" was chosen over relabelling BASE rows, which the browser read's row N3 leaves for your ruling.
- Local days were printed only as words (the newest day held, each place's window). The constraint's own first and last days stay UTC with a note, because changing them moves a date a reader sees.
- Findings 5 (ceiling prices, extreme months) and 6 (SP15 October) got no branch: the page says nothing false there, and sizing them needs the hourly tables.
- The ERCOT wording (finding 7) rides on branch 4 rather than a branch of its own.

## For Samuel's ruling (default "left as it is" for each)

- The places table holds the chosen operator's places only: SPP North shows 1 of 2 instead of 2 of 9.
- An element's keys are joined: TEXAS_CO_TXPS_TXCO_PHSHFT_PS goes from 60,293 to 92,128 hours (every year held), and CAISO's largest 2025 sum from 553,893 to 605,827.
- A constraint's first and last days are given by the operator's clock: 187 of 614 SPP dates and 127 of 480 CAISO dates move back a day.

## Needs the key

- Nothing. No model was called, and no step needs one.

## Problems

- One rule broken: while checking that the figures were unchanged, one command held an empty inline `python -c ""` inside a process substitution, beside `cmp`. It ran nothing and wrote nothing, but it is inline code, which the brief forbids. Every later check used `cmp` alone.
- Merging branch 4 into the words branch joined the note's decision 3 onto the line before it; it was found in the diff and set right before the commit.
