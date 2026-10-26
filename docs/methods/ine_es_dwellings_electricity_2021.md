# Spain's dwellings by their electricity consumption, every municipality, 2021 census (INE)

Energy Research Warehouse (ERW), method note written in session 2773 (chain 140) for a table first written on 25 October 2026 (session 2765).

Tables: `ine_es_dwellings_electricity_2021`

## Publisher and address

Spain's National Statistics Institute (Instituto Nacional de Estadística, INE), Censo de Población y Viviendas 2021, the table "Viviendas según su intensidad de uso" (JAXI tpx 59531, `https://www.ine.es/jaxi/Tabla.htm?tpx=59531`), "dwellings by intensity of use from electricity consumption". The table reads its CSV export, `https://www.ine.es/jaxi/files/tpx/es/csv_bdsc/59531.csv` (semicolon-separated, the thousands marked with points). No key. Source id `ine_es:jaxi_tpx_59531`. Connector: `warehouse/connectors/ine_es_dwellings_electricity.py` (session 2765), whose raw store is `warehouse/raw/ine_es/`. www.ine.es's robots file closes cgi-bin, search, test and admin paths and names no Claude agent (read 1519).

## Vintage and revision

Written by run `20261025T235036Z` (the write under the lock, offline), which read the file retrieved at 2026-10-25T23:46:30Z (last modified 2 March 2026). The table page says INE updated the data on 22 November 2024. A census table: the next census will replace it, not revise it each year.

## Shape and variables

Series, 58,626 rows, 3,257 areas, 18 variables, one period:
- `entity`: `ine_viv:es` (Spain), `ine_viv:ccaa_<code>` (19 autonomous communities and cities), `ine_viv:prov_<code>` (52 provinces) or `ine_viv:mun_<code>` (3,185 municipalities), INE's codes; `x_level` names the level.
- `variable`, counts of dwellings (`unit` count): `dwellings_total`, `dwellings_empty`, `dwellings_low_consumption`, `dwellings_occasional_use` with its two bands (251 to 500 and 501 to 750 kWh), and eleven bands from 751 kWh to over 10,000 kWh; and `median_annual_consumption` (`unit` MWh per dwelling: INE's kWh divided by 1,000).
- `ts_utc` 2021-01-01T00:00:00Z, the census; `freq` P1Y; `geo` ES; `node` the area's code and name and INE's item.

**Figures:** Spain had 26,623,708 dwellings, 3,828,307 of them empty, 941,637 of low consumption and 2,517,628 of occasional use. The median annual consumption was 2,196 kWh.

## Reading the source

- The run stops at once, asking nothing, while `ine_es` or www.ine.es is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- An area is read from its "<code> <name>" cell at the innermost level filled; each municipality's province and each province's community are read from the same row.
- **Checks,** exact, for every area, all passing:
  - the total equals the empty, low-consumption and occasional-use dwellings plus the eleven bands;
  - occasional use equals its two bands;
  - each count of the nation, a community and a province equals the sum of its communities, provinces or municipalities.
- A header not INE's, an item not in the eighteen, an area or item given twice, or a value not a number stops the run. Nothing is filled.

## License

Public. INE's legal notice (read 1529): CC BY 4.0, commercial use included, cited as "Elaboración propia con datos extraídos del sitio web del INE: www.ine.es" with the date of the data's last update, as the header does. The verdict, may be public, was given in session 2765. In the release package; held from the live set.

## Cross-check

Against `eurostat_electricity_consumption_annual` (Spain's households, 2021: 73,149 GWh). The census bands give at least 49,731 GWh (each band at its lower edge, the 391,748 dwellings above 10,000 kWh at 10,001). The bands up to 10,000 kWh give at most 64,368 GWh at their upper edges, to which the dwellings above 10,000 kWh add what they use. To reach Eurostat's figure, those 391,748 dwellings would have to average about 22.4 MWh. The two measure different things: the census classes metered dwellings, and the energy balance counts the household sector. The table is for how dwellings are used, not for national consumption.
