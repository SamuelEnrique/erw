# Alberta's internal load by the hour, a series (the AESO's Historical Pool Price report)

Energy Research Warehouse (ERW), method note written in session 2079 (chain 067) for a table first written on 23 October 2026 (session 2071).

Tables: `aeso_alberta_load_hourly`

## Publisher and address

Alberta Electric System Operator (AESO), Historical Pool Price report on its Energy Trading System, asked as CSV for a range of days: `http://ets.aeso.ca/ets_web/ip/Market/Reports/HistoricalPoolPriceReportServlet?beginDate=MMDDYYYY&endDate=MMDDYYYY&contentType=csv` (the end date not included). Source id `aeso:historical_pool_price`. Connector: `warehouse/connectors/aeso_load.py` (session 2071).

## Vintage and revision

1 January 2025, Alberta's midnight, to the hour beginning 13:00 MDT on 23 October 2026; in UTC, `ts_utc` runs from 2025-01-01T07:00:00Z to 2026-10-23T19:00:00Z. Written by run `20261023T201137Z` (23 October 2026) from two reports: `beginDate=01012025&endDate=12312025`, retrieved 2026-10-23T20:08:46Z (1 January to 30 December 2025 local, 8,736 rows), and `beginDate=12312025&endDate=10242026`, retrieved 2026-10-23T20:09:04Z (31 December 2025 on, 7,117 rows). Session 2071's report says the trial and the write reused the two saved reports (`--offline`). `vintage` is empty in every row: the report states no publication time.

Each run asks last year (fetched once, then reused from `warehouse/raw/aeso_load/`) and this year to tomorrow (fresh each run unless `--offline`). The table is merged, not replaced: a run's rows replace earlier rows with the same (entity, variable, ts_utc), and earlier rows not in the run are kept.

## Shape and variables

Series, 15,853 rows, one an hour: entity `aeso:alberta`, variable `ail_demand` (Alberta internal load), unit MW, freq PT1H, geo `CA-AB`, node `Alberta`, `market` empty.

| Local year | Hours | Mean, MW | Highest, MW | Lowest, MW |
|---|---|---|---|---|
| 2025 | 8,760 | 10,316.3 | 12,785 (11 December, hour beginning 17:00 MST) | 8,295 (1 June, 05:00 MDT) |
| 2026 to 23 October | 7,093 | 10,429.2 | 12,404 (17 February, 18:00 MST) | 8,678 (14 September, 02:00 MDT) |

- The local days around the clock changes hold 23 hours (9 March 2025, 8 March 2026) and 25 (2 November 2025), as Alberta's clock has them.
- The highest hour of April to October 2025 is 12,005 MW (27 August, hour beginning 17:00 MDT).

## Reading the source

- The lines after the report's title are `Date (HE),Price ($),30Ravg ($),AIL Demand (MW)`; the header must be exactly that. Only the load is taken.
- The AESO's hour is an hour ending in Alberta's local time with daylight saving: the spring day has 23 lines (no `02`), the autumn day 25 (`02`, then `02*`). Each hour is placed by its order within its local day: the day's local midnight in UTC (through America/Edmonton) plus one hour a line before it. So `02*` is the standard time hour. A day whose lines are not its hours ending in order stops the run; only the report's last day may stop short.
- An hour the report lists as `-` (not yet reached) is no row. A time not in the AESO's form, a load that is not a number, or an hour given twice stops the run. Values as published; nothing is filled.
- Not taken: the pool price and its 30-day average, for want of a Canadian dollar unit (the standing question of session 2070).
- Ceiling: two requests. ets.aeso.ca has no robots file (read 219, HTTP 404).

## License

`license_verdicts.csv` records the AESO, read 46 (its legal page): "may be public" for public use, "needs written permission" if commercial: "The material may be used and copied for non-commercial, personal or educational purposes, provided that the material is not modified and that copyright notices are not deleted. [...] Any other use of this material without the AESO's written permission is prohibited." `license_tables.csv` maps the table to the AESO (the source registry). `docs/licenses.md` gives it "may be public", flagged public, agreeing, "needs written permission" if the ERW sells anything, and counts it as the AESO's one table among the 13 that would then need permission; `sources.csv` names the source's license as public.

## Cross-checks (session 2079)

- The counts above were computed from the rows, read past the header lines; they match the header's 15,853 rows and its range. The 15,853 rows are every hour from the first to the last, with no hour given twice and no gap; the two reports meet at 2025-12-31T07:00:00Z without overlap.
- Session 2071's check against the AESO's 2025 Annual Market Statistics, recomputed on Alberta's local year 2025 (8,760 hours): average 10,316.3 MW (the report and the AESO: 10,316 MW); highest 12,785 MW in the hour beginning 17:00 MST on 11 December (the AESO's winter peak: 12,785 MW, December); 12,005 MW the highest of April to October (the AESO's summer peak: 12,005 MW; the AESO's own summer months were not read here).

## What it does not hold

- The pool price, its 30-day average, and any price.
- Alberta's load by area, its generation and its interties.
- Hours before 2025, and hours the report had not yet reached when it was asked.
