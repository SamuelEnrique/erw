# Poland's power balance a quarter hour: demand, generation by kind of unit, wind, solar and the cross-border exchange balance, 13 June 2024 to 23 October 2026 (PSE, Raporty OSP, report his-wlk-cal)

Energy Research Warehouse (ERW), method note written in session 2261 (chain 102) for a table first written on 24 October 2026 (session 2252).

Tables: `pse_poland_balance_15min`

## Publisher and address

PSE S.A. (Polskie Sieci Elektroenergetyczne), Poland's transmission system operator, its reports app Raporty OSP (`https://raporty.pse.pl/report/his-wlk-cal`), report his-wlk-cal ("Wielkosci podstawowe", the basic quantities of the KSE, Poland's power system). The connector reads the reports API (Data API builder 2.1.5, OData filters), one request a calendar year of business days:

`https://api.raporty.pse.pl/api/his-wlk-cal?$filter=business_date ge '<year>-01-01' and business_date le '<year>-12-31'&$first=40000`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `pse:his-wlk-cal`. Connector: `warehouse/connectors/pse_poland.py` (session 2252), its only table. api.raporty.pse.pl has no robots file (HTTP 404, the app's page; read 431), and www.pse.pl's disallows only a careers path (read 432). The API publishes no metadata (its root and `$metadata` answered 404, reads 433 and 434); each field is named by PSE's own English label, found in the reports app's script bundle (read 435). The OpenAPI description (read 436) states no license.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2261), and `run_status.csv` holds no row for it. It was written once, by run `20261024T034209Z` on the data machine, offline from the session's probe copies.

## Vintage and revision

From 21:45 UTC on 13 June 2024 (the report's first period) to 21:45 UTC on 23 October 2026 (`ts_utc`). The three yearly answers were retrieved by the session's probe at 2026-10-24T03:39:01Z (2025), 03:39:15Z (2024) and 03:39:20Z (2026), and the write read those copies; each row's `retrieved_at` is its year's time, as the probe's manifest records it. `vintage` is empty: the API sends no Last-Modified. `coverage.csv` gives the same 909,219 rows, 1 node and the same first and last `ts_utc`.

PSE republishes its figures: the answers carry a publication stamp on each quarter hour (`publication_ts_utc`), from 15 June 2024 to 18 January 2026 for 2024's business days, 18 to 19 January 2026 for 2025's, and from 18 January 2026 to 03:37 UTC on 24 October 2026 for 2026's. The connector does not keep the stamp. Each run writes the whole table again (`ip.write_snapshot`), and every year is asked again unless `--offline`.

The business day in progress at retrieval (24 October 2026, Warsaw time) is not taken: PSE lists its later quarter hours empty ahead (96 quarter hours, counted in the header).

## Shape and variables

Series, 909,219 rows, 1 entity, 14 variables, 14 series. Every one of the 82,753 quarter hours from the first to the last `ts_utc` is present for demand; none is missing and no (entity, variable, ts_utc) is given twice.

- `entity` `pse:pl`; `unit` MW, the quarter hour's power as PSE gives it; `freq` PT15M; `ts_utc` the quarter hour's start (PSE's UTC period); `geo` PL; `market` empty; `node` "Poland (KSE)".
- `x_field` PSE's field name; `x_business_date` PSE's business day in Polish local time (863 days). The days of the clock changes hold 92 quarter hours (30 March 2025, 29 March 2026) and 100 (27 October 2024, 26 October 2025); the first business day, 13 June 2024, holds one.

| Variable (`x_field`) | Rows | First | Zero | Negative | Mean MW |
|---|---|---|---|---|---|
| demand (demand) | 82,753 | 13 Jun 2024 | 0 | 0 | 18,154.5 |
| generation_scheduled_total (jg) | 82,753 | 13 Jun 2024 | 0 | 0 | 10,116.5 |
| generation_jgw1 (jgw1) | 82,753 | 13 Jun 2024 | 0 | 0 | 9,948.6 |
| generation_jgw2 (jgw2) | 29,852 | 16 Dec 2025, 23:00 UTC | 0 | 0 | 60.7 |
| generation_jgm1 (jgm1) | 82,753 | 13 Jun 2024 | 38,844 | 0 | 135.9 |
| generation_jgm2 (jgm2) | 33,980 | 3 Nov 2025, 23:00 UTC | 16 | 0 | 7.4 |
| charging_jgm (jgm) | 82,753 | 13 Jun 2024 | 5,810 | 76,943 | -177.9 |
| generation_jgz2 (jgz2) | 17,856 | 20 Apr 2026, 22:00 UTC | 4,859 | 0 | 33.0 |
| generation_jnwrb (jnwrb) | 82,753 | 13 Jun 2024 | 0 | 0 | 8,345.6 |
| generation_jga (jga) | 1 | 13 Jun 2024, 21:45 UTC | 0 | 1 | -15.0 |
| wind (wi) | 82,753 | 13 Jun 2024 | 0 | 0 | 2,452.6 |
| solar (pv) | 82,753 | 13 Jun 2024 | 37,023 | 0 | 2,448.7 |
| exchange_parallel (swm_p) | 82,753 | 13 Jun 2024 | 0 | 50,178 | -395.2 |
| exchange_non_parallel (swm_np) | 82,753 | 13 Jun 2024 | 0 | 14,690 | 268.6 |

Every series runs to 21:45 UTC on 23 October 2026, except generation_jga. jgw2, jgm2 and jgz2 begin later: their earlier quarter hours are blank at PSE and have no row (the header counts them: jgw2 52,901, jgm2 48,773, jgz2 64,897, jga 82,752). The zeros are of solar at night, idle storage and the jgz2 units at night (4,859 zeros: 464 to 478 in each UTC hour from 22:00 to 02:00, and 21 to 40 in each hour from 05:00 to 16:00); no series is all zero, and only generation_jga, with one row, is constant.

How the fields add up, from the rows:

- generation_scheduled_total equals generation_jgw1 + jgw2 + jgm1 + jgm2 + jgz2 + jga within 0.003 MW in every quarter hour; charging_jgm is not in it.
- demand is close to generation_scheduled_total + generation_jnwrb + charging_jgm + exchange_parallel + exchange_non_parallel: a median difference of -3.4 MW, from -20.8 to 14.8 MW at the 5th and 95th percentiles. So charging is negative, a positive exchange is a flow into Poland, and wind and solar are inside the generation figures, not added to them.

The counts were computed in session 2261 from the rows, read past the 10 header lines with pandas (every column as text).

Not taken: the day in progress (96 quarter hours), the blank figures, PSE's fields jgo, jgz1 and jgz3 (empty in every year read), and prices (PLN).

## Checks the connector makes

- Before any request, the connector and api.raporty.pse.pl are checked against `warehouse/metadata/paused_sources.csv`; a paused publisher stops the run with no request. It is not paused.
- An answer that fills its page (40,000 rows) stops the run, since rows might be missing. The largest year, 2025, holds 35,040.
- A field not in the map, a figure in jgo, jgz1 or jgz3, a period unlike its stamp (`period_utc` must start 15 minutes before `dtime_utc`), or a UTC period given twice stops the run.
- A business day on or after the retrieval's Warsaw day is not taken, and is counted. A blank figure has no row and is counted. Nothing is filled.
- Ceiling: one request a year from 2024 (three in 2026), a pause of 1 second after each, timeout 300 seconds; each asked again unless `--offline`.

## The cross-check

Session 2252 summed the quarter hours to months (MW times 0.25 hour) in `runs/c102/s2252/cross.py` (on the data machine, not in git), reading the trial copy of the table (the same rows as the table), and set them beside Eurostat's monthly figures for Poland (`eurostat_electricity_monthly`: `flow:AIM`, the supply available for the internal market; `net_production:RA300` wind and `RA400` solar), for the 25 whole months from July 2024 to July 2026:

| Ratio, PSE to Eurostat | Lowest | Highest | Median |
|---|---|---|---|
| demand to supply for the internal market | 0.936 (March 2026) | 1.128 (November 2024, January 2026) | 1.037 |
| wind | 0.583 (March 2026) | 1.006 (January 2025) | 0.930 |
| solar | 0.877 (April 2025) | 1.407 (January 2026) | 1.027 |

March 2026's wind is the outlier: PSE 1,549.4 GWh, Eurostat 2,659.6 GWh. PSE's demand in 2025 is 158.42 TWh, 91 percent of Ember's 174.31 TWh (`owid_ember_electricity_annual`). PSE's is the transmission system's demand, without the generation used where it is made.

## License

The header: "License: internal until the licenses' round reads PSE's terms. Cite PSE S.A., Raporty OSP." `license_verdicts.csv` holds no verdict for PSE. Neither the reports app's script bundle, the API's OpenAPI description, PSE's home page nor its system data page names any terms of use for its data (reads 431 to 436, 458 and 459; the last two in session 2257's round). `docs/licenses.md` gives "not settled (needs written permission by default)", and `coverage.csv` internal. Session 2257 put PSE's terms to the owner: is the data public, published openly with no license stated, or held until PSE answers?

## Found while writing this note

- The one generation_jga figure (-15.026 MW, 21:45 UTC on 13 June 2024, the report's first quarter hour) is negative. In that quarter hour charging_jgm is 0.0, while the next three quarter hours' charging is -15.179, -15.332 and -15.103 MW, and generation_scheduled_total (11,946.3) is generation_jgw1 (11,961.327) plus it. The raw answer holds it so. It reads like the storage units' charging written under jga, not generation by JGa units; the docstring calls it "the scheduled generator units JGa".
- The docstring and the header give no sign for charging_jgm or the exchange balances. The rows show charging is never positive (76,943 negative, 5,810 zero), and the balance above shows a positive exchange is a flow into Poland.
- `vintage` is empty, though PSE stamps each quarter hour's publication; a later run that finds a republished figure has no column to show it.

Acted on in session 2261: the docstring now gives the signs (charging never positive, a positive exchange a flow into Poland) and the one jga figure's reading. The table is unchanged; its `vintage` stays empty (PSE's publication stamps are not kept).

## What it does not hold

- Prices (PLN), and PSE's other reports (generation by fuel, unit outages, reserves).
- Quarter hours before 21:45 UTC on 13 June 2024, the report's first period, and the business day in progress at retrieval.
- PSE's fields jgo, jgz1 and jgz3, empty in every year read.
- Hours: the quarter hours are kept as published, not summed.
