# Session 951 report: federal oil, gas and coal production and royalties (ONRR)

23 October 2026, from 12:06 UTC, on lab-desktop (the data machine), the first session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`, taken right after chain 053 landed. Model spend USD 0. Pulls: 14 requests of 15 (revenuedata.doi.gov's robots file, asked in a call of its own and read first; its downloads page, two pages that answered 404, its page data, its webpack runtime and three page chunks, to find the files' names, the page being drawn in the browser; revenuedata.onrr.gov's robots file; the three files).

## Read these first

- **Chain 055 written and pushed first:** `queue/next/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md` (sessions 978 to 991, machine: data), committed alone and pushed to main (`2615fa85`; `git status -sb` showed nothing ahead), with a snapshot pair (`c054-055-before`, `-after`: 0 differences; Vercel rate-limited the deploy). The queue move of 054 was pushed before it with its own pair (`c054-take-before`, `-after`: 0 differences).
- **Three tables written, validated, archived, in coverage (sectors oil, gas, coal, public), in the release package, both holds,** from ONRR's Natural Resources Revenue Data downloads:
  - `onrr_production_monthly`: 2,264 rows, 8 series: oil, gas and coal produced on federal and Native American lands, onshore and offshore, a month, January 2003 to July 2026 (bbl, Mcf, short tons).
  - `onrr_production_annual`: 15,068 rows, 830 series: the energy products (oil, gas, coal and its kinds, geothermal electricity as MWh) by state and county or offshore region, a calendar year, 2003 to 2025.
  - `onrr_revenue_monthly`: 413,554 rows, 5,047 series: the revenue ONRR collects by county or offshore region, revenue type (royalties, rents, bonuses, other revenues, penalties, fees), lease type, commodity and product, a month, January 2003 to August 2026 (USD; 29,103 negative values, ONRR's adjustments, kept).
- **The cross-checks:**
  - **The Gulf against BOEM:** ONRR's annual federal offshore Gulf of America oil and gas against `boem_ogor_lease_production_monthly` summed by year, within 0.5 percent in all 23 years (2024: 656.2 million barrels in both; gas 685.1 and 686.7 billion cubic feet). ONRR's monthly offshore figure also holds the Pacific and Alaska, so it runs 3 percent over BOEM's Gulf (median).
  - **The years against the months:** federal onshore coal summed from the annual file equals the monthly file's within 0.04 percent in all 23 years; oil and gas within 1 percent in 21 of 23 (2024 and 2025 differ by 1 to 3 percent: the monthly file is revised later than the annual).

## Decisions made without you

- **ONRR's "tons" taken as short tons,** the U.S. convention for coal; said in the header.
- **The annual file's minerals not taken** (salt, potash, soda ash, gold and the rest, and geothermal's direct use and steam, in units the ERW has no word for); its energy products are.
- **A FIPS code with two of ONRR's county names** (Kenai (Post) and Kenai (Pre)) kept as two places: the county's name is part of the key.
- **ONRR's terms not read in this session** (one request was left): ONRR is a bureau of the Department of the Interior, its data a federal work; session 956's round reads its terms first.

## Errors

- **The first file's request was redirected** from revenuedata.doi.gov to revenuedata.onrr.gov, a host whose robots file had not been read. Its robots file was asked at once, in a call of its own: the same as the first host's (it disallows only `/patterns/`). The two later files were asked of revenuedata.onrr.gov directly.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/onrr.py`, `tests/test_session951.py` (5 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv` (one row for the three tables, merged by hand after the resolver), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On main: `queue/next/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`.
- On the data machine only: `runs/c054/s951/`, `runs/license_reads/s951/`, `runs/s951*`, `warehouse/raw/onrr/`.
