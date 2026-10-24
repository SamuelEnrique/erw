# Session 2286 report: crude oil stocks at tank farms and pipelines, Cushing among them (EIA), a source of the session's own choosing

24 October 2026, from 05:21 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/104-day-7-november-data-portugal-italy-japan-argentina.md`, unattended. Model spend USD 0. Pulls: EIA's API, 3 requests of 20 (below).

## Read these first

- **Why this source:** Cushing, Oklahoma, is the delivery point of the NYMEX WTI contract. Its stocks, with the tank farms and pipelines of each PADD, are the crude market's balance between the field and the refinery. The ERW held Cushing only weekly (`eia_petroleum_supply_weekly`), and no PADD tank farm series. No chain plans it, and EIA's verdict is on record.
- **One table written, validated, archived, in coverage (sector oil), in the release package, both holds:** `eia_crude_tank_farm_stocks_monthly`, January 1981 to July 2026, 3,553 rows, in thousand barrels (kbbl).
  - Tank farm and pipeline stocks for the U.S. and the five PADDs (547 months each).
  - Cushing's ending stocks from 2004 (271 months), with geo US-OK.
  - Each row carries the time EIA served its page.
- **A correction made before the write:** the first docstring called the "ending stocks" series the U.S.'s. The cross-check showed it is Cushing's (from January 2004), and the docstring now says so.
- **The cross-check** (`runs/c104/s2286/cross.py`, `cross.out`):
  - The five PADDs sum to the U.S. exactly in all 547 months.
  - Cushing never exceeds PADD 2's tank farms (a median 38.4% of them).
  - The monthly Cushing figure is within a median 1.30% of the month's last weekly figure in `eia_petroleum_supply_weekly` (199 months, at most 10.58%: a week is not a month's end).
  - Cushing held 16,557 kbbl at the end of 2004, 35,866 at the end of 2019, and 20,428 at the end of 2024.

## The pulls

1. EIA's route metadata (1981-01 to 2026-07) and one page of 2025 (2 requests).
2. The trial's one page. The write reused it (0 requests).

## Errors

- **The docstring's first reading of the "ending stocks" series** (above), corrected before the write.

## Decisions made without you

- **EIA's tank farm stocks as the session's own choice,** for the reasons above.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_crude_tank_farm_stocks.py`, `tests/test_session2286.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - the coverage, sources, archive manifest and license files
  - `docs/redivis/release-v1/`
- On the data machine only: `runs/c104/s2286/`, `runs/s2286_*`, `warehouse/raw/eia_crude_tank_farm_stocks/`.
