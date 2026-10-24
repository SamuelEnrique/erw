# Session 2183 report: the generating units of EPA's power sector model (NEEDS)

24 October 2026, from 01:59 UTC, on lab-desktop (the data machine), a session of `queue/done/097-day-1-november-data-canada-offshore-inspections-supply.md`, the second source of the session's own choosing. Model spend USD 0. Pulls: www.epa.gov, 1 request of 20: the NEEDS workbook for the 2025 reference case. Its robots file and the NEEDS page were read in session 2181 (reads 360 and 361). The trials and the write ran offline. Also Supabase, for the locks and the archive.

## Why this source

NEEDS is the unit inventory EPA's Integrated Planning Model starts from, the fleet behind EPA's regulatory analyses of the power sector. It gives each unit's IPM region, heat rate, fuels, emission controls and emission rates, and what EPA retires, adds or drops. The ERW held EIA's inventory (EIA-860 and 860M) but not EPA's view of it. It is EPA's own record (EPA's verdict, read 55).

## Read these first

- **One entities table, `epa_needs_units`:** 38,030 units from the four unit sheets of "NEEDS for the 2025 Reference Case" (December 2025):

  | Sheet | Units | MW |
  |---|---|---|
  | active | 22,688 | 1,155,380 |
  | retired by 2028 | 1,094 | 65,351 |
  | hardwired capacity | 2,755 | 117,400 |
  | dropped capacity | 11,493 | 582,669 |

  - Generators are typed `generator`, and boilers (EPA's B, where coal units carry their capacity) are typed `equipment` (Decision 54).
  - `x_needs_sheet` keeps EPA's sheet, and `status` is `active` only for the active sheet (Decision 20).
  - The `x_` columns carry EPA's ORIS code, unit, plant type, IPM region, county, heat rate, on-line and retirement year, fuels, controls, SO2 and NOx rates, owners, regulatory status, and a dropped unit's reason.
  - EPA's retirement year 9999 (none) is written blank.
- **Each unit id appears once across the four sheets** (checked in the connector).
- **The dropped sheet gives no state code for 10,581 units,** only names. States are mapped by name and checked against the code wherever both are given. 1,339 dropped units are in Alaska, Hawaii or Puerto Rico, which IPM does not model.
- **Seven dropped units have no capacity in EPA's file.** Their `capacity_mw` is blank and the header counts them.
- **The cross-check** (`runs/c097/s2183/cross.py`) compares against EIA-860M's operating generators (`eia860m_operating_generators`, net summer MW, the same 49 states and DC):
  - **Matching:** 21,345 of NEEDS's 21,660 active generators match EIA's plant and generator id, and 10,892 of NEEDS's 11,061 plant codes are in EIA-860M.
  - **Capacity:** NEEDS's active and hardwired units together hold 1,272,779 MW against EIA-860M's 1,312,452 (0.97). By state the median is 0.97, from 0.81 to 1.29 (Rhode Island 1.29, Wyoming 1.21). Texas is 0.97 and California 1.00.
  - **Generators alone are 0.72 of EIA,** because coal units' capacity sits on their boilers in NEEDS.
- **Dropped units' reasons, the most common:**
  - retired or planned to retire by June 2028 (5,783);
  - onsite, a net buyer of electricity in 2021 (1,878);
  - canceled or postponed (1,417);
  - in Alaska, Hawaii or Puerto Rico (1,339).
- **Registered:**
  - the sector rule (`power`);
  - both holds;
  - the release package's rows (1 table, 48 variables);
  - the license tables (licenses check: 0 problems; release check: 0 differences).

  No row is given twice. The test is `tests/test_session2183.py` (3 tests).

## Errors

- **The first trial stopped on the dropped sheet's missing state codes.** The connector now maps states by name and checks them against the code where both are given.
- **The first draft named a column list iso_prices does not define, and EPA's publisher not as `sources.csv` writes it.** Both were fixed before any run wrote a table.

## Decisions made without you

- **This source chosen,** for the reason above.
- **All four sheets taken,** each unit keeping its sheet, rather than the active sheet alone. The retirements, additions and drops are what a reader of EPA's modelling needs beside the fleet.
- **The workbook's address held fixed.** A later reference case has a new address, which a later session reads from the page.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/epa_needs.py`, `tests/test_session2183.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c097/s2183/`.

## Corrected by session 2185

- **"The same 49 states and DC" should read 48 states and DC:** NEEDS's active units sit in 49 `geo` values.
- **California's ratio of 1.00 includes EPA's one I unit,** "IMPORT1 1", 1,000 MW of imports typed as a generator in the active sheet.
- **The ratio of 0.97 counts 276 hardwired units that come on line only in 2026 to 2028,** against EIA-860M's operating generators. It overstates the match a little.

The connector's description now names the import unit and the unit kind C (none in this workbook).
