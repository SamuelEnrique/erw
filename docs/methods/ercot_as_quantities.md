# Ancillary service quantities ERCOT plans to buy in the day-ahead market, an hour (ERCOT NP4-33-CD, DAM Ancillary Service Plan)

Energy Research Warehouse (ERW), method note written in session 2152 (chain 092) for a table first written on 3 October 2026 (session 74).

Tables: `ercot_as_quantities`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), report NP4-33-CD, "DAM Ancillary Service Plan" (report type 12316), on ERCOT's public reports site: one zip a day, each holding one CSV with the plan for the next seven delivery days (columns DeliveryDate, HourEnding, AncillaryType, Quantity, DSTFlag; Central time). Every file in the table was published at 10:00 UTC (05:00 Central).

`https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=12316` (the document list, JSON)

`https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<DocID>` (each zip)

Product page `https://www.ercot.com/mp/data-products/data-product-details?id=NP4-33-CD`, named in the header and not asked. Every request goes to the host `www.ercot.com`, under `/misapp/` and `/misdownload/`, paths ERCOT's robots file disallows (read by session 850, and again by session 2002 at 15:11:50 UTC on 23 October 2026, read 170 of `warehouse/metadata/license_reads.csv`). No User-Agent of its own is sent. Source id `ercot:np4-33-cd` (lower case, unlike the ids of the other ERCOT reports). Connector: `warehouse/connectors/ercot_as_quantities.py` (session 74), its only table; it takes ERCOT's time handling, completeness rule and addresses from `warehouse/connectors/ercot_as_prices.py`.

It is not scheduled: no line of `warehouse/run_daily.sh`, the `warehouse/refresh_*.sh` scripts, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh` or `.github/workflows/` calls it. Session 74's report gave the line a person could add (`run_other ercot_as_quantities "$PYTHON" warehouse/connectors/ercot_as_quantities.py`); it was not added. The table was written by two runs, on 3 October 2026 (session 74) and at 20:02:29 UTC on 11 October 2026 (the header and `warehouse/output/logs/ercot_as_quantities_20261011T200229Z.log`); `run_status.csv` holds no row for this connector. The first date is from session 74's report (3 October 2026, about 10:20 to 10:55 UTC: 3,840 rows, 2026-09-03 to 2026-10-04) and from the rows: the earliest `retrieved_at` is 3 October 2026 10:23:53 UTC, and `sources.csv` first saw the report on 2026-10-03.

## Vintage and revision

Central delivery days 3 September to 12 October 2026 (3 September 2026 05:00 UTC to 13 October 2026 04:00 UTC), 40 days, in the file on the data machine, last written by run `20261011T200229Z`, whose header reads: "Window: delivery days 09/11/2026 to 10/12/2026 (32 days)". The rows' `retrieved_at` are 3 October 2026 (960 rows, delivery days 3 to 10 September) and 11 October 2026 (3,840 rows, 11 September to 12 October). `vintage` is the file's PublishDate: 40 files, one for each day held, and every row's delivery day is the day after its file's publish day (checked on every row). `coverage.csv` gives the same 4,800 rows, 2026-09-03T05:00:00Z to 2026-10-13T04:00:00Z: it agrees.

A run reads every CSV file the list holds (ERCOT keeps about the last month) and keeps, of each, only the delivery day after the day it was published: the plan that day's day-ahead market used. A day whose file is gone from the list is never taken from another publication. `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc), so a day read again replaces the one held, and the table keeps days the list has dropped. A file saved by an earlier run of this connector on the machine is read from `warehouse/raw/ercot_as_quantities/` and not asked again. `retrieved_at` is the moment the run read each file, not when the file was downloaded.

## Shape and variables

Series, 4,800 rows, five entities. `entity` `ercot:<service>`; `variable` `quantity_mw_plan`, the MW ERCOT plans to procure in the day-ahead market for the hour; `unit` MW; `freq` PT1H; `ts_utc` the hour's start, from DeliveryDate and HourEnding (Central) less one hour, DSTFlag Y marking the repeated autumn hour; `market` `ercot_dam`; `geo` US-TX; `node` the service; `source_url` the file's address. Every value is a whole number.

| Entity | Variable | Hours | Mean MW | Lowest | Highest |
|---|---|---|---|---|---|
| `ercot:REGUP` | `quantity_mw_plan` | 960 | 477.2 | 251 (28 hours, 08:00 UTC on 3 to 30 September 2026) | 848 (12 hours, 14:00 UTC on 1 to 12 October 2026) |
| `ercot:REGDN` | `quantity_mw_plan` | 960 | 451.0 | 246 (12 hours, 08:00 UTC on 1 to 12 October 2026) | 697 (28 hours, 22:00 UTC on 3 to 30 September 2026) |
| `ercot:RRS` | `quantity_mw_plan` | 960 | 2,517.4 | 2,344 (112 hours, first 3 September 2026, 23:00 UTC) | 2,867 (48 hours, first 1 October 2026, 15:00 UTC) |
| `ercot:NSPIN` | `quantity_mw_plan` | 960 | 2,553.9 | 1,670 (28 hours, 20:00 UTC on 3 to 30 September 2026) | 3,936 (12 hours, 12:00 UTC on 1 to 12 October 2026) |
| `ercot:ECRS` | `quantity_mw_plan` | 960 | 1,676.1 | 808 (12 hours, 08:00 UTC on 1 to 12 October 2026) | 2,842 (12 hours, 21:00 UTC on 1 to 12 October 2026) |

The plan repeats: the same figure recurs at the same hour on most days of a month, and changes at the month's turn. No clock change falls in the window; every day holds 24 hours.

## Reading ERCOT's reports site

- The list is asked afresh each run; only documents whose name ends `_csv` are read, oldest first.
- A zip must hold exactly one CSV, with exactly the columns DeliveryDate, HourEnding, AncillaryType, Quantity, DSTFlag, or the run stops and nothing is written. A service other than REGUP, REGDN, RRS, NSPIN and ECRS stops the run.
- The hour ending must read HH:00, from 1 to 24, and the flag Y or N; an hour the spring clock change skips stops the run. An empty quantity gives no row; a value that is not a number stops the run.
- A file that does not hold the day after its publish day is named in the header's "Left out" and adds nothing. No day at all stops the run.
- Never filled: a (service, Central day) is written only when every hour of the day is there exactly once; a (service, hour) given twice stops the run. The run of 11 October left out none.
- Ceiling: 400,000 rows kept (session 74's approved pull), not rows read. Past it the run stops and writes nothing.
- A request is tried up to four times, 5, 10 and 15 seconds apart (`iso_prices.with_retries`); HTTP 404 is not retried and stops the run. Three seconds after each request asked of ERCOT.
- No `--out-dir` and no `--offline`: the connector takes no argument.
- No pause check: the connector does not ask `iso_prices.paused()` before its requests (ERCOT is not paused).

## License

The header: "License: public (ERCOT's terms, https://www.ercot.com/help/terms, item 5)." `coverage.csv`: public. `license_tables.csv` names ERCOT as the table's one publisher (from the source registry); `license_verdicts.csv` gives ERCOT "may be public" (read 2 of `license_reads.csv`, 12 October 2026). `docs/licenses.md`: flag and verdict agree; ERW verdict public.

## Cross-checks (session 2152)

- The counts above were computed from the rows, read past the 10 header lines; no hour is given twice.
- Hours complete: each service holds all 960 hours from 3 September 2026 05:00 UTC to 13 October 2026 04:00 UTC.
- Every row's delivery day is the day after its file's publish day, as the docstring says.
- The connector has no cross-check of its own beyond its reading rules.

## Found while writing this note

- The connector asks `/misapp/` and `/misdownload/` on `www.ercot.com`, paths ERCOT's robots file disallows (read 23 October 2026, session 2002). Neither its docstring nor its header says so.
- `CLAUDE.md` says every connector that reaches a publisher's servers asks `iso_prices.paused()` first. This one does not.
- The docstring says the table "grows by a day each run if the connector is scheduled". It is not scheduled, and no run since 11 October 2026 is recorded, so delivery days from 13 October are not held. ERCOT's list keeps about a month: a day not read within about a month of its plan is lost for good.
- `retrieved_at` is set when the run reads a file, also for a file reused from an earlier run's raw files, so a row does not always say when its document was fetched (CLAUDE.md, rule 5). `iso_prices.fetch_raw` returns the first download's time, and this connector does not use it.

## What it does not hold

- Delivery days before 3 September 2026: ERCOT's public site keeps about a month, and no keyless public source of the history was found (session 74; ERCOT's archive API needs a subscription key).
- What ERCOT bought, or at what price (the prices are `ercot_as_prices`), and any change ERCOT made to the plan after the day-ahead market.
