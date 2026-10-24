# Georgia's electricity balance a month from the Electricity Market Operator (ESCO): generation by kind of plant, imports, transit, losses, supply to consumers and exports, January 2021 to September 2026

Energy Research Warehouse (ERW), method note written in session 2429 (chain 115) for a table first written on 24 October 2026 (session 2423 of chain 115, `archive/sessions/SESSION_2423_REPORT.md`, commit `0ae8713d`), taken in place of Cambodia, whose regulator's robots file disallows every path. The license verdict is session 2425's (`archive/sessions/SESSION_2425_REPORT.md`). Ember's yearly demand for Georgia, against which session 2423 compared it, is in `owid_ember_electricity_annual` (entity `owid_energy:GEO`).

Tables: `esco_georgia_electricity_monthly`

## Publisher and address

Electricity Market Operator of Georgia (ESCO), Energy Balance, "Actual Balance": one HTML page a year under `https://esco.ge/en/energy-balance/by-year-1`, each with two tables (supply and consumption, million kWh, a column a month and a total), asked by GET without a key. The six pages read, by the slugs in the connector's `YEARS`:

- `https://esco.ge/en/energy-balance/by-year-1/elektroenergiis-balansi-2021`
- `.../elektroenergiis-balansi-2022`, `.../balansi-2023`, `.../elektroenergiis-balansi-2024`, `.../balance-2025`, `.../balnsi-2026`

Source id `esco_ge:actual_balance` (`sources.csv`: license internal, first and last seen 2026-10-24). The balances for 2006 to 2020 are on pages of their own, not read (session 2423's ceiling).

Saved pages, in `warehouse/raw/esco_georgia/20261024T110109Z_probe/`, fetched by session 2423's probe, not by the connector, each HTTP 200 with no Last-Modified:

| Year | Bytes | sha256 | Retrieved (UTC) |
|---|---|---|---|
| 2021 | 67,216 | `f3b63ede...` | 2026-10-24T11:03:34Z |
| 2022 | 67,546 | `1ac33f74...` | 11:03:30Z |
| 2023 | 67,410 | `3a82e96a...` | 11:03:26Z |
| 2024 | 67,472 | `d5f543c7...` | 11:03:23Z |
| 2025 | 67,378 | `f857b931...` | 11:02:48Z |
| 2026 | 67,515 | `ec04efc8...` | 11:03:19Z |

The 2025 page is also read 783 in `docs/licenses.md` (the same size and time). The connector's run folders (`20261024T110707Z`, an empty manifest, and `20261024T110718Z`) hold only the data-lock check, so its runs were offline. esco.ge has no robots file (read 721, HTTP 404). Session 2423 made 14 requests of 15, 8 of them to esco.ge (the report). In the saved pages the wind line reads "Kartli Wind Power Plant" from 2021 to 2025 and "Wind Power Plants" in 2026, the line "Solar power plants" is on the 2026 page only, and the line "Supplied to the Consumers and Export" is on every page but 2021's.

Connector: `warehouse/connectors/esco_georgia.py` (session 2423), `[--offline] [--out-dir DIR]`.
- **Ceiling:** one request a year's page, 2 seconds apart; a page saved is reused unless `fresh`. In the code, a page is fetched again online when its year is the current year or the one before (`y >= this_year - 1`); the docstring said only the current year's until session 2429 (Checks). A paused `esco_ge` or host esco.ge is never asked.
- **Values:** ESCO's million kWh times 1,000, written as MWh rounded to 0.001.
- **"Total Consumption":** placed once a year by its arithmetic in January: `supplied_and_export` where it equals supplied plus exports plus transit (2021), `total_consumption` where it equals supplied plus the plants' losses plus the network losses (2022 on); a line that is neither stops the run.
- **Checks a month,** within 0.01 million kWh: the kinds add to generation and the three hydro kinds to hydro; generation, imports and transit to the total resource; the resource less the plants' losses to the delivery to the network; distribution, direct customers and stopped plants to the supply to consumers; supply, exports and transit to `supplied_and_export`; that plus the network losses to the total demand; the total demand equal to the delivery; from 2022, supply plus both losses to the total consumption. A check that fails is ESCO's own figure: every figure is kept and the month and check are named in the header. A blank cell in a month published has no row and is named. More than 12 such cases stops the run.
- **Stops also:** months not ESCO's, a label not in the map, a value that is not a number, a line's months not adding to its printed total within 0.15, a line twice, months published not from January on, or a key given twice.

## Schedule and records

Schedule: none. No shell script under `warehouse/`, no workflow in `.github/workflows/`, no file in `scripts/` and not `warehouse/scheduled.py` names it.

Records:
- `runs/status/esco_georgia.json` (main checkout): run `20261024T110718Z`, ok, "1514 rows". `run_status.csv`: no row.
- `archive_manifest.csv`: 1,514 rows, run `20261024T110723Z-local`, `data_sha256` `1c91791f...`, which is the data hash of the file in the main checkout (recomputed in session 2429).
- `coverage.csv`: iso `esco`, 1 node, P1M, 2021-01-01 to 2026-09-01, 1,514 rows, last run 2026-10-24T11:07:18Z, validator pass, license internal, sector power, tier source.
- Live set: listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`, not loaded.
- Release: no row in `docs/redivis/release-v1/tables.csv`, `redivis_uploads.csv` or `redivis_uploads_stanford.csv`.
- Package: `package/src/erw/data/tables.csv` has its row since session 2431 (internal, "needs written permission"); `site/data/table_citations.json` and `table_verdicts.json` have none.
- `license_tables.csv`: Electricity Market Operator of Georgia (ESCO), "the source registry".

Readers: none. `tests/test_session2423.py` (5 tests) tests the reader on a page built in the test.

License: `license_verdicts.csv`, read 782 (session 2423's read of the English home page's footer): "(c) 2016 ESCO ALL RIGHTS RESERVED" (the page and the verdict file have the copyright sign where this note writes "(c)"), verdict "needs written permission", the same if the ERW sells anything (session 2425). `docs/licenses.md`, the table's row: verdict "needs written permission", flag internal, "agrees", ERW verdict internal; under "Permission needed", ESCO: "Write to: no person or address on the page read." Header line 9 and the docstring said "internal until a ruling" until session 2429 (Checks).

## Vintage and revision

One write, run `20261024T110718Z`, offline from the saved pages; header line 10: "This run wrote 1514 rows: 1514 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `retrieved_at` is the year's page's fetch (the table above) in every row of that year; `source_url` is the year's page. `vintage` is blank in every row: the pages carry no Last-Modified.

ESCO's months not yet published have no row; October 2026 on comes with a later run of the 2026 page. A revised figure replaces the old one by (entity, variable, ts_utc); no earlier version is kept.

## Shape and variables

Series, 1,514 rows, 13 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`), 10 header lines. `entity` `esco_ge:GE` in every row; `node` Georgia; `geo` GE; `unit` MWh; `freq` P1M; `ts_utc` the month's 1st at 00:00:00Z, 69 months, January 2021 to September 2026; `market` blank.

- **Variables, 23:** on the supply side `generation`, `generation_thermal`, `generation_wind`, `generation_solar`, `generation_hydro`, `generation_hydro_regulating`, `generation_hydro_seasonal`, `generation_hydro_small`, `imports`, `transit_in`, `total_resource`, `plant_losses_self_consumption`, `delivery_to_network`; on the consumption side `supplied_to_consumers`, `supplied_distribution`, `supplied_direct_customers`, `self_consumption_stopped_plants`, `exports`, `transit_out`, `supplied_and_export`, `network_losses` (ESCO's "Transportation Expences"), `total_demand_incl_losses`, `total_consumption`.
- **Rows:** 69 for 20 variables; `generation_solar` 9 (January to September 2026, the line ESCO adds in 2026); `total_consumption` 57 (2022 on: in 2021 ESCO's line of that name is written as `supplied_and_export`); `transit_in` 68 (June 2021 blank).
- **Rows a year:** 251 (2021), 264 (2022 to 2025 each), 207 (2026, nine months).
- **Values:** every value is a whole number of MWh. No negative. 65 zeros: `transit_in` 25, `transit_out` 25, `exports` 6, `imports` 5, `generation_thermal` 4.
- **The largest value** is the total demand of March 2023, 1,908,666 MWh, the month whose total demand is 318.05 GWh over the delivery (Checks).

Years, GWh (sums of the months written; 2026 to September):

| Year | Generation | Hydro | Thermal | Wind | Solar | Imports | Exports | Transit in | Transit out | Consumption |
|---|---|---|---|---|---|---|---|---|---|---|
| 2021 | 12,645.0 | 10,182.1 | 2,379.6 | 83.4 | | 2,006.2 | 391.0 | 1,148.2 | 1,183.7 | 14,260.3 |
| 2022 | 14,246.5 | 10,771.3 | 3,387.7 | 87.5 | | 1,533.2 | 971.1 | 3,160.3 | 3,160.3 | 14,808.6 |
| 2023 | 14,395.8 | 10,863.2 | 3,446.5 | 86.1 | | 789.8 | 1,468.4 | 3,444.5 | 3,762.5 | 13,717.3 |
| 2024 | 14,234.1 | 11,344.4 | 2,812.2 | 77.6 | | 1,227.5 | 1,047.4 | 1,074.3 | 1,074.3 | 14,414.3 |
| 2025 | 13,837.7 | 10,986.6 | 2,767.1 | 79.4 | | 1,557.5 | 511.2 | 665.3 | 665.3 | 14,884.0 |
| 2026 | 10,308.4 | 8,422.5 | 1,783.5 | 88.3 | 14.1 | 1,186.5 | 250.0 | 0.0 | 0.0 | 11,244.9 |

Consumption here is supplied to consumers plus the plants' losses plus the network losses, the arithmetic of ESCO's "Total Consumption" from 2022.

## Checks

Counted in session 2429 from the table in the main checkout (`C:\Users\Shared\Documents\erw\warehouse\output`), read past its 10 header lines with `keep_default_na=False`, and from the saved pages' line labels, by scripts outside the repository. No request was made.

- 1,514 rows, 2021-01-01 to 2026-09-01, as header line 10 states; no (entity, variable, ts_utc) twice; no blank value.
- **The connector's identities, recomputed** within 0.01 million kWh (10 MWh), a blank counted as 0:

| Check | Months | Hold | Fail |
|---|---|---|---|
| thermal + wind + solar + hydro = generation | 69 | 64 | 5: August to December 2025, the kinds 0.346, 0.782, 1.298, 1.218 and 0.928 GWh under generation |
| regulating + seasonal + small = hydro | 69 | 69 | 0 |
| generation + imports + transit in = total resource | 69 | 68 | 1: June 2021, 1,327.734 against 1,363.202 GWh (35.468 under; transit in blank) |
| total resource - plants' losses = delivery | 69 | 69 | 0 |
| distribution + direct + stopped plants = supply to consumers | 69 | 68 | 1: January 2023, 962.310 against 1,283.130 GWh (320.82 under) |
| total demand = delivery | 69 | 68 | 1: March 2023, 1,908.666 against 1,590.615 GWh (318.051 over) |
| supply + exports + transit out = supplied_and_export | 69 | 69 | 0 |
| supplied_and_export + network losses = total demand | 69 | 69 | 0 |
| supply + plants' losses + network losses = total consumption | 57 | 56 | 1: November 2025, 1,240.226 against 1,240.311 GWh (0.085 under the printed figure) |

  These are the nine failed checks named in header line 3, and with June 2021's blank inbound transit the ten cases the docstring and the report count. The figures agree with header line 3 to the 0.001 GWh.
- **Transit:** outbound transit equals inbound in every month but two. In June 2021 inbound is blank and outbound is 35.467 GWh, within 0.001 of that month's resource gap (35.468). In March 2023 inbound is 444.774 and outbound 762.825, 318.051 more, the same as that month's total demand over the delivery. These are observations; nothing is filled or corrected.
- **Against Ember** (`owid_ember_electricity_annual`, `owid_energy:GEO`, `electricity_demand`, MWh, to 2025): consumption as above over Ember's demand is 1.0000 (2021), 0.9999 (2022), 0.9976 (2023), 1.0216 (2024) and 1.0125 (2025). The report's table (ESCO 14,260.3, 14,808.6, 13,717.3, 14,414.3, 14,884.0 GWh against Ember's 14,260, 14,810, 13,750, 14,110, 14,700) holds; the report reads Ember's 2021 and 2022 as ESCO's own figures.
- **The docstring against the code on re-fetching:** the docstring says "one request a year (six when written; the current year's page fetched again on a run, the others reused)"; the code (`fresh=not args.offline and y >= this_year - 1`) fetches the current year's page and the previous year's again on an online run, two requests in 2026, not one. Changed in session 2429 (below).
- **License wording:** header line 9 and the docstring say "internal until a ruling"; session 2425 has since recorded "needs written permission" for ESCO (read 782). The flag (internal) and the verdict agree. Changed in session 2429 (below).

## What it cannot say

- **2006 to 2020:** on ESCO's other pages, not read.
- **Which figure is wrong** in a month that does not add (above): the table keeps ESCO's figures as published.
- **Solar before 2026:** ESCO has no solar line before 2026; the remainder under generation in August to December 2025 has no line of its own.
- **Plant by plant, hours, prices, peak demand and the partner of a trade:** not in the balance tables.
- **Earlier versions of a revised month.**

## Acted on in session 2429

The two helpers who drafted this chain's notes made no request and changed no other file; every point was read and acted on or recorded:

- **The docstring on re-fetching** now says what the code does: the current and the previous year's pages are asked again on an online run, the others reused. The code is kept: a year's balance is revised early in the next.
- **The license wording:** the docstring and header line 9 now give session 2425's verdict, "needs written permission", and the footer as the page has it, with the copyright sign. The table was written again offline (run `20261024T115505Z`): the same 1,514 rows, its metadata rows replaced by key; only the header changed, and the archive's data hash is the same (`1c91791f...`).
- **The transit observations** (June 2021, March 2023) are recorded here and in the chain's note; nothing is filled or corrected.
