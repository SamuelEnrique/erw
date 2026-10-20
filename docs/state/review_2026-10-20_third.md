# The third machine's night, 20 October 2026 (sessions 344 to 350)

Energy Research Warehouse (ERW). Samuel's personal laptop (`portable-laptop`), unattended, from about 07:45 to 10:20 UTC. Rulings: Samuel, 20 October 00:25, in chat: tool 17 (economic impact), phase one, and the project map, phase two. Model spend USD 0. **Nothing of this chain is on `main`** except session 344's queue file: the two branches below wait for the old laptop.

## What was built

| Session | What | Branch | Report |
|---|---|---|---|
| 344 | The old laptop's chain filed for the queue: `queue/next/010-night-20-october-code.md` (sessions 351 to 356), committed alone and pushed to `main` (`9cf0aea2`) | main | below |
| 345 | `nlr_jedi_multipliers`: NLR's JEDI models (wind, utility PV, gas, geothermal) read for every state by their own formulas; jobs, earnings and output per MW by technology, state, phase and effect; 5,562 rows, loaded (review_hold), drafted, archived; `docs/methods/economic_impact.md` section 1 | `wip/345-impact` | `archive/sessions/SESSION_345_REPORT.md` |
| 346 | `impact_tax_rules`: the /severance rules of TX, LA and NM as a table (42 rows, each cited) and seven property-tax rows that say **no rule held**; loaded, drafted, archived; the method's section 2 | `wip/345-impact` | `SESSION_346_REPORT.md` |
| 347 | `/impact`, "What a project does for a state", in review, in the Economics menu: three questions, every figure a checked Num (340 of 340); the review pack `docs/reviews/packs/impact.md` | `wip/345-impact` | `SESSION_347_REPORT.md` |
| 348 | `iso_queue_statistics`: the six queues by entry year (1,511 rows), with each ISO's status words stated; loaded, drafted, archived; the LBNL cross-check | `wip/348-map` | `SESSION_348_REPORT.md` |
| 349 | The map, phase two: positions placed by a city or a town (355 of 710 by measurement), the card's generator link, the Queues tab, the daily rebuild of the map's copy | `wip/348-map` | `SESSION_349_REPORT.md` |
| 350 | This note | `wip/348-map` | |

Screenshots: `docs/brand/review-347/` (the impact page, three views, 1280 and 390) and `docs/brand/review-349/` (the map's Queues and Projects tabs, 1280 and 390).

## The landing order, for the old laptop

1. **`wip/345-impact`** (sessions 345 to 347): merge origin/main first, then the landing gate (freeze status, snapshots before and after, the full check-values, check-routes). The four `/impact` addresses are new in check-values' list and have no floor yet.
2. **`wip/348-map`** (sessions 348 to 350): made from `wip/345-impact` and merged with it again after 347's last commit, so once the first has landed it holds only its own three sessions. The same gate; the three `/map?tab=queues` addresses are new in check-values' list.

Expect merge work in the shared metadata files (`coverage.csv`, `docs/coverage.md`, `sources.csv`, `live_set.yaml`, `license_*.csv`, `docs/licenses.md`, `site/data/license_status.json`, `archive_manifest.csv`, `redivis_uploads.csv`), which the data machine also wrote tonight: each side's rows are to be kept; the generated files are rebuilt by their own scripts after the merge (`build_coverage.py`, `licenses.py write` and `status`) rather than merged by hand.

## Every "To finish"

- **Session 345, 346, 348:** none for the tables themselves: each is in Supabase (review_hold), in its Redivis draft and in the archive. The Redivis drafts are not released (a person's click).
- **Session 347** (the code machine): Impeccable `detect --json` on `site/app/impact/page.tsx`, `site/app/impact/StateChart.tsx`, `site/lib/impact.ts` (Impeccable is not installed on this machine); the landing's full check-values with `CHECK_VALUES_WRITE_FLOOR=1` once it passes in full, so the new pages get their floors.
- **Session 347** (the data machine): `warehouse/redivis/release_v1.py` to add the two new tables to the release-v1 package (`tests.test_session275` fails until then). It was not run here: this machine holds only some tables, and its run would have dropped most of the package (reverted at once).
- **Session 348** (the data machine): its next `load.py` settles the `sources` mismatch (Supabase holds `erw:price_years`, loaded by the data machine tonight, which these branches' `sources.csv` lacks until they meet main).
- **Session 349** (the data machine, the desktop): nothing by hand: its daily run now has the step `dm_project_map` (`warehouse/run_data_machine.sh`), and `energy_projects` places positions by place with the code of this branch once it is landed.
- **Session 349** (the code machine): Impeccable `detect` on `site/app/map/page.tsx`, `QueuesView.tsx`, `QueueCharts.tsx`, `ProjectMap.tsx` and `site/lib/projectmap.ts`.

## Decisions made without Samuel

- **Session 344:** the queue file is named `010-night-20-october-code.md`, not the prompt's `010-code-night-20-october.md`: `scripts/chain_queue.py` skips every name that begins `NNN-code-` (the task queue's names), so the old laptop's queue step would never have taken it. The contents are the prompt's section exactly; `chain_queue.py list` showed it waiting.
- **Session 345:** the table name `nlr_jedi_multipliers`; JEDI recalculated by its own formulas (pycel, in `.venv-jedi`, outside git; pycel pins networkx below 2.7, so it could not join `.venv`: installing it there first downgraded networkx, which was put back at once); utility PV as the PV model's own Utility option; the wind workbook W9.14.18, not the Beta program; the effect part of the row; three new units (Decision 48); tier derived.
- **Session 346:** the events shape; severance not computed for a plant; the sources registered public and the table "not settled" until their terms are read.
- **Session 347:** a plain GET form; capital cost and local content as percents of JEDI's defaults (the local content one factor per phase, the page's one approximation, said); no default life; the tax table not offered for download; the state chart's 16 places with every state in a table; the project MW and local shares added to the JEDI table as rows (the live set's series keep no `x_` columns).
- **Session 348:** inputs from the archive's copies (this machine's were 19 days old); the branch from `wip/345-impact`; the withdrawal rate by count; no "all years" row.
- **Session 349:** one precision word `place` for both gazetteers; the county first, a shared name never; no table or map file written here; a gas unit linked only as a peaker by its own words; the Queues tab opens on CAISO.

## What waits for Samuel

1. **The impact pack's ten questions** (`docs/reviews/packs/impact.md`, part 9): the four tax publishers' terms; pulling the property-tax statutes (TX chapters 312 and 313, LA ITEP, NM IRB); a default life; severance on a gas plant's fuel; utility PV as JEDI's Utility option; the wind release; one dollar year; the local content lever exact or approximate; more JEDI models; IMPLAN's multipliers behind the results.
2. **Session 349:** whether the resources tool should count a position placed by a place (today it stays "not drawn" there).
3. **Session 348:** ERCOT's withdrawn positions would need ERCOT's past GIS reports (a pull), if wanted.

## Session 344's report

- Precheck passed (`portable-laptop`, a data machine). The file was written with the prompt's section exactly, from its first "# Chain" line to its last; no em dash; committed alone with the message "Queue: the code machine's chain of 20 October, night (sessions 351 to 356)"; `git pull --no-rebase` then `git push origin main`: accepted at the first push (`0c5c5042..9cf0aea2`). A push to `main` deploys: the commit adds one file under `queue/next/` and changes nothing a page reads, so no snapshot was taken (the chain's prompt named this one commit as the exception to "no landing on main").
- The name above, under "Decisions made without Samuel".
