# Session 2426 report: Europe's hard coal imports by country of origin (Eurostat), a source of the session's own choosing

24 October 2026, from 11:21 UTC, on lab-desktop (the data machine), a session of `queue/done/115-day-16-november-data-zambia-botswana-mongolia-cambodia.md`. Precheck passed (`runs/c115/precheck_2426.out`). Model spend USD 0.

Pulls: 4 requests of 20:
- **ec.europa.eu's robots file:** the same file as session 2369's, sha256 `fc082fc2`.
- **`nrg_ti_sffm`:** HTTP 404, "not available for dissemination". I guessed a monthly code that does not exist.
- **Eurostat's table of contents:** 1,975,318 bytes; it lists every data set code.
- **`nrg_ti_sff`, hard coal from 2010:** answered at once, 1,454,579 bytes.

The trial and the write ran offline.

## Read these first

- **Why:** Eurostat's imports of hard coal by partner show where Europe's coal comes from, the United States and Russia among the origins. It sits beside the monthly solid fuels balance (chain 110's session 2364) and the crude oil imports by partner (session 2369). It is not held and no chain has taken it.
- **Annual only:** Eurostat's table of contents lists solid fuel imports and exports by partner only a year (`nrg_ti_sff` and `nrg_te_sff`, 1990 to 2024). There is no monthly set.
- **One series table, `eurostat_hard_coal_imports_annual`:** 99,288 figures, 2010 to 2024, public under Eurostat's copyright notice (flag and verdict agree).
  - **Areas:** 39 importing countries and Eurostat's EU27 and euro area rows. The United Kingdom and Kosovo are left out by Eurostat's terms.
  - **Partners:** 167, aggregates among them (a sum over partners double counts).
  - **Unit:** `t` (thousand tonnes times 1,000).
  - **Hard coal** is SIEC C0100: anthracite, coking coal, other bituminous and sub-bituminous coal.
  - **Values:** 93,045 rows are zero, as published. No observation is flagged.
- **What it shows,** the EU's hard coal imports in Mt:

  | | 2010 | 2018 | 2022 | 2023 | 2024 |
  |---|---|---|---|---|---|
  | All partners | 164.5 | 154.4 | 126.7 | 92.4 | 67.7 |
  | From the United States | 25.3 | 26.7 | 20.9 | 20.3 | 17.1 |
  | From Russia | 36.8 | 61.0 | 27.2 | 0.8 | 0.2 |

  From the United States the peak was 36.1 Mt (2012) and the low 13.4 Mt (2020). Russia's fall follows the EU's embargo on Russian coal from August 2022.
- **Against the monthly balance** (`eurostat_solid_fuels_monthly`, hard coal imports summed over twelve months): of 321 country-years, 102 agree within 1,000 t and 147 within 1 percent. For the EU, the annual figure is 7 percent under the monthly sum in 2016, 6 percent over in 2017, and within 2 percent from 2019 (2024: 67.7 against 68.6 Mt). Eurostat's annual and monthly collections are separate. This report says so, and session 2429's method note will; neither table is corrected.
- **Registered:**
  - the sector rule (`coal`), the live-set hold;
  - the release package's held list and its rows (the release check passes);
  - the license tables (licenses check: 524 tables, 0 problems);
  - the test, `tests/test_session2426.py` (3 tests).
- **Not yet in the Stanford draft:** session 2429 uploads it.

## Errors

- **I asked for a monthly code without reading the catalogue first** (`nrg_ti_sffm`, HTTP 404): one request lost. The table of contents was read next and settled it.
- **The write's metadata patch conflicted again;** `runs/c102/add_own_rows.py` put in one row each.

## Decisions made without you

- **Annual data taken,** since Eurostat has no monthly coal imports by partner.
- **Hard coal only,** not lignite or coke: the traded solid fuel that matters for U.S. exports.
- **From 2010,** fifteen years, rather than 1990.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_coal_imports.py`, `tests/test_session2426.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`;
  - `docs/redivis/release-v1/`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c115/s2426/`, `runs/license_reads/s2426/`, `warehouse/raw/eurostat_hard_coal_imports_annual/`.
