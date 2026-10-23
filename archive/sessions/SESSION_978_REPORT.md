# Session 978 report: the world's energy outlook (EIA's International Energy Outlook 2023)

23 October 2026, from 13:38 UTC, on lab-desktop (the data machine), the first session of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`, taken right after chain 054 landed. Model spend USD 0. Pulls: 15 requests of 15 (api.eia.gov's robots file: none, HTTP 403 without a key; the `ieo` route's metadata, its 2023 release's, two facet lists and a third answered 429, a sample of five rows; the data's four pages twice, the first time sorted without the region).

## Read these first

- **Chain 056 written and pushed first:** `queue/next/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md` (sessions 2000 to 2013, machine: data), committed alone and pushed to main (`7dbd3722`; `git status -sb` showed nothing ahead), with a snapshot pair (`c055-056-before`, `-after`: 0 differences; Vercel rate-limited the deploy). The queue move of 055 went first with its own pair (`c055-take-before`, `-after`: 0 differences). **Its numbers:** 992 to 999 are the only free numbers below the old laptop's 1000, 965 to 969 a block of five, and the old laptop's files claim 1108 upward, so chain 056 takes 2000 to 2013, which no machine holds.
- **One table written, validated, archived, in coverage (sectors power and carbon, public), in the release package, both holds:** `eia_ieo_projections`, 17,856 rows (EIA's total for the five tables), 2020 to 2050 (2020 to 2022 marked HISTORIC, the rest PROJECTION), the reference case of the International Energy Outlook 2023: primary energy consumption by region (table 1) and by region and fuel (2), energy-related CO2 by region (10), and net electricity generation (20) and generating capacity (21) by region and fuel. Series: 51 consumption, 21 emissions, 231 generation, 273 capacity.
- **The cross-checks of the base years against EIA's statistics (`eia_world_energy_co2_annual`, `eia_world_electricity_annual`):** world CO2 within 1.6 percent (2021: 35,420 and 35,779 million tonnes), world net generation within 2 percent (2021: 27,364 and 27,842 TWh). Primary energy runs higher in the outlook: the U.S. by 4 percent (2021: 96,784 TBtu, against 93,364 in the international statistics and 93,375 in `eia_primary_energy_monthly`), the world by 9 percent (625,235 and 573,039). A difference of accounting is the likely cause: EIA's statistics now count noncombustible renewables by captured energy, which the outlook's 2023 model may not. Not checked further.

## Decisions made without you

- **The reference case and five tables,** as the chain asked first; the six other cases and 54 other tables (GDP, population, vehicles, sectors, coal trade) are not taken.
- **The region in the entity** (`eia_ieo2023:<table>:<regionId>:<seriesId>`): tables 20 and 21 repeat a series id for each of their 21 regions; the node adds the region's name.

## Errors

- **The first full fetch was sorted without the region,** so two of its four pages shared six rows and six others were missed; the run stopped on the repeated key, as it should. The sort now names every facet, the connector checks that the rows read equal EIA's total, and the pages were asked again: the ceiling's last four requests.
- **EIA's units were not the ones the documentation shows** ("MMmt", "bill kWh", "gigawatts"); each stopped a trial run until mapped (the saved pages reused, no extra request).
- **One facet request answered HTTP 429** (too many requests in a few seconds); later requests waited.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_ieo.py`, `tests/test_session978.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On main: `queue/next/056-evening-23-october-data-jobs-reactors-large-loads-hydro.md`.
- On the data machine only: `runs/c055/s978/`, `runs/license_reads/s978/`, `runs/s978*`, `warehouse/raw/eia_ieo/`.
