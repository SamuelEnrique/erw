# Aland's electricity supply by origin a year, 1994 to 2025 (ASUB's PxWeb table MI009)

Energy Research Warehouse (ERW), method note written in session 2653 (chain 132) for a table first written on 25 October 2026 (session 2651).

Tables: `asub_aland_electricity_annual`

## Publisher and address

Statistics and Research Aland (Alands statistik- och utredningsbyra, ASUB), PxWeb table MI009, "Anskaffning och produktion av el efter ar, statistik och ursprung": `https://pxweb.asub.ax/PXWeb/api/v1/sv/Statistik/MI/MI009.px`, one JSON-stat 2.0 query by POST (the GWh figures, every origin and every year), no key. Source id `asub_ax:MI009`. Connector: `warehouse/connectors/asub_aland_electricity.py` (session 2651), whose raw store is `warehouse/raw/asub_ax/` (`query_MI009.json`, the answer with its time of retrieval). pxweb.asub.ax has no robots file (HTTP 404, read 1321); www.asub.ax's closes only Drupal's system paths (read 1317).

## Vintage and revision

Written by run `20261025T085607Z` (the write under the lock, offline), which read the answer retrieved at 2026-10-25T08:54:42Z. `vintage` is empty: the answer's "updated" field is the table's creation in 2008, not its last update (29 January 2026, in the API's table list, read 1324). ASUB revises the table as each year is added.

## Shape and variables

Series, 190 rows, 7 entities, each year from 1994 to 2025. `entity` `asub:ax:<origin>`:
- `import_sweden` and `import_finland` (`variable` `imports`);
- `oil`, `wind`, `bioenergy` (from 2008) and `solar` (from 2014) (`generation`);
- `total` (`supply`).

`unit` MWh (the table's GWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` AX; `node` the origin as ASUB names it (Swedish).

Supply was 209.4 GWh in 1994 and 350.6 GWh in 2025. In 2025: wind 202.4, imports from Sweden 127.4, solar 15.8, imports from Finland 4.0, bioenergy 0.9, oil 0. Wind was 14.6 GWh in 2000.

ASUB's note: the table shows how electricity is physically produced on Aland, not its trade (all of it is traded on Nord Pool); solar is estimated from the installed panels' capacity. Exports are not in the table.

## Reading the source

- The run stops at once, asking nothing, while `asub_ax` or pxweb.asub.ax is paused.
- One request a run (the POST); `--offline` reads the saved answer.
- **The answer** must have the dimensions year (`år`), statistic and origin, the statistic GWh alone, every origin in the map, and a value array the size of its dimensions. A cell without a number has no row.
- **Check:** each year's six origins add to its total within 0.5 GWh.
- The run stops, and no file is written, for: a dimension not as above, an origin not in the map, a year not of four digits, a key given twice, a check missed.

Nothing is filled. Not taken: the per cent rows; MI010 (sales by region and sector).

## License

Public. ASUB's Anvandarvillkor (read 1326): "For material pa ASUB:s webbplats anvands licensen Creative Commons Erkannande 4.0 Internationell (CC BY)" (with its accents in the record), covering texts, tables and diagrams, with ASUB named as the source and changes stated; third parties' material, photographs and the logo are excepted. Verdict: may be public. Cited as "Source: Statistics and Research Aland (ASUB)". In the release package; held from the live set.

## Cross-check

EIA's world table holds no Aland. ASUB's pocket yearbook (searched, not fetched) gives 2024 as 351 GWh in all, 127 from Sweden, 8 from Finland and about 204 of wind; MI009 gives 351.5, 127.0, 7.5 and 203.5. ASUB's text gives 2023's wind as 172.3 GWh, as MI009 does.
