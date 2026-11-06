# Session 2885 report: the note, the next file, the landing, the queue

6 November 2026, about 01:48 to 03:05 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: GitHub only.

## Read these first

- **The note:** `docs/state/note_2026-11-06_data_c147.md`. The name the chain gave, `note_2026-11-06_data.md`, is chain 058's note, and it was not overwritten.
- **`queue/next/148-...` updated on main:**
  - `765a80d55`: its sessions 2886 to 2888 take this chain's unfinished steps (the Ask evaluation's rest; the tariff registry for the tab's rows' utilities and the named ones not reached; the wiring and the run's catch-up).
  - `0d0e41e66`: session 2888 also takes session 2875's connection rules.
  - Its sessions 2889, 2894 and 2899 now start from the tables already held. Its successor takes the first number after the code machine's 149 and 150.
  - Rule 8's snapshots around both pushes: 0 differences.
- **This chain's branch `wip/c147-data` landed as `a41dd2e41`** (task/c147-data, run 42152196214, checks passed 03:00 UTC; deployed 03:03). Its gate's third round: suite 7,623 OK, npm ci, build and serve passed; check-values had 2 failures, both known (the `/deals` and `/learn/problems/know-your-grid` floors); 7,743 of 7,743 values matched. The first two rounds failed on the license record, the release package and the runner's thinned page files, repaired below. Freeze: none. Snapshots `s2885-before` (02:44) and `s2885-after` (03:03): 25 pages, **0 differences**.
- **The queue step:** `chain_queue.py next` from the main checkout, pulled first, took `148-day-6-november-data-large-load-continued.md` (the code machine's 150 was left for it). 148 is run next, the same way.

## Repairs made before the landing

- **The license record:** the daily run added `ercot_wind_solar_hsl_monthly` to coverage without a `license_tables.csv` row, so `test_session505` failed. `licenses.py tables/write/check` were run (632 tables, 0 problems) and the package's tables rebuilt.
- **The release package:** `release_v1.STORAGE_HELD` now holds `utility_large_load_tariffs` (unsettled, refused by the uploader) and `ercot_wind_solar_hsl_monthly` (not on Redivis) from v1, so v1 holds 136 tables, and the steps document and README say so. 1,274 release tests pass. Session 2871's two release rows had not changed the steps document's count; that was my error, found here.
- **The page files the runner's catch-up run thinned:** 164 files under `site/data/mix/`, `site/data/board.json`, `site/public/board/` and `site/data/curtailment_profile.json` were put back as `e2794ff0`'s parent had them. The runner had rebuilt them from tables shorter than the history: CAISO's mix lost 2019 and 2020. Tests 94, 98, 133, 1118 and 1139 pass again (113 tests).
- **This chain's tables held from the catalogue** (`live_set.yaml` `catalogue_hold`) until they are in the public Redivis draft (`test_session410`). `subregion_demand_growth.py` now reads with `header_rows` (`test_session103`).

## Decisions made without you

- **The thinned files put back,** not left for tomorrow's run to fail on. Each is generated; the earlier build was from the full history.

## Files

- On `wip/c147-data`: the note, this report.
