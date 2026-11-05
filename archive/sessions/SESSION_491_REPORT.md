# Session 491 report: EIA's Short-Term Energy Outlook

21 October 2026, from 17:38 UTC, on lab-desktop (the data machine), the third session of `queue/done/022-evening-21-october-sources.md`. Model spend USD 0.

## Read these first

- **The API keeps only the current release**, so each run keeps its release by date: `vintage` is the release date from EIA's STEO page ("Release Date: October 6, 2026"), and the table's key includes it (rule 5 of `docs/datastandard.md`, which the header states). A month from the release's month on is `x_kind` forecast; an earlier one is EIA's history.
- **The series**:
  - retail electricity prices, residential, commercial, industrial and all sectors (`ESRCU`, `ESCMU`, `ESICU`, `ESTCU`), for the U.S. and every census division: 44 series;
  - the Henry Hub spot (`NGHHUUS`);
  - the U.S. generation shares (`*EPSHR_US`): 8 series.
  - 53 series, monthly from January 2020 to December 2027.
- **`warehouse/connectors/eia_steo.py`**:
  - one series table `eia_steo_forecasts`;
  - units into the standard: cents per kWh, in both of EIA's spellings, as USD/kWh (nominal); dollars per million Btu as USD/MMBtu; a percentage as a ratio;
  - a unit not in the map stops the run, which caught "percentage" and "cents per kilowatt hour" in the trials before any table was written;
  - the sector rule (`power;gas`) and `tests/test_session491.py` (5 tests).
- **Trial**: 5,088 rows, 53 series, 4 requests; the validator passes.
- **Cross-check against EIA's monthly retail prices** (`eia_retail_electricity_prices`, the U.S. all-sector price, USD/MWh): of 79 history months, 78 are equal within USD 0.05/MWh; March 2026 differs by USD 1.00/MWh, a revision between the two publications.

## To finish (session 489's part, when the lock is free)

`python warehouse/connectors/eia_steo.py`, the validator, `build_coverage.py --only '^eia_steo_forecasts$'`, `archive.py write --tables '^eia_steo_forecasts$'`. Each later run adds that month's release.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 11 | the route, the series list, three trials' series lists and data |
| www.eia.gov | 3 | the STEO page (once a trial) |

## Files

- New: `warehouse/connectors/eia_steo.py`, `tests/test_session491.py`, this report. Changed: `warehouse/metadata/build_coverage.py`.
