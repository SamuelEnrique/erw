# Session 2302 report: the two ERCOT data-center positions, matched by operator name in the read layer

23 October 2026, about 20:29 to 20:40 UTC, unattended, on portable-laptop (the code machine). Chain `queue/done/087-day-23-october-portable-map-tracker.md`, session 2302. Model Fable 5.1. Precheck 0. Model spend USD 0. No warehouse data written; no request but GitHub and the ERW's own database (one read of the live set, and the probe). Code in the worktree `C:\Users\samen\Documents\erw-2302` on `wip/2302-map-tracker`, stacked on `wip/2301-map-tracker` (neither 2300 nor 2301 has landed).

## Read these first

- **The tracker's power side will show Bullock Gas and Liberty Thermal Energy Center.** `queueSites` (`site/lib/data.ts`) matched the builder's pattern against a queue position's name and fuel field; it now reads the operator too (`QUEUE_SITE_FIELDS` in `site/lib/datacenter/bygrid.ts`), so a position whose only data-center word is its owner's name (Bullock Data Center, LLC; Liberty Data Center I, LLC; 1,400 MW of combined-cycle each, Hill County, Texas) is a site a public source names. Which field named a site is kept on the row (`extra.matched_by`, from the pure rule `queueSiteMatch`), and a row named by its operator alone says so under its name, with a hover saying the derived table `datacenter_queue_positions` follows at the data machine's next run (session 2102's review). The pattern's words are unchanged; the derived table is unchanged; no warehouse row is written.
- **The live set holds both rows** (one read, 20:31 UTC): `ercot_queue:33INR0005` and `ercot_queue:33INR0006`, vintage 2026-10-19, 1,400 MW each, Hill County, TX, active, queued 2026-06-12, proposed in service 2032-07-01; ERCOT's queue holds 1,758 rows in the live set. After the landing the power side shows 4 ERCOT positions (the 2 it showed, and these 2); the grids view's ERCOT row counts 4 sites and 5,600 MW asked more than before (its `dcq|` keys are recomputed by `check-values.mjs` over the same three fields, so the checker and the page agree).
- **A test on fixtures** (`site/scripts/test-queue-sites.mjs`, 16 of 16): the two rows as the review prints them match by the operator; a row matched by its name; one by its fuel field; a solar row with "load" in its point of interconnection does not match; the readers use the same fields. The two Python tests that read the pattern (`test_session467`, `test_session468`: 17 tests) pass.
- **The map's queue marks do not change** (`data/map.json` is the data machine's build) and `datacenter_queue_positions` does not change: both for the desktop's chain, as session 2102 wrote.
- **Not built, not landed.** The probe took 5.60 s and the build lock was held by chain 086's session 2203; free memory 2.5 GB. The gate's commands are under "To finish".

## What to review (on a build of `wip/2302-map-tracker`, in the internal view)

- `/datacenters`, "On the power side: the sites a public source names": four ERCOT rows; Bullock Gas and Liberty Thermal Energy Center carry "named a data center by its operator's name" under the site; hover the site for the words on the derived table.
- `/datacenters?view=grids`: the ERCOT row's "Sites" and "MW the sites ask to connect".

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2302"` | 0 | on duty |
| `node --import ./scripts/alias-register.mjs scripts/test-queue-sites.mjs` (new) | 0 | 16 of 16 |
| `node --import ./scripts/alias-register.mjs scripts/test-map-sources.mjs` | 0 | 43 of 43 (the stack's earlier test still passes) |
| `python -m unittest tests.test_session467 tests.test_session468` (in the worktree, the main checkout's interpreter) | 0 | 17 tests OK |
| `eslint` on the changed files | 0 | 3 warnings, all pre-existing in `check-values.mjs` (lines 1213 and 1260, not this session's) |
| `tsc --noEmit`, this session's files | 0 errors | |
| the live set, one read (`entities`, `ercot_interconnection_queue`, operator matching the pattern) | 200 | the two rows, vintage 2026-10-19; 1,758 ERCOT rows |
| `scripts/db_probe.py` | 1 | 5.60 s: no build this session (and the build lock held by `s2203`) |
| free memory | | 2,499,204 KB after the tests |
| `scripts/db_probe.py`, again at the report | 1 | CLOSED 3.25 s 1000 rows of iso_dam_hub_prices (free memory then 2698328 KB) |
| `scripts/check-datacenters.mjs` (a served site) | not run | extended: reads the live set for the operator-named positions and asserts each is on the power side marked `data-matched-by="operator"`; says "skip" when the live set cannot be read or holds none |

## The landing

Not run. The branch is pushed. Session 2303 stacks on `wip/2302-map-tracker`.

## Files

- `site/lib/datacenter/bygrid.ts`: `QUEUE_SITE_FIELDS`, `QueueSiteField`, `queueSiteMatch`, `matchWords`.
- `site/lib/data.ts` (`queueSites`), `site/app/datacenters/PowerSide.tsx` (the site cell), `site/scripts/check-values.mjs` (the `dcq|` recomputation over the fields), `site/scripts/check-datacenters.mjs`, `site/scripts/test-queue-sites.mjs` (new).

## Decisions made without you

1. The operator is the third field read, after the name and the fuel field, so a row matched by its name is still said to be matched by its name; the pattern's words are not widened (session 2102's wider pattern found only two solar rows with "load" in a substation's name, which the fixture test now forbids).
2. `check-values.mjs` was changed in its `dcq|` branch alone, so the keys the grids view carries stay checkable; `tests/test_session468` still finds the pattern there.
3. The match is kept in the row's `extra` under `matched_by` rather than a new column of the row type, so no other reader of `EntityRow` changes.
4. The sentence under an operator-named site is the page's words; the review's CSV block for the data chain stands as it was.

## For Samuel's ruling

- None from this session. (The derived table's one-field change is the desktop's, listed in `docs/state/review_2026-10-28_portable.md`, "To finish".)

## To finish (the gate)

From the main checkout, each its own command, its exit read, on a probe under 3 s and a free build lock: `.venv\Scripts\python.exe scripts\land_check.py --ref wip/2302-map-tracker --lock-as s2302 --port 3302`, then the commands it prints. When 2303 and 2304 stack on this branch, the last branch's gate carries this work.
