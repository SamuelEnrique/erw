# Session 523 report: EIA's nuclear outages by plant, 2007 to 2014

21 October 2026, from 20:37 UTC, on lab-desktop (the data machine), the first session of `queue/done/028-night-22-october-sources.md` (its trial run while chain 027's landing waited for its checks). Model spend USD 0.

## Read these first

- **`eia_nuclear_outages_facility_daily` now runs from 1 January 2007 to 21 October 2026**: 1,312,872 rows, 66 plants, all 7,234 days. Session 516 held 2015 on.
- **The connector reads two windows**, `WINDOWS` in `eia_nuclear_outages_facility.py`:
  - 2007 to 2014, with EIA's `end` parameter, which is 190,457 records;
  - 2015 on, open-ended, at the same address as session 516's saved pages, so those were reused.
  - The writer stays a snapshot: both windows are read in one run and written together.
  - A page past its window's end, a page out of day order, or a missing day anywhere (where the windows meet included) stops the run. `--from` and `--to` read one window.
- **Cross-check**: the plants' outage and capacity summed by day against `eia_nuclear_outages_daily`, EIA's U.S. total. They are equal on all 7,234 days, with the largest gap 0.0 MW.
- **Written under the data lock** (20:55 UTC) with `--offline` (0 requests). The validator, coverage and archive exited 0 (571,371 new rows archived). The table's release row was replaced from a fresh regeneration (`runs/release_replace.py`, on the data machine).
- **A fault of my write script, found and fixed**: `runs/write_table.sh` removed the connector it copied into the main checkout. Since chain 027's landing, `eia861m_sales.py` is on main, and the script had deleted it from the main checkout. Nothing was committed: the queue step's commit held only its move. The file was restored, and the script now puts a tracked connector back as main has it.
- Tests: `tests/test_session523.py`, 4; `tests/test_session516.py`'s reading test now names its window with `--from`.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 39 of 100 | 2007 to 2014 (the trial); 2015 on reused; the write 0 |

## Files

- New: `tests/test_session523.py`, this report. Changed: `warehouse/connectors/eia_nuclear_outages_facility.py`, `tests/test_session516.py`, `docs/redivis/release-v1/tables.csv`, `docs/coverage.md`, `warehouse/metadata/{coverage,archive_manifest}.csv`.
