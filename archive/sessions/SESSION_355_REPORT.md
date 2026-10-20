# Session 355 report: the battery's node band, and Research's statistics on the cards

20 October 2026, from about 14:20 UTC, unattended, on samueloldlaptop (the code machine), the fifth session of the chain of 20 October, night (`queue/done/010-night-20-october-code.md`). Branch `wip/355-node-research` in the worktree `erw-296`, from session 354's branch; lands on main with 352 to 354. Model spend USD 0; no warehouse data written; nothing pulled. Precheck exit 0.

## Read these first

- **The battery's node band** (`/cost-of-power/battery`, ERCOT at `HB_HUBAVG`), under "Income by stream", beside the line that says energy is priced at the hub, not the battery's node. Over the battery's own last twelve months, from the data machine's `node_basis_summary` (session 358; `dam_storage_*`): the day-ahead four-hour spread at ERCOT's storage nodes at the 10th percentile, median and 90th, against the hub's over the same days, and the share of storage nodes wider than the hub, the twelve months' means weighted by the days held, each month in a fold with its keys. October 2025 to September 2026 (335 days): USD 34.24, 48.90 and 65.84 per MWh against the hub's 47.26; 57.65 percent of storage nodes wider; the median node's spread is 103.5 percent of the hub's. One line says what that means and what it does not: "the energy this page counts at the hub would scale about with it, the reserves not at all". **Added to no figure.** The read is in `site/lib/nodebasisread.ts`, so the page's own reads stay `read.ts`'s (tests 148 and 178). `node_basis_daily` is not read: its summary holds the band, and the daily rows are 888 points by 335 days.
- **Research's cards show what the data machine's session 361 wrote into them** (`statistics`): under the table of estimates, in the card's fold and never in the PNG renderer's frame, a table of each regression's SE and p by HC1 and by Newey-West with the lags; the round's multiple-comparisons line (claims tested and passing, the card's own Benjamini-Hochberg q-values, the caveat); and, on a hunt draft that carries it, the flag "A step, not a trend" with its two levels. No figure, verdict or word of a card changes. Today's eleven library cards carry the first two. The hunt writes the shape from its version 1.3.0, which session 361 ran only as a dry run, so drafts loaded before it carry none; the flag shows on a draft that carries it (not checked against the live drafts tonight).
- Docs: `battery_earns_algorithm.md` 11.3; `automated_analysis_findings.md`, "On the page (session 355)"; packs `battery.md` item 4 and `research.md` items 2, 4 and 5.

## What to review

In the internal view, after the landing:

1. https://erw-flame.vercel.app/cost-of-power/battery : "At its own node", under "Income by stream", and its fold.
2. https://erw-flame.vercel.app/research/card/batteries_lunch : open the fold; the second table and the round's line. Then `batteries_lunch_grids` and `batteries_curtailment`.
3. `docs/brand/review-355/`.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 355"` | 0 | |
| `tests.test_session355` and every test that reads a file this session changed (37 modules, 680 tests) | 1, then 0 | two: the page made a read of its own (148, 178 hold the battery page to `read.ts`'s): the read moved to `lib/nodebasisread.ts` |
| The tests reading the four docs | 0 | |
| `tsc --noEmit`; `eslint` on the three files | 0 | |
| `finish_build.sh 355` (`bf673cde`): build | 0 | no statement timeout |
| `check-values` on `/cost-of-power/battery` and `/research` | 0 | 888 of 888 (the band's 72 keys among them) |
| `check-routes` | 0 | every page |
| `check-battery-face` | 0 | all passed |
| `check-battery-scenarios` | 1 | the one CAISO 2-hour failure production has too (session 352's report) |
| `check-findings-grids` | 1 | waits 30 seconds for "the small multiples" and stops; **the same on production** (run at 14:40 UTC). Not this session's |
| The probe at 390 | 0 | the battery page 390 within 390; the card page 390 within 390, its chart's right legend reaching 436 inside the chart's own box, **the same on production** |
| `check-table-downloads` | 1 | asked of pages with no downloads line: a mistake of the call |
| Impeccable `detect --json` | 0 | no finding |
| Shots, 1280 and 390 | 0 | `docs/brand/review-355/` |

After the build, one word fixed ("The q-values over the round", not "The q-value over the rounds"); the landing's build carries it.

## Landing

Below, with 352, 353 and 354: no landing from 14:00 to 16:15 UTC.

## Decisions made without you

- **The band is the spread, not the basis.** A battery earns from the spread between its dear and cheap hours; a node's basis moves both ends. The page writes the storage nodes' four-hour spread against the hub's and states the ratio at the median; the basis stays in the pack and the method note.
- **Weighted by the days held**: September 2026 holds 11 days of the day-ahead disclosure, so a plain mean of months would weigh them as a full month.
- **The statistics stay in the fold**, under the estimates, as a caveat beside the card; the card's sentence keeps HC1 (session 361's question for you stands).
- **The PNG renders are unchanged**: the renderer's frame does not draw the statistics.

## For Samuel's ruling

- Session 361's two questions, now visible on the page: whether a card should state the Newey-West error in its sentence where it moves a p across 0.05 (none does today), and whether the step flag should keep a draft from the review list.

## Files

- `site/app/cost-of-power/battery/page.tsx`, `site/lib/nodebasisread.ts` (new); `site/components/analysis/FindingCard.tsx`, `site/lib/findings.ts`.
- `docs/methods/battery_earns_algorithm.md`, `docs/methods/automated_analysis_findings.md`, `docs/reviews/packs/battery.md`, `docs/reviews/packs/research.md`.
- `tests/test_session355.py` (new).
- `docs/brand/review-355/` (shots).
