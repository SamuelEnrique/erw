# Session 2017 report: buildings' energy (EIA's CBECS 2018 and RECS 2020)

23 October 2026, from 18:36 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/057-night-23-october-data-wholesale-solar-industry-buildings.md`. Model spend USD 0. Pulls: 11 requests of 15 (www.eia.gov's robots file, asked in a call of its own, unchanged; the CBECS 2018 and RECS 2020 data pages and their consumption views; six tables through the connector's trial). The writes reused the saved tables (`--offline`).

## Read these first

- **The latest surveys with consumption:** CBECS 2018 (consumption and expenditures released September to December 2022) and RECS 2020 (final March 2024). RECS 2024 has published preliminary housing characteristics only, and CBECS 2024 nothing yet.
- **Two tables written, validated, archived, in coverage (sectors power, gas and oil, public), in the release package, both holds,** one a survey (the chain file allowed either):
  - `eia_cbecs_commercial_buildings`, 5,944 rows: Tables C1 (consumption by major fuel, TBtu, and the number of buildings), C2 (expenditures by major fuel, USD) and E1 (consumption by end use, TBtu), for all buildings and 278 categories under 44 headings (principal building activity, census region and division, size, age, climate zone, equipment and the rest).
  - `eia_recs_households`, 2,802 rows: Tables CE4.1 (site consumption by fuel and end use, TBtu) and CE4.11 (expenditures by fuel and end use, USD), with housing units, for all homes and 76 categories under 11 headings (census region and division, housing unit type, income, climate region, main heating fuel and the rest).
- **The crosstabs' structure is kept:** each row carries its heading (`x_heading`), its indent in EIA's sheet (`x_level`: a level-1 row such as Inpatient is a part of the level-0 row above it, Health care) and that parent (`x_parent`); a part's entity names its parents (RECS prints Single-family under Owned and again under Rented). Under every heading that is not "more than one may apply", the level-0 rows add up to the total within rounding (CBECS 6,786 to 6,788 TBtu against 6,787; RECS 9,480 to 9,482 against 9,481).
- **The codes:** a coded cell has no row; each header counts them: CBECS Q 272, N 49, (*) 14; RECS Q 190, N 44, * 7.
- **The totals:** commercial buildings in 2018, 5.9 million buildings, 6,787 TBtu (site), USD 141.2 billion; homes in 2020, 123.5 million housing units, 9,481 TBtu, USD 232.8 billion.

## The cross-check

The surveys' totals against EIA's sector figures for the same years (`runs/c057/s2017/cross.py`; SEDS's US row):

| Survey | Sector figure | Share |
|---|---|---|
| CBECS 2018 electricity (site), 4,081 TBtu | MER commercial retail electricity (ESCCBUS), 4,715; SEDS (ESCCB), 4,715 | 86.6% |
| CBECS 2018 natural gas, 2,300 | MER commercial natural gas (NNCCBUS), 3,639; SEDS (NGCCB), 3,655 | 63.2%, 62.9% |
| RECS 2020 electricity, 4,453 | SEDS residential electricity (ESRCB), 4,997 | 89.1% |
| RECS 2020 natural gas, 4,241 | SEDS residential natural gas (NGRCB), 4,876 | 87.0% |

CBECS covers commercial buildings of more than 1,000 square feet; the commercial sector also holds street lighting, water and sewage works and other users outside buildings, which take a large part of its natural gas. RECS covers occupied primary homes, not vacant or seasonal ones. The shares are EIA's usual ones for both surveys.

## Errors

- **The connector's unit check failed twice before it read:** a lower-cased header compared with "trillion Btu", then CBECS's "trillion British thermal units": the unit is now a pattern.
- **RECS's Single-family stopped the run as a category given twice:** it is printed under Owned and under Rented. A part's entity now names its parents.
- **The first of the two writes' release checks failed** (`eia_recs_households` was held in the license record and not yet in the package between the two runs); the second run added it and the check passed: 0 differences.

## Decisions made without you

- **Two tables, one a survey,** from one connector (`eia_buildings.py`).
- **Every heading kept,** not only building type, region and end use: the chain file asked for those, and the others are the same tables' rows.
- **The relative standard errors not taken** (the rse sheets), said in each header.
- **Footnote letters left in labels as printed** ("Climate zonec", "Some other fuelg"): EIA glues them to the words, and no rule tells a letter from a word's end ("Hot-humid").
- **Floorspace not taken:** square feet are not an ERW unit, and a new unit waits for a reason; the number of buildings and housing units are.
- **CE1.1 (the U.S. summary with intensities) not taken;** its totals are CE4.1's and CE4.11's.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_buildings.py`, `tests/test_session2017.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c057/s2017/`, `runs/license_reads/s2017/`, `runs/s2017*`, `warehouse/raw/eia_buildings/`.
