# EIA-930's hourly interchange of every pair and hourly demand, for Winter Storm Uri and the June 2025 heat (Form EIA-930)

Energy Research Warehouse (ERW), method note written in session 2228 (chain 099) for a table first written on 2 October 2026 (session 68).

Tables: `eia930_event_hourly_interchange`

The two stories of `/network` that read it are in `docs/methods/grid_network.md` ("The stories (session 68)"), through `warehouse/derived/network_stories.py`; this note describes the code and the rows as they stand.

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-930, Hourly Electric Grid Monitor (`https://www.eia.gov/electricity/gridmonitor/`), through the EIA API v2:

- `https://api.eia.gov/v2/electricity/rto/interchange-data/data/`, hourly, every directed pair EIA reports (no facet), sorted by period, fromba and toba; source id `eia:electricity/rto/interchange-data`;
- `https://api.eia.gov/v2/electricity/rto/region-data/data/`, hourly, `facets[type][]=D` (demand), sorted by period and respondent; source id `eia:electricity/rto/region-data`.

Connector: `warehouse/connectors/eia930_event_hourly.py` (session 68), run by hand (`python warehouse/connectors/eia930_event_hourly.py`); no step of the daily run calls it. The key comes from `EIA_API_KEY` and is removed from every URL, log line and row (`api_key=REDACTED` in `source_url`). Every page is saved under `warehouse/raw/eia930_event_hourly/<run_id>/`, and each window and route is one checkpoint under `warehouse/raw/eia930_event_hourly/checkpoints/`.

## Vintage and revision

One pull, run `20261002T225619Z` (2 October 2026): the rows' `retrieved_at` run from 2026-10-02T22:56:24Z to 2026-10-02T22:58:40Z, 55 distinct page times. EIA revises EIA-930 after first publication; the table is not refreshed, so it holds EIA's figures as read that evening. `vintage` is empty. The file on the data machine was restored from the Redivis draft by `scripts/sync.py` (its last header line).

| `event` | Local days | Hours | `ts_utc` | Interchange rows | Directed pairs | Demand rows | Respondents with demand |
|---|---|---|---|---|---|---|---|
| uri_2021 | 2021-02-07 to 2021-02-24, America/Chicago | 432 | 2021-02-07T06:00:00Z to 2021-02-25T05:00:00Z | 151,184 | 350 | 29,185 | 68 |
| east_heat_2025 | 2025-06-20 to 2025-06-28, America/New_York | 216 | 2025-06-20T04:00:00Z to 2025-06-29T03:00:00Z | 71,992 | 338 | 14,472 | 67 |

266,833 rows in all, as the header says, of the 400,000-row ceiling. The header's API count, 266,857, is the rows written and the 24 Uri demand rows without a number.

## Shape and variables

Series. Columns: the series columns, then `ba`, `x_to_ba` and `event`; the key is (entity, variable, ts_utc, event), and no key appears twice.

- `interchange_mw` (223,176 rows): `entity` `eia930:<FROM>-<TO>`, the reporting respondent's net flow with its neighbour, positive when it exports; `ba` FROM and `x_to_ba` TO, lowercase. Both directions of a pair are kept, as EIA publishes them.
- `demand_mw` (43,657 rows): `entity` `eia930:<respondent>`, `ba` the respondent in lowercase, `x_to_ba` empty.
- `unit` MW, `freq` PT1H; `ts_utc` the hour's start, UTC (EIA's period, the hour's end, less one hour); `geo`, `market`, `node` and `vintage` empty.

**Not only balancing authorities.** EIA's interchange route also reports its regions and country totals, and the connector keeps demand for every respondent that appears in a window's interchange. So 14 of the respondents with demand in each window are EIA's regions (CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN, TEX, US48): 6,048 demand rows in Uri and 3,024 in the heat. Interchange rows that name a region or country (those 14 and CAN, MEX): 19,440 and 9,360. The header's "68" and "67 balancing authorities" count them. The connector's docstring (lines 23 and 24) says demand is kept "for the respondents that are balancing authorities (those that report an interchange in the window), not for EIA's regional sums"; the code's filter (`bas`, every code in the window's interchange) keeps the regions, and the rows hold them. The header's API count says "EIA's regional sums of demand included", and none was left out: the 24 rows between the count and the table are the rows without a number.

Each ISO grid's highest hour of demand in each window, and its own reported interchange in that hour:

| Grid | Uri: peak, MW | Hour (UTC) | Its interchange, MW | Heat: peak, MW | Hour (UTC) | Its interchange, MW |
|---|---|---|---|---|---|---|
| CISO | 27,303 | 2021-02-10 02:00 | -7,269 | 34,504 | 2025-06-29 03:00 | -4,937 |
| ERCO | 69,215 | 2021-02-15 01:00 | -1,194 | 77,040 | 2025-06-20 21:00 | 279 |
| ISNE | 17,898 | 2021-02-09 22:00 | -2,986 | 25,898 | 2025-06-24 22:00 | -3,040 |
| MISO | 98,962 | 2021-02-16 00:00 | -8,462 | 116,404 | 2025-06-23 20:00 | -3,433 |
| NYIS | 21,746 | 2021-02-08 23:00 | -4,145 | 31,857 | 2025-06-24 22:00 | -3,238 |
| PJM | 117,372 | 2021-02-08 13:00 | 11,102 | 160,560 | 2025-06-23 21:00 | 1,484 |
| SWPP | 43,476 | 2021-02-15 14:00 | -5,909 | 50,760 | 2025-06-20 21:00 | none reported |

CISO's heat peak is the window's last hour. SWPP reports interchange in 168 of the heat's 216 hours (1,008 rows, 6 neighbours), and not in its peak hour.

Gaps, never filled: in Uri, 6 of 350 directed pairs lack hours (GWA-NWMT and WWA-NWMT 427 of 432, AECI-MISO 429, AECI-SPA, AECI-SWPP and LDWP-CISO 431), and TEPC's demand stops after the second hour of 17 February 2021, Eastern time (241 hours); in the heat, 24 of 338 pairs lack hours (the fewest, SPA-SWPP, 25 of 216), and every respondent has all 216 hours of demand.

## Reading the source

- Before any page is asked for, the connector counts both routes over both windows (requests with `length` 0, reading `total`) and stops without pulling if the sum passes `CEILING` (400,000).
- A window and route with a checkpoint is read from it; otherwise it is paged 5,000 rows at a time (`eia930.PAGE`), 0.5 seconds apart. A page that answers other than HTTP 200 raises; each request has up to 4 attempts (`RETRIES`), waiting 5, 10, 15 and 20 seconds after each failure, and none after the pull budget is spent. Rows received other than the API's `total` stop the run.
- A row without a number is counted and not written; a row outside the window is dropped. A pair and hour, or a respondent's hour of demand, that appears twice stops the run.
- Demand is kept only for respondents that appear as reporter or neighbour in that window's interchange.
- After both windows, more than 400,000 rows, or a key twice, stops the run without writing. The file is deleted and written whole from the checkpoints.
- The connector does not ask `iso_prices.paused()` or `paused_host()` before its first request. EIA is not in `paused_sources.csv`. The request hook of `iso_prices.py` (`_send`) saves each answer and cuts its timeout to the pull budget; it checks no pause.

## License

Public. The header: "License: public domain (U.S. Government data, EIA)." `sources.csv` flags `eia:electricity/rto/interchange-data` and `eia:electricity/rto/region-data` public, each naming the table; `license_tables.csv` lists it under EIA ("the source registry"). `license_verdicts.csv` records EIA, read 1: "may be public", for public and for commercial use. The sentence: "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service." EIA asks for the acknowledgment "Source: U.S. Energy Information Administration" with the date. `docs/licenses.md` (line 603): may be public, and the flag agrees.

## Cross-checks (session 2228)

- The counts above were computed from the rows, read past the header lines, and agree with the header's: 151,184 + 71,992 interchange rows, 29,185 + 14,472 demand rows.
- The two reports of one pair, A to B against minus B to A: in Uri, 71,264 pairs and hours reported by both sides, 49,857 within 1 MW; in the heat, 32,919 and 23,707. In both the median gap is 0 and the 90th percentile 170 MW.
- Against `eia930_daily_demand` (EIA's daily demand, type D, Eastern day), each respondent's hourly demand summed over the Eastern days the table holds whole: in Uri, 1,148 respondent days, each with a daily row (8 to 24 February 2021; the Eastern days of 7 and 25 February are partial, and TEPC's 17 February), 1,147 equal and the largest gap 52 MWh (SEC, 22 February 2021); in the heat, 603 respondent days, 573 equal, 598 within 1 percent, the largest gap 15,582 MWh (PACW, 25 June 2025). ERCO, PJM and NYIS are equal on every day of both windows.
- Against `eia930_daily_total_interchange` (EIA's daily total interchange, type TI, Eastern day), each reporter's interchange summed over its neighbours and the day, where every neighbour has all 24 hours: in Uri 1,302 reporter days, 922 within 1 MWh; in the heat 650, 425. By ISO grid, the largest gap: CISO, ISNE and MISO 0 MWh in both windows; NYIS 4 and 5; ERCO 16 and 8; SWPP 3,662 and 4,677; PJM 243,841 and 105,377. The largest of all are regions' rows (MIDA 289,267 MWh on 15 February 2021, US48 228,956 MWh on 27 June 2025). EIA's daily total is the respondent's own figure and need not equal the sum of its pair reports.
- Scripts: `event_check.py`, `event_check2.py` and `event_check3.py` in the session's scratchpad.

## What it does not hold

- Any hour outside the two windows. The warehouse's rolling hourly interchange, `eia930_all_interchange`, starts in September 2026.
- Net generation or generation by fuel: only interchange and demand.
- Hours EIA did not report, or reported without a number (24 Uri demand rows).
