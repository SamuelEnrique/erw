# Session 615 report: EIA's refinery and blender net input, a month

22 October 2026, from 02:05 UTC, on lab-desktop (the data machine), a session of `queue/done/037-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia_refinery_inputs_monthly`: 122,400 rows, 970 series, January 2015 to July 2026.** From EIA's Petroleum Supply Monthly (route `petroleum/pnp/inpt`).
  - Refinery and blender net input of 36 products, in `kbbl` (`net_input`) and `kbbl/d` (`net_input_per_day`).
  - The areas are the U.S., the five PADDs and the ten refining districts within them (East Coast and Appalachian No. 1 in PADD 1; three in PADD 2; five in PADD 3).
  - EIA's 131,681 records gave 122,400 rows; the blanks have no row.
- **Cross-checks** (areas and products from EIA's codes in the saved pages; the series names spell the areas several ways):
  - **The PADDs against the U.S.**: 8,943 of 9,010 keys within 1 kbbl.
  - **The districts against their PADD**: PADD 1, 7,938 of 7,954; PADD 2, all 7,956; PADD 3, 8,192 of 8,252.
  - The larger differences (up to 103 kbbl) fall where one part is blank, as EIA withholds a figure.
  - **The same series in `eia_petroleum_snd_monthly`**: all 29,990 rows equal.
  - **U.S. crude input against the weekly table's monthly mean** (`eia_refinery_weekly`, WCRRIUS2), 139 months: median ratio 1.002, from 0.956 to 1.045, within 2% in 129.
- **Written under the data lock** (02:09 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (122,400 rows archived).
  - The metadata patch met session 614's rows in four files (coverage, sources, the archive manifest, `docs/coverage.md`), each side adding its own table's line.
  - The union resolver kept both. Each of this chain's four tables has one row in each file.
  - The release step was then run again: `licenses.py check` 0 problems (280 tables).
  - **Held** from `/data` and Redivis v1. Sector rule (`products`). Tests: `tests/test_session615.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 29 of 30 | the count from 2015, a March 2026 page, the trial (27) |

## Files

- New: `warehouse/connectors/eia_refinery_inputs.py`, `tests/test_session615.py`, this report. Changed: the sector rule, both holds, the release package, the license record, coverage and the archive manifest.
