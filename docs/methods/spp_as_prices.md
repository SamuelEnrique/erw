# SPP day-ahead operating reserve clearing prices by the hour: the SPP and SWPW rows (DA-MCP)

Energy Research Warehouse (ERW), method note written in session 2124 (chain 079) for a table first written on 4 October 2026 (session 85). The method shared by the day-ahead reserve price tables is `docs/methods/capacity_and_ancillary.md`, which the header names.

Tables: `spp_as_prices`

## Publisher and address

Southwest Power Pool (SPP), "Day-Ahead Market Clearing Prices (MCP)" for operating reserve, `https://portal.spp.org/pages/da-mcp`, one CSV an operating day, `DA-MCP-<YYYYMMDD>0100.csv`, through the portal's file browser: a year SPP has archived as one zip, `https://portal.spp.org/file-browser-api/download/da-mcp?path=/2024/2024.zip`, a later year one file a day, `https://portal.spp.org/file-browser-api/download/da-mcp?path=/YYYY/MM/DA-MCP-YYYYMMDD0100.csv`; the folder listing `https://portal.spp.org/file-browser-api/?fsName=da-mcp&path=/<year>&type=folder` says whether a year is archived. Source id `spp:DA-MCP` (in `sources.csv`, license public, first and last seen 2026-10-04). Raw files: `warehouse/raw/spp_as_prices/`.

Connector: `warehouse/connectors/spp_as_prices.py` (session 85), with the loop shared by the reserve price connectors, `warehouse/connectors/iso_as_common.py`. A day already in the raw files is not asked again; requests a second apart. The window starts 2024-09-01 (the approved start) and runs to the day before tomorrow, Central. Ceiling 500,000 rows. A run asks nothing while SPP is in `paused_sources.csv`.

No schedule runs it: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh` or `.github/workflows/` names it. `license_verdicts.csv` says why: "Session 308 (the owner's default of 18 October 2026 to ruling 1 of docs/state/morning_2026-10-14.md): spp_as_prices gets no scheduled step until this license is answered." Reader named in `license_tables.csv`: `battery_stack_review_monthly`.

## Vintage and revision

One run, `20261004T040948Z` (4 October 2026): "This run wrote 159432 rows: 159432 new, 0 replacing". `retrieved_at` runs from 2026-10-04T03:33:35Z to 2026-10-04T03:56:53Z; the run began at 04:09:48Z, so every time is that of a raw file already saved. The 2024 archive's 20,503 rows share 2026-10-04T03:37:40Z. The last header line: "Restored from the Redivis draft (energy_research_warehouse) by scripts/sync.py". `vintage` is empty. No run has refreshed the table since 4 October 2026.

## Shape and variables

Series, 159,432 rows. `unit` USD/MW-hour (US dollars per MW of capacity held for one hour), `freq` PT1H, `market` spp_dam, `geo` "US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY" in every row, `node` the reserve zone as the file names it, `source_url` the archive or the day's file (642 addresses: the 2024 zip and 641 daily files); `vintage` empty.

`entity` spp:SPP (every file, 18,312 hours a variable) and spp:SWPW (the files from 2026-04-01, 4,464 hours a variable). What SWPW stands for is not stated in the file and not guessed.

| `variable` | SPP's column | spp:SPP: highest (hour), mean | spp:SWPW: highest (hour), mean |
|---|---|---|---|
| as_price_dam_regup | RegUP | 192.1666 (2026-05-04T13:00:00Z), 14.0713 | 393.0001 (2026-06-28T13:00:00Z), 24.7477 |
| as_price_dam_regdn | RegDN | 178.0 (2026-04-02T02:00:00Z), 3.7937 | 447.0 (2026-10-02T06:00:00Z), 12.8380 |
| as_price_dam_spin | Spin | 126.7695 (2026-01-28T00:00:00Z), 5.5591 | 269.403 (2026-06-11T04:00:00Z), 19.7789 |
| as_price_dam_supp | Supp | 118.7724 (2026-01-28T00:00:00Z), 1.2380 | 268.4029 (2026-06-11T04:00:00Z), 11.0913 |
| as_price_dam_rampup | RampUP | 45.0 (2026-03-17T00:00:00Z), 2.3406 | 147.0 (2026-08-07T00:00:00Z), 12.9358 |
| as_price_dam_rampdn | RampDN | 0.0, 0.0 | 0.0, 0.0 |
| as_price_dam_uncup | UncUP | 67.0 (2025-03-31T14:00:00Z), 0.3367 | 216.6 (2026-07-27T00:00:00Z), 5.4608 |

The lowest value of every series is 0.0 except RegUP (SPP 0.3005, SWPW 0.0005) and SWPW's RegDN (0.0009).

## Placing values in time

- Each row of SPP's file has a `GMTIntervalEnd` (MM/DD/YYYY HH:MM:SS, UTC); `ts_utc` is that less one hour, the start of the hour.
- A file holding an hour outside its operating day (the Central day's hours in UTC) stops the run, as does a change of columns or a file with no row named SPP.

## What is and is not filled

- A (zone, product, operating day) is written only when every hour of the day is there exactly once (24, or 23 and 25 at the clock changes); an empty cell is not a price. The header: "0 are left out of this run."
- The numbered reserve zones are not held; in every file the connector counts the cells where a numbered zone's price is neither the SPP row's nor the SWPW row's. The header: "in the 763 daily files read by this run, a numbered zone carried a price of neither named row in 0 zone-product-hours".
- Nothing is filled.

## License

Header: "License: public, with citation. SPP's terms (https://www.spp.org/terms-conditions/): "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication". A commercial use needs SPP's written authorization." `license_verdicts.csv` records SPP, read 6: "may be public"; if commercial, "needs written permission". `docs/licenses.md` lists `spp_as_prices` under SPP: "may be public", flag public, "needs written permission" if the ERW sells anything, ERW verdict public.

## Checks (session 2124)

The figures in this note were computed from the rows of `warehouse/output/spp_as_prices.csv`, read past its 13 header lines.

- 159,432 rows, `ts_utc` from 2024-09-01T05:00:00Z to 2026-10-04T04:00:00Z: operating days 2024-09-01 to 2026-10-03 (Central), 763 days with none absent, as the header says. SPP: 763 days of 7 series; SWPW: 186 days (2026-04-01 to 2026-10-03) of 7 series; with two 23-hour and two 25-hour days for SPP, that is 128,184 + 31,248 = 159,432.
- No (entity, variable, ts_utc) is given twice. Every series holds every day of its span; the days of other than 24 hours are 2024-11-03 and 2025-11-02 (25) and 2025-03-09 and 2026-03-08 (23). The first SWPW hour is 2026-04-01T05:00:00Z, local midnight of 1 April.
- Consistency down the products: in every hour of both rows, RegUP is at least Spin and Spin at least Supp (0 exceptions in 18,312 SPP hours and 4,464 SWPW hours).
- RampDN is 0.0 in every hour of both rows.
- SWPW against SPP over their 4,464 shared hours: RampDN equal in all; UncUP equal in 2,928, RampUP in 1,139, Spin and Supp in 5 each, RegUP and RegDN in none. SWPW's price is at least SPP's in 3,422 hours for RegUP and 3,980 for Spin.

## Where the description and the data disagree

None found. The docstring, the header and the rows agree on the two rows and their start, the seven products, the hour's placing, the window and the count of numbered-zone cells left out.

## What it does not hold

- The numbered reserve zones (1 to 5, and 21 from April 2026, as the docstring says), real-time prices, and reserve quantities (`spp_as_quantities`, `docs/methods/reserve_quantities_nyiso_spp.md`).
- Any day before 2024-09-01 or after 2026-10-03.
