# Zone and hub prices from 2019: NYISO's eleven zones, CAISO's ZP26 and SPP's South hub, day-ahead and real time

Energy Research Warehouse (ERW), method note written in session 2222 (chain 098) for a table first written on 7 October 2026 (session 140, `archive/sessions/SESSION_140_REPORT.md`, "What a datacenter pays", an approved pull). ISO-NE's zones, from the same connector, are in `isone_zone_prices_history` (internal, `docs/methods/isone_zone_prices_history.md`).

Tables: `iso_zone_prices_history`

## Publisher and address

Five markets from three publishers, each file saved once under `warehouse/raw/zone_price_history/<iso>/` with `manifest.csv`:

- `nyiso_dam`: New York Independent System Operator (NYISO), Day-Ahead Market LBMP, zonal (P-2A), a zip a month, `http://mis.nyiso.com/public/csv/damlbmp/<YYYYMM>01damlbmp_zone_csv.zip`; source id `nyiso:damlbmp`.
- `nyiso_rtm`: NYISO, Time-Weighted/Integrated Real-Time LBMP, zonal, hourly (P-4A), `http://mis.nyiso.com/public/csv/rtlbmp/<YYYYMM>01rtlbmp_zone_csv.zip`; `nyiso:rtlbmp`.
- `caiso_dam` and `caiso_rtm`: California ISO (CAISO), OASIS PRC_LMP (day-ahead, hourly) and PRC_INTVL_LMP (real-time dispatch, 5-minute), a calendar month a request, node TH_ZP26_GEN-APND; `caiso:PRC_LMP`, `caiso:PRC_INTVL_LMP`.
- `spp_dam`: Southwest Power Pool (SPP), Day-Ahead LMP by Settlement Location, a file a day, SPPSOUTH_HUB; a finished year read from SPP's yearly archive by HTTP range requests; `spp:DA-LMP-SL`.

Connector: `warehouse/connectors/zone_price_history.py` (session 140). `--pull` saves files, newest first, one request at a time a publisher (no lock, no table); `--write` reads only the saved files and merges them into the table a market at a time; `--check` compares with the six-week tables. Ceiling: 3,000,000 rows of these series read over every run of the history pull, both tables (the header: 2,885,403 read; 81,816,868 rows in the files); a weekly refresh (`--recent`) has its own 250,000.

Schedule: the data machine's weekly steps (`warehouse/run_data_machine_tables.sh`, session 277: "the zone price history's CAISO part (ZP26), which refresh_supply.sh asked only on the GitHub runner, where the table is not held, so no run refreshed it (NYISO's and SPP's parts are not this machine's to ask: a ruling)"): `dm_zone_history_pull` (`--pull --iso caiso --recent 9`) and `dm_zone_history_write` (`--write --iso caiso --recent 9`). `warehouse/refresh_supply.sh` (Saturdays, from `run_daily.sh` on the GitHub runner) runs its own step only where this file exists, so it does nothing there. `warehouse/run_data_machine.sh` and `warehouse/scheduled.py` name the table among the histories the data machine holds and restores. In `catalogue_hold` of `warehouse/supabase/live_set.yaml` (not loaded). Readers: `warehouse/derived/datacenter_page.py`, `capture_price.py`, and through `scheduled.py` the seller's hub files.

## Vintage and revision

The header's run: `20261019T174045Z` (`--write`, CAISO's newest files: "This run wrote 1104 rows: 600 new, 504 replacing ...; 1664541 rows are kept from earlier runs"). `retrieved_at` has 3,076 values, 2026-10-07T09:18:36Z to 2026-10-19T17:40:36Z (NYISO and SPP to 2026-10-09; CAISO to 2026-10-19). `vintage` is the file's Last-Modified for NYISO (189 values, 2019-01-30T14:34:03Z to 2026-10-09T07:07:04Z) and blank for CAISO and SPP (171,911 rows). 39,281 day-ahead NYISO rows have a vintage before their hour, by 17 minutes to 1 day 13.5 hours: day-ahead prices are published ahead. 912 distinct `source_url` values. A month refetched after it ended replaces its rows on a merge by (entity, variable, ts_utc).

## Shape and variables

Series, 1,665,645 rows, partition column `market`; `unit` USD/MWh; `entity` `<iso>:<node>`, `node` the zone or node.

| Market | Variable | freq | Entities | Rows | First | Last |
|---|---|---|---|---|---|---|
| nyiso_dam | lmp_dam | PT1H | 11 zones | 749,485 | 2019-01-01T05:00:00Z | 2026-10-10T03:00:00Z |
| nyiso_rtm | lmp_rtm | PT1H | 11 zones | 744,249 | 2019-01-01T05:00:00Z | 2026-10-09T07:00:00Z |
| caiso_dam | lmp_dam | PT1H | TH_ZP26_GEN-APND | 29,088 | 2023-06-26T07:00:00Z | 2026-10-20T06:00:00Z |
| caiso_rtm | lmp_rtm_15m_mean | PT15M | TH_ZP26_GEN-APND | 74,688 | 2024-09-01T07:00:00Z | 2026-10-19T06:45:00Z |
| spp_dam | lmp_dam | PT1H | SPPSOUTH_HUB | 68,135 | 2019-01-01T06:00:00Z | 2026-10-10T04:00:00Z |

NYISO's zones: CAPITL, CENTRL, DUNWOD, GENESE, HUD VL, LONGIL, MHK VL, MILLWD, N.Y.C., NORTH, WEST; `geo` US-NY. CAISO `geo` US-CA; SPP `geo` the fourteen states of its footprint in one string.

| Entity | Day-ahead mean | Real-time mean | Real-time lowest | Real-time highest |
|---|---|---|---|---|
| NORTH | 34.28 | 33.84 | -1,300.74 | 2,751.55 |
| WEST | 37.16 | 35.85 | -583.48 | 2,571.68 |
| GENESE | 36.41 | 35.69 | -792.93 | 2,733.54 |
| CENTRL | 37.91 | 37.34 | -571.46 | 2,907.33 |
| MHK VL | 39.06 | 38.32 | -568.23 | 2,982.98 |
| HUD VL | 46.18 | 45.18 | -217.81 | 3,082.68 |
| MILLWD | 46.83 | 46.22 | -81.38 | 3,108.82 |
| DUNWOD | 46.97 | 46.37 | -81.69 | 3,111.09 |
| N.Y.C. | 47.95 | 47.71 | -88.11 | 3,207.74 |
| CAPITL | 49.21 | 48.09 | -80.05 | 3,016.94 |
| LONGIL | 53.85 | 53.86 | -1,086.21 | 4,522.13 |
| ZP26 | 34.07 | 29.94 (15-minute) | -105.64 | 1,303.04 |
| SPP South | 35.10 | not held | | |

Highest prices: NYISO day-ahead 1,060.28 (DUNWOD, 2026-01-28T20:00:00Z), real time 4,522.13 (LONGIL, 2025-06-24T22:00:00Z); SPP South 4,630.5689 (2021-02-18T11:00:00Z); ZP26 day-ahead 1,092.8085 (2023-08-17T02:00:00Z). Lowest: NYISO real time -1,300.74 (NORTH, 2019-02-26T16:00:00Z). Negative values: nyiso_dam 38, nyiso_rtm 5,603, caiso_dam 3,134, caiso_rtm 8,947, spp_dam 4,233.

## Placing values in time, and what is filled

`ts_utc` is the interval's start in UTC. NYISO stamps the hour's start in Eastern time and gives the autumn hour twice, placed by its order; CAISO and SPP give GMT. CAISO's real time is the mean of the three 5-minute RTD prices in a quarter hour, written only when all three are held. Nothing is filled or estimated; a zone hour a file gives twice is written once when its rows agree and not at all when they differ.

Missing between first and last: none in `nyiso_dam`, `caiso_dam`, `caiso_rtm` or `spp_dam`. `nyiso_rtm` lacks 456 hours at every zone, 2026-07-01T04:00:00Z to 2026-07-19T03:00:00Z and 2026-07-20T04:00:00Z to 2026-07-21T03:00:00Z: 19 days of July 2026 that NYISO's monthly archive does not hold and whose daily files answer HTTP 404 (the docstring). Every NYISO hour held has all 11 zones. NYISO's real time ends after 28 hours of 8 and 9 October (Eastern), the current month's file as it stood when fetched.

## License

Header: "Licenses by publisher (every source of this table is public in the registry): NYISO public with a caution (its notice grants no license and forbids republishing "any image or video on this website as a stand-alone file", not data, https://www.nyiso.com/legal-notice); CAISO public with credit (https://www.caiso.com/privacy-terms-of-use); SPP public with citation (...); all read 6 October 2026." `license_verdicts.csv`: NYISO (read 5) "needs written permission"; CAISO (read 3) public with credit; SPP (read 6) public with citation, commercial use needing written authorization. `license_status.csv`: "license needed" from 2026-10-21, NYISO, "needs written permission". `docs/licenses.md`: verdict "needs written permission", decided by NYISO, flag public, "ruled: license needed from 2026-10-21", ERW verdict "unsettled"; held figures from this table still shown on `/research` and five of its views and cards.

## Checks (session 2222)

The figures in this note were computed from the rows of `warehouse/output/iso_zone_prices_history.csv`, read past its 17 header lines (scripts `runs/c098/s2222/check_zone_hist.py` and `cross_iso_hist.py`).

- 1,665,645 rows; each market's rows, first and last interval as header line 3 states; no (entity, variable, ts_utc) twice; no blank value; no row of an ISO-NE market.
- Against the six-week tables over the intervals both hold, from 2026-08-26: `nyiso_dam_zone_prices`, 11,880 zone hours, all equal to the cent; `iso_dam_hub_prices` ZP26, 1,320 hours, all equal; `iso_rtm_hub_prices` ZP26, 5,088 quarter hours, all within 0.0001.
- NYISO's own hourly real time against the hourly mean of the four quarter hours of `nyiso_rtm_zone_prices` (the 5-minute prices): 11,660 zone hours; equal to the cent in 11,146, within 0.01 in 11,647 (session 2214 counted 11,646 with its rounding), within 0.15 in all (largest 0.1408).
- No ERW table holds SPPSOUTH_HUB to check `spp_dam` against.

## Where the description and the data disagree

1. **The license.** The docstring and header give NYISO as "public, with a caution" and say "every source of this table is public in the registry" (`sources.csv` still says public); the license record rules NYISO's data "license needed" from 2026-10-21, ERW verdict unsettled, and pages still show figures from the table.
2. **A weekly refresh for three grids, done for one.** The docstring's usage gives `--pull --recent 9` as "the weekly run: the newest files", and `refresh_supply.sh` describes NYISO's and CAISO's current month and SPP's last nine daily files; only CAISO's part is refreshed (on the data machine, session 277). NYISO's rows end at 2026-10-09T07:00:00Z (real time) and 2026-10-10T03:00:00Z (day-ahead), SPP's at 2026-10-10T04:00:00Z, while CAISO's run to 20 October.
3. **Spans that read as complete.** Header line 3 gives `nyiso_rtm` as "744,249 rows, 2019-01-01T05:00:00Z to 2026-10-09T07:00:00Z" without the 19 July days absent at every zone; the docstring and session 140's report say them, the header does not.

Recorded, not changed in session 2222: NYISO's and SPP's parts are not the data machine's to ask without a ruling, and the license record governs the table's standing whatever its header says; no request was made.

## The session report against the table

Every figure of `SESSION_140_REPORT.md` about this table that the rows can test holds: CAISO's ZP26 day-ahead from 26 June 2023; NYISO's archive lacking 19 days of July 2026; NYISO's eleven zones from 2019; and "Day-ahead power there cost USD 60.16 per MWh in the West zone and 73.10 in the city over the same twelve months", which the rows give for October 2025 to September 2026 (60.16 and 73.10). "SPP South was 149 days at this landing ... a later rebuild fills it": the table now holds SPP South every hour from 2019. The landing's 1,598,612 public rows are not testable from today's 1,665,645.

## What it does not hold

- ISO-NE (in `isone_zone_prices_history`), MISO and PJM; SPP's real time (not asked for); CAISO's day-ahead before 26 June 2023 (OASIS keeps about 39 months) and real time before 1 September 2024; NYISO's generator nodes; the loss and congestion parts; NYISO's real time for 19 days of July 2026; NYISO and SPP after 9 and 10 October 2026.
