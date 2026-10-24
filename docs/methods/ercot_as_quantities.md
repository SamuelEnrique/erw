# ERCOT's ancillary service plan, MW by product and hour (ERCOT's DAM Ancillary Service Plan)

Energy Research Warehouse (ERW), method note written in session 2138 (chain 090) for a table first written on 3 October 2026 (session 74).

Tables: `ercot_as_quantities`

How the battery model uses these quantities is in `docs/methods/battery_stack.md` (session 74 and later); this note describes the code and the rows as they stand.

## Publisher and address

Electric Reliability Council of Texas (ERCOT), "DAM Ancillary Service Plan", data product NP4-33-CD (report type 12316), page `https://www.ercot.com/mp/data-products/data-product-details?id=NP4-33-CD`. The connector reads ERCOT's list, `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=12316`, and asks for each zip at `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>`, the route `ercot_as_prices.py` uses. Source id `ercot:np4-33-cd`. Connector: `warehouse/connectors/ercot_as_quantities.py` (session 74), one step: it asks, reads and writes in one run. It borrows the time handling, the service list and the completeness rule of `ercot_as_prices.py`.

## Vintage and revision

Delivery days 3 September to 12 October 2026 (Central) in the file on the data machine, 40 days, none absent between them. The file was last written by run `20261011T200229Z` (11 October 2026). That run's header gives its own window, "delivery days 09/11/2026 to 10/12/2026 (32 days)", and its merge line: "File holds 4800 rows ... This run wrote 3840 rows: 960 new, 2880 replacing earlier rows ... 960 rows are kept from earlier runs." The 960 kept rows are 3 to 10 September, from the first run of 3 October 2026, whose rows say `retrieved_at` 2026-10-03T10:23:53Z or 10:23:54Z; the other 3,840 rows say one of 32 times of 11 October, 20:02:39Z to 20:04:22Z.

ERCOT posts one CSV a day at 05:00 Central, each with the plan for the next seven delivery days: every one of the 32 zips saved by the run of 11 October holds seven delivery days, and every row's `vintage` (the list's PublishDate, in UTC) is 05:00 Central. A delivery day is taken from the file published the day before it, the plan that day's market used: in all 4,800 rows the delivery day is one day after the publish day. The other six days of each file are not read, so a later plan for a day never replaces this one. Rows are merged into the file held on (entity, variable, ts_utc) (`iso_prices.write_csv`), so a day once written stays.

No job runs the connector: neither `warehouse/run_daily.sh` nor `warehouse/run_data_machine_tables.sh` names it. The docstring says the table "grows by a day each run if the connector is scheduled"; it is not scheduled, and the file has not been written since 11 October 2026. ERCOT's list held 32 CSV files on 11 October (published 10 September to 11 October 2026), so a day not read within about a month is lost to the public list.

## Shape and variables

Series, 4,800 rows: 5 entities, 1 variable, 960 rows each. `variable` quantity_mw_plan, the MW ERCOT plans to procure in the day-ahead market for the hour; `unit` MW; `freq` PT1H; `ts_utc` the start of the delivery hour (`ercot_as_prices.to_utc`: hour ending 01:00 to 24:00 Central, the repeated hour told apart by DSTFlag); `geo` US-TX; `market` ercot_dam; `node` the service as ERCOT names it; `source_url` the zip the day came from (40 addresses); `vintage` its publish time. Every value is a whole number of MW.

| Entity | Rows | Days | Lowest MW | Mean MW | Highest MW |
|---|---|---|---|---|---|
| ercot:ECRS | 960 | 40 | 808 | 1,676.1 | 2,842 |
| ercot:NSPIN | 960 | 40 | 1,670 | 2,553.9 | 3,936 |
| ercot:REGDN | 960 | 40 | 246 | 451.0 | 697 |
| ercot:REGUP | 960 | 40 | 251 | 477.2 | 848 |
| ercot:RRS | 960 | 40 | 2,344 | 2,517.4 | 2,867 |

Each entity holds 24 hours on each of its 40 days; no day of the window has a clock change. The mean plan was higher in the October days held than in September for NSPIN (3,068.8 against 2,333.2 MW) and RRS (2,734.7 against 2,424.3 MW).

## Reading the source

- The connector does not ask `iso_prices.paused()` before it reaches ERCOT. ERCOT is not in `paused_sources.csv` today; if it were, this connector would still ask.
- The list is asked afresh each run; each zip goes through `iso_prices.fetch_raw`, which reuses a saved copy when an earlier run of this connector on the machine saved it. A request that is not answered with HTTP 200 is tried up to four times (`iso_prices.with_retries`, the waits growing by 5 seconds), timeout 180 seconds; HTTP 404 is not retried. Requests are 3 seconds apart (`ercot_as_prices.PAUSE`). Any failure stops the run and no file is written.
- `parse` stops the run when a zip holds other than one CSV, when the columns are not exactly DeliveryDate, HourEnding, AncillaryType, Quantity, DSTFlag, when a service is not one of REGUP, REGDN, RRS, NSPIN, ECRS, when a quantity is not a number, when an hour ending is not HH:00 from 1 to 24, when a DSTFlag is not Y or N, or when a time does not exist in Central time. A blank quantity is no row.
- Completeness (`ercot_as_prices.complete_days`): a repeated (service, hour) stops the run; a (service, delivery day) is written only with every hour of the Central day once, 24, or 23 or 25 at a clock change. A day left short, or a day missing from the file published the day before, is named in the header under "Left out"; the run of 11 October names none.
- Ceiling: 400,000 rows (session 74's approved pull), counted on the rows this run writes, not on the file after the merge. The file holds 4,800.
- `retrieved_at` is the time each document was read in the run (`pd.Timestamp.now`), not the first download that `fetch_raw` records: a zip reused from the raw files is cited at its reading time.

## License

Public. `license_verdicts.csv` records ERCOT, read 2 (`https://www.ercot.com/help/terms`, 12 October 2026 in `license_reads.csv`): "may be public", for public and for commercial use. The sentence: "raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices." The header cites the terms' item 5; the saved verdict does not number the item. `sources.csv` flags `ercot:np4-33-cd` public; `license_tables.csv` lists the table under ERCOT.

## Cross-checks (session 2138)

- The counts above were computed from the rows, read past the header lines. No (entity, variable, ts_utc) is given twice, and no hour of the 40 days is missing for any service.
- The delivery day of every row is the day after its `vintage` (Central), as the docstring says, and each saved file holds seven delivery days, as it says.
- Against `ercot_as_prices` (ERCOT's day-ahead clearing prices, variable mcpc_dam): all 4,800 (service, hour) rows of this table have a price for the same service and hour there; none lacks one. The two tables come from different ERCOT reports (a plan published the day before, and the market's clearing price), so this checks that their hours and service names line up, not their values.

## What it does not hold

- Delivery days before 3 September 2026: ERCOT's public list keeps about a month, and no keyless public source of the history was found (session 74; ERCOT's archive API needs a subscription key).
- Days after 12 October 2026, until the connector is run again.
- The cleared or awarded quantities: this is the plan. What each storage resource was awarded is in `ercot_sced_esr_hourly` (real time) and `ercot_dam_esr_awards` (day-ahead).
- The later plans for a day (the six other days of each file).
