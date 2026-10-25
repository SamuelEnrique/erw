# Peru's crude oil, natural gas liquids and natural gas production a month (BCRPData, INEI's and MINEM's figures)

Energy Research Warehouse (ERW), method note written in session 2569 (chain 126) for a table first written on 25 October 2026 (session 2567).

Tables: `bcrp_peru_hydrocarbons_monthly`

## Publisher and address

The Banco Central de Reserva del Peru (BCRP), BCRPData's monthly series "Produccion minera e hidrocarburos (miles de unidades recuperables)", its three hydrocarbons series: crude oil (PN01882AM) and natural gas liquids (PN01883AM) in thousand barrels, natural gas (PN01884AM) in million cubic feet; their sources INEI and the Ministerio de Energia y Minas (MINEM). One request to BCRPData's API:

    https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01882AM-PN01883AM-PN01884AM/json/2000-1/2026-8/ing

The list of the series: `https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/produccion-minera-e-hidrocarburos-miles-de-unidades-recuperables` (read 1084). No key. Source id `bcrp_pe:bcrpdata_produccion_hidrocarburos`. Connector: `warehouse/connectors/bcrp_peru_hydrocarbons.py` (session 2567). estadisticas.bcrp.gob.pe has no robots file (HTTP 404, read 1079).

## Vintage and revision

January 2000 to August 2026, written by run `20261025T010114Z` (the write under the lock, offline), which read the response saved at 2026-10-25T00:59:38Z. BCRP's list gave the series' last update as 23-10-2026. `vintage` is empty: the API sends no last-modified time. A later run asks a later last month with `--to`.

## Shape and variables

Series, 960 rows (3 series times 320 months), 3 entities; `variable` `production`; `ts_utc` the month's first day; `freq` P1M; `geo` PE; `node` BCRP's series name; `x_series_code` BCRP's code.

| `entity` | `unit` | 2025 |
|---|---|---|
| `bcrp_pe:crude_oil` | `kbbl` | 16,116 thousand barrels |
| `bcrp_pe:natural_gas_liquids` | `kbbl` | 26,764 thousand barrels |
| `bcrp_pe:natural_gas` | `MMcf` | 493,829 million cubic feet (493.8 bcf) |

The figures as BCRP gives them; a reader converts barrels a month to barrels a day by the month's days.

## Reading the source

- The run stops at once, asking nothing, while `bcrp_pe` or estadisticas.bcrp.gob.pe is paused.
- One request a run; `--offline` reads the saved response.
- **The response** must name the three series asked, in order, each ending in the label and unit the connector's map gives it ("Hidrocarburos - Petroleo (miles de barriles)", with its accents, and the others), and hold every month from January 2000 to the last month asked.
- **A cell** "n.d." is not written; any other cell that is not a figure stops the run.

Nothing is filled. Not taken: the eight mining series of the same list.

## License

Public. BCRPData's Condiciones de Uso (read 1082) allow reproduction in whole or in part without express permission, the source cited (BCRP's verdict: may be public). Cited as BCRP's, with INEI and MINEM as the original sources. In the release package; held from the live set.

## Cross-check

EIA's Peru (`eia_world_oil_gas_annual`): crude oil with lease condensate, 40.631 thousand barrels a day in 2024, 14,871 thousand barrels over the year, BCRP's 14,871; 2019, 19,339 against 19,339. Natural gas: 2019, EIA 474.1 bcf against BCRP's 474.2; 2024, EIA 478.9 against BCRP's 510.7.
