# Daily vessel transits of the Strait of Hormuz, the Suez Canal and the Panama Canal (IMF PortWatch)

Energy Research Warehouse (ERW), method note written in session 2032 (chain 058) for a table first written on 26 September 2026 (session 8).

Tables: `portwatch_chokepoint_transits`

## Publisher and address

International Monetary Fund, IMF PortWatch, Daily Chokepoints Data, a public ArcGIS FeatureServer (`https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query`, `URL`); portal `https://portwatch.imf.org/pages/cb5856222a5b4105adc6ee7e880a1730` (`PAGE`). For each chokepoint of `CHOKEPOINTS` the connector asks `where=portid='<id>'`, every field, JSON, ordered by ObjectId, no geometry, `PAGE_SIZE` (1,000) rows a request, and moves on by offset until a page holds fewer than 1,000 rows and the service does not report `exceededTransferLimit`, or a page is empty (`fetch`). Source id `imf:portwatch-daily-chokepoints`. Connector: `warehouse/connectors/portwatch.py` (session 8); the daily sequence runs it as the step `portwatch` (`warehouse/run_daily.sh`).

## Vintage and revision

The file on the data machine was rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261021T153147Z-github`, as its first header line says; that run's own header follows: retrieved `20261021T145125Z` (21 October 2026), "Window: the full history the service offers (from 2019-01-01); every run replaces all of it."

`retrieved_at` takes 32 values, from 2026-09-29T01:08:45Z to 2026-10-21T14:51:42Z; `source_url` is the address of the page of results a row came from (9 addresses). The archive keeps the rows each run found new or changed (`ARCHITECTURE.md`), so a restored row carries the `retrieved_at` it has in the archive, not the time of the latest run.

Each run reads every row the service holds for the three chokepoints; the code asks for no start date, and the rows begin on 1 January 2019. The rows are merged into the existing file by (entity, variable, ts_utc) (`iso_prices.write_csv`, `merge_series`); the file is not deleted first. A value PortWatch changes replaces the old row; a row PortWatch no longer serves stays in the file. A chokepoint whose newest date is more than `STALE_DAYS` (10) days before today, on the machine's local clock (`pd.Timestamp.now()`), stops the table.

## Shape and variables

Series, 119,616 rows: 42 series, 14 variables on each of 3 entities, 2,848 days each, every calendar day from 1 January 2019 to 18 October 2026. `ts_utc` PortWatch's date at 00:00:00Z; `freq` P1D; `node` the chokepoint's name; `geo`, `market` and `vintage` empty.

| Entity | `node` |
|---|---|
| `portwatch:chokepoint6` | Strait of Hormuz |
| `portwatch:chokepoint1` | Suez Canal |
| `portwatch:chokepoint2` | Panama Canal |

| Variables | Unit | Rows |
|---|---|---|
| `n_tanker`, `n_container`, `n_dry_bulk`, `n_general_cargo`, `n_roro`, `n_cargo`, `n_total`: vessel transits in the day | count | 59,808 |
| `capacity_tanker`, `capacity_container`, `capacity_dry_bulk`, `capacity_general_cargo`, `capacity_roro`, `capacity_cargo`, `capacity`: the deadweight tonnage of those transits | dwt | 59,808 |

## Reading the source

- A chokepoint with no rows stops the table (`main`).
- Every row's `portname` must be the name `CHOKEPOINTS` gives its `portid`, or the table stops.
- A field of the 14 variables, or `date`, missing from the answer stops the table.
- A date given twice stops the table.
- A calendar day missing between a chokepoint's first and last date stops the table: the completeness rule.
- A newest date more than 10 days old stops the table.
- An empty value stops the table; nothing is skipped or counted.
- Every field is asked for (`outFields=*`); only the 14 variables and the date are written.
- Each page is tried up to 4 times (`iso_prices.with_retries`, `RETRIES`), with a wait of 5 seconds times the attempt number after each failure; an answer that is not HTTP 200, or JSON carrying `error`, is a failure; timeout 120 seconds.
- No row ceiling is set in the code.
- Any failure is recorded as a failure, and no file is written: `main` does not call `iso_prices.gap_skip`.
- The connector does not call `iso_prices.paused()`; the IMF is not in `warehouse/metadata/paused_sources.csv`.

## License

Internal. `sources.csv` has `internal` for `imf:portwatch-daily-chokepoints`; the header of the file on the data machine (the connector's line was corrected by session 2032 and takes effect at the next run): "License: internal. Cite "IMF PortWatch"; IMF terms unconfirmed (terms page 403), so internal until confirmed (session 8 ruling)." `license_verdicts.csv`, IMF PortWatch, read 13 (the IMF's Copyright and Usage page, read 12 October 2026, HTTP 200; session 311: PortWatch has no terms page of its own, and its contact page sends terms questions to the IMF): "may be public", and "needs written permission" for commercial use (contact copyright@imf.org). The sentence read includes "The IMF prohibits bulk download of information by automated technology without explicit permission". PortWatch's own page was not read.

## Cross-checks (session 2032)

- The counts above were computed from the rows, read past the header lines; the 119,616 rows equal the header's count, and no (entity, variable, ts_utc) appears twice.
- On all 8,544 chokepoint days, `n_cargo` equals the sum of `n_container`, `n_dry_bulk`, `n_general_cargo` and `n_roro`, and `n_total` equals `n_tanker` plus `n_cargo`. The same sums of capacity differ by at most 3 dwt (`capacity_cargo` against its four kinds, on 7,521 days) and 1 dwt (`capacity` against `capacity_tanker` plus `capacity_cargo`, on 4,366 days): PortWatch's figures are not exact sums.
- No value is below zero; every count is a whole number.
- Mean daily tanker transits of the Strait of Hormuz: 41.99 in 2019, 48.18 in 2025, 9.47 in 2026 to 18 October. The table does not say why.
- 18 October 2026: Hormuz 2 tanker transits of 4; Suez 15 of 43; Panama 13 of 29.
- The connector's own cross-check is its completeness rule.

## What it does not hold

- Chokepoints other than the three `portid`s of `CHOKEPOINTS`, and port calls.
- The service's other fields: read and not written.
- Single vessels, cargo carried or flags: a row is a day's count or tonnage.
