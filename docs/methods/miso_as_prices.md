# MISO's day-ahead reserve prices for the system, regulating, spinning and supplemental, one row a product and hour, operating days 1 September 2024 to 3 October 2026

Energy Research Warehouse (ERW), method note written in session 2298 (chain 105) for a table first written on 4 October 2026 (session 85, `archive/sessions/SESSION_85_REPORT.md`, day-ahead reserve prices of four more grids; commit `1ba59d31`). The section "Four more grids' day-ahead reserve prices" of `docs/methods/capacity_and_ancillary.md` is the table's first method (its sources, the regions kept, the never-fill rule and MISO's terms quoted); the pause is `docs/methods/miso_pause.md`; `docs/methods/battery_stack.md` says why no battery result is built on it. They are cited here, not repeated. MISO's day-ahead energy prices at its hubs are in `iso_dam_hub_prices` (`docs/methods/iso_dam_hub_prices.md`).

Tables: `miso_as_prices`

## Publisher and address

Midcontinent Independent System Operator (MISO), market report "ASM Day-Ahead Market ExPost MCPs" (`asm_expost_damcp`), one csv an operating day, `https://docs.misoenergy.org/marketreports/<YYYYMMDD>_asm_expost_damcp.csv`, page `https://www.misoenergy.org/markets-and-operations/real-time--market-data/market-reports/`. Source id `miso:asm_expost_damcp` (its `sources.csv` row carries "[PAUSED 2026-10-04: MISO's terms forbid automated access ...]"). Raw files on this machine: `warehouse/raw/miso_as_prices/20261004T033317Z/` (9 files, operating days 25 September to 3 October 2026) and `20261004T035700Z/` (754 files, 1 September 2024 to 24 September 2026), 514,458,808 bytes in all, each with its `Last-Modified` in the manifest; a third folder, `20261004T041952Z/`, holds only the data lock's check.

Connector: `warehouse/connectors/miso_as_prices.py` (session 85) over the loop `warehouse/connectors/iso_as_common.py`, ceiling 500,000 rows. It keeps the file's three "MISO Wide" generation rows, `GENREGMCP`, `GENSPINMCP` and `GENSUPPMCP`, as `as_price_dam_reg`, `as_price_dam_spin` and `as_price_dam_supp`; it leaves out the demand-side and stored-energy types (`DEMREGMCP`, `DEMSPINMCP`, `DEMSUPPMCP`, `SERREGMCP`) and the rows that repeat a price for each resource with its reserve zone, counting the (zone, product, hour) cells in which a resource row differs from MISO Wide. It stops if the file no longer says "All Hours-Ending are Eastern Standard Time (EST)". "Never fill. A (product, day) is written only when all 24 hours hold a number."

**MISO is paused** since 4 October 2026 (`warehouse/metadata/paused_sources.csv`, "Samuel, 4 October 2026 (the closing ruling of session 89)", pending "a review of MISO's terms by a person"; `docs/methods/miso_pause.md`). The table was last written on 4 October 2026 by run `20261004T041952Z` (header line 6; `coverage.csv` `last_run` 2026-10-04T04:19:52Z), archived at 04:25:02Z and uploaded to the internal Redivis draft at 04:25:55Z, about an hour before the pause was committed (`ebcfe63f`, 05:40Z). Since then nothing asks for it: the connector was never scheduled ("Not in the daily run", `capacity_and_ancillary.md`; no line of `warehouse/run_daily.sh`, `run_data_machine.sh`, `run_data_machine_tables.sh` or `run_monthly.sh`, no workflow and no step of `warehouse/scheduled.py` names it, which `tests/test_session89_miso_pause.py` asserts: "the reserve connector is in no run"), and run by hand it asks `iso_prices.paused("miso")` before anything else, prints the pause line and returns 0. That check comes before the `--offline` branch, so even a rebuild from the raw files on this machine is refused while MISO's row stands.

`run_status.csv`: no row (a run by hand writes `runs/status/miso_as_prices.json`, not on this machine, which `run_status.py record` appends only when a scheduled run calls it; disagreement 2). `archive_manifest.csv`: 54,936 rows, run `20261004T042502Z-local`. `redivis_uploads.csv`: `energy_research_warehouse_internal`, 54,936 rows. Live set: no rule of `warehouse/supabase/live_set.yaml` names it ("The two internal tables are in the internal Redivis draft and are in no live-set rule", `capacity_and_ancillary.md`); it is not in Supabase. Readers: none. `warehouse/derived/battery_stack.py` names it only to say the battery model is not built on it ("Their reserve prices (isone_as_prices, miso_as_prices) are internal").

## Vintage and revision

One write, from 763 files: 7,992 rows (the 9 newest days) retrieved from 03:33:17Z to 03:33:32Z by run `20261004T033317Z`, and 46,944 rows (754 days) from 03:57:01Z to 04:19:03Z by run `20261004T035700Z`, one `retrieved_at` a file (763 values). The run named in the header, `20261004T041952Z`, read them all from the raw files (disagreement 1). Header line 12: "This run wrote 54936 rows: 54936 new ... 0 rows are kept from earlier runs." No row has been written since.

`vintage` is blank in every row, though each file's `Last-Modified` is in the raw manifest: 763 values, from Sat, 31 Aug 2024 18:04:41 GMT (the file for 1 September 2024) to Fri, 02 Oct 2026 18:04:44 GMT (3 October 2026), each before its operating day began, except one: **the file for 21 July 2026 was last modified on 18 August 2026 at 12:34:39 GMT**, four weeks after its day. The table holds that later copy and cannot say so (disagreement 3).

The copy on this machine was restored from the Redivis draft by `scripts/sync.py` (header line 13); its data hash, `ce833c76...`, equals the archive manifest's, rows in the same order.

## Shape and variables

Series, 54,936 rows, 13 columns (`entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage`), 13 header lines. One entity, `miso:MISO Wide` (`node` MISO Wide); unit USD/MW-hour, `freq` PT1H, `market` miso_dam, `geo` the 15 states "US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI" in every row; `vintage` blank. `source_url` is the day's file in every row (763 values).

| Variable | MISO's type | Rows | Mean | Median | Lowest (hour, UTC) | Highest (hour, UTC) | 99th percentile |
|---|---|---|---|---|---|---|---|
| `as_price_dam_reg` | GENREGMCP, regulating reserve | 18,312 | 17.54 | 15.59 | 4.02 (2024-09-04T08:00:00Z) | 273.30 (2026-09-03T23:00:00Z) | 50.00 |
| `as_price_dam_spin` | GENSPINMCP, spinning reserve | 18,312 | 3.64 | 2.50 | 0.16 (2025-07-13T11:00:00Z) | 173.30 (2026-09-03T23:00:00Z) | 21.40 |
| `as_price_dam_supp` | GENSUPPMCP, supplemental reserve | 18,312 | 0.79 | 0.20 | 0.16 (2025-04-29T03:00:00Z) | 173.30 (2026-09-03T23:00:00Z) | 13.46 |

USD per MW of capacity held for one hour, never per MWh (`capacity_and_ancillary.md`, "USD/MW-hour is not USD/MWh").

- **No price is zero or negative.**
- **The order holds in every hour:** regulating above spinning in all 18,312 hours (never equal), spinning at or above supplemental in all, equal in 1,354.
- **The highest hours** are 2026-09-03T23:00:00Z (273.30, 173.30, 173.30) and 2026-09-04T23:00:00Z (267.51, 167.51, 167.51), then 2026-01-26T13:00:00Z (246.55, 98.07, 98.07) and 12:00Z (222.28, 92.71, 92.71); in each, spinning and supplemental are equal. Spinning's 99.00 on 2025-07-28T23:00:00Z is the highest hour outside those days.
- **Monthly means of regulating** run from 13.03 (September 2024) to 27.88 (January 2026); of spinning, from 2.29 (June 2026) to 5.12 (July 2025); of supplemental, from 0.21 (March 2025) to 3.13 (July 2025).
- **What is left out loses nothing in this window.** In all 763 files, `DEMREGMCP` and `SERREGMCP` equal `GENREGMCP`, `DEMSPINMCP` equals `GENSPINMCP` and `DEMSUPPMCP` equals `GENSUPPMCP` in every one of the 18,312 hours, and no reserve zone's resource rows differ from MISO Wide in any (zone, product, hour), as header line 4 says ("in 0 zone-product-hours"). The table's three prices are therefore also the demand-side and stored-energy prices of every hour held (disagreement 5).
- Values are MISO's digits: 37,278 with two decimals, 17,658 with one.
- Rows a year, by operating day: 8,784 (2024, from 1 September), 26,280 (2025), 19,872 (2026, to 3 October).

## Placing values in time, and what is filled

`ts_utc` is the start of the hour in UTC. MISO's hours are hour-ending 1 to 24 in Eastern Standard Time all year, so every operating day is 24 hours and begins at 05:00Z, in winter and summer alike (`TZ = "Etc/GMT+5"`). 763 operating days, 2024-09-01 to 2026-10-03, none missing; every (product, day) has its 24 hours; the first hour is 2024-09-01T05:00:00Z and the last 2026-10-04T04:00:00Z. Every row's `source_url` names the file of its own Eastern Standard Time day. Nothing is filled, and nothing needed to be: header line 5, "0 are left out of this run". The window was set by session 85's run, `--start` 2024-09-01 (`iso_as_common.START`, "the approved window") to the last day published; it ends there because MISO is paused.

## License

Header line 10: "License: internal. MISO's terms (https://www.misoenergy.org/meet-miso/legal-and-privacy/): 'You are not permitted to modify, publish, transmit, participate in the transfer or sale of, reproduce, create derivative works of, distribute, publicly perform, publicly display or in any way exploit any of the materials or content'." `coverage.csv` and `sources.csv`: internal. `license_verdicts.csv`, MISO (read 7): "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App.", "needs written permission", and the same if the ERW sells anything; note: "NOT ASKED: MISO is paused since 4 October 2026 ... The sentence is the one that file holds, read on 4 October 2026". `license_reads.csv` #7: "not asked: paused (www.misoenergy.org is in warehouse/metadata/paused_sources.csv)". `docs/licenses.md`, the table's row: MISO, "needs written permission", decided by MISO, flag internal, "agrees", ERW verdict internal. No row in `license_status.csv`. The package: "The ERW holds it for its own use only (needs written permission); it is never redistributed." `docs/reviews/licenses/miso-permission-letter.md` names the table among MISO's own tables a permission would cover.

## Checks (session 2298)

The figures in this note were computed from the rows of `warehouse/output/miso_as_prices.csv` in the main checkout, read past its 13 header lines (counted, never parsed as comments), by `runs/c105/s2298/check_miso_as_prices.py` and `check_miso_as_prices_2.py` (outputs beside them, `.out`). No request was made.

- 54,936 rows and 2024-09-01T05:00:00Z to 2026-10-04T04:00:00Z, as header line 12 states; no (entity, variable, ts_utc) twice; no blank value; rows in (entity, variable, ts_utc) order; one unit, one entity, three variables of 18,312 rows each (763 days of 24 hours).
- **Against MISO's files** (the 763 raw files the rows cite, matched by `source_url` and `retrieved_at`): every row of the table is in them with the same value, and every MISO Wide generation cell of them is in the table. The zones counted again: 0 cells differ, for each of the three products.
- **Against MISO's own day-ahead energy prices** (`iso_dam_hub_prices`, `market` miso_dam, eight hubs; their own requests, a different MISO report): 936 hours in both, 2026-08-26T05:00:00Z to 2026-10-04T04:00:00Z, where both end. The reserve prices rise with the energy price: correlation with the eight hubs' mean 0.815 for regulating, 0.584 for spinning, 0.581 for supplemental; no reserve price exceeds the hubs' mean in any hour. The highest reserve hour, 2026-09-03T23:00:00Z, is an energy price peak too (hubs' mean 448.07, MINN.HUB 535.17), as is the next, 2026-09-04T23:00:00Z (hubs' mean 459.45, the hour of MINN.HUB's 719.54).
- **Against the ERW's other grids' day-ahead reserve prices**, the same 18,312 hours (different markets and products; a check of scale, not of equality):

| MISO | Mean, median | Other grid | Mean, median | Correlation |
|---|---|---|---|---|
| regulating | 17.54, 15.59 | SPP regulation up (`spp:SPP`) | 14.07, 11.99 | 0.401 |
| regulating | 17.54, 15.59 | NYISO regulation (`nyiso:NYCA`) | 15.77, 11.00 | 0.460 |
| regulating | 17.54, 15.59 | ERCOT regulation up (`ercot:REGUP`) | 2.68, 1.12 | 0.294 |
| spinning | 3.64, 2.50 | SPP spinning (`spp:SPP`) | 5.56, 2.97 | 0.406 |
| spinning | 3.64, 2.50 | ERCOT responsive reserve (`ercot:RRS`) | 2.35, 0.69 | 0.227 |
| spinning | 3.64, 2.50 | NYISO 10-minute spinning, West (`nyiso:WEST`) | 6.74, 4.50 | 0.160 |
| supplemental | 0.79, 0.20 | SPP supplemental (`spp:SPP`) | 1.24, 0.67 | 0.250 |
| supplemental | 0.79, 0.20 | ERCOT non-spinning (`ercot:NSPIN`) | 3.34, 1.00 | 0.138 |
| supplemental | 0.79, 0.20 | NYISO 30-minute operating, West (`nyiso:WEST`) | 6.58, 4.50 | 0.206 |

  MISO's regulating price is near SPP's and NYISO's and well above ERCOT's; the correlations, 0.14 to 0.46, are those of separate markets, and no hour is equal often enough to suggest a copied series (at most 248 equal hours, MISO's and SPP's supplemental).

## Where the description and the data disagree

1. **"Retrieved: 20261004T041952Z."** Header line 6 names the run that wrote the file, and line 4 speaks of "the 763 daily files read by this run"; that run requested none of them (its raw folder holds only the lock check). The files were fetched from 03:33:17Z to 04:19:03Z by runs `20261004T033317Z` and `20261004T035700Z`, as `retrieved_at` says.
2. **No record of the runs.** `CLAUDE.md` describes `run_status.csv` as "every run and every gap"; it holds no row of `miso_as_prices`: a run by hand writes only `runs/status/miso_as_prices.json`.
3. **`vintage` blank though the publish time is known.** `docs/datastandard.md` (rule 5): "v0 tables keep the value the connector retrieved and record the publication time in `vintage`". Every file's `Last-Modified` is in the raw manifest, and MISO's hub prices carry theirs in `iso_dam_hub_prices`; here `iso_as_common.run` writes `"vintage": ""`. One file, 21 July 2026's, was modified on 18 August 2026, and the table cannot show it.
4. **"2026-10-04" as the last day.** `docs/accelerator/evidence_pack.md` gives the table's end as "2026-10-04" with no operating day beside it, where the same table's MISO hub rows give "2026-10-04, 2026-10-03 (file)"; the last operating day is 2026-10-03 (its last hour starts 2026-10-04T04:00:00Z).
5. **"What that loses."** The docstring and `capacity_and_ancillary.md` ("Which regions are kept, and what that loses") list the demand-side and stored-energy types as left out; in all 18,312 hours they equal the generation prices kept, so nothing is lost in this window. The docstring's "the three 'MISO Wide' prices a generator or a battery is paid" holds for a battery only because `SERREGMCP` equals `GENREGMCP` in every hour.
6. **"493 MB."** `SESSION_85_REPORT.md` gives MISO's 763 files as 493 MB; the files the rows cite are 514,458,808 bytes (514.5 MB, 490.6 MiB).

Not acted on: this note changes no file but itself.

## The session report against the table

`SESSION_85_REPORT.md`: "`miso_as_prices` | 54,936 | 763 | 2024-09-01 | The system ('MISO Wide'): regulating, spinning and supplemental reserve | internal": holds. "No day and no hour is missing in any of them": holds. "763 files: a zone's price differed from the system's in **0** hours (checked a second way on 60 files chosen at random)": holds, recounted over all 763. "MISO's file keeps Eastern Standard Time all year and says so": holds, every day begins at 05:00Z. "763 daily files from MISO (493 MB)": the count holds, the size does not (disagreement 6). The report left with Samuel whether MISO's daily pulls should continue; the ruling of 4 October 2026 paused them, and this table with them.

## What it does not hold

- Reserve zones' own prices (which equal the system's in every hour of the 763 files) and the demand-side and stored-energy types (equal too); short-term reserve and the ramp products ("Short-term reserve and the ramp products are not in this report", the docstring); real-time reserve prices; cleared or awarded MW.
- Operating days before 1 September 2024 or after 3 October 2026 (paused); MISO's earlier copies of a revised file (`vintage` blank).
- Energy prices (`iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_hub_prices_history`, all ending on 3 October 2026 for MISO); MISO's capacity prices (`iso_all_capacity_prices`, `miso_pra`).
