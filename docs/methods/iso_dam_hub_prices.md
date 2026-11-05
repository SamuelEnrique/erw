# Day-ahead prices at the trading hubs of CAISO, ERCOT, MISO and SPP, one row a hub and hour, from 26 August 2026 (MISO to 3 October 2026)

Energy Research Warehouse (ERW), method note written in session 2284 (chain 104) for a table first written on 29 September 2026 (session 29, `archive/sessions/SESSION_29_REPORT.md`, the consolidation of four tables into one, commit `5dc81a19`); its four members were first written on 24 and 25 September 2026 (ERCOT's in session 1, the other three in session 2, `archive/sessions/SESSION_2_REPORT.md`, commit `7b4b5177`). The real-time prices at the same hubs are `iso_rtm_hub_prices`; NYISO's and ISO-NE's day-ahead prices are their zone tables.

Tables: `iso_dam_hub_prices`

## Publisher and address

Four grid operators, one report each, read through the `gridstatus` package (0.36.0 in the newest headers):

- `caiso_dam`: California ISO (CAISO), OASIS report PRC_LMP, market DAM, `https://oasis.caiso.com/mrioasis/logon.do`; one request a day for the three hubs (`https://oasis.caiso.com/oasisapi/SingleZip?resultformat=6&queryname=PRC_LMP&version=12&market_run_id=DAM&node=TH_NP15_GEN-APND,TH_SP15_GEN-APND,TH_ZP26_GEN-APND&startdatetime=...`). Source id `caiso:PRC_LMP`.
- `ercot_dam`: ERCOT, report NP4-190-CD "DAM Settlement Point Prices", `https://www.ercot.com/mp/data-products/data-product-details?id=NP4-190-CD`, document list `https://www.ercot.com/misapp/servlets/IceDocListJsonWS?reportTypeId=12331`; one document a day (`https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=<id>`). Source id `ercot:NP4-190-CD`.
- `miso_dam`: MISO, "Day-Ahead Ex-Post LMP (daily csv)", `https://docs.misoenergy.org/marketreports/<YYYYMMDD>_da_expost_lmp.csv`, page `https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/`. Source id `miso:da_expost_lmp`.
- `spp_dam`: Southwest Power Pool (SPP), "Day-Ahead LMP by Settlement Location", `https://portal.spp.org/file-browser-api/download/da-lmp-by-settlement-location?path=/<YYYY>/<MM>/By_Day/DA-LMP-SL-<YYYYMMDD>0100.csv`, page `https://portal.spp.org/pages/da-lmp-by-location`. Source id `spp:DA-LMP-SL`.

Connector: `warehouse/connectors/iso_prices.py` (session 2; ERCOT's part from session 1's `ercot_prices.py`, now a thin wrapper), one function a grid: `pull_caiso`, `pull_ercot`, `pull_miso`, `pull_spp`. Each writes its member (`caiso_dam_hub_prices`, `ercot_dam_hub_prices`, `miso_dam_hub_prices`, `spp_dam_hub_prices`), and `warehouse/consolidate.py build` writes the four into this table, told apart by `market` (`warehouse/metadata/table_migrations.csv` rows 24 to 27, session 29). The window is the N complete operating days before today in the grid's local time, plus any later operating day already published whole (the next day's auction). A market's file is written only if every hub has every hour of the window ("strict completeness"); a failed download is retried, then fails the market. Raw files under `warehouse/raw/<iso>/<run_id>/` (none on this machine).

**MISO is paused** since 4 October 2026 (`warehouse/metadata/paused_sources.csv`, `docs/methods/miso_pause.md`): its terms forbid automated access. No request goes to MISO; its rows stay as they are and end on 3 October 2026.

Schedule: the daily run, `warehouse/run_daily.sh`: `warehouse/consolidate.py split` writes the members out, `iso_prices.py <iso> --days 3` runs for `ISOS="ercot caiso nyiso spp isone"` (MISO left out), and `consolidate.py build` writes the table back. It runs on the GitHub runner (`.github/workflows/daily-prices.yml`, cron `0 14 * * *`, started on time by pg_cron through `workflow_dispatch`). The table is restored before the run (`warehouse/redivis/config.yaml`, `restore_before_run`, `'^iso_(dam|rtm)_hub_prices$'`). No step of `warehouse/run_data_machine.sh`, `run_data_machine_tables.sh`, `run_monthly.sh` or `refresh_supply.sh` runs the connector; `warehouse/scheduled.py` requires the table for its steps `price_compare` (monthly), `battery_scenario_steps` and `seller_hybrid` (the data machine, daily). `run_status.csv`: CAISO 29 runs ok, ERCOT 30 ok, MISO 14 ok, SPP 28 ok and 1 failed (run `20261011T141032Z`: "DAM 2026-10-08 failed after 4 attempts", a connection timeout). `archive_manifest.csv`: 23,016 rows as of run `20261023T152740Z-github`. Live set: `warehouse/supabase/live_set.yaml`, `recent` (35 days), `'^iso_(dam|rtm)_hub_prices$'`. Readers, among others: `hub_history.py` (which copies the main hubs' rows into `iso_hub_prices_history`), `price_board.py`, `board_page.py`, `cost_of_power.py`, `battery_stack.py`, `price_years.py`, `price_compare.py`, `scarcity_hours_by_grid.py`, `trader_view.py`, `ercot_hub_prices_daily.py`, the chat's ERCOT answers, `site/lib/data.ts` and the `erw` package.

## Vintage and revision

The copy here was rebuilt from the ERW's archive "as of run 20261023T152740Z-github" (header line 1); the consolidated header's newest retrieval is `20261023T141824Z` (SPP), and every member's own header follows. Each run merges its window into the member by (entity, variable, ts_utc): a value asked for again replaces the old one, every other row is kept. The window is 3 days a run, so a day is asked for on about three runs (and once more as a forward day); after that it is not asked again. Nothing trims the table: it has grown from session 2's first day, 26 August 2026, and holds 59 operating days (a comment in `warehouse/redivis/config.yaml` still calls these "the 30-day table").

`vintage` is the operator's publish time where one is known: ERCOT's document time (59 values, 2026-08-25T17:42:39Z to 2026-10-22T17:32:46Z, each before its operating day) and MISO's file `Last-Modified` (39 values, 2026-08-25T18:04:40Z to 2026-10-02T18:04:44Z). CAISO's and SPP's 7,032 rows have no vintage; the headers say "publish time not given by source". `retrieved_at` runs from 2026-09-25T06:59:51Z to 2026-10-23T14:18:30Z (209 values).

## Shape and variables

Series, 23,016 rows, 13 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`). Unit USD/MWh and `freq` PT1H in every row; `entity` is `<iso>:<node>` in every row; `node` the operator's hub name. 19 hubs.

| market | variable | Hubs | Rows | First hour (UTC) | Last hour (UTC) | Days | Mean | Lowest | Highest | Hours below 0 |
|---|---|---|---|---|---|---|---|---|---|---|
| caiso_dam | lmp_dam | 3 | 4,248 | 2026-08-26T07:00:00Z | 2026-10-24T06:00:00Z | 59 | 46.12 | -40.00 | 242.52 | 4 |
| ercot_dam | spp_dam | 6 | 8,496 | 2026-08-26T05:00:00Z | 2026-10-24T04:00:00Z | 59 | 38.65 | -15.88 | 179.40 | 26 |
| miso_dam | lmp_dam | 8 | 7,488 | 2026-08-26T05:00:00Z | 2026-10-04T04:00:00Z | 39 | 48.57 | 6.83 | 719.54 | 0 |
| spp_dam | lmp_dam | 2 | 2,784 | 2026-08-26T05:00:00Z | 2026-10-24T04:00:00Z | 58 of 59 | 33.95 | -31.74 | 228.31 | 165 |

USD/MWh, rounded to two decimals; days are the grid's local operating days.

| Hub | Mean | Hub | Mean |
|---|---|---|---|
| caiso:TH_NP15_GEN-APND | 48.23 | miso:ARKANSAS.HUB | 44.47 |
| caiso:TH_SP15_GEN-APND | 45.86 | miso:ILLINOIS.HUB | 51.34 |
| caiso:TH_ZP26_GEN-APND | 44.29 | miso:INDIANA.HUB | 57.40 |
| ercot:HB_BUSAVG | 38.28 | miso:LOUISIANA.HUB | 45.69 |
| ercot:HB_HOUSTON | 40.06 | miso:MICHIGAN.HUB | 52.84 |
| ercot:HB_HUBAVG | 38.73 | miso:MINN.HUB | 44.93 |
| ercot:HB_NORTH | 37.56 | miso:MS.HUB | 44.43 |
| ercot:HB_SOUTH | 38.64 | miso:TEXAS.HUB | 47.43 |
| ercot:HB_WEST | 38.64 | spp:SPPNORTH_HUB | 35.33 |
| | | spp:SPPSOUTH_HUB | 32.58 |

- **ERCOT's variable is `spp_dam`**: ERCOT's "settlement point price", not the grid SPP. All 26 of ERCOT's negative hours are at HB_WEST (lowest -15.88 on 2026-10-16T17:00:00Z; highest 179.40 on 2026-10-07T23:00:00Z).
- The highest price is MISO's MINN.HUB, 719.54 at 2026-09-04T23:00:00Z; CAISO's lowest is -40.00 at SP15 (2026-10-11T07:00:00Z); SPP's lowest -31.7402 at the South hub (2026-10-11T08:00:00Z), which has 114 of SPP's 165 negative hours.
- Digits are the operators': CAISO up to five decimals, SPP up to four, ERCOT and MISO two.
- `geo`: US-CA (CAISO), US-TX (ERCOT), a list of 15 states (MISO) and of 14 (SPP).
- `source_url` is the day's file or request in every row (215 values: 59, 59, 39 and 58 a market).

## Placing values in time, and what is filled

`ts_utc` is the start of the delivery hour in UTC. Every hub of a market has the same hours, 24 a local operating day: the window holds no daylight-saving change (the next is 1 November 2026). CAISO's day begins at 07:00Z, ERCOT's and SPP's at 05:00Z, MISO's at 05:00Z all year (EST). Nothing is filled: an hour the operator did not publish has no row.

**SPP's operating day 15 October 2026 is missing** for both hubs (24 hours, 2026-10-15T05:00:00Z to 2026-10-16T04:00:00Z). The other three markets hold it. `run_status.csv` has no row of the daily run of 15 October (whose CAISO and ERCOT rows, retrieved at 14:11 to 14:15Z, are in the table), no daily-run row from 16 to 18 October, and no SPP row on 19 October, although CAISO's and ERCOT's rows were retrieved that day too; SPP's rows for 16 to 19 October were retrieved on 19 October, so the 15th fell between two windows and was never asked again (disagreement 2).

## License

The header has no License line, neither the consolidated header nor the members' headers. `coverage.csv`: public. `warehouse/metadata/license_status.csv`: "iso_dam_hub_prices,license needed,2026-10-21,MISO,needs written permission,,,flagged public; the publisher's sentence read in session 205 asks for it (docs/licenses.md)". `docs/licenses.md`, the table's row: publishers CAISO; ERCOT; MISO; SPP, verdict "needs written permission" (decided by MISO), flag public, "ruled: license needed from 2026-10-21", ERW verdict unsettled. `license_verdicts.csv`:

- MISO (read 7): "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App.", "needs written permission".
- CAISO (read 3): "... may be used by you provided that you keep intact all copyright, trademark and other proprietary notices and that you credit the California ISO when using such materials and/or information.", "may be public".
- ERCOT (read 2): "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified ...", "may be public".
- SPP (read 6): "Permission is implicitly granted to copy and distribute ... (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication ...", "may be public", if the ERW sells anything "needs written permission".

The site holds MISO's rows and keeps the others (`site/lib/license.ts`: a consolidated table decided by grid operators is held row by row, for the rows of those grids).

## Checks (session 2284)

The figures in this note were computed from the rows of `warehouse/output/iso_dam_hub_prices.csv`, read past its 60 header lines (counted, never parsed as comments), with the scripts `runs/c104/s2284/profile.py`, `check_iso_dam.py`, `iso_days.py`, `cross_iso_dam.py` and `cross_iso_dam2.py` (outputs beside them).

- 23,016 rows, the sum the header gives; each member's rows and first and last hours equal its header's "File holds" line (4,248, 8,496, 7,488 and 2,784). No (entity, variable, ts_utc) twice; no blank value; one unit; no constant or placeholder column but `unit` and `freq`.
- Every hub of a market has the same count of hours, and every hour from the market's first to its last is there, except SPP's 15 October.
- The hubs are those of the code: `CAISO_HUBS` (3), `ERCOT_HUBS` (6), `MISO_HUBS` (8), `SPP_HUBS` (2).
- ERCOT's and MISO's vintages are all before the operating day they price, and none is after its row's `retrieved_at`.
- **Against an independent pull:** `iso_zone_prices_history` (session 140's connector, its own requests; `retrieved_at` never the same) holds CAISO's ZP26 and SPP's South hub day-ahead: 2,400 hours in both, all equal.
- Against `iso_hub_prices_history` (5,160 hours: NP15, SP15, INDIANA.HUB, SPPNORTH_HUB) and `ercot_all_hub_prices_history` (8,496 hours, ERCOT's six hubs): all equal, but both cite the same files (`source_url` the same in every row), so they are copies of these rows, not a second source.

## Where the description and the data disagree

1. **Forward days "marked by `vintage`".** The docstring says the next day's auction is included "marked by `vintage`", and session 2's report says `vintage` is the operator's publish time, "otherwise the file's HTTP Last-Modified". CAISO's and SPP's 7,032 rows have no vintage at all, so their forward day is marked only in the member header's "Forward DAM days also included" line, which names the newest run's day alone.
2. **A missing day with no record.** "Strict completeness" holds within a run's window, and a day not written in a window is a failure of that market in `run_status.csv`. SPP's 15 October 2026 is absent from the table with no row in `run_status.csv` naming it; the daily run of 15 October left no row there at all, though its CAISO and ERCOT rows are in the table.
3. **No license in the header, and two flags.** The header names no license; `coverage.csv` says public; the license record says "license needed" for MISO's rows since 21 October 2026, and the ERW verdict is unsettled.
4. **"The 30-day table."** `warehouse/redivis/config.yaml` calls the rolling price tables 30-day tables; nothing trims this one, and it holds 59 days (MISO's 39).

Not acted on: this note changes no file but itself.

Recorded, not changed in session 2284 (no request): CAISO's and SPP's forward days without a vintage, SPP's missing 15 October 2026, the header's missing License line (the license record governs MISO's rows) and `config.yaml`'s 30 days are for the price connector's next change.

## The session report against the table

- `SESSION_29_REPORT.md`: `iso_dam_hub_prices` replaces `{caiso,ercot,miso,spp}_dam_hub_prices` (4), partition column `market` (existing), 15,960 rows, "4 of 4 equal", "ok, row for row": the members and the partition column hold; the 15,960 rows were the table on 29 September, and it has grown to 23,016 since.
- `SESSION_2_REPORT.md`: CAISO's three hubs, MISO's 8, SPP's two, the window from 26 August with a forward day: hold. ERCOT's "5 hubs" were five then; session 8 added HB_HUBAVG (commit `f52bb19d`), and the table holds six hubs back to 26 August. "`vintage` records the publish time where the ISO gives one: the ERCOT document time, otherwise the file's HTTP Last-Modified": holds for ERCOT and MISO; CAISO and SPP give none (disagreement 1).

## What it does not hold

- NYISO's and ISO-NE's day-ahead prices (`nyiso_dam_zone_prices`, `isone_dam_zone_prices`); PJM (licensed, not pulled); MISO after 3 October 2026; real-time prices (`iso_rtm_hub_prices`); nodes and load zones other than the hubs named; days before 26 August 2026 (the hub histories: `ercot_all_hub_prices_history`, `iso_hub_prices_history`, `iso_zone_prices_history`); SPP's 15 October 2026; the operators' price components (energy, congestion, losses).
