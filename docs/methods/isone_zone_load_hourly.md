# Real-time demand by load zone and for the control area, an hour (ISO-NE, Zonal Information, SMD Hourly Data)

Energy Research Warehouse (ERW), method note written in session 2110 (chain 069) for a table first written on 7 October 2026 (session 138).

Tables: `isone_zone_load_hourly`

## Publisher and address

ISO New England (ISO-NE), the "Zonal Information" page, its yearly workbook "SMD Hourly Data":

- the page `https://www.iso-ne.com/isoexpress/web/reports/load-and-demand/-/tree/zone-info`
- its file list (JSON, 40 entries a page, up to three pages asked) `https://www.iso-ne.com/isoexpress/web/reports/download/docWidgetGetMore?start=<N>&treenode=zone-info`
- a year's workbook `https://www.iso-ne.com/static-assets/documents/<folder>/<YYYY>_smd_hourly.xlsx`; the rows come from `.../documents/100020/2025_smd_hourly.xlsx` and `.../documents/100032/2026_smd_hourly.xlsx`

Nine sheets are read, ISO NE CA (the control area, ISO-NE's own total) and ME, NH, VT, CT, RI, SEMA, WCMA and NEMA, and one column of each, RT_Demand. Plain requests, with the User-Agent "Mozilla/5.0 (Energy Research Warehouse; https://github.com/SamuelEnrique/erw)": the connector's docstring says that on 6 October 2026 the page, its list and each workbook answered HTTP 200 with no cookie, no account and no CAPTCHA, and that the page's CAPTCHA guards only its several-files download form, which is not used. Source id `isone:smd_hourly`. Connector: `warehouse/connectors/isone_zone_load.py` (session 138), its only table, with the frame it shares with the other load connectors in `warehouse/connectors/zone_load.py` (and the row counter of `dam_cleared.py`). `warehouse/connectors/zone_price_history.py` reuses the workbooks it keeps for `isone_zone_prices_history`, with no request of its own.

It is run once a week, on Saturday (UTC), by `warehouse/refresh_supply.sh`, which `warehouse/run_daily.sh` calls (`SUPPLY=1` forces it on another day), under `warehouse/health.py` and a pull budget of 15 minutes. The last run `run_status.csv` records is `20261010T150238Z` (10 October 2026, on GitHub): "52,479 rows; 52,479 rows read". The first date is session 138's report ("Run on 7 October 2026 (UTC)"; ISO-NE: two yearly workbooks, 2025 and 2026, 131,319 rows) and the rows: the earliest `retrieved_at` is 7 October 2026 01:44:08 UTC (the 2025 workbook).

## Vintage and revision

Eastern days 1 January 2025 to 31 August 2026 (1 January 2025 05:00 UTC to 1 September 2026 03:00 UTC) in the file on the data machine, restored from the Redivis draft (energy_research_warehouse_internal) by `scripts/sync.py`, with the header of the connector's run `20261010T150238Z`: "This run wrote 52479 rows: 0 new, 52479 replacing earlier rows". The rows' `retrieved_at`: 7 October 2026 for the 78,840 rows of 2025, 10 October 2026 for the 52,479 rows of 2026; `vintage` is empty in every row. `coverage.csv` gives the same 131,319 rows and dates (last run 2026-10-10T15:02:38Z).

Each run asks for the file list again, then each year's workbook from this year back to the year of its first day (`--days`, default 10 days back; `--from` for a history). A workbook already kept in `warehouse/raw/isone_zone_load/` is read from there unless the list's publish date for it is later than the kept copy's retrieval; on GitHub's runner no copy is kept, so the workbook is asked for every run. Every hour of each workbook read is written, not only the days asked for: the run of 10 October rewrote all of 2026 to 31 August. `ip.write_csv` merges the rows into the file on (entity, variable, ts_utc), so a year no longer asked for stays as it was. The header: "ISO-NE extends the current year's workbook about once a month, so the newest hour can be many weeks old."

## Shape and variables

Series, 131,319 rows: nine entities of 14,591 hours each (8,760 in 2025 and 5,831 in 2026 to 31 August, Eastern). `entity` `isone:system` for the sheet ISO NE CA and `isone:<zone>` for the zones, with the names of the ISO-NE price tables (`.Z.MAINE` and so on), so load and price join on entity; `variable` `load`; `value` ISO-NE's RT_Demand, MWh for the hour, which is MW over the hour; `unit` MW; `freq` PT1H; `ts_utc` the hour's start in UTC (Hr_End, Eastern, less one hour); `market` `isone_load`; `geo` US-CT,US-MA,US-ME,US-NH,US-RI,US-VT; `node` the sheet's name; `vintage` empty.

| Entity | Sheet | Mean MW | Lowest | Highest |
|---|---|---|---|---|
| `isone:system` | ISO NE CA | 13,379 | 7,577 (20 April 2025, 18:00 UTC) | 26,086 (24 June 2025, 22:00 UTC) |
| `isone:.Z.CONNECTICUT` | CT | 3,135 | 1,687 (20 April 2025, 18:00) | 6,525 (24 June 2025, 22:00) |
| `isone:.Z.MAINE` | ME | 1,239 | 590 (18 April 2026, 17:00) | 2,040 (2 July 2026, 23:00) |
| `isone:.Z.NEMASSBOST` | NEMA | 2,760 | 1,773 (2 June 2025, 07:00) | 5,491 (24 June 2025, 20:00) |
| `isone:.Z.NEWHAMPSHIRE` | NH | 1,336 | 836 (27 April 2025, 07:00) | 2,572 (24 June 2025, 21:00) |
| `isone:.Z.RHODEISLAND` | RI | 891 | 114 (10 May 2026, 02:00) | 1,934 (24 June 2025, 20:00) |
| `isone:.Z.SEMASS` | SEMA | 1,630 | 818 (20 April 2025, 17:00) | 3,618 (24 June 2025, 21:00) |
| `isone:.Z.VERMONT` | VT | 549 | 31 (11 May 2025, 17:00) | 901 (25 January 2026, 20:00) |
| `isone:.Z.WCMASS` | WCMA | 1,839 | 1,008 (20 April 2025, 18:00) | 3,354 (24 June 2025, 22:00) |

Rhode Island's lowest hour stands alone: the next lowest is 325 MW (23 March 2025, 02:00 UTC). Vermont's lowest hours are three midday hours of 11 May 2025 (16:00 to 18:00 UTC, 31 to 34 MW). The clock changes: 9 March 2025 and 8 March 2026 hold 23 hours, 2 November 2025 holds 25.

## Reading ISO-NE

- The list and each workbook are fetched by `iso_prices.fetch_raw`: up to four tries, 5, 10 and 15 seconds apart (no retry once the pull budget has passed); an HTTP 404 is not retried and, like a request that still fails, stops the run. Three seconds after each request.
- The list. A page with fewer than 40 entries ends it. A workbook is known by its address, `/static-assets/documents/<folder>/<YYYY>_smd_hourly.xlsx`; a year the list holds no workbook for is not written and is named in the header.
- A workbook's answer must begin as a zip ("PK"), or the run stops. Each of the nine sheets must be there and hold Date, Hr_End and RT_Demand, or the run stops. An hour ending that is not 1 to 24 (after an "X" is taken off) stops the run.
- The hour (`zone_load.to_utc`). "02X" is the second 01:00 to 02:00 hour of the autumn change. The spring day's 23 lines go 01, 03: the line labelled 03 is placed by its end. A repeated hour held once only could be either of two hours and is not written, counted in the log and the header (none in these rows).
- A blank cell, or one that is not a number, gives no row. A zone's hour given twice in one workbook stops the run; given by two workbooks, the newer workbook's row is kept.
- Ceiling: 80,000 rows read from ISO-NE in a run (`--ceiling`), every line of the nine sheets counted; a workbook read from a kept copy does not count. Before asking for a workbook that is not kept, or is newer than the kept copy, the run stops asking (and says so in the header) if another year, 79,056 lines, would pass the ceiling: one fresh workbook a run.
- No hour at all stops the run. A newest hour more than 100 days old stops it as "stale at source", a skip (exit 75), and nothing is written.
- ISO-NE is checked against `warehouse/metadata/paused_sources.csv` before any request (it is not paused); a paused publisher is a skipped status row and no request.

## License

The header: "License: internal. ISO-NE's legal notice: "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws" (https://www.iso-ne.com/legal-privacy, read 6 October 2026). Not published, in no public dataset and no download." `coverage.csv`: internal. `license_tables.csv` names ISO-NE as the table's one publisher (from the source registry); `license_verdicts.csv` gives ISO-NE "needs written permission" (read 4 of `license_reads.csv`, 12 October 2026). `docs/licenses.md`: flag and verdict agree; ERW verdict internal.

## Cross-checks (session 2110)

- The counts above were computed from the rows, read past the 13 header lines; no (entity, variable, ts_utc) is given twice.
- Hours complete: each of the nine entities holds every hour of the 608 Eastern days from 1 January 2025 to 31 August 2026.
- The eight zones add up to ISO NE CA within 0.002 MW in every one of the 14,591 hours (the largest difference on 26 June 2025, 16:00 UTC). The total is ISO-NE's own sheet; the ERW sums nothing.
- Session 138's report, against EIA-930's hourly demand: ISO-NE's hour "does not settle it (0.935 at the same hour, 0.951 one hour later, on 148 hours)". The hour convention is not confirmed.
- No hour is shared with `isone_dam_cleared_energy`, which begins on 1 September 2026.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The workbook's other columns (day-ahead demand, the day-ahead and real-time LMP and their components, dry bulb and dew point): read and not written. Its LMP columns are in `isone_zone_prices_history` (internal, `zone_price_history.py`).
- Years before 2025: session 138 pulled 2025 and 2026 only.
- Hours after 31 August 2026: the 2026 workbook as last read.

## Found while writing this note

- The usage line and the frame's help give `--days N` as "how many days back to ask for", and the frame's "stale at source" test looks for no hour on or after that first day. For ISO-NE the days only choose which years' workbooks are read: every hour of each workbook is written, so a default run rewrites the whole current year, and that test can fire only on a workbook with no hour at all.
- Not a contradiction, but unsaid: neither docstring says what becomes of text where a number should be. The code drops such a cell without a word (`pd.to_numeric(..., errors="coerce")`), where the other ISO-NE connectors stop the run.
