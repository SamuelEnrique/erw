# Delivered and estimated undelivered energy of ISO-NE's dispatchable wind and solar plants, the whole system, a month (ISO-NE ISO Express, Aggregate Monthly DDG Undelivered Energy)

Energy Research Warehouse (ERW), method note written in session 2110 (chain 069) for a table first written on 7 October 2026 (session 149).

Tables: `isone_ddg_undelivered_monthly`

## Publisher and address

ISO New England (ISO-NE), ISO Express report "Aggregate Monthly DDG Undelivered Energy" (DDG: Do Not Exceed Dispatchable Generator, ISO-NE's name for a wind or solar plant it dispatches by a limit), one workbook a year and fuel:

- the page `https://www.iso-ne.com/isoexpress/web/reports/operations/-/tree/aggregate-monthly-ddg-undelivered-energy`
- its file list (JSON, the first page only) `https://www.iso-ne.com/isoexpress/web/reports/download/docWidgetGetMore?start=0&treenode=aggregate-monthly-ddg-undelivered-energy`
- a workbook `https://www.iso-ne.com/static-assets/documents/<folder>/<file>.xlsx`, named in the list "<YYYY> Undelivered Wind (or Solar) Energy Aggregate Report"

Eleven workbooks are in the table: wind for each year from 2018 to 2026 (`undeliveredaggregate2018.xlsx` to `undeliveredaggregate2025.xlsx`, and `2026-undelivered-wind-energy-aggregate-report.xlsx`) and solar for 2025 and 2026 (`2025-undelivered-solar-energy-aggregate-report.xlsx`, `2026-undelivered-solar-energy-aggregate-report.xlsx`). Plain requests with the one contact string the ERW sends, User-Agent "ERW research project, github.com/SamuelEnrique/erw": no cookie, no account. Source id `isone:ddg_undelivered_monthly`. Connector: `warehouse/connectors/isone_ddg_undelivered.py` (session 149), its only table, in two steps: `--pull` saves ISO-NE's files under `warehouse/raw/isone_ddg_undelivered/` (with its own `manifest.csv`, the list copies and `legal_notice.html`), and `--write` builds the table from them.

It is on no schedule, by the owner's ruling of 7 October 2026 as the connector states it: "The pull is made once; it is on no schedule, and a refresh needs a new ruling." No line of `warehouse/run_daily.sh`, `warehouse/refresh_*.sh`, `warehouse/run_data_machine.sh` or `.github/workflows/` runs it. The first date is session 149's report ("Run on 7 October 2026 (UTC)"; `isone_ddg_undelivered_monthly`, 840 rows) and the rows: the workbooks were retrieved on 7 October 2026 from 21:35:51 to 21:40:39 UTC, and the table was written by `--write` run `20261007T221501Z`.

## Vintage and revision

January 2018 to September 2026 in the file on the data machine, rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261007T221509Z-local`, with the header of the `--write` run `20261007T221501Z`. The header: "Held: solar 2025-07 to 2026-09 (15 months); wind 2018-01 to 2026-09 (105 months)", and "The pull against its ceilings, every run: 840 rows of the series (ceiling 2,000); 14 requests (ceiling 20); 1,954,281 bytes (ceiling 52,428,800)." Every row's `retrieved_at` is 7 October 2026. ISO-NE's list gave the 2026 workbooks a publish date of 10/07/2026 (12:39 PM EDT wind, 12:41 PM EDT solar), and the older ones dates from 10/15/2019 to 01/12/2026. `coverage.csv` gives the same 840 rows and dates (last run 2026-10-07T22:15:01Z).

`--write` rebuilds the whole table from the workbooks kept, each read as the table reads it; `ip.write_csv` merges on (entity, variable, ts_utc). `--pull` asks only for a workbook whose address is not already kept, so a workbook ISO-NE extends at the same address (the current year's) is not asked for again: months after September 2026 would need a new pull, and a ruling.

## Shape and variables

Series, 840 rows, one entity, 14 variables: seven for wind over 105 months (735 rows) and seven for solar over 15 months (105 rows). `entity` `isone:system`, the sheet "<YYYY> System" of each workbook, ISO-NE's own aggregate of the plants it dispatches by a limit; `freq` P1M; `ts_utc` the first of the month at 00:00:00Z; `unit` MWh for the four energies and pct for the three shares; `market` and `node` empty; `geo` US-CT,US-MA,US-ME,US-NH,US-RI,US-VT; `vintage` empty. The variables are `<fuel>_delivered_mwh` (DE [MWH]), `<fuel>_undelivered_mwh` (UE [MWH]), `<fuel>_undelivered_nonbinding_mwh` (UE-NonBind [MWH]), `<fuel>_undelivered_binding_mwh` (UE-Bind [MWH]), and `<fuel>_undelivered_pct`, `<fuel>_undelivered_nonbinding_pct`, `<fuel>_undelivered_binding_pct` (ISO-NE's fraction of UE plus DE, written times 100). ISO-NE's definitions are quoted in the table's header.

| Variable | Months | Mean | Lowest | Highest |
|---|---|---|---|---|
| `wind_delivered_mwh` | 105 | 293,917 | 125,291 (July 2023) | 453,594 (September 2026) |
| `wind_undelivered_mwh` | 105 | 4,870 | 161 (July 2023) | 18,029 (April 2025) |
| `wind_undelivered_nonbinding_mwh` | 105 | 1,529 | 81 (August 2021) | 12,774 (June 2025) |
| `wind_undelivered_binding_mwh` | 105 | 3,341 | 57 (July 2023) | 14,578 (April 2025) |
| `wind_undelivered_pct` | 105 | 1.564 | 0.128 (November 2024) | 5.690 (June 2025) |
| `wind_undelivered_nonbinding_pct` | 105 | 0.502 | 0.027 (November 2024) | 5.157 (June 2025) |
| `wind_undelivered_binding_pct` | 105 | 1.062 | 0.045 (July 2023) | 4.357 (May 2025) |
| `solar_delivered_mwh` | 15 | 136,264 | 52,526 (January 2026) | 198,625 (July 2026) |
| `solar_undelivered_mwh` | 15 | 837 | 4.06 (November 2025) | 2,879 (May 2026) |
| `solar_undelivered_nonbinding_mwh` | 15 | 608 | 4.06 (November 2025) | 1,539 (June 2026) |
| `solar_undelivered_binding_mwh` | 15 | 228 | 0 (July, August and November 2025) | 1,573 (May 2026) |
| `solar_undelivered_pct` | 15 | 0.573 | 0.005 (November 2025) | 1.686 (May 2026) |
| `solar_undelivered_nonbinding_pct` | 15 | 0.429 | 0.005 (November 2025) | 0.877 (February 2026) |
| `solar_undelivered_binding_pct` | 15 | 0.144 | 0 (July, August and November 2025) | 0.921 (May 2026) |

By year, from the monthly rows (undelivered as a share of undelivered plus delivered): wind 2018 3,356,351 MWh delivered, 2.799% undelivered; 2019 3,470,824, 1.917%; 2020 3,425,914, 1.585%; 2021 3,452,292, 1.813%; 2022 3,721,071, 1.376%; 2023 3,148,025, 1.092%; 2024 3,273,205, 0.717%; 2025 3,701,894, 1.854%; 2026 to September 3,311,726, 1.421%. Solar July to December 2025 743,550 MWh, 0.091%; 2026 to September 1,300,409, 0.904%. The binding part is 59% to 79% of wind's undelivered energy in each year, and 11% (2025) and 28% (2026) of solar's.

## Reading ISO Express

- `--pull` first checks ISO-NE against `warehouse/metadata/paused_sources.csv` (it is not paused) and makes no request if it is. It saves ISO-NE's legal notice once (when the manifest holds none), then the list's first page (or, with `--reuse-list`, the copy saved last), then each workbook not kept, at most `--limit` a run. A full first page (40 entries) is logged; a second page is not asked for.
- Ceiling, over every run of the connector: 2,000 rows of the series, 20 requests and 50 MB. Each request is counted before it is made, a workbook allowed 84 rows and 2 MB, and the request that would pass any of the three is not made. The rows are counted from the kept workbooks themselves.
- One try a request, no retry: a request that fails is recorded in the manifest and stops the pull. HTTP 401 or 403, or a page where a workbook should be (an answer not beginning "PK"), is an access control: recorded, and nothing more is asked. Any other answer that is not HTTP 200 is recorded and stops the pull. Three seconds after each request answered.
- A workbook is read only as session 149 read it: ISO-NE's description must name the year and fuel; the sheet "<YYYY> System" must be there, with a line holding DE [MWH]; every column label must be one of the seven; the twelve lines under it must be January to December in order. A blank cell (a month not yet published) is no row; text where a number should be, or a number that is not finite, stops the read. ISO-NE's fractions are written times 100.
- `--write` makes no request (and does not consult the pause file). Two workbooks that print the same fuel, month and figure stop the build: nothing is chosen between them. It reports, never corrects, ISO-NE's figures against each other (below). No test of the newest month's age.

## License

The header: "License: internal. The owner's ruling of 7 October 2026: pulled and held internal. ISO-NE's legal notice: "You are also hereby put on notice that the Content is protected by copyright under United States laws. Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." (https://www.iso-ne.com/legal-privacy, read 7 October 2026). Not published, in no public dataset, no download and no page." `coverage.csv`: internal. `license_tables.csv` names ISO-NE as the table's one publisher (from the source registry); `license_verdicts.csv` gives ISO-NE "needs written permission" (read 4 of `license_reads.csv`, 12 October 2026). `docs/licenses.md`: flag and verdict agree; ERW verdict internal. The curtailment page's ISO-NE hover reads "Held, not shown" (session 149).

## Cross-checks (session 2110)

- The counts above were computed from the rows, read past the 19 header lines; no (entity, variable, ts_utc) is given twice.
- Months complete: wind holds every month from January 2018 to September 2026 for all seven figures, and solar every month from July 2025 to September 2026. The 2025 solar workbook gives July to December only (42 rows).
- UE equals UE-NonBind plus UE-Bind in every month, to within 0.00000000001 MWh, and ISO-NE's percent UE equals 100 times UE over UE plus DE to within 0.0000000001 points, for both fuels, as the header's own check says.
- The connector has no cross-check beyond these and its reading rules.

## What it does not hold

- The six other sheets of each workbook (ME, System wo ME, ORR_SO, System wo ORR_SO, Congested, Uncongested): kept in the raw files, not in the table. Session 149: all seven aggregations would be about 5,900 rows, past the ceiling.
- Wind and solar plants ISO-NE does not dispatch as DDG, and any hour or day: ISO-NE's estimate, monthly, not a metered curtailment.
- Wind before January 2018, solar before July 2025, and any month after September 2026.

## Found while writing this note

- The connector's docstring gives the owner's ruling as "about 1,000 rows"; the table holds 840 (the pull counted 840 of its ceiling of 2,000). An estimate, not a fault in the rows.
