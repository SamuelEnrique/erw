# Session 3060: chain 166's seventh session (its 2266): the monitor's table

Personal laptop, second window, 6 November 2026, 12:25 to 13:05 UTC (begun while session 3059's tests ran). Opus 5.5. Branch `wip/3060-policy` cut from `wip/3059-policy`.

## What it did

- `warehouse/policy/monitor_site.py` (new): the monitor's one data file, `site/data/policy/monitor.json`, one row a proceeding (the records of session 3057) with body, instrument, status, sector, grids, states, highest significance, next step, figure, impact sentence, plain read, the table it bears on, sources and history. Built here from this laptop's tables: 2,020 documents, 1,495 records, 1.24 MB. A daily soft step (`policy_monitor_records`, after `policy_monitor_site` in `warehouse/run_daily.sh`), never a thinner file.
- `warehouse/policy/impact_reads.csv`: session 3058's reads, kept beside the code as `scores.csv` is, read by the builder.
- `site/lib/policymonitor.ts` (new): the filters (body, instrument, status, sector, grid, state, date range, significance), the sort on every column (an empty value last), the choices with counts, the address of a set of filters, the CSV of the filtered rows with every source.
- `site/app/policy/MonitorView.tsx` (new) and `/policy?view=monitor` (a third view in `site/lib/policyweek.ts`'s `VIEWS`): filters left, results right; the evidence of the next step and the figure and the quotation of the impact sentence as hovers; "N shown of M records held"; a row opens to its proceeding, history and sources.
- `warehouse/policy/fields.py`: the status rule tightened (below).
- Tests: `site/scripts/test-policy-monitor.mjs` (37), `tests/test_policy_monitor_site.py` (3); three older tests updated for the third view (`test_session157_page.py`, `test_session332.py`, `test_session241a.py`), and `test-policy-week.mjs`.

## What it found

- **Building on the whole table found a status fault**: 49 records read "withdrawn", of which about 21 were not (BLM's "Reinstatement of Terminated ... Lease", a Public Land Order's land withdrawal, "Proposed Termination", a meeting on a termination plan); "Motion To Vacate" and "Partial Vacatur" asked for read "vacated"; "Stay Informed" read "stayed". Fixed: 28 withdrawn now, none vacated or stayed on this copy of the table.
- On this laptop's copy (no printed texts held here) the fields come from the summaries (1,752 rows) or titles (268): 36 records carry a dated next step and 212 a figure. The data machine's run, with its texts, gives more.
- Tests: Node `test-policy-monitor.mjs` 37 of 37, `test-policy-week.mjs` 90 of 90; Python, every test file that names policy: 1,034 passed, 24 skipped, then the one failure (the wrapper count) fixed and its file 17 passed.
- Not built, not type-checked: this laptop's `site/` has no `node_modules`, and this window never builds. The gate's build is the first.

- **Five files of this chain held the em and en dash characters** (`impact.py`, `monitor_site.py`, `test_policy_impact.py`, `test_policy_monitor_site.py`, `test-policy-monitor.mjs`): the editing tool wrote the escapes `—` and `–` that their dash checks name as the characters themselves. Each is now the escape, written as text; the tests pass the same.

## Decisions made without you

- **A third view of `/policy`, not a new address**, so `site/lib/release.ts` stays untouched and the monitor is in review with the page.
- **The data file is in git** (the daily workflow's commit step already adds `site/data/policy`), built here from the archive's copy of the tables; the first daily run after the landing rebuilds it from the day's.
- **300 rows listed**, the rest through the filters or the CSV (the old table lists 400 actions; a record is wider).
- **The pushes to main of this chain are docs and queue files only** (the take, the next file, the landing request): no page reads them, so no snapshot was taken, as for every chain's queue push.

## For Samuel's ruling

- Whether the monitor should become the page's first view once you have read it.

## Cost

- Model: none (USD 0.00).
