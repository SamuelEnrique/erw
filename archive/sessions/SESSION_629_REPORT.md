# Session 629 report: one more source: natural gas plant production of natural gas liquids by district

22 October 2026, from 04:40 UTC, on lab-desktop (the data machine), a session of `queue/done/039-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia_ngl_production_monthly`: 31,956 rows, 276 series, January 2015 to July 2026.** From EIA's Petroleum Supply Monthly (route `petroleum/pnp/gp`), made from session 618's connector.
  - Field production of natural gas liquids at gas processing plants: the total and its parts (ethane, propane, butanes, pentanes plus), nine products in all.
  - In `kbbl` (`field_production`) and `kbbl/d` (`field_production_per_day`), for the U.S., the PADDs and the refining districts.
- **Why this source**: the ERW held natural gas liquids' production for the U.S. and the PADDs only (in `eia_petroleum_snd_monthly`). The districts (Texas Gulf Coast, Texas Inland, New Mexico and the others) show where NGLs come from. The route is in a unit the vocabulary holds and needs no ruling.
  - Probed beside it: `petroleum/pnp/oxy` (oxygenate plant production, 24 records a month, the U.S. and PADDs only). It was not taken; it is left for a later chain.
- **Cross-checks** (areas from EIA's codes in the saved pages):
  - **The PADDs against the U.S.**: 2,062 of 2,076 keys within 1 kbbl (the largest difference 2).
  - **The districts against their PADD**: PADD 1, all 2,076; PADD 2, 2,035 (the largest 83, where a part is blank); PADD 3, 2,050 (the largest 2).
  - **The same series in `eia_petroleum_snd_monthly`** (`field_production`): 84 series, all 10,336 rows equal.
  - 278 rows of normal butane are negative, kept as EIA gives them.
- **Written under the data lock** (04:42 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (31,956 rows archived). Release rows added; `licenses.py check` 0 problems (287 tables). **Held** from `/data` and Redivis v1. Sector rule (`products`). Tests: `tests/test_session629.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 10 of 20 | a January 2026 page of `pnp/gp` and of `pnp/oxy`, the trial (8) |

## Files

- New: `warehouse/connectors/eia_ngl_production.py`, `tests/test_session629.py`, this report. Changed: the sector rule, both holds, the release package, the license record, coverage, sources and the archive manifest.
