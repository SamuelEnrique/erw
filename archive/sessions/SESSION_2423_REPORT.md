# Session 2423 report: Cambodia closed; Georgia's electricity balance a month from ESCO in its place

24 October 2026, from 11:01 UTC, on lab-desktop (the data machine), a session of `queue/done/115-day-16-november-data-zambia-botswana-mongolia-cambodia.md`. Precheck passed (`runs/c115/precheck_2423.out`). Model spend USD 0.

Pulls: 14 requests of 15:
- **Cambodia, six:**
  - eac.gov.kh's robots file;
  - edc.com.kh's robots file (none: an error page), its home page and its annual reports page;
  - admin.edc.com.kh's robots file (HTTP 404) and the 2025 English report.
- **Georgia, eight:**
  - esco.ge's robots file (HTTP 404: none);
  - the English home page;
  - six yearly balance pages, 2021 to 2026.

The trial and the write ran offline.

## Read these first

- **Cambodia is closed to the reader:**
  - **The Electricity Authority of Cambodia:** its robots file disallows `/` to every reader.
  - **Electricite du Cambodge:** its annual reports page lists English reports to 2017 under plain names. The newer files are the Rural Electrification Fund's reports (labelled "REF"): the 2025 one has no generation tables, and its text barely extracts.
  - The file's rule replaces a host that bars the reader with another public grid source.
- **In Cambodia's place: Georgia, from the Electricity Market Operator (ESCO)** (not held; no chain planned it; chain 110 found Geostat's PxWeb has no energy section).
  - **Table:** `esco_georgia_electricity_monthly`, 1,514 figures, January 2021 to September 2026, internal (the footer reads "(c) 2016 ESCO ALL RIGHTS RESERVED", and no terms were found).
  - **Variables (23), MWh** (ESCO's million kWh times 1,000):
    - generation by thermal, wind, solar (2026) and hydro, with the regulating, seasonal and small hydro plants;
    - imports and inbound transit, the total resource, the plants' own losses, delivery to the network;
    - supply to the distribution companies and direct customers, stopped plants' consumption, exports, outbound transit;
    - network losses, total demand and total consumption.
  - **Source:** ESCO publishes each year's balance as two HTML tables on a page of its own. The connector reads the six pages from 2021. The pages for 2006 to 2020 are left for a later session (this session's ceiling).
- **The checks,** a month, within 0.01 million kWh:
  - the kinds add to generation and the hydro kinds to hydro;
  - generation, imports and transit add to the resource, and the resource less the plants' losses to the delivery;
  - the parts add to the supply to consumers;
  - supply, exports and transit add to `supplied_and_export`, and that plus the network losses to the total demand, which equals the delivery;
  - from 2022, the supply plus both kinds of losses equals the total consumption;
  - each line's months add to its printed annual total.
- **ESCO's own figures fail ten of these checks** (the numbers below are in million kWh).
  - **Kept as published,** each named in the header, never corrected:
    - August to December 2025: generation is 0.3 to 1.3 above its kinds, a remainder with no line (in 2026 ESCO adds a solar line of that size);
    - November 2025: total consumption is 0.085 over its parts;
    - January 2023: distribution plus direct customers is 320.82 under the supply to consumers;
    - March 2023: the total demand is 318.05 over the delivery.
  - **June 2021's inbound transit is blank:** it has no row. The total resource is 35.468 above generation plus imports that month, and that figure is not filled in.
  - **More than twelve such failures stops the run,** as a sign the pages changed form.
- **2021's form differs:** its line labelled "Total Consumption" equals supplied plus exports plus transit in every month, which later years call "Supplied to the Consumers and Export". The connector places such a line by its arithmetic, and stops if it matches neither.
- **Against `owid_ember_electricity_annual`'s Georgia demand**, ESCO's consumption (supply plus the plants' and the network's losses), in GWh:

  | Year | ESCO | Ember |
  |---|---|---|
  | 2021 | 14,260.3 | 14,260 |
  | 2022 | 14,808.6 | 14,810 |
  | 2023 | 13,717.3 | 13,750 |
  | 2024 | 14,414.3 | 14,110 |
  | 2025 | 14,884.0 | 14,700 |

  Ember's figures for 2021 and 2022 appear to be ESCO's.
- **Registered:**
  - the sector rule (`power`), the live-set hold;
  - the license tables (licenses check: 519 tables, 0 problems);
  - the test, `tests/test_session2423.py` (5 tests).

## Errors

- **The connector's first runs stopped:**
  - at 2021's form, which my code placed month by month and should have placed once a year;
  - at ESCO's own failed sums, which first stopped the run and are now kept and named;
  - at the blank cell.
- **The test's fixture could not build its own bad-value case;** corrected.
- **The write's metadata patch conflicted again** next to this chain's earlier rows. `runs/c102/add_own_rows.py` put in one row each.

## Decisions made without you

- **Georgia in Cambodia's place.** Its monthly balance is public HTML, back to 2006, and the ERW held no Georgian grid table.
- **ESCO's failed sums kept as published and named,** not corrected or dropped. Which cell is wrong cannot be told.
- **"All Rights Reserved" read as internal,** as for ERB (session 2420) and KPX.

## For Samuel's ruling

- **ESCO's terms:** a word from ESCO on reuse would settle whether the table can be public. Not asked.

## Files

- New: `warehouse/connectors/esco_georgia.py`, `tests/test_session2423.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c115/s2423/`, `runs/license_reads/s2423/`, `warehouse/raw/esco_georgia/`.
