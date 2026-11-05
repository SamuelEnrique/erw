# ISO-NE's own hourly real-time LMPs, the Internal Hub and the eight load zones, an hour (final report; preliminary until the final is posted)

Energy Research Warehouse (ERW), method note written in session 2242 (chain 101) for a table first written on 25 September 2026 (session 5, on the human ruling in its prompt, "for ISO-NE add its hourly final real-time" prices; commit `765839ca`, `archive/sessions/SESSION_5_REPORT.md`, decision 7). The 15-minute means of ISO-NE's five-minute prices are `isone_rtm_zone_prices` (`docs/methods/isone_rtm_zone_prices.md`); day-ahead is `isone_dam_zone_prices`; the zones' history from 2019 is `isone_zone_prices_history` (internal).

Tables: `isone_rtm_zone_prices_hourly`

## Publisher and address

ISO New England (ISO-NE), "Real-Time Energy Market Hourly LMPs", final, `https://www.iso-ne.com/isoexpress/web/reports/pricing/-/tree/lmps-rt-hourly-final`. The connector asks one file an operating day, `https://www.iso-ne.com/static-transform/csv/histRpts/rt-lmp/lmp_rt_final_<YYYYMMDD>.csv`, after opening ISO-NE's fuel mix page for its cookies; the rows name `https://www.iso-ne.com/histRpts/rt-lmp/lmp_rt_final_<YYYYMMDD>.csv`, the address the answer was recorded under (the run log of 25 September records the same). Where no final file is posted yet (HTTP 404, or since session 202 an answer with no table), the day comes from ISO-NE's preliminary hourly report through gridstatus 0.36.0 (`ISONE.get_lmp(..., REAL_TIME_HOURLY)`), and its rows say so in `source`. Source ids `isone:rt_lmp_hourly_final` and `isone:rt_lmp_hourly_prelim`. Raw files under `warehouse/raw/isone/<run_id>/` with a manifest (on the runner; none on this machine).

Connector: `warehouse/connectors/iso_prices.py isone --days N`, `pull_isone`, spec RTM_HOURLY. Nine locations: `.H.INTERNAL_HUB`, `.Z.CONNECTICUT`, `.Z.MAINE`, `.Z.NEMASSBOST`, `.Z.NEWHAMPSHIRE`, `.Z.RHODEISLAND`, `.Z.SEMASS`, `.Z.VERMONT` and `.Z.WCMASS`. ISO-NE's hour ending (Eastern) becomes the interval start with gridstatus's own helper, the autumn's repeated hour inferred. Completeness per operating day (session 13): a day is written only when every location has every hour; a day that is not is a gap row in `run_status.csv`, and any earlier rows of it are kept. Rows merge by (entity, variable, ts_utc).

Schedule: the daily run, `warehouse/run_daily.sh` (the loop over `ISOS`, `ercot caiso nyiso spp isone`, `iso_prices.py "$iso" --days "$DAYS"`), on the GitHub runner (`.github/workflows/daily-prices.yml`, cron `0 14 * * *`, `DAYS` 3). No step of `run_data_machine.sh`, `run_data_machine_tables.sh`, `run_monthly.sh` or `refresh_supply.sh` runs it (the ISO-NE step of `refresh_supply.sh` is `isone_dam_cleared.py`); `warehouse/scheduled.py` requires the table for `network_replay` (daily) and `price_compare` (monthly). `run_status.csv`: 50 rows from 20260925T193710Z (local) to 20261023T143058Z (github): 29 ok, 18 gap, 3 failed. `archive_manifest.csv`: 11,664 rows as of run 20261023T152740Z-github. Live set: the last 35 days (`live_set.yaml`, `recent`, the ISO price rule). Readers: the builders `board_page.py`, `cost_of_power.py`, `merchant_revenue.py`, `price_board.py`, `price_compare.py`, `trader_view.py` and `watch.py`; `site/app/prices/compare/page.tsx` and the chat's table list.

## Vintage and revision

The copy here was rebuilt from the ERW's archive "as of run 20261023T152740Z-github" (header line 1); the connector's header that follows is run `20261023T143058Z`, window "ISO-NE operating days 2026-10-20 to 2026-10-22", which "wrote 648 rows: 216 new, 432 replacing earlier rows ...; 11016 rows are kept from earlier runs". `retrieved_at` takes 54 values, one an operating day, from 2026-09-25T19:46:22Z to 2026-10-23T14:31:17Z.

`vintage` of a final row is its file's Last-Modified: the final file of a day was published 1 day after it for 6,912 rows, 2 days for 2,808, 3 for 1,296, 4 for 216 and 5 for 216. The 216 preliminary rows (all of 2026-10-22, the newest day) have no `vintage` ("publish time not given by source"). A preliminary day is replaced by the final one when a later run's three-day window holds it and ISO-NE has posted it; a final day is replaced only while it is in a run's window, so a correction ISO-NE posts later is not taken.

## Shape and variables

Series, 11,664 rows: 9 locations x 1,296 hours, 54 operating days from 2026-08-26 to 2026-10-22 (America/New_York), each held whole (24 hours a location). `entity` `isone:<location>`, `node` the location, `variable` `lmp_rtm`, `unit` USD/MWh, `freq` PT1H, `market` isone_rtm, `geo` "US-CT,US-MA,US-ME,US-NH,US-RI,US-VT" in every row (ISO-NE's footprint, also for a zone in one state).

- Final rows 11,448, preliminary 216. No day mixes the two.
- Four operating days are absent: 2026-10-02, 2026-10-09, 2026-10-14 and 2026-10-15 (disagreement 2).
- Lowest -59.20 (Maine, 2026-08-31T14:00:00Z), highest 112.65 (Vermont, 2026-10-05T11:00:00Z); 82 negative prices, no zero; every value to two decimals or fewer.

| Location | Hours | Mean | Median |
|---|---|---|---|
| .H.INTERNAL_HUB | 1,296 | 38.72 | 36.20 |
| .Z.CONNECTICUT | 1,296 | 38.11 | 35.53 |
| .Z.MAINE | 1,296 | 35.74 | 34.20 |
| .Z.NEMASSBOST | 1,296 | 38.97 | 36.47 |
| .Z.NEWHAMPSHIRE | 1,296 | 38.49 | 36.05 |
| .Z.RHODEISLAND | 1,296 | 38.23 | 35.78 |
| .Z.SEMASS | 1,296 | 38.91 | 36.38 |
| .Z.VERMONT | 1,296 | 39.09 | 36.50 |
| .Z.WCMASS | 1,296 | 38.81 | 36.30 |

## Placing values in time, and what is filled

`ts_utc` is the start of ISO-NE's hour, in UTC; an operating day is the Eastern day, 04:00:00Z to 03:00:00Z while daylight time holds (the whole span here; the clocks go back on 1 November 2026). A day not written whole has no row; nothing is filled from the 15-minute table or the preliminary report of another day.

## License

The header has no License line (nor have the headers of `isone_rtm_zone_prices` and `isone_dam_zone_prices`). `coverage.csv` flags the table public. `license_verdicts.csv`, ISO-NE (read 4): "You are also hereby put on notice that the Content is protected by copyright under United States laws. Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws. [...] To request permission to use a graph, chart, or other image on this website, please email info@iso-ne.com", verdict "needs written permission". `docs/licenses.md`, the table's row: ISO-NE, "needs written permission", flag public, "ruled: license needed from 2026-10-21", ERW verdict "unsettled"; under "Settled by a ruling (session 324)": "needs written permission, by ISO-NE; license needed from 2026-10-21". `license_status.csv`: "license needed", from 2026-10-21, "flagged public; the publisher's sentence read in session 205 asks for it": the pages show "license needed" in place of its numbers until a permission is recorded.

## Checks (session 2242)

The figures in this note were computed from the rows of `warehouse/output/isone_rtm_zone_prices_hourly.csv`, read past its 14 header lines (script `runs/c101/s2242/check_isone.py`, output beside it).

- 11,664 rows, 2026-08-26T04:00:00Z to 2026-10-23T03:00:00Z, as the header states; no (entity, variable, ts_utc) twice; `entity` is `isone:` plus `node` in every row; every `ts_utc` on the hour; every day held has 24 hours for each of the 9 locations; the date in every final row's file name is its operating day.
- Against `isone_rtm_zone_prices` (15-minute means of five-minute prices): in the 9,720 location hours where that table holds all four quarter hours, the hourly price equals the mean of the four within 0.02 USD/MWh in every hour (within 0.01 in 9,557; median difference 0.0033).
- Against `isone_zone_prices_history` (ISO-NE's SMD workbook, internal): the 1,152 zone hours both hold, 2026-08-26T04:00:00Z to 2026-09-01T03:00:00Z, are equal to the cent, as `docs/methods/isone_zone_prices_history.md` says. The Internal Hub is not in that table.

## Where the description and the data disagree

1. **The preliminary report's address is the final report's page.** The header's line "Source: isone:rt_lmp_hourly_prelim Real-Time Energy Market Hourly LMPs, preliminary" gives `.../tree/lmps-rt-hourly-final`, and so do the 216 preliminary rows' `source_url` and `sources.csv`: `pull_isone` gives both reports one page (`ISONE_RTH_PAGE`). The title says "(final)"; the newest day is preliminary.
2. **Days absent, two with no gap row.** The header: "Each day not written is a gap row in warehouse/metadata/run_status.csv." 2026-10-02 and 2026-10-09 are gap rows (each "failed after 4 attempts: EmptyDataError('No columns to parse from file')", the empty final file session 202 since reads as "no final yet"), and no later run in whose window they fell wrote them. 2026-10-14 and 2026-10-15 have no row in `run_status.csv` at all: it records no ISO-NE run between 20261014T142656Z and 20261020T002541Z, and the three-day window of the runs after did not reach back to them.
3. **The license flag.** `coverage.csv` flags the table public; ISO-NE's sentence asks for permission, and the record shows "license needed" from 2026-10-21. The header states no license.

Recorded, not changed in session 2242: the license record governs the table's standing (ISO-NE's terms ask for written permission) whatever its header lacks, as for ISO-NE's other tables; the page address and the four missing days are for the connector's next change, with no request now.

## The session report against the table

`SESSION_5_REPORT.md`: "ISO-NE hourly final (new, 30 days)" and "Finals were posted for every day of the window." Both hold of the rows that remain: the table begins on 2026-08-26, thirty days before 25 September, and every row from then to 2026-10-21 is final.

## What it does not hold

- Five-minute prices or their 15-minute means (`isone_rtm_zone_prices`); day-ahead (`isone_dam_zone_prices`); the LMP's energy, congestion and loss parts; ISO-NE's other nodes; days before 2026-08-26 (`isone_zone_prices_history`, internal, holds the zones from 2019 to August 2026); the four absent days; corrections posted after a day left the run's window.
