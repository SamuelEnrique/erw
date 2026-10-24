# ISO-NE's eight load zones, day-ahead and real-time LMP by the hour, 2019 to August 2026 (SMD Hourly Data), internal

Energy Research Warehouse (ERW), method note written in session 2222 (chain 098) for a table first written on 7 October 2026 (session 140, `archive/sessions/SESSION_140_REPORT.md`, "What a datacenter pays", an approved pull). The public table of the same connector is `docs/methods/iso_zone_prices_history.md`.

Tables: `isone_zone_prices_history`

## Publisher and address

ISO New England (ISO-NE), Zonal Information, "SMD Hourly Data": a workbook a year, one sheet a load zone, columns DA_LMP and RT_LMP, listed at `https://www.iso-ne.com/isoexpress/web/reports/load-and-demand/-/tree/zone-info`. Source id `isone:smd_hourly_lmp`. Raw files under `warehouse/raw/zone_price_history/isone/` with `manifest.csv`; the 2025 and 2026 workbooks are those `isone_zone_load.py` keeps in `warehouse/raw/isone_zone_load/` and are not asked for again.

Connector: `warehouse/connectors/zone_price_history.py` (session 140), which writes two tables split by license: ISO-NE's markets here, NYISO's, CAISO's and SPP's in `iso_zone_prices_history`; the writer refuses a row of the other table's market. `--pull` saves files (no lock, no table); `--write` reads only saved files and merges them, a market at a time; `--check` compares with the six-week tables. Ceiling: 3,000,000 rows of these series read, over every run of the history pull and both tables (the header: 2,821,084 read, 9,924,939 rows in the files).

Schedule: **none reaches this table where it is held.** `warehouse/refresh_supply.sh` runs `zone_price_history.py --pull --recent 9` and `--write --recent 9` only when `warehouse/output/iso_zone_prices_history.csv` exists, and is called by `run_daily.sh` on Saturdays on the GitHub runner, which holds neither history. The data machine's weekly steps (`warehouse/run_data_machine_tables.sh`, session 277) ask CAISO only (`--iso caiso`). The table is in `catalogue_hold` of `warehouse/supabase/live_set.yaml` (not loaded; "the page reads the site's own files, built from them"). Reader: `warehouse/derived/datacenter_page.py`.

## Vintage and revision

One write, run `20261007T103526Z` ("This run wrote 1075024 rows: 1075024 new"); the last header line says the copy here was restored from the internal Redivis draft by `scripts/sync.py`. `retrieved_at` has 8 values, 2026-10-07T01:43:56Z to 09:21:21Z (each row's is its file's); `vintage` is blank in every row; 8 distinct `source_url` values. A later workbook of the current year would revise its months on a merge by (entity, variable, ts_utc); none has been merged.

## Shape and variables

Series, 1,075,024 rows: 8 load zones, 2 markets, 67,189 hours each, 2019-01-01T05:00:00Z to 2026-09-01T03:00:00Z. `entity` `isone:<zone>` (.Z.CONNECTICUT, .Z.MAINE, .Z.NEMASSBOST, .Z.NEWHAMPSHIRE, .Z.RHODEISLAND, .Z.SEMASS, .Z.VERMONT, .Z.WCMASS), `node` the zone; `variable` `lmp_dam` (market `isone_dam`) or `lmp_rtm` (market `isone_rtm`, ISO-NE's own hourly average of its five-minute prices); `unit` USD/MWh, `freq` PT1H, `geo` "US-CT,US-MA,US-ME,US-NH,US-RI,US-VT" on every row.

| Zone | Day-ahead mean | Real-time mean |
|---|---|---|
| .Z.CONNECTICUT | 48.74 | 47.75 |
| .Z.MAINE | 48.76 | 47.15 |
| .Z.NEMASSBOST | 50.47 | 49.11 |
| .Z.NEWHAMPSHIRE | 50.15 | 48.83 |
| .Z.RHODEISLAND | 49.84 | 48.49 |
| .Z.SEMASS | 50.37 | 48.98 |
| .Z.VERMONT | 49.49 | 48.22 |
| .Z.WCMASS | 49.99 | 48.70 |

Day-ahead: lowest -3.22 (.Z.MAINE, 2025-05-11T17:00:00Z), highest 975.00 (.Z.NEMASSBOST, 2026-01-27T23:00:00Z), 7 negative. Real time: lowest -151.82 (.Z.CONNECTICUT, 2022-05-21T16:00:00Z), highest 2,274.99 (.Z.NEMASSBOST, 2022-12-24T22:00:00Z), 2,955 negative. The mean of the zones a year, day-ahead: 31.11 (2019), 23.23, 45.77, 85.20 (2022), 36.72, 41.40, 67.54, 75.53 (2026 to August).

## Placing values in time, and what is filled

`Hr_End` is the hour ending in Eastern prevailing time; `ts_utc` is the hour's start in UTC. The workbooks from 2024 give 23 lines on the spring day and 25 on the autumn day. Those of 2019 to 2023 give 24 on both, and their Notes sheet says the spring line 02 averages the lines 01 and 03 and the autumn line 02 averages two hours; neither is written (the header's two notes: 40 lines each). So each zone and market lacks two hours in each autumn of 2019 to 2023: from 05:00Z for two hours on 2019-11-03, 2020-11-01, 2021-11-07, 2022-11-06 and 2023-11-05, 10 hours a series, 80 a market. Nothing else is missing between the first and last hour; nothing is filled, averaged across zones or estimated. A cell held as a binary fraction within a millionth of a cent figure is written as that figure.

## License

Header: "License: internal. ISO-NE's legal notice: "Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws." (https://www.iso-ne.com/legal-privacy, read 6 October 2026). Not published, in no public dataset and no download." `license_verdicts.csv`, ISO-NE (read 4): verdict "needs written permission" (contact info@iso-ne.com). `docs/licenses.md`: "needs written permission", decided by ISO-NE, flag internal, "agrees", ERW verdict internal.

## Checks (session 2222)

The figures in this note were computed from the rows of `warehouse/output/isone_zone_prices_history.csv`, read past its 15 header lines (scripts `runs/c098/s2222/check_zone_hist.py` and `cross_isone_hist.py`).

- 1,075,024 rows, `ts_utc` 2019-01-01T05:00:00Z to 2026-09-01T03:00:00Z, and 537,512 rows a market, as the header states; "80 intervals missing between each entity's first and last" a market holds (8 zones, 10 hours each); no (entity, variable, ts_utc) twice; no blank value.
- Against the six-week tables over the 144 hours both hold (2026-08-26 to 2026-08-31, Eastern): `isone_dam_zone_prices` and `isone_rtm_zone_prices_hourly` agree to the cent in all 1,152 zone hours of each.

## Where the description and the data disagree

1. **A weekly refresh that does not happen.** The docstring's usage gives `--pull --recent 9` and `--write --recent 9` as "the weekly run" and `refresh_supply.sh` says ISO-NE's current-year workbook is read each week as `isone_zone_load.py` keeps it; no schedule runs that write where the table is held, so the table ends at 2026-09-01T03:00:00Z (31 August, Eastern) while ISO-NE's six-week tables run to 24 October.

Recorded, not changed in session 2222: a write from the saved workbooks is the data machine's to schedule (the owner's rulings govern which grids it asks); session 2222 made no request.

## The session report against the table

`SESSION_140_REPORT.md` gives "1,075,024 internal" rows for this table, and the table holds 1,075,024. Its ceiling count at the landing (2,820,388 of 3,000,000) is below this header's 2,821,084, which counts a later run; not testable from the rows.

## What it does not hold

- ISO-NE's Internal Hub (in the six-week tables and `iso_hub_prices_history`), its nodes, the loss and congestion parts, five-minute prices, days after 31 August 2026, and the two autumn hours of 2019 to 2023 noted above.
