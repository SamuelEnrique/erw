# Grid conditions: what each operator publishes in the open (chain 601, part B, session 9000, 20 November 2026)

What the seven grids and the large balancing authorities outside them publish about six things: (1) binding transmission constraints and their shadow prices; (2) the congestion part of a hub's or zone's price; (3) generation out of service; (4) operating reserves and scarcity pricing; (5) alerts and emergency notices; (6) flows on their ties at five minutes. For each: the address, the archive's depth as found tonight, the robots file, the terms, the verdict of `docs/licenses.md`, and what the warehouse already holds. Parts C to F of chain 601 take the feeds this file clears, the clearest and deepest first.

Every request of this file is in `runs/c601/probe.csv` (robots and listings, through the chain 140 probe with redirects capped at 5) or was one trial day through `runs/c601/trial_feeds.py` (gridstatus 0.36.0, which prints each address). No paid service was asked. Times are UTC.

## The verdicts that decide

| Operator | `docs/licenses.md` (as the ERW is today) | Robots file, read tonight | What this chain does |
|---|---|---|---|
| CAISO | may be public ("freely available for public use", read #3) | `oasis.caiso.com/robots.txt`: 404, no file (10:32:31). `www.caiso.com/robots.txt`: `Disallow: /resources/*`, `Allow: /` | pulled |
| SPP | may be public as the ERW is today (read #6: "Permission is implicitly granted to copy and distribute ... with appropriate citation", except commercial publication) | `portal.spp.org/robots.txt`: the portal's page, no robots file (as the existing SPP connectors found). `www.spp.org/robots.txt`: 404 | pulled |
| ERCOT | may be public (read #2) | `www.ercot.com/robots.txt` (10:32:31): disallows `/misapp` and `/misdownload`, where every ERCOT market report is listed and served | **not pulled.** The owner's ruling 2 of 6 November 2026: no new request to those paths; the public API needs a key the owner has not made. What the warehouse already holds of ERCOT is shown |
| PJM | needs a paid license (read #15) | not asked | **not pulled.** Drawn blank, "license needed" |
| NYISO | needs written permission (read #5) | not asked | **not pulled.** Drawn blank, "license needed" |
| ISO-NE | needs written permission (read #4) | not asked | **not pulled.** Drawn blank, "license needed" |
| MISO | paused since 4 October 2026 (`paused_sources.csv`) | not asked | **not pulled.** Drawn blank, "paused" |
| BPA | federal (the ERW holds `bpa_ba_hourly` as public) | `www.bpa.gov/robots.txt`: `Disallow: /customerportal/`, `Allow: /`; `transmission.bpa.gov/robots.txt` is sent on to a page (no file) | its path flows not read tonight; part H |
| EIA (all authorities) | may be public (read #1) | read by earlier sessions | held: hourly interchange by authority and pair since July 2018 |
| DOE OE-417 (all authorities) | public (held as `doe_oe417_events`) | read by earlier sessions | held: emergency incident reports 2016 to 2025 |

## 1. Binding constraints and their shadow prices

| Operator | Feed | Address | Depth found | Warehouse today |
|---|---|---|---|---|
| CAISO | OASIS `PRC_NOMOGRAM` (nomogram and branch shadow prices), day-ahead (`market_run_id=DAM`) and fifteen-minute (`HASP`) hourly; `PRC_RTM_NOMOGRAM` five-minute real time; `PRC_RTM_INTERTIE` intertie constraints | `http://oasis.caiso.com/oasisapi/SingleZip?queryname=PRC_NOMOGRAM&version=1&market_run_id=DAM&startdatetime=...` | day-ahead: 2015-01-15 answered (49 rows), 2019-01-15 (42), 2026-11-18 (137). Columns: interval, the constraint's name and XML id, the market, the contingency ("Constraint Cause"), the shadow price in USD per MWh. No limit or flow is published | nothing |
| SPP | Marketplace file browser, `da-binding-constraints` (day-ahead, hourly) and `rtbm-binding-constraints` (real time, five minutes) | `https://portal.spp.org/file-browser-api/download/da-binding-constraints?path=/YYYY/MM/By_Day/DA-BC-YYYYMMDD0100.csv`; earlier years as one zip a year (`/2024/2024.zip`, 6.6 MB) | year folders 2013 to 2026; the daily files stand for the current year, earlier years in the year's zip. 2026-11-18: 617 rows. Columns: interval, constraint name, type, NERC flowgate id, state, shadow price, monitored facility, contingent facility, contingency name. No limit or flow | nothing |
| ERCOT | NP4-191-CD (DAM shadow prices), NP6-86-CD (SCED shadow prices and binding constraints, with limit and flow) | `/misapp`, `/misdownload` | not asked | nothing |
| PJM, NYISO, ISO-NE | each publishes its binding constraints | not asked | held by license | nothing |

## 2. The congestion part of a hub's or zone's price

| Operator | Feed | Depth | Warehouse today |
|---|---|---|---|
| CAISO | OASIS `PRC_LMP` (day-ahead) gives LMP, energy, congestion and loss for every node; the trading hubs and default load aggregation points | rolling: 2026-11-18 answered, 2022-06-15 and 2019-01-15 did not ("No data found"); the warehouse's own CAISO hub history starts 2023-07, the same rolling window of about 39 months | LMP only (`iso_hub_prices_history`, `iso_zone_prices_history`), no components |
| SPP | `da-lmp-by-settlement-location`: LMP, energy (MEC), congestion (MCC), loss (MLC) for hubs and settlement locations | the same year folders as the existing SPP price pull (2014 on) | LMP only, no components |
| ERCOT | the settlement point price has no congestion split; the DAM and SCED shadow prices carry it | not asked | nothing |

## 3. Generation out of service

| Operator | Feed | Depth | Warehouse today |
|---|---|---|---|
| SPP | `capacity-of-generation-on-outage`: megawatts out each hour by balancing area (SPP, SWPW, total) and fuel (coal, oil, hydro, gas, nuclear, solar, wind, waste, other) | year folders 2016 to 2026, one zip a year before the current one | nothing |
| CAISO | "Curtailed and non-operational generator prior trade date report", one workbook a day: each outage's id, resource, planned or forced, nature of work, start, end, megawatts curtailed, Pmax | `https://www.caiso.com/documents/curtailed-non-operational-generator-prior-trade-date-report-YYYYMMDD.xlsx` (not under `/resources/`); from 17 June 2021. 2026-11-18: 1,997 rows | nothing |
| ERCOT | NP3-233-CD (hourly resource outage capacity) | `/misapp` | not asked | nothing |
| Nuclear, every grid | NRC power reactor status (daily percent power, federal) | held | `nrc_reactor_status` (2020 on), `eia_nuclear_outages_*` (2007 on) |

## 4. Operating reserves, scarcity adders and scarcity hours

| Operator | Feed | Warehouse today |
|---|---|---|
| ERCOT | NP6-792-ER, the real-time ORDC and reliability deployment price adders and reserves | held: `ercot_rtm_price_adders` (2014-06 to 2026-11-15, public): the online and offline reserve adders, the reliability deployment adder, hourly means and highs. Read as held; no new request |
| SPP | `operating-reserves`: cleared regulation, ramp, uncertainty, spinning and supplemental reserve by reserve zone, five minutes (2026-11-18 answered). No requirement column | nothing |
| CAISO | OASIS ancillary service prices and procurement | held: `caiso_as_prices` (2023-07 on) |
| ERCOT, SPP, NYISO | ancillary service quantities | held: `ercot_as_quantities`, `spp_as_quantities`; `nyiso_as_prices` |
| CAISO, ERCOT | the hours the warehouse already counts as scarce | held: `scarcity_hours_by_grid` (2023-11 on), `grid_stress_days` |

## 5. Alerts, watches and emergency notices

| Operator | Warehouse today |
|---|---|
| CAISO | held: `caiso_grid_emergencies` (1,906 notices, 1998-05-30 to 2026-10-08: Flex Alerts, RMO, EEA, restricted maintenance), the source of `/grid/caiso/alerts` |
| ERCOT | held: `ercot_grid_notices` (178 notices, 2011-02-02 to 2026-10-15: EEA levels, conservation appeals, watches) |
| Every authority | held: `doe_oe417_events` (3,313 reports, 2016-01 to 2025-12, the federal emergency incident and disturbance reports, with the authority named) |
| SPP | its conservative operations and EEA notices are published as news on www.spp.org (no robots file); not read tonight, part H |
| PJM, NYISO, ISO-NE | held by license; MISO paused |

## 6. Ties at five minutes

| Operator | Feed | Warehouse today |
|---|---|---|
| CAISO | OASIS real-time tie flows (`tie_flows_real_time`, five minutes, and fifteen) | nothing at five minutes |
| SPP | none found in the file browser's folders read tonight | nothing |
| Every authority | EIA-930 interchange, hourly | held: `eia930_ba_interchange_hourly_*`, `eia930_region_pair_hourly` (2018-07 on) |

## What parts C to F take, clearest and deepest first

1. **C, constraints:** SPP day-ahead (2013 on) and CAISO day-ahead (2015 on), into `constraints_binding_hourly`. Real time later (larger files), newest year first.
2. **C, congestion part of price:** SPP hubs (day-ahead), CAISO hubs (day-ahead, rolling 39 months), into `price_congestion_hourly`.
3. **D, outages:** SPP by fuel and hour (2016 on), CAISO by resource (2021-06-17 on, summed by day and planned or forced), into `generation_outages`, with `nrc_reactor_status` beside it.
4. **E, reserves and scarcity:** SPP cleared reserves; ERCOT's held adders give `scarcity_pricing_hours`; `grid_alerts` folds the held CAISO, ERCOT and OE-417 notices.
5. **F, ties:** CAISO's five-minute tie flows, the last thirty-five days.

## For Samuel's ruling (the default taken in brackets)

- ERCOT's shadow prices, outages and binding constraints are only on the paths its robots file disallows or behind the API key not made [not pulled; ERCOT's strips are drawn blank with "source needed" except what the warehouse holds].
- PJM, NYISO and ISO-NE publish constraints, outages and reserves under terms the ERW holds [not pulled; blank with "license needed"].
- MISO is paused [not pulled; blank with "paused"].
