# NYISO day-ahead reserve and regulation prices by the hour: five zones and the control area (P-5, damasp)

Energy Research Warehouse (ERW), method note written in session 2124 (chain 079) for a table first written on 4 October 2026 (session 85). The method shared by the day-ahead reserve price tables is `docs/methods/capacity_and_ancillary.md`, which the header names.

Tables: `nyiso_as_prices`

## Publisher and address

New York Independent System Operator (NYISO), "Day-Ahead Market Ancillary Services Prices", report P-5 (`damasp`), list page `http://mis.nyiso.com/public/P-5list.htm`. One zip a month, `http://mis.nyiso.com/public/csv/damasp/<YYYYMM>01damasp_csv.zip`, holding one CSV an operating day (`<YYYYMMDD>damasp.csv`). Source id `nyiso:damasp` (in `sources.csv`, license public, first and last seen 2026-10-04). Raw files: `warehouse/raw/nyiso_as_prices/`.

Connector: `warehouse/connectors/nyiso_as_prices.py` (session 85), with the loop shared by the reserve price connectors, `warehouse/connectors/iso_as_common.py`. One request a month; the month in progress is fetched again on each run and a finished month is read from the raw files. The window starts 2024-09-01 (the approved start) and runs to the day before tomorrow, Eastern. Ceiling 500,000 rows. A run asks nothing while NYISO is in `paused_sources.csv`.

No schedule runs it: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh` or `.github/workflows/` names it. `license_verdicts.csv` says why: "Session 308 (the owner's default of 18 October 2026 to ruling 1 of docs/state/morning_2026-10-14.md): nyiso_as_prices gets no scheduled step until this license is answered." Reader named in `license_tables.csv`: `battery_stack_review_monthly`.

## Vintage and revision

One run, `20261004T040915Z` (4 October 2026): "This run wrote 293376 rows: 293376 new, 0 replacing". `retrieved_at` runs from 2026-10-04T03:33:06Z to 2026-10-04T04:09:33Z, 26 values, one per monthly zip; the run began at 04:09:15Z, so the earlier times are those of raw files already saved, from which a finished month is read. The last header line: "Restored from the Redivis draft (energy_research_warehouse) by scripts/sync.py". `vintage` is empty. No run has refreshed the table since 4 October 2026.

## Shape and variables

Series, 293,376 rows: 16 series of 18,336 hours each. `unit` USD/MW-hour (US dollars per MW of capacity held for one hour; the file's "$/MWHr"), `freq` PT1H, `geo` US-NY, `market` nyiso_dam, `node` the zone as NYISO names it (or NYCA), `source_url` the monthly zip; `vintage` empty.

| `entity` | Variables | Stands for |
|---|---|---|
| nyiso:WEST | spin10, nsync10, op30 | WEST, and GENESE, CENTRL, NORTH and MHK VL, which NYISO prices alike |
| nyiso:CAPITL | spin10, nsync10, op30 | CAPITL |
| nyiso:HUD VL | spin10, nsync10, op30 | HUD VL, and MILLWD and DUNWOD |
| nyiso:N.Y.C. | spin10, nsync10, op30 | N.Y.C. |
| nyiso:LONGIL | spin10, nsync10, op30 | LONGIL |
| nyiso:NYCA | reg | the New York Control Area's one regulation price |

Variables are `as_price_dam_spin10` (10 Min Spinning Reserve), `as_price_dam_nsync10` (10 Min Non-Synchronous Reserve), `as_price_dam_op30` (30 Min Operating Reserve) and `as_price_dam_reg` (NYCA Regulation Capacity).

| Series | Lowest | Highest (hour) | Mean |
|---|---|---|---|
| WEST spin10 / nsync10 / op30 | 1.75 / 1.75 / 1.75 | 391.12 each (2026-07-02T23:00:00Z) | 6.7427 / 6.5935 / 6.5756 |
| CAPITL spin10 / nsync10 / op30 | 2.0 / 2.0 / 1.75 | 710.78 (2026-01-28T11:00:00Z) / 710.78 (same) / 391.12 (2026-07-02T23:00:00Z) | 9.1120 / 8.4312 / 6.5756 |
| HUD VL spin10 / nsync10 / op30 | 2.0 / 2.0 / 1.95 | 710.78 / 710.78 (2026-01-28T11:00:00Z) / 652.97 (2026-07-03T21:00:00Z) | 9.9368 / 9.2561 / 7.4004 |
| LONGIL spin10 / nsync10 / op30 | 2.0 / 2.0 / 1.95 | 710.78 / 710.78 / 652.97 | 9.9368 / 9.2561 / 7.4004 |
| N.Y.C. spin10 / nsync10 / op30 | 2.0 / 2.0 / 2.0 | 757.66 / 757.66 (2026-07-03T22:00:00Z) / 677.97 (2026-07-03T21:00:00Z) | 12.4609 / 11.7801 / 8.1204 |
| NYCA reg | 1.35 (2024-12-17T05:00:00Z) | 746.92 (2026-01-28T20:00:00Z) | 15.7963 |

## Placing values in time

- Each row of NYISO's file has a `Time Stamp` (MM/DD/YYYY HH:MM, local) and a `Time Zone` (EDT or EST). The connector adds 4 hours for EDT and 5 for EST and takes the result as UTC: `ts_utc` is the start of the hour. The repeated autumn hour is told apart by its zone label.
- A file whose stamps fall on another day than its name, whose zones are not NYISO's eleven, or whose columns changed stops the run.

## What is and is not filled

- A (zone, product, operating day) is written only when every hour of the day is there exactly once (24, or 23 and 25 at the clock changes); an empty cell is not a price and gives no row. The header: "0 are left out of this run."
- The six zones not kept are compared in every file with the kept zone of their set; the header: "a zone not kept differed from the kept zone of its set in 0 zone-product-hours". Regulation must be one price across all eleven zones in every hour, or the run fails.
- Nothing is filled.

## License

Header: "License: public, with a caution. NYISO's legal notice (https://www.nyiso.com/legal-notice) does not forbid republishing its market data and grants no license: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site"." `license_verdicts.csv` records NYISO, read 5: "needs written permission", for public and for commercial use. `docs/licenses.md` lists `nyiso_as_prices` under NYISO: verdict "needs written permission", decided by NYISO, flag public, "ruled: license needed from 2026-10-21", ERW verdict "unsettled".

## Checks (session 2124)

The figures in this note were computed from the rows of `warehouse/output/nyiso_as_prices.csv`, read past its 13 header lines.

- 293,376 rows, `ts_utc` from 2024-09-01T04:00:00Z to 2026-10-05T03:00:00Z: operating days 2024-09-01 to 2026-10-04 (Eastern), 764 days with none absent, as the header says. 764 days of 16 series at 24 hours, with two 23-hour and two 25-hour days, gives the 293,376.
- No (entity, variable, ts_utc) is given twice. Each series holds all 764 days; the days of other than 24 hours are 2024-11-03 and 2025-11-02 (25) and 2025-03-09 and 2026-03-08 (23).
- Consistency down the cascade: in every one of the 18,336 hours, in every zone, spin10 is at least nsync10 and nsync10 at least op30 (0 exceptions).
- Consistency across zones: in every hour and product, N.Y.C. is at least HUD VL, HUD VL at least CAPITL, CAPITL at least WEST (0 exceptions). CAPITL's op30 equals WEST's in all 18,336 hours.
- LONGIL against HUD VL: equal in every hour of nsync10 and op30; spin10 differs in 3 hours, by 0.01 each: 2024-10-25T11:00:00Z (19.93 against 19.94), 2024-10-27T21:00:00Z (7.82 against 7.83), 2026-05-02T02:00:00Z (12.68 against 12.67). The docstring's count, "differed from HUD VL's in 3 hours", holds.

## Where the description and the data disagree

1. **The license line.** The header says "License: public, with a caution" and `sources.csv` gives the source's license as public; the docstring says the table is "Public by the ERW's standing rule (every ISO but PJM); a person can rule otherwise." The warehouse's own license records have since ruled otherwise: `license_verdicts.csv` gives NYISO "needs written permission" and `docs/licenses.md` "ruled: license needed from 2026-10-21", ERW verdict "unsettled". The header has not been rewritten since the run of 4 October 2026.
2. **The window of the LONGIL count.** The docstring gives LONGIL's 3 differing hours "over the whole window (2024-09-01 to 2026-10-03)"; the table's window runs to 2026-10-04. Counted over the table, the figure is still 3.

Recorded, not changed in session 2124: the license record (`docs/licenses.md`, the ruling of 21 October 2026) governs the table's standing, whatever its header says.

## What it does not hold

- The six zones priced like a kept one (GENESE, CENTRL, NORTH, MHK VL, MILLWD, DUNWOD), real-time reserve prices, and reserve quantities (`docs/methods/reserve_quantities_nyiso_spp.md`).
- Any day before 2024-09-01 or after 2026-10-04.
