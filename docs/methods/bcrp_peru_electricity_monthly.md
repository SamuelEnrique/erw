# Peru's electricity production a month by department (BCRPData, MINEM's figures)

Energy Research Warehouse (ERW), method note written in session 2569 (chain 126) for a table first written on 25 October 2026 (session 2566).

Tables: `bcrp_peru_electricity_monthly`

## Publisher and address

The Banco Central de Reserva del Peru (BCRP), BCRPData's monthly series "Produccion de electricidad por departamento" (RD13043DM to RD13067DM: the 24 departments and the total, in GWh), whose source is the Ministerio de Energia y Minas (MINEM). Read through BCRPData's API, ten series a request at most, so three requests:

    https://estadisticas.bcrp.gob.pe/estadisticas/series/api/<codes>/json/2005-1/2026-6/ing

The list of the series: `https://estadisticas.bcrp.gob.pe/estadisticas/series/mensuales/produccion-de-electricidad-por-departamento`. No key. Source id `bcrp_pe:bcrpdata_produccion_electricidad_departamento`. Connector: `warehouse/connectors/bcrp_peru_electricity.py` (session 2566). estadisticas.bcrp.gob.pe has no robots file (HTTP 404, read 1079).

## Vintage and revision

January 2005 to June 2026, written by run `20261025T005601Z` (the write under the lock, offline), which read the responses saved at 2026-10-25T00:53:45Z to 00:53:57Z. BCRP's list gave the series' last update as 16-09-2026. `vintage` is empty: the API sends no last-modified time. A later run asks a later last month with `--to`.

## Shape and variables

Series, 6,450 rows (25 series times 258 months), 25 entities. `entity` `bcrp_pe:<department>` (`amazonas`, `ancash`, `apurimac`, ..., `ucayali`: the name in lower case without accents, each run of other characters an underscore) and `bcrp_pe:total`; `variable` `production`; `unit` MWh (BCRP's GWh times 1,000); `ts_utc` the month's first day; `freq` P1M; `geo` PE; `node` the department as BCRP spells it; `x_series_code` BCRP's code.

The total for 2025 is 65.109 TWh; Lima produced 2,888 GWh of June 2026's 5,634. The total holds the departments, so a sum over entities takes one or the other.

## Reading the source

- The run stops at once, asking nothing, while `bcrp_pe` or estadisticas.bcrp.gob.pe is paused.
- Three requests a run, two seconds apart; `--offline` reads the saved responses.
- **Each response** must name the ten (or five) series asked, in order, each "Produccion de electricidad por departamento - <name> (gwh)", the last the Total, and hold every month from January 2005 to the last month asked.
- **A cell** "n.d." (no data) is not written; any other cell that is not a figure stops the run (none was n.d. on 25 October 2026).
- **The departments and the total:** BCRP's departments add to its total within 10 GWh a month (0.22% at most, April 2021). The run stops beyond 0.5%; both are kept as given.

Nothing is filled. Not taken: the series' annual changes (RD13068DM to RD13092DM).

## License

Public. BCRPData's Condiciones de Uso (read 1082): "Puede reproducirse total o parcialmente, sin autorizacion expresa, siempre y cuando se cite la fuente." (as printed, with its accent). The same page says the responsibility for statistics from outside sources rests with the entity that provides them. Verdict: may be public. Cited as BCRP's, with MINEM as the original source. In the release package; held from the live set.

## Cross-check

EIA's Peru (`eia_world_electricity_annual`): 2019, 56.864 TWh against BCRP's 56.967; 2023, 60.863 against 61.962; 2024, 59.303 (EIA's estimate) against 63.565.
