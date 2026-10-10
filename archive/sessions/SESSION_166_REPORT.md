# Session 166 report: the data fresh for 11:00, and the health gate open

Run on 9 October 2026 (UTC), 06:31 to about 08:15, then paused, then 22:05 to the end, unattended, first of the chain
166 to 171 (`CHAIN_OCT8_PROMPT.md`). Parts A to E were built in the main copy; part F by an agent in a working copy
(`runs/session166/BRIEF_F.md`, its report `runs/session166/agent_report_F.md`).

## Read these first

- **The deploy cutoff was missed, and nothing of the chain's page work reached production.** The account's weekly usage
  limit paused this session from about 08:15 UTC to 22:00 UTC (it also cut session 170's agent off mid-build). Sessions
  166, 167, 168 and 169 were handed over by 07:40 UTC and the landing was being prepared when the pause came. The one
  thing that did reach production before the meetings is the data: the live set was loaded at 08:10 UTC.
- **The live set is current.** 72 tables loaded and matched; every live-set table is at least as fresh as this machine
  (`runs/session166/live_after.csv`); `eia930_all_demand` reaches 8 October 23:00 UTC. Ask ERCOT on production answers
  "yesterday" from the newest whole Central day, 7 October: 73,194 MW (asked 22:05 UTC, two model calls, USD 0.153, charged
  to session 168's Ask ERCOT cap of USD 0.50; session 166's own cap is USD 0 and no other model call was made).
- **The loader's root cause:** every API statement runs under the authenticator role's 8-second `statement_timeout`; the
  paged read of `ercot_as_prices` (336,692 rows, 337 ordered pages with a growing offset) and the unindexed sort for its
  newest `retrieved_at` crossed it on the runner on 5, 6, 7 and 8 October ("canceling statement due to statement timeout",
  then "JSON could not be generated"). The whole-table reads now go through the direct Postgres connection with a
  600-second timeout; the API path stays as the fallback.
- **Why nobody was told for four days:** the load ran outside `warehouse/health.py`, so its failure was a word in the
  commit message and never a row of `erw_health`, which is what the same-day failure email reads. The load now runs under
  `health.py run --strict --step supabase_load`: the gate chosen is the health summary plus that email.
- **The health gate is still closed** (`build_status.py --gate` exit 1): it reads the latest GitHub run, 9 October's,
  which ran main's old code (grid_network and the SPP day failed there again). It opens with the first daily run after the
  landing, if the network build passes there.

## What to review (after the landing; everything is on `wip/166-health`, nothing is on production yet)

1. `https://erw-flame.vercel.app/ask/ercot` (internal view): ask "What was ERCOT's peak demand yesterday?"; the answer
   names the newest whole Central day and its peak in MW, with a date no older than two days.
2. `https://erw-flame.vercel.app/board`: the "built" line at the top reads 9 October 2026 or later; ERCOT's ancillary
   service rows (REGUP, REGDN, RRS, NSPIN, ECRS) show values; click any row to open the workbench.
3. `https://erw-flame.vercel.app/supply`: the petroleum rows read the week of 2 October (EIA's report of 7 October) and
   gas storage the week of 2 October (the report of 8 October).
4. `https://erw-flame.vercel.app/cost-of-power/battery`, `/network`, `/storage` as a visitor (a private window): each
   shows the in-review page; in the internal view each opens as before.
5. `https://erw-flame.vercel.app/datacenters` (internal view): the Status filter holds cleaned words only (no
   "inDevelopment"); the first card reads 251 US rows not cancelled, 18,274 MW stated by 19; the Country filter's
   "country not stated" shows Firmus's two rows, which are on neither bar.
6. `https://erw-flame.vercel.app/datacenters/v2`: "374 datacenter sites: 255 in a named US state, 39 of those in Texas,
   and 119 with no US state stated, sites outside the US among them".

## A. The live set

- Diagnosed from the runs' artifacts (`runs/session166/art1005` to `art1008`): the loader failed on `ercot_as_prices`
  every day from 5 October, and on `ercot_hub_prices_daily` on 5 and 7 October, always after a timed-out
  older-than-live check. Locally the same paged read took 133 s (337 pages of 0.3 s); the runner's pages hit 8 s.
- `warehouse/supabase/load.py`: `db_reader()` (the direct connection, `SUPABASE_DB_URL`), `existing_rows` as one
  SELECT with no ORDER BY and no OFFSET, `live_count`, `older_than_live` through `max(retrieved_at)`; a dropped
  connection fails one table and is reopened. Tests: `tests/test_session166.py` (12).
- The load from this machine at 08:00 to 08:09 UTC (after `scripts/sync.py` restored 47 tables behind the cloud and
  refreshed 2 snapshot tables, 0 failed): 72 tables matched; **19 refused by session 60's guard as older than the live
  copy** (`ai_power_regions`, `battery_stack_monthly`, `caiso_interconnection_queue`, `carbon_intensity_monthly`,
  `eia860m_retired_generators`, `eia_retail_sales_monthly`, `eia_sector_energy_consumption_monthly`, `energy_projects`,
  `ercot_as_prices_monthly`, `ercot_interconnection_queue`, `ercot_storage_dam_awards_monthly`,
  `ercot_storage_dam_offers_monthly`, `ferc_eqr_contracts`, `iso_curtailment_monthly`, `isone_interconnection_queue`,
  `price_board_carbon`, `spp_interconnection_queue`, `storage_buildout_monthly`, `storage_capacity`). The runner
  re-retrieves them daily, so the live set holds its newer copies (retrieved 5 to 8 October); the sync shows the same
  rows and newest timestamps for 17 of them; `energy_projects` and `ercot_interconnection_queue` are bigger here (the
  MISO queue is on this machine, not the runner) and were left as the live set holds them.
- Newest timestamp before and after, the tables a page reads that moved: `eia930_all_demand` 2026-10-07 23:00 to
  2026-10-08 23:00 (ERCOT's 5 and 6 October UTC days are gaps in EIA's forecast series and stay out, per day);
  `ercot_hub_prices_daily` 10-08 to 10-09; `iso_rtm_hub_prices` 10-08 06:45 to 10-09 06:45; `iso_dam_hub_prices` 10-09
  06:00 to 10-10 06:00; `storage_daily_cycle` 10-07 to 10-08; `weather_obs_hourly` 10-08 13:00 to 10-09 13:00;
  `datacenter_facilities` 374 rows with the new `country` column; the 19 above unchanged. Full table:
  `runs/session166/live_before.csv` and `live_after.csv`.
- Every page that reads Supabase: `check-values` against production at 22:12 UTC, 6,925 of 6,925 values match.

## B. The price board

- Two faults on the runner: `board_page.py` opened `ercot_as_prices.csv` before the connector that writes it (the table
  is not restored from the draft), and `refresh_board.sh` validated `carb_lcfs_credit_prices.csv`, never on the runner,
  so "board validate" failed every day with the validator's exit 2.
- Fixed: the board step runs after the ancillary service connectors; the builder skips an ancillary service table not on
  the machine (NYISO's and SPP's are held out of the runner) and `page_keep.py` keeps the held rows, so the board is
  never thinner; the validate step lists only the files present.
- Refreshed here under the lock at 07:20 UTC: 794 rows, 740 with values, all from this build, 0 kept. Nothing else on
  `/board` changed (session 168's placeholder is its own commit).

## C. Supply and trade

- `warehouse/refresh_supply.sh` at 07:20 to 07:36 UTC under the lock: 100 rows, 92 with values, all from this build.
  One step failed and was recorded: `ercot_zone_load` ("the operator answered no hour"), retried once, the held rows kept.
  The Saturday schedule stays.

## D. The health gate

- `wip/held-grid-network` (session 149's fix of the daily grid network build, failed since 4 October) is merged in.
- `test_large_table_by_partition[ercot_dam_esr_awards]` failed because this machine's table was behind the cloud's
  (1,833,357 rows against coverage's 1,865,325); the sync restored it and the test passes. No code change.
- `carb_lcfs_credit_prices` is in `known_gaps.csv`, "decided: Samuel, 8 October 2026".
- SPP's real-time market now runs under session 13's per-day rule (`per_day=True`); the row of 8 October's run for 7
  October was rewritten as a gap day on the owner's ruling (`run_status.csv`, one row).
- `build_status.py --gate`: exit 1 at the end, as said above; expected to open after the next GitHub run on the landed code.

## E. No page live

- `site/lib/release.ts`: `/cost-of-power/battery`, `/network`, `/storage` are `review`; a test holds that no line is
  `live`. 20 tests that pinned the three live pages, `/map/v2` or `/network/v3` are being brought to the ruling
  (`runs/session166/tests_fix/report.md`).

## F. Datacenter data errors (the agent's part; `runs/session166/agent_report_F.md`)

- The Status column and filter read the cleaned `status` (planned 60, operating 30, withdrawn 7, under construction 5,
  completed 1, active 1, empty 270 of 374).
- The Utah 9,400 MW row was joined upstream, in the news extractor's `same_as` (accepted without a check), not by the
  facilities dedup; `same_site` now requires the same operator or developer, site name, or county or city in the same
  state. The held row stays one row until the next model extraction (no model call tonight). Trial against the held
  table: 374 rows both ways, 0 split, 0 merged, 0 MW or status changed; a new `country` column (US on 255, empty on 119;
  `geo` "US" corrected to "" on those 119). No source records a country.
- Totals and both bars count US rows not cancelled (251 rows, 18,274 MW by 19; before 25,320 MW by 31); Firmus's two
  rows stay in the table, out of every total.
- Report only, unchanged: `datacenter:nyiso_queue-1630` (Suffern Quarry Data Center) stands in the public
  `datacenter_facilities` and `datacenter_queue_positions` while `nyiso_load_queue` is held internal
  (`docs/methods/datacenter_cost.md`, "New York's load in line").

## Pulls and spend

- Pulls: the daily connectors' usual requests only: EIA-930 (the last six UTC days, every BA), the board's six small
  series, the supply refresh's reports, the facilities builder's two gazetteer requests. No new host.
- Model spend: USD 0 by this session's code; the one Ask ERCOT check, USD 0.153, against session 168's cap.

## Checks

- `tests/test_session166.py` 12 tests, `test_session166_datacenters.py` 9: exit 0. The validator on every table
  (198): exit 0. `npm run build` of the merged tree in the main copy: exit 0. The whole suite in a clean copy: at
  `0261d49` 20 tests failed, all pinning the old live pages or the old map and network addresses
  (`runs/session166/suite_clean.out`); after the fixes of E, at the pushed commit `5c7c7b5`: 2,660 tests, OK, 226 skipped
  (`suite_clean2.out`). `check-values` against production: 6,925 of 6,925.
- The one local commit main held before the chain (`859ee58`, the reports of 162 to 165) is the base of `wip/166-health`
  and reaches `origin/main` with its landing. The main copy is left checked out on `wip/166-health`.

## Decisions made without you

1. The 19 tables the guard refused were left as the live set holds them (the runner's newer copies), not rolled back
   with `--allow-older`.
2. The Redivis draft upload was skipped: `upload.py --changed` would upload 131 tables from this machine's stale
   manifest, an hour under the lock; the daily run re-pulls the same days itself and the archive holds every row
   (112 tables archived, 1,407 rows, at 22:14 UTC after the merge of main).
3. Two stray tables of session 130 (`power_deals.csv`, `power_deals_evidence.csv`, written 6 October by
   `warehouse/deals/extract_v3.py`, which is not in git, in no coverage) stopped `build_coverage.py`; they were moved
   to `runs/session166/stray/`, not deleted.
4. The daily run's commits of 9 October were merged; the runner's coverage, sources and archive manifest were taken,
   and coverage rebuilt for the facilities table.
5. The board step moved after the ancillary service connectors in `run_daily.sh` (a small reorder, so the runner's
   board carries ERCOT's reserve prices of the day).

## To finish (the landing of sessions 166, 167 and 168, from the main copy, outside 14:04 to 16:10 UTC)

```
cd C:/Users/lossa/Documents/erw
git fetch origin
git checkout wip/166-health
git merge origin/main                                   # if main moved; resolve, then rebuild under the lock as in this report
python scripts/freeze.py status
cd site && npm run build; echo "exit=$?"; cd ..          # must print exit=0
node site/scripts/snapshot-live.mjs take 166_before     # its own command; read "take exit=0"
git push origin wip/166-health:task/166-168-chain
python runs/gh_api.py wait task/166-168-chain 15
python runs/gh_api.py deploys                           # "success" for the merge commit
node site/scripts/snapshot-live.mjs take 166_after
node site/scripts/snapshot-live.mjs compare 166_before 166_after
```

Expected in the comparison: the three pages answer the in-review page to a visitor (every number of theirs leaves the
visitor view); `/network` shows version 3; `/board` and `/supply` show 9 October's rows; the 42 checked numbers of the old
network page are gone with its table. Anything else is unexpected and to be reverted.

## Landing state (added by the chain's session 172 at 02:15 UTC on 10 October 2026)

- **Landed.** `wip/166-health` (`4ab8587`) was pushed as `task/166-168-chain` at 01:40 UTC on 10 October 2026, checks run 38014071454 passed, main holds the merge `551ba12`, Vercel's production deployment completed at 01:49:20 UTC. Snapshots `166_before` and `166_after` (`runs/session172/compare_166.out`): 25 pages, 5,726 differences, every one expected (the three live pages now answer the in-review page to a visitor, 3,357 checked numbers left the visitor view, the menus read "in review"); 0 numbers changed, 0 statuses changed. `check-routes` against production: pass 2, 0 failed. Ask ERCOT on production at 01:58 UTC: correct for what the live set holds (the 9 October daily run's load failed on main's old code, so the live set is as this session loaded it at 08:10 UTC on 9 October). Details: `archive/sessions/SESSION_172_REPORT.md`.
