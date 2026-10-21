# Session 494 report: FERC Form 714 hourly demand, 2006 to 2022

21 October 2026, from 18:39 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/022-evening-21-october-sources.md`, run after session 489 under the data lock. Model spend USD 0.

## Read these first

- **17 yearly tables, `ferc714_area_demand_2006` to `_2022`**, written by `ferc714_demand.py --from 2006 --to 2022` under the lock (18:39 to 18:41 UTC). PUDL's core parquet, saved by session 484, was reused: no request.
  - 17,188,254 rows in all, from 91 to 177 respondents a year (2006 has 175, 2021 has 99, 2022 has 91).
  - 2006's first hour is 04:00 UTC, as filed: no hour is filled.
- **With 2023 to 2025, FERC Form 714 is held from 2006 to 2025: 20 tables, about 19.5 million rows.** The files take 5.7 GB on the data machine (`warehouse/output` is not in git).
- **The gates**:
  - the validator exited 0 (values 0 to 147,716 MW in these years);
  - `build_coverage.py --only '^ferc714_area_demand_(200[6-9]|201\d|202[0-2])$'` exited 0;
  - `archive.py write` exited 0: 17 tables, 17,188,254 rows, 0 failed.
- **A merge fault, caught before the push.** The backfill's metadata rows were applied as a patch onto session 489's rows. Both sides had added lines at the same place, and the first commit held the conflict markers. It was undone at once (`reset --hard` of that one commit, never pushed). It was then resolved by `runs/s494_resolve.py`:
  - the earlier years go first;
  - PUDL's source row names all 20 tables.
  - `licenses.py check`: 241 tables, 0 problems.
- No table of this chain is in the live set. Nothing was uploaded to Redivis.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| s3.us-west-2.amazonaws.com | 0 of 2 | PUDL's parquet reused |

## Decisions made without you

1. 2006 to 2022 as yearly tables, the same as 2023 to 2025, and internal under the same license as session 484's tables until you rule on FERC's terms.

## For Samuel's ruling

- Whether the 20 FERC 714 tables (about 5.7 GB of CSV) go to Redivis. Their archive copy is in the bucket.

## Files

- Changed: `docs/coverage.md`, `docs/licenses.md`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`. New: this report. `runs/s494_resolve.py` stays on the data machine (`runs/` is not in git).
