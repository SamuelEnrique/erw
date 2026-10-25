# Aland's electricity sales by distributor and sector, with its exports, 1980 to 2025 (ASUB's PxWeb table MI010)

Energy Research Warehouse (ERW), method note written in session 2667 (chain 133) for a table first written on 25 October 2026 (session 2670).

Tables: `asub_aland_electricity_sales_annual`

## Publisher and address

Statistics and Research Aland (ASUB), PxWeb table MI010, "Elforsaljningen efter ar, region, sald effekt och bransch": `https://pxweb.asub.ax/PXWeb/api/v1/sv/Statistik/MI/MI010.px`. It is read with one JSON-stat 2.0 query by POST (the GWh figures, every region, sector and year), no key. Source id `asub_ax:MI010`. Connector: `warehouse/connectors/asub_aland_sales.py` (session 2670), whose raw store is `warehouse/raw/asub_ax/` (`query_MI010.json`). pxweb.asub.ax has no robots file (HTTP 404, read 1371). The table stands beside `asub_aland_electricity_annual` (MI009, supply by origin).

## Vintage and revision

Written by run `20261025T104743Z` (the write under the lock, offline), which read the answer retrieved at 2026-10-25T10:46:02Z. `vintage` is empty. ASUB revises the table as each year is added.

## Shape and variables

Series, 603 rows, 18 entities. The years are 1980, 1985, 1990 and each year from 1994 to 2025. `entity` `asub:ax:<region>:<sector>`:
- **Regions:** `aland` (all of Aland), `mariehamns_energi` (Mariehamn, Mariehamns Energi Ab), `alands_elandelslag` (the rural municipalities, Alands elandelslag) and `export`.
- **Sectors:** `total`, `households`, `agriculture`, `industry`, `services` and `public_sector`.

`variable` sales (exports for the region export); `unit` MWh (the table's GWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` AX; `node` the region and the sector as ASUB names them.

Aland's sales were 87 GWh in 1980, 209 in 2000, 297 in 2021 and 276 in 2025. In 2025:
- by sector: households 121, services 56, the public sector 45, industry 38 and agriculture 16;
- by distributor: Mariehamns Energi 98 and Alands elandelslag 178.

Exports were 0 from 2018 to 2021, then 22 GWh in 2022 and 47 in 2025. Exports are given as a total only, and Mariehamn has no agriculture row.

## Reading the source

- The run stops at once, asking nothing, while `asub_ax` or pxweb.asub.ax is paused.
- One request a run (the POST); `--offline` reads the saved answer.
- A cell without a number has no row. The per cent rows are not taken.
- **Checks for whole-GWh rounding:** a distributor's sectors meet its total within 3 GWh (the table's largest gap is 2), and the two distributors meet Aland's total within 1.5 GWh.
- The run stops for:
  - dimensions not as above, or a statistic other than GWh;
  - a region or sector not in the map;
  - a year not of four digits;
  - a value array not the size of the dimensions;
  - a key given twice;
  - a check missed.

Nothing is filled.

## License

Public. ASUB's Anvandarvillkor (read 1326, session 2651): the site's material is under Creative Commons Erkannande 4.0 Internationell (CC BY), with ASUB named as the source and changes stated. Verdict on record: may be public. Cited as "Source: Statistics and Research Aland (ASUB)". In the release package; held from the live set.

## Cross-check

Against MI009's supply (`asub_aland_electricity_annual`), in GWh:
- **2000:** supply 242.1, sales 209; the rest is 33.1.
- **2025:** supply 350.6, sales 276 and exports 47; the rest is 27.6, or 7.9 per cent.

The rest is grid losses and use that neither table names.
