# Costa Rica's official generation by plant, a month (CENCE's web service EnergiaMensualOficial)

Energy Research Warehouse (ERW), method note written in session 2394 (chain 113) for a table first written on 24 October 2026 (session 2387).

Tables: `cence_costarica_generation_monthly`

## Publisher and address

The Centro Nacional de Control de Energia (CENCE), the system operator of the Instituto Costarricense de Electricidad (ICE, its DOCSE), through its public web services (`https://apps.grupoice.com/CenceWeb/paginas/ServiciosWeb.html`). The service EnergiaMensualOficial "devuelve el dato de generación mensual de energía en MWh de las plantas del SEN. Retorna solamente datos ya oficializados". One GET a year, no key: `https://apps.grupoice.com/CenceWeb/data/sen/json/EnergiaMensualOficial?anno=<year>`. Source id `cence:EnergiaMensualOficial`. Connector: `warehouse/connectors/cence_costarica_electricity.py` (session 2387). apps.grupoice.com has no robots file (HTTP 404, session 2387).

## Vintage and revision

January 2020 to August 2026, written by run `20261024T092055Z` (the write under the lock, offline), which read the seven years saved from 2026-10-24T09:18:40Z to 09:19:51Z (`retrieved_at`, a year each). `vintage` is blank: the answers carry no date of their own. Only official months are returned; CENCE's word is that the current and the previous month are still under review. A year saved by an earlier run is reused unless `--fresh`, since a past year is official and no longer changes; the current year is asked again by a `--fresh` run.

## Shape and variables

Series, 7,731 rows, 117 entities.

- `entity`: `cence:<the plant as a slug>`; `node` the plant as CENCE names it.
- `variable`:
  - `generation` (7,571 rows): a plant's generation in the month.
  - `interchange` (160 rows): CENCE's source "Intercambio", two entities (`cence:intercambio_norte`, `cence:intercambio_sur`), the exchanges with the regional market, signed as CENCE gives them (83 of them negative). It is not a plant's generation and is not summed into it.
- `x_source`: CENCE's source. Hidro (71 plants, 4,722 rows), Eólico (20, 1,420), Geotérmico (7, 560), Térmico (7, 460), Solar (7, 249), Bagazo (3, 160), Intercambio (2, 160).
- `x_company`: the operating company (ICE, Privadas, CNFL, BOT, Coopeguanacaste, Coopelesca, ESPH, JASEC, Conelectrica, Coopesantos, ICE Alquiler; Intercambio for the exchanges).
- `unit` MWh, as CENCE gives it. `ts_utc` the month's first day; `freq` P1M; `geo` CR.

463 values are 0 (a plant that did not run that month); no generation value is negative. Generation, TWh a year: 2020 11.53, 2021 12.54, 2022 12.59, 2023 11.94, 2024 12.57, 2025 13.35, January to August 2026 9.09.

## Reading the source

- The run stops at once, asking nothing, while `cence_electricity` or apps.grupoice.com is paused.
- One request a year from 2020 to the current year, 2 seconds apart, at most 8 a run (`CEILING`); `iso_prices.fetch_raw` tries a failed request again. `--offline` reads the saved years only and stops if one is missing.
- The run stops, and no file is written, for any of these:
  - an answer without `data`;
  - a record without its plant, month or year;
  - a record of a year other than the one asked;
  - a month outside 1 to 12;
  - an answer set with no value;
  - a plant and month given twice.
- A record without a number has no row. Nothing is filled.

## License

Internal. `license_verdicts.csv` records the Centro Nacional de Control de Energia (CENCE, ICE, Costa Rica), read 640 (session 2390): "needs written permission". Every answer of the web services ends "Declaración de Privacidad © 2025 ICE Todos los Derechos Reservados." and no reuse is granted. The table is held from the Redivis storage and the live set until ICE consents.

## Cross-checks (session 2387)

- Generation by source, January 2020 to August 2026: hydro 60.1 TWh, geothermal 10.3, wind 10.0, thermal 2.6, bagasse 0.4, solar 0.1; interchange -2.0.
- Generation over `owid_ember_electricity_annual`'s demand for Costa Rica: 0.989 to 1.120, 2020 to 2025; with interchange added, 0.982 to 1.140.

## What it does not hold

- Months before 2020 (the service was asked from 2020 only); the months still under review; the daily or hourly generation (CENCE's chart service answers one day a request); prices, capacity and demand.
