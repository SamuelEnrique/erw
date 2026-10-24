# Session 2342 report: a source of the session's own choosing (session 2339's EIA petroleum stocks by state, finished)

24 October 2026, from 07:46 UTC to 07:51 UTC, on lab-desktop (the data machine), chain 109, unattended. Model spend USD 0. Pulls: 3 requests of 20 (the three data pages session 2339's ceiling left; the write ran offline).

## Read these first

- **Why this source:** session 2339 wrote the connector for EIA's route `petroleum/stoc/st`, but the route from 2015 is 15 pages and its ceiling stopped the trial at 12. This session spends three requests to finish the table rather than leave a written connector without its table.
- **A new table, `eia_petroleum_stocks_state_monthly`** (series, 73,997 rows, `products`): EIA's stocks of 13 petroleum products at refineries, bulk terminals and natural gas plants.
  - It covers 593 series: the 50 states (those EIA lists), the five PADDs and the U.S., January 2015 to July 2026.
  - It is in kbbl at the month's end, with EIA's area and product codes kept as `x_area` and `x_product`.
  - 100 values are 0 and kept, 69 of them reformulated gasoline blending components; none is negative.
  - Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added (public: EIA, read 1).
- **Cross-checks:**
  - **Within the table:** the PADDs sum to the U.S. within 0.0001 in every product and month. The states sum to the U.S. at a median of 1.000 for every product. Propane's states sum to 0.991 to 1.000, and in some months a product's states run above the U.S. (reformulated gasoline up to 1.368), where EIA's state figures and its U.S. total are published separately.
  - **Against `eia_petroleum_stocks_monthly`** (route `stoc/ts`, all stocks), the U.S. figures:
    - residual fuel is 1.000;
    - distillate is 0.716 to 0.820;
    - propane is 0.648 to 0.886.

    This route counts stocks at refineries, bulk terminals and gas plants only, not stocks in pipelines or at other primary terminals.
- **Not taken:** the months 1993 to 2014 (about 50,000 rows more). The connector's `--from` reaches them in a later run with a ceiling to match.

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | data pages 13 to 15, from 2015-01 | 200: 13,997 rows, EIA's count met |

## Decisions made without you

- **This session's own choice is the completion of session 2339's table,** said here.

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session2342.py`, this report (the connector is session 2339's).
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record.
- On the data machine only: `warehouse/raw/eia_petroleum_stocks_state/`, `warehouse/output/eia_petroleum_stocks_state_monthly.csv`, `runs/c109/s2342_*`.
