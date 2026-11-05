# Session 631 report: oxygenate plant production, a month, 1981 on

22 October 2026, from 05:04 UTC, on lab-desktop (the data machine), a session of `queue/done/040-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `eia_oxygenate_production_monthly`: 6,006 rows, 30 series, January 1981 to July 2026.** From EIA's Petroleum Supply Monthly (route `petroleum/pnp/oxy`), made from session 618's connector.
  - Oxygenate plant production (`oxygenate_plant_production`) of fuel ethanol (from 1981), MTBE (from 2005) and oxygenates excluding fuel ethanol (from 2010).
  - Biofuels plant net production of other oxygenates (`biofuels_plant_net_production`, from 2010).
  - In `kbbl` and, with `_per_day`, `kbbl/d`, for the U.S. and the PADDs.
  - The whole history: 7,726 records, 2 pages.
- **Cross-checks**:
  - **The PADDs against the U.S.**: 1,625 of 1,634 keys within 1 kbbl (the largest difference 2).
  - **U.S. fuel ethanol** against `eia_petroleum_snd_monthly`'s renewable plant production of fuel ethanol (M_EPOOXE_YNP_NUS_MBBL): equal in all 139 months both hold (2015 on).
- **Written under the data lock** (05:07 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (6,006 rows archived). Release rows added; `licenses.py check` 0 problems (288 tables). **Held** from `/data` and Redivis v1. Sector rule (`products`). Tests: `tests/test_session631.py`, 4.
- **Chain 039's landing deployed** (`5ff2fad5`, Vercel success at 05:03 UTC); s630-before against s630-after: 0 differences. The queue move (`fa7c1af1`) was rate limited.

## Errors

- The first count request was not sent as meant: curl read the brackets of `sort[0][column]` as a glob and the answer was not JSON. Sent again with `-g`. It is counted below as a request.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 4 of 10 | the count (twice, the first malformed), the trial (2) |

## Files

- New: `warehouse/connectors/eia_oxygenate_production.py`, `tests/test_session631.py`, this report. Changed: the sector rule, both holds, the release package, the license record, coverage, sources and the archive manifest.
