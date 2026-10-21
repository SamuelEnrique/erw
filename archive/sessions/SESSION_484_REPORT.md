# Session 484 report: FERC Form 714 hourly demand by planning area

21 October 2026, from 16:48 UTC, on lab-desktop (the data machine), at the owner's instruction of 21 October ("probe and pull ... FERC Form 714 hourly demand ... through the erw-add-connector form; read each one's robots file and terms first"). Model spend USD 0.

## Read these first

- **FERC's own site refuses automated requests.** `www.ferc.gov/robots.txt` allows the paths (200, behind Cloudflare), but the Form 714 data page answers HTTP 403 from Cloudflare's bot protection, as FERC's terms page did in session 311. That is an access control, and it was not worked around.
- **The source is PUDL instead**: Catalyst Cooperative's Public Utility Data Liberation project republishes FERC Form 714 as open data. The table is `core_ferc714__hourly_planning_area_demand` of its stable release (14 October 2026), one 122 MB parquet on its public AWS bucket.
  - The host's robots file: `docs.catalyst.coop` allows every page (comments only, no rule). The AWS bucket has none (403), so the convention allows it.
  - The terms: PUDL's data-access page was read into the record (record 85, 200): "Copyright 2016-2026, Catalyst Cooperative, CC-BY-4.0." Its verdict is "may be public" (attribution), written to `license_verdicts.csv`; `docs/licenses.md` was written again (0 problems).
- **Only PUDL's core table, never its `out_` table.** PUDL's `out_ferc714__hourly_planning_area_demand` adds imputed demand where FERC's was missing or anomalous. The core table is FERC's filings as filed: 19,520,949 rows, 219 respondents, 2006 to 2025. Its 105,192 negative values are kept (an area can export more than it serves); a missing hour is absent.
- **The hour, checked against data**: PUDL's `datetime_utc` marks the hour's end (form hour 1 is T01). Against ERCOT's own system load for 2025 (respondent 58, 8,759 hours, `ercot_zone_load_hourly`), the mean difference is:

  | FERC's hours | Mean difference from ERCOT's load |
  |---|---|
  | one hour earlier | 1,184 MW on a mean of 55,734 |
  | as stamped | 2,717 MW |
  | one hour later | 4,176 MW |

  So `ts_utc`, the interval's start by the standard, is PUDL's stamp less one hour.
- **`warehouse/connectors/ferc714_demand.py`**:
  - yearly series tables `ferc714_area_demand_<year>` (about 780,000 rows a year): entity `ferc714:<respondent id>`, variable `demand` (MW), node the respondent's name, vintage the release file's time;
  - the sector rule (`power`) and `tests/test_session484.py` (6 tests);
  - landed as `ffc3b0c0`.
- **License `internal` until you rule.** PUDL's CC-BY-4.0 is read and FERC's filings are a U.S. government work, but FERC's own terms page could not be read. By the skill's rule (unconfirmed terms), the tables are built internal.
- **Trial**: `--from 2025 --out-dir`: 770,886 rows, 89 respondents, 2025-01-01 00:00 to 2025-12-31 23:00 UTC; the validator passes (after the vintage was made an ISO time).

## To finish (session 489 of `queue/next/022-...`; the daily run held the data lock from 17:00 UTC)

`python warehouse/connectors/ferc714_demand.py` (2023 to 2025; the raw file is reused, no request), then the validator, `build_coverage.py --only '^ferc714_area_demand_'`, `archive.py write --tables '^ferc714_area_demand_'`, `licenses.py tables` and `write` in a worktree, and land.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.ferc.gov | 2 | robots file (200), the Form 714 data page (403) |
| docs.catalyst.coop | 2 | robots file, the data-access page (license record 85) |
| s3.us-west-2.amazonaws.com | 7 | robots (403), two HEADs, the two parquet files twice (a probe download, then the connector's own capture) |

## Decisions made without you

1. PUDL's copy of FERC's data, not FERC's protected site.
2. The core table, not the imputed one.
3. Yearly tables from 2023 first; 2006 to 2022 are session 494's (about 16.6 million rows: the archive's room first).
4. `internal` until FERC's terms are read or you rule.

## For Samuel's ruling

- `ferc714_area_demand_*` public (PUDL's CC-BY-4.0 and a U.S. government work), or internal until FERC's terms page can be read.

## Files

- New: `warehouse/connectors/ferc714_demand.py`, `tests/test_session484.py`, this report. Changed: `warehouse/metadata/build_coverage.py`, `license_reads.csv` (record 85), `license_verdicts.csv`, `docs/licenses.md`, `scripts/licenses.py` (the line of sweeps).
- On this machine (not in git): `warehouse/raw/ferc714_demand/`, `warehouse/raw/pudl_ferc714/` (the probe's download), `runs/s484/`.
