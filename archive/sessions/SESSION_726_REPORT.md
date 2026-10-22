# Session 726 report: the utility's path, fixed

22 October 2026, from 14:06 UTC, on portable-laptop, unattended, in the worktree `C:\Users\samen\Documents\erw-726` on `wip/726-allgrids` (cut from `wip/725-allgrids`). Chain `queue/done/062-day-23-october-code-allgrids-2.md`, session 726. Model spend USD 0. No warehouse data written; no request to a publisher. The database was read only by the site's own pages on the local build and by check-values' recomputation; the tab reads none.

## Read these first

- **The three faults of session 725's walk are fixed**, each inside this chain's files, each with a test (`tests/test_session726.py`, 5 tests), and the failed steps walked again on a build (`docs/reviews/siting-utility-path.md`, the "After" column and its last section):
  1. **Each utility figure says its basis under it** ("bundled; Harris County, TX", "delivery only; New York County, NY", "energy only; the state's stand-in (MA)"): EIA-861's service and whether the seller is the row's county's or the state's stand-in (`utilityBasisWords` in `lib/siting.ts`; sans, captions size, by a rule in `tokens.css`). The sort line, when the sort is the utility's figure, says what the column compares.
  2. **The rule's document is a link** beside the rule's words ("document", opening in a new tab, with an aria label naming the regulator and docket): 31 on the page, the PUCT's docket 58481 for ERCOT's rows, FERC's orders for CAISO's and NYISO's.
  3. **The A and B panel's utility row carries a tip** with each side's basis ("A bundled; Harris County, TX; B bundled; the state's stand-in (TX) ... alike only when both are the same service and the same kind of seller").
- **No figure moved, none added**: check-values on every cost-of-power address of the build, 2,705 of 2,705; check-existing-tab, production against the build, every figure the same.
- **The data corrected two of my test's expectations**: TXU Energy Retail's rows are bundled in EIA-861 (not energy only, as I had guessed from its name), and PJM's row is placed in Allegheny County by session 718's hub counties (so it has a basis). The test now asserts what the files say.

## What to review

After the landing (session 730), on `https://erw-flame.vercel.app` after `/internal/open`:

1. `/cost-of-power?view=allgrids&mw=1000&sort=utility&grid=ercot`: the basis under each utility figure and the sort line's added sentence.
2. `/cost-of-power?view=allgrids&mw=1000&sort=connect&dir=asc`: "document" beside each rule; click one (a new tab).
3. `/cost-of-power?view=allgrids&mw=1000&sort=utility&grid=ercot&a=ercot%3ALZ_HOUSTON&b=ercot%3ALZ_NORTH`: hover or Tab to "Utility" in the panel's first column.
4. Shots: `docs/brand/review-726/` (`before_*` from production; `03-utility-ercot_1280.png`, `07-rule-doc_1280.png`, `09-ab-zones_1280.png` and the 390 pair of each).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | on duty for "session 726" |
| `npm ci` in the worktree | 0 | |
| `tests.test_session726` with 724, 718, 708, 710, 716 | 0 (after the two expectations were corrected) | 29 tests, 2 skipped |
| `db_probe.py` | 1, then 0 | 3.38 s closed at 14:09; 1.65 s open a minute later |
| `npm run build` (lock `s726`, beat), three times (the fixes; the basis line's words; its stylesheet rule) | 0, 0, 0 | TypeScript clean |
| `walk-726.mjs` on the build, three times | 0 | 10 of 10 steps each, no page error, no page wider than 390 |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power`, `MSYS_NO_PATHCONV=1` | 0 | 2,705 of 2,705 |
| `check-existing-tab.mjs`, production against the build | 0 | every figure the same |
| em dashes in the changed files | 0 | none |
| the server stopped, the lock released | 0 | |

## The landing

Not in this session: at 14:22 UTC a full gate ends inside the no-landing window (14:00 to 16:15 UTC), so **the push waits for session 730**, the chain's next landing session ("Land 725 to 730 together"), which lands 719 to 730 in one push.

## To finish (for session 730)

- `python scripts/land_check.py --ref wip/730-allgrids --task 719-730-allgrids`, the snapshot before, the push to `task/719-730-allgrids`, the snapshot after, `compare`; then delete the merged `wip/` branches 721 to 730 on the remote.

## Decisions made without you

1. **The basis is written under the figure, not as a third figure**: words, no key, so the sort and the panel are read for what they compare while no value changes.
2. **The document link stands beside the rule's words** rather than inside the tip (a link inside a hover tip cannot be clicked, and the tip closes when the keyboard leaves its trigger).
3. **The state's stand-in is named as such** ("the state's stand-in (TX)") rather than "the state's largest seller in TX": shorter, and the tip holds the rest.
4. **The landing waits for 730**, as above.

## For Samuel's ruling

- Nothing new. Houston's and San Antonio's utilities (718's item) and the heavy-industry interruptions (702's item) stay as they were.

## Files

- Changed: `site/lib/siting.ts` (`SERVICE_WORDS`, `utilityBasisWords`), `site/app/cost-of-power/AllGridsView.tsx` (`UtilBasis`, the document link, the sort line, the panel's row head), `site/app/tokens.css` (one rule), `docs/reviews/siting-utility-path.md` (the After column, the 726 section).
- New: `tests/test_session726.py`, `docs/brand/review-726/` (the script, 10 shots, 10 before shots, two records), this report.
