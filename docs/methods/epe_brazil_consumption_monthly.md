# Brazil's monthly electricity consumption and consumers by state, class and sector (EPE, the Statistical Yearbook's raw data)

Energy Research Warehouse (ERW), method note written in session 2443 (chain 117) for a table first written on 24 October 2026 (session 2446).

Tables: `epe_brazil_consumption_monthly`

## Publisher and address

The Empresa de Pesquisa Energetica (EPE), "Dados do Anuario Estatistico de Energia Eletrica" (`https://www.epe.gov.br/pt/publicacoes-dados-abertos/dados-abertos/dados-do-anuario-estatistico-de-energia-eletrica`), its raw data workbook ("Dados Brutos"): `https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/dados-abertos/Documents/Dados%20brutos.xlsx`. One GET, no key. Source id `epe:anuario_dados_brutos`. Connector: `warehouse/connectors/epe_brazil_electricity.py` (session 2446). www.epe.gov.br's robots file closes its system paths, `.aspx` pages and restricted areas only, and names no AI agent (read 808).

## Vintage and revision

January 2011 to December 2025, written by run `20261024T115620Z` (the write under the lock, offline), which read the workbook saved at 2026-10-24T11:53:13Z (`retrieved_at`). `vintage` is its last-modified time, 2026-06-03T16:54:55Z: EPE replaces the file with each yearbook. Every run that is not `--offline` asks again and writes the table again (`write_snapshot`).

## Shape and variables

Series, 105,032 rows, 354 entities.

- **The source rows:** one sheet of 423,751 rows, one a month and a leaf of EPE's breakdown (class, system, state, sector at three levels, voltage at three levels, consumption band at two), with its consumers and its consumption.
- **The table's rows:** summed over system, the sector's lower levels (the low-income subclasses among them), voltage and band. `x_rows` counts the leaves summed.
- `entity`: `epe:br:<state>:<class>:<sector>`.
  - state: the two-letter code, lower case, 27;
  - class: `captive` (EPE's "Cativo", the distributors' customers) or `free` ("Livre", the open market's);
  - sector: EPE's first level as a slug: residencial, comercial, industrial, rural, poder_publico, servico_publico, iluminacao_publica, consumo_proprio.
- `variable`: `consumption` (MWh, as EPE gives it) or `consumers` (count, the month's consumers).
- `ts_utc` the month's first day; `freq` P1M; `geo` BR-<state>.
- `node`: the state, class and sector as EPE names them.

No value is 0. Five sums are negative, EPE's own figures kept as given, likely corrections of earlier months (EPE does not say):
- four of consumption, the least -4,093.6 MWh (the Federal District's captive industrial, January 2025);
- one consumer count, -71 (Amapá's captive public service, April 2024).

Consumption, TWh a year: 2011 433.0, 2015 465.5, 2020 475.7, 2024 561.6, 2025 566.7.

## Reading the source

- The run stops at once, asking nothing, while `epe_brazil_electricity` or www.epe.gov.br is paused.
- One request a run (timeout 300 seconds); `--offline` reads the saved workbook.
- A blank consumption or consumer count has no part in a sum, and a cell with neither has no row. Nothing is filled.
- The run stops, and no file is written, for any of these:
  - a workbook of more than one sheet;
  - a header not as read;
  - a date not of the form YYYYMM01;
  - a class or state not in the map;
  - a value that is not a number;
  - a state, class, sector and month given twice.

## License

Public. `license_verdicts.csv` records the Empresa de Pesquisa Energetica (EPE), read 809 (session 2446): "may be public", for public and for commercial use. The open data page's footer: "Todo o conteúdo deste site está publicado sob a licença Creative Commons Atribuição 4.0 Internacional (CC BY 4.0)". The header names EPE.

## Cross-checks (session 2446)

- Over `owid_ember_electricity_annual`'s demand for Brazil: 0.728 to 0.763. Ember's demand counts losses (high in Brazil) and self-supplied generation, which billed consumption does not.
- The free market's share of consumption: 0.26 in 2011, 0.448 in 2025.

## What it does not hold

- Voltage, consumption band, system and the low-income subclasses (summed);
- the yearbook's other chapters (generation, capacity, tariffs in BRL);
- months before 2011.
