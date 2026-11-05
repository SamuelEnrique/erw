# Switzerland's electricity balance on each Wednesday, from 2003 (the SFOE's weekly statistics, ogd51)

Energy Research Warehouse (ERW), method note written in session 2815 (chain 143) for a table first written on 26 October 2026 (session 2808).

Tables: `bfe_ch_electricity_wednesdays`

## Publisher and address

The Swiss Federal Office of Energy (SFOE, BFE), "ENSTAT: Wochenstatistik Elektrizitätsbilanz - Erzeugung und Abgabe elektrischer Energie in der Schweiz". It is listed on opendata.swiss; its one CSV is `https://www.bfe-ogd.ch/ogd51/ogd51_wochenstatistik_elektrizitaetsbilanz.csv`.

Source id `bfe:ogd51`. Connector: `warehouse/connectors/bfe_weekly_balance.py` (session 2808), whose raw store is `warehouse/raw/bfe_weekly/`.
- www.bfe-ogd.ch has no robots file (HTTP 404, read 1612).
- The dataset's DCAT record (`ckan.opendata.swiss/dataset/<name>.xml`, read 1611) gives the file and the licence. ckan.opendata.swiss's robots file disallows `/api/` (read 1608).
- **Session 2808 reached that `/api/` once, by a redirect from opendata.swiss, before reading the robots file;** its report says so. The table does not depend on that answer.

The Federal Statistical Office was the session's first choice; it publishes no electricity dataset on opendata.swiss.

## Vintage and revision

Written by run `20261026T045710Z`, which read the file retrieved at 2026-10-26T04:52:40Z (last modified 18 September 2026). The SFOE rewrites the file as weeks are added.

## Shape and variables

Series, 11,154 rows, 1,222 days, 1 January 2003 to 24 June 2026:
- `entity` `bfe_weekly:ch`.
- `variable` the file's columns: `run_of_river`, `storage_hydro`, `nuclear`, `thermal`, `wind`, `solar`, `other`, `storage_pumps`, `imports`, `exports`, `national_consumption`. The file's `Erzeugung_netto` is written as `generation_less_storage_pumps` or `net_generation` (below).
- `unit` MWh (the file's GWh times 1,000), **the energy of that one day**: "based on Wednesday data", in the dataset's description.
- `ts_utc` the Wednesday's date at 00:00:00Z, a Swiss local day as the file gives it; `freq` P1D; `geo` CH.
- `x_column` the file's column; `x_definition`, for `Erzeugung_netto`, `less_pumps` or `before_pumps`.

**Before 2025, thermal, wind and solar are inside "other"; from 2025 they are columns of their own, and "other" is blank.** 3,510 blanks have no row.

**Figures:** on 10 June 2026, nuclear 46,358 MWh and national consumption 163,033 MWh. On 1 January 2025, `net_generation` was 132,778 MWh and the storage pumps 26,509 MWh.

## Reading the source

- **`Erzeugung_netto` changed meaning with the 2025 split** (session 2808 found it). On every one of the 1,144 days through 2024 it is the generation less the storage pumps; on every one of the 78 days from 2025 it is the generation before them, each within 0.05 GWh. **Each day is written under the measure it is:** `generation_less_storage_pumps` (through 2024) and `net_generation` (from 2025). Neither series mixes the two.
- National consumption equals the generation less the storage pumps plus imports less exports on all 1,222 days.
- Kept and counted: one date not a Wednesday (27 October 2009), and steps of 14 and 35 days (after 20 October 2004 and 28 November 2007).
- The run stops, asking nothing, while the SFOE is paused. It also stops, filling nothing, on:
  - a header not the file's;
  - a date not a date;
  - a value not a number;
  - a date given twice.

## License

opendata.swiss's `terms_by`, "Open use. Must provide the source.": the SFOE's verdict on record (read 594, session 2343). Source: Swiss Federal Office of Energy (SFOE). In the release package; held from the live set.

## Cross-check

Against `energy_charts_central_europe` (Energy-Charts' hourly public net generation for Switzerland), summed over each Wednesday in Swiss time, on the 182 Wednesdays both give (from 2023):

| Measure | Median difference (Energy-Charts less the SFOE) |
|---|---|
| Nuclear | 0.09 per cent (90th percentile of the absolute difference 0.74) |
| Run-of-river | 3.11 per cent |
| Load against national consumption | 7.39 per cent |

On 10 June 2026, nuclear was 46,358 MWh here and 46,350 at Energy-Charts. Energy-Charts' load and hydro follow its own definitions.
