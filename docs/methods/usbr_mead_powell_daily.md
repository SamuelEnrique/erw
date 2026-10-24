# Lake Mead and Lake Powell a day: pool elevation, storage, total release and inflow, over each reservoir's period of record (Reclamation's hydrodata)

Energy Research Warehouse (ERW), method note written in session 2218 (chain 098) for a table first written on 24 October 2026 (session 2211 of chain 098, `archive/sessions/SESSION_2211_REPORT.md`). The two dams' monthly generation is in `usbr_hydropower_monthly` (`docs/methods/usbr_hydropower_monthly.md`).

Tables: `usbr_mead_powell_daily`

## Publisher and address

U.S. Bureau of Reclamation (USBR), Upper Colorado Basin Region, reservoir data (hydrodata). The source page in the header is Lake Powell's dashboard, `https://www.usbr.gov/uc/water/hydrodata/reservoir_data/919/dashboard.html`; the files are `https://www.usbr.gov/uc/water/hydrodata/reservoir_data/<site>/csv/<data type>.csv`, one CSV a reservoir and data type, "datetime,<name>", one line a day over the whole period of record. Sites: 919 Lake Powell (Glen Canyon Dam), 921 Lake Mead (Hoover Dam). Data types: 49 pool elevation, 17 storage, 42 total release, 29 inflow (Lake Powell only: Lake Mead's address answered HTTP 404, 196 bytes, in the trial's raw manifest). Source id `usbr:hydrodata_reservoirs`. Files saved under `warehouse/raw/usbr_colorado_reservoirs/` (run `20261024T013511Z`: seven files of 466,903 to 715,967 bytes). data.usbr.gov's RISE API is not asked (its robots file disallows `/rise/api`, read 171).

Connector: `warehouse/connectors/usbr_colorado_reservoirs.py` (session 2211): `[--offline] [--out-dir DIR]`, at most seven requests, each reused from the raw store with `--offline`. A header not "datetime,<name>", a date not YYYY-MM-DD, a value that is not a number or a day given twice stops the run. The files state no unit; the connector takes them from Reclamation's Lower Colorado levels page ("ft=feet above mean sea level, cfs=cubic feet per second, kaf=1000 acre-feet", read 346) and the Glen Canyon Dam status page (read 347): `ft` (Decision 71), `acre-ft` (Decision 72), `ft3/s` (Decision 65). **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

One run, `20261024T013619Z`, written offline from the seven files retrieved at 2026-10-24T01:35:11Z and 01:35:12Z (`retrieved_at`: 46,073 rows at 01:35:11Z, 146,436 at 01:35:12Z). `vintage` is each file's Last-Modified, seven values: Lake Powell's four files 2026-10-23T22:06:34Z to 22:11:30Z, Lake Mead's three 22:37:52Z to 22:37:57Z. The header: "This run wrote 192509 rows: 192509 new, 0 replacing ...; 0 rows are kept from earlier runs."

Reclamation: "All data considered provisional and subject to revision" (header line 2). No row carries a provisional flag; every row is provisional. A later run merges by (entity, variable, ts_utc): a revised value replaces the old one, but a day Reclamation later blanks writes no row, so the earlier value would be kept.

## Shape and variables

Series, 192,509 rows, two entities: `usbr_hydrodata:919` (92,544 rows) and `usbr_hydrodata:921` (99,965), `node` the reservoir's name, `freq` P1D, `geo` US-AZ (session 2211's choice: both dams stand on Arizona's border), `market` blank.

| Entity | Variable | Unit | Rows | First day | Last day | Lowest (day) | Highest (day) |
|---|---|---|---|---|---|---|---|
| 919 Lake Powell | inflow | ft3/s | 23,237 | 1963-03-11 | 2026-10-22 | 86.93039 (2001-12-10) | 191,303.961 (1984-06-01) |
| 919 Lake Powell | pool_elevation | ft | 22,945 | 1963-12-28 | 2026-10-22 | 3,394.5 (1964-05-11) | 3,708.34009 (1983-07-14) |
| 919 Lake Powell | storage | acre-ft | 23,128 | 1963-06-28 | 2026-10-22 | 0 (1963-06-28) | 25,695,200 (1983-07-14) |
| 919 Lake Powell | total_release | ft3/s | 23,234 | 1963-03-14 | 2026-10-22 | 869 (1977-05-22) | 92,600 (1983-06-29) |
| 921 Lake Mead | pool_elevation | ft | 33,501 | 1935-02-02 | 2026-10-22 | 670 (1935-02-02) | 1,225.82996 (1983-07-24) |
| 921 Lake Mead | storage | acre-ft | 32,655 | 1937-05-28 | 2026-10-22 | 6,783,480 (2026-10-22) | 29,904,000 (1942-07-08) |
| 921 Lake Mead | total_release | ft3/s | 33,809 | 1934-04-01 | 2026-10-23 | 0 (1935-02-10) | 50,800 (1983-07-29) |

Every series holds every day from its first to its last; no day is missing inside a series. Two values are zero (Lake Powell's storage on its first day, Lake Mead's release on 1935-02-10); none is negative. Values keep Reclamation's digits: up to six decimals for elevation (Lake Mead 1,214.04004 ft on 2000-01-01), five for release and inflow, two for storage.

The latest days: Lake Mead on 2026-10-22 stood at 1,037.16 ft and 6,783,480 acre-ft, its lowest elevation since 1937-04-20 (while the lake was filling) and the lowest storage in the table. Lake Powell's lowest elevation since 1968-05-15 is 3,516.62 ft on 2026-09-15; on 2026-10-22 it stood at 3,523.59 ft and 5,464,123.59 acre-ft, after inflows of 37,181.845 and 63,368.3764 ft3/s on 21 and 22 October.

Storage is Reclamation's figure as the files give it, and the files do not say which elevation-capacity table stands behind each year. Lake Mead's storage is highest, 29,904,000 acre-ft, on 1942-07-08 at 1,213.44 ft, while on the day of its highest elevation, 1,225.83 ft on 1983-07-24, storage is 26,864,000 acre-ft: a higher level with less storage. A reader comparing storage across decades checks it against elevation.

## Placing values in time, and what is filled

`ts_utc` is the day at 00:00:00Z (Decision 11); Reclamation's day is the reservoir's local day (UTC-7 at both dams in October). The files do not say whether a day's elevation and storage are a reading at a fixed hour or the day's end, nor how a day's release and inflow are averaged. A blank has no row; nothing is filled. The last day of Lake Mead's release is a day that had not ended when the file was written (below).

## License

Header: "License: public (U.S. Bureau of Reclamation, a work of the U.S. government; the Department of the Interior's notice). Cite: U.S. Bureau of Reclamation, reservoir data, provisional." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 173 (session 2005, Reclamation's disclaimer pointing to the Department's notice: "Generally, materials produced by federal agencies are in the public domain and may be reproduced without permission"), verdict "may be public", if the ERW sells anything "may be public"; the table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2218)

The figures in this note were computed from the rows of `warehouse/output/usbr_mead_powell_daily.csv`, read past its 10 header lines (scripts `runs/c098/s2218/usbr.py` and `usbr2.py`, outputs beside them).

- 192,509 rows, `ts_utc` from 1934-04-01T00:00:00Z to 2026-10-23T00:00:00Z, as the header states; each series' first and last day as header line 3 lists them; no (entity, variable, ts_utc) twice; units ft (56,446 rows), acre-ft (55,783) and ft3/s (80,280), as the header names them.
- The trial's table (`runs/c098/s2211/trial/usbr_mead_powell_daily.csv`) has the same rows, byte for byte.
- Session 2211's cross-check (`runs/c098/s2211/cross.py`), run again on the table from the main checkout: its output is identical to the saved `cross.out`. Lake Powell on 2026-09-30: 3,518.08 ft and 5.16 million acre-ft, the Glen Canyon Dam page's end of September as the script quotes it. Total release against the USGS gauge below each dam (`usgs_streamflow_daily`), 2020 to 2025: Hoover against 09421500, 2,192 days, median 1.000, within 10 percent on 100.0 percent (no day outside; the largest difference 2.59 percent, `usbr2.py`); Glen Canyon against Lees Ferry (09380000), 2,192 days, median 0.988, within 10 percent on 99.7 percent (6 days outside, the largest 21.9 percent). Hoover's monthly net generation (`usbr_hydropower_monthly`) against Lake Mead's mean elevation, 130 months of 2015 to 2025: correlation 0.262.
- The trial's raw manifest (`warehouse/raw/usbr_colorado_reservoirs/20261024T013511Z/`): seven answers of HTTP 200 with their Last-Modified, and Lake Mead's inflow file HTTP 404.

## Where the description and the data disagree

1. **A last day not yet over.** The header describes a value a day, and session 2211's report says the table runs "to 22 October 2026". Lake Mead's total release holds 2026-10-23 as well: 4,638.2 ft3/s, against 7,527.79167 to 11,627.75 in October's first 22 days (their mean 8,982.9; a release this low is not impossible, 84 days since 2020 are lower). Its file was last modified at 2026-10-23T22:37:54Z (15:37 at the dam) and retrieved at 2026-10-24T01:35:12Z (18:35 at the dam): the day had not ended. The value is most likely a part day's; the file does not say. Every other series ends on 2026-10-22. A later run would replace the row, but no schedule runs the connector.

Acted on in session 2218: the connector now leaves out any day on or after the retrieval's own date in Arizona's time (no daylight saving), and counts it in the header; session 2221's connector does the same in Mountain time. The table was written again offline from the saved files, its file removed first under the data lock: 192,508 rows, Lake Mead's total release ending 2026-10-22 like every other series. The figures above (192,509 rows, 99,965 for Lake Mead, the release to 2026-10-23) describe the table as session 2211 wrote it.

## The session report against the table

Every figure of `SESSION_2211_REPORT.md` checked against the table, the saved raw manifest and the rerun cross-check holds (192,509 rows, Lake Mead's release from 1934 and its elevation from 1935, Lake Powell's from 1963, Lake Mead's inflow answering HTTP 404, the units as Decisions 71 and 72, 3,518.08 ft and 5.16 million acre-ft, the two gauge comparisons, 130 months and 0.262, the trial's eight requests in the raw manifest; the other seven of the fifteen pulls are not testable from the table), except:

- "to 22 October 2026": Lake Mead's total release runs to 23 October 2026, a day not over when the file was written (disagreement 1).

## What it does not hold

- Lake Mead's inflow (Reclamation publishes no file for it), Reclamation's other reservoirs, readings within the day, Reclamation's projections, and the dams' generation (`usbr_hydropower_monthly`).
