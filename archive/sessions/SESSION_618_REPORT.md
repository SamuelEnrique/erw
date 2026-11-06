# Session 618 report: EIA's refinery and blender net production by district, a month

22 October 2026, from 02:35 UTC, on lab-desktop (the data machine), a session of `queue/done/038-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia_refinery_production_monthly`: 175,413 rows, 1,422 series, January 2015 to July 2026.** From EIA's Petroleum Supply Monthly (route `petroleum/pnp/refp`), made from session 615's connector.
  - Net production by product, in `kbbl` (`net_production`) and `kbbl/d` (`net_production_per_day`).
  - The areas are the U.S., the five PADDs and the ten refining districts.
  - EIA's 182,999 records gave 175,413 rows; the blanks have no row.
- **Negative values are kept, as EIA gives them**: 20,147 rows, for liquids refineries use up more than they make (butanes, natural gas liquids, unfinished oils and others). The validator passes them.
- **Cross-checks** (areas and products from EIA's codes in the saved pages):
  - **The PADDs against the U.S.**: 13,070 of 13,185 keys within 1 kbbl.
  - **The districts against their PADD**: PADD 1, all 12,130; PADD 2, 12,020 of 12,034; PADD 3, 13,011 of 13,076.
  - The larger differences (up to 121 kbbl) fall where a part is blank, as in session 615.
  - **The same series in `eia_petroleum_snd_monthly`** (`refinery_net_production`): 432 series, all 56,926 rows equal.
- **Written under the data lock** (02:40 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (175,413 rows archived). Release rows added; `licenses.py check` 0 problems (281 tables). **Held** from `/data` and Redivis v1. Sector rule (`products`). Tests: `tests/test_session618.py`, 5.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 38 of 40 | a March 2026 page, the trial (37) |

## Files

- New: `warehouse/connectors/eia_refinery_production.py`, `tests/test_session618.py`, this report. Changed: the sector rule, both holds, the release package, the license record, coverage and the archive manifest.
