# Session 2014 report: the wholesale hubs outside the ISOs (ICE's indices, as EIA republishes them), chain 058 written, chain 056 finished

23 October 2026, from 17:57 UTC, on lab-desktop (the data machine), the first session of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`. Model spend USD 0. Pulls: 3 requests of 15 (www.eia.gov's robots file, asked in a call of its own; EIA's wholesale market data page; the 2026 workbook, through the connector's trial). The write reused the saved workbook (`--offline`).

## Read these first

- **Chain 058 written and pushed first:** `queue/next/058-day-24-october-data-outages-fuels-mines-vehicles.md` (sessions 2028 to 2041: DOE's OE-417 disturbances, Oak Ridge's EAGLE-I outages, EPA's RIN generation, EIA's biofuels plant capacity, MSHA's mines, FHWA's motor fuel, the AFDC's vehicle registrations, the licenses' twelfth round and the rest), committed alone and pushed to main (`ceca658d`, after rebasing on a queue commit of the old laptop's). Before and after snapshots `s2014-before` and `s2014-after`: **0 differences in all** (25 pages); Vercel's status for `ceca658d` was "Deployment rate limited", so nothing deployed. **Another agent on this machine took chain 058 at once** (main's `f0919baa`) and wrote chain 059; it runs beside this chain, in `erw-c058`.
- **Chain 056 was finished first, as chain 056 finished chain 055.** Its agent had stopped inside session 2013: the note written but not committed, the branch never pushed, the landing and the queue step not run; and session 2010 (the Stanford draft) had not run (its reconcile found this machine's daily task holding the data lock until 19:00 UTC, and no report was written). This session committed chain 056's note on `wip/2000-2013-data`, with session 2010's and 2013's lines corrected (`c9c93313`), merged origin/main, ran the whole suite on it, and pushed `wip/2000-2013-data` and `task/2000-2013-data` (`25ecf7f7`, 18:12 UTC). Its draft work is folded into this chain's session 2024, which the chain file already gives chain 056's tables.
- **The whole suite on chain 056's branch** (after merging origin/main), run in two halves so each fits the ten-minute foreground limit (`runs/c057/suite_half.py`): 6,363 tests, 1 failure, `test_session705` (the known artifact of a run from a worktree: it passes in the main checkout and skips on GitHub). Snapshot before the landing: `c056-land-before` (18:12:12 UTC). The check run and the after snapshot: session 2015's report.
- **This chain's branch** is `wip/2014-2027-data` in `erw-c057`, cut from chain 056's tip `25ecf7f7`; its reads are numbered after chain 056's last (174).
- **One table written, validated, archived, in coverage (sector power, internal), held from the live set:** `eia_ice_electricity_daily`, 7,056 rows: the Intercontinental Exchange's day-ahead on-peak indices at seven hubs (Mid-C, Palo Verde, SP15, NP15, Mass Hub, PJM West real time, Indiana real time), a delivery day, from 29 December 2025 to 14 October 2026: high, low and weighted average prices and the change (USD/MWh), volume (MWh), trades and counterparties (count). Mid-Columbia and Palo Verde are the hubs no ISO table holds.
- **The hubs are not those the chain file guessed:** EIA's agreement with ICE covers eight electricity hubs (New England, PJM, Midwest, Texas, Northwest, Northern and Southern California, the Southwest); there is no Southeast or Rockies hub, and the 2026 file has no row for ERCOT North.
- **Only 2026:** EIA's robots file disallows `/*archive/`, and every earlier year's file (`xls/archive/ice_electric-<YEAR>final.xlsx`, 2014 to 2025, and the history zip from 2001) is under it. Not asked.
- **Held internal:** EIA's page says the data are "republished, with permission, from data collected by the Intercontinental Exchange (ICE)". EIA's public domain statement (read 1) covers EIA's own work; these are ICE's data, under an agreement between EIA and ICE that grants nothing to others. Read 175 (the page) and a verdict of its own, "ICE, whose prices EIA republishes": needs written permission; `scripts/licenses.py` maps the table to EIA and ICE by hand, as the NYMEX futures EIA republished are mapped.

## The cross-check

ICE's weighted average against the ISOs' own hub prices (`iso_hub_prices_history`), averaged over the same delivery days' peak hours (Eastern peak HE8 to HE23 Monday to Friday; WECC peak HE7 to HE22 Monday to Saturday; a package over its days' peak hours), `runs/c057/s2014/cross.py`:

| ICE product | ISO price | Days | ICE mean | ISO mean | Mean difference | Correlation |
|---|---|---|---|---|---|---|
| SP15 EZ Gen DA LMP Peak | CAISO TH_SP15 day-ahead | 178 | 25.57 | 25.69 | -0.12 | 0.980 |
| NP15 EZ Gen DA LMP Peak | CAISO TH_NP15 day-ahead | 81 | 36.41 | 36.14 | +0.27 | 0.964 |
| Nepool MH DA LMP Peak | ISO-NE internal hub day-ahead | 166 | 77.79 | 76.88 | +0.91 | 0.941 |
| Indiana Hub RT Peak | MISO Indiana hub real time (to 3 October) | 37 | 93.56 | 80.74 | +12.82 | 0.590 |

The day-ahead products follow the ISOs' day-ahead prices within a dollar on average: a fixed-price trade made the morning before against the auction's clearing. Indiana's is a real-time product traded a day ahead against a real-time price that was not yet known, so it is looser, and thinly traded (40 days in ten months). PJM West is not cross-checked: the ERW holds no PJM hub price.

## Errors

- **The first test of a bad price passed:** pandas reads the text "n/a" as an empty cell by default, so a cell the publisher wrote as text would have been dropped without a word. The connector now reads with `keep_default_na=False`: only an empty cell is empty, and text in a number's place stops the run. The trial was run again offline: the same 7,056 rows.
- **The first push of the queue file was refused** (the old laptop had pushed its chain 078 file a moment before): rebased on it and pushed.

## Decisions made without you

- **Chain 056 finished and pushed to land before this chain's writes,** and its session 2010 folded into session 2024.
- **The suite run in two halves**, each under the ten-minute limit, the whole of it in the foreground.
- **The table held internal** on EIA's own sentence (reversible by a ruling).
- **A multi-day package one row at its delivery start,** its end in `x_delivery_end`; nothing spread over the days.
- **`price_change` kept as the file gives it** (the change in the weighted average from the product's previous trade).
- **No natural gas hubs:** the page's gas files stop at 2017 and are under `/archive/`; the session's task was the electricity hubs.

## For Samuel's ruling

- **ICE's indices as EIA republishes them** (`eia_ice_electricity_daily`, held internal): publish on EIA's page, ask ICE, or keep internal. ICE's own terms are for session 2019's round.

## Files

- New: `warehouse/connectors/eia_ice_electricity.py`, `tests/test_session2014.py` (3 tests), `queue/next/058-day-24-october-data-outages-fuels-mines-vehicles.md` (on main), this report.
- Changed: `build_coverage.py`, `live_set.yaml`, `scripts/licenses.py`, `license_reads.csv`, `license_verdicts.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`. On chain 056's branch: `docs/state/note_2026-11-04_data.md`.
- On the data machine only: `runs/c057/`, `runs/license_reads/s2014/`, `runs/s2014*`, `warehouse/raw/eia_ice_electricity/`.
