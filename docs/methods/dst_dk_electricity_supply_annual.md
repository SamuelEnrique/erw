# Denmark's electricity supply, production and imports, and its wind, hydro and solar power, 1966 to 2025 (Statistics Denmark's ENE1HT)

Energy Research Warehouse (ERW), method note written in session 2759 (chain 139) for a table first written on 25 October 2026 (session 2756).

Tables: `dst_dk_electricity_supply_annual`

## Publisher and address

Statistics Denmark (Danmarks Statistik), StatBank table ENE1HT, "Energy Account in specific units (detailed table)", supply (`https://www.statbank.dk/ENE1HT`). The table reads one extract from StatBank's open API, in semicolon-separated CSV with each value's code and text:

`https://api.statbank.dk/v1/data/ENE1HT/CSV?lang=en&delimiter=Semicolon&valuePresentation=CodeAndValue&TILGANG=ETIL,EIMPORT,ETILVE,EPRODI&ENERGI1=EMEL,EMVIND,EMVAND,EMSOLK&Tid=*`

No key. Source id `dst:statbank_ene1ht`. Connector: `warehouse/connectors/dst_energy_account.py` (session 2756), whose raw store is `warehouse/raw/dst_statbank/`. www.dst.dk's and dst.dk's robots files are the same file: they close Sitecore, upload and Extranet paths, give GPTBot a crawl delay of 10, and name no Claude agent (reads 1498 and 1499). api.statbank.dk has no robots file (read 1500). The table's information (read 1503) gives it as updated 18 June 2026.

## Vintage and revision

Written by run `20261025T221830Z` (the write under the lock, offline), which read the extract retrieved at 2026-10-25T22:15:24Z. Statistics Denmark revises the energy account each June, with the year just ended added.

## Shape and variables

Series, 360 rows, one entity `dst_ene:dk`, six variables, each year from 1966 to 2025, in MWh (Statistics Denmark's GWh times 1,000):
- `electricity_total_supply` (ETIL, EMEL), `electricity_imports` (EIMPORT, EMEL) and `electricity_production` (EPRODI, EMEL, the electricity produced in Denmark from every fuel and from wind, water and sun);
- `wind_power_supply`, `hydro_power_supply` and `solar_power_supply` (ETILVE, the supply of renewable energy, of EMVIND, EMVAND and EMSOLK).

`ts_utc` the year's first day; `freq` P1Y; `geo` DK; `node` the StatBank codes and texts as given.

**Figures:**
- Production: 8,956 GWh in 1966, 24,012 in 1990, 33,038 in 2025.
- Imports: 1,654 GWh in 1966, 26,249 in 2025; total supply 10,610 and 59,287.
- Wind: 610 GWh in 1990, 19,078 in 2025. Solar: 4,491 GWh in 2025.

## Reading the source

- The run stops at once, asking nothing, while `dst_statbank` or api.statbank.dk is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- The extract's other cells are not written: imports and the "total production" of wind, hydro and solar power, and the renewable supply of electricity, which StatBank gives as 0 in every year; and the total supply of wind, hydro and solar, which equals their renewable supply.
- Each kept or checked cell's sixty years must be there, each a whole number of GWh. A missing year, a cell given twice or a value not a whole number stops the run.
- **Checks,** exact in every year, all passing: the electricity's total supply equals its production plus its imports; each renewable's total supply equals its renewable supply; the cells left out are 0.
- Nothing is filled.

## License

Public. Statistics Denmark's source references page (read 1501): "You are free to re-use and reproduce contents from dst.dk and statbank.dk. This includes even commercial use"; the free use "corresponds to the license known as Creative Commons, CC 4.0 BY". The verdict, may be public, was given in session 2756. Credit: "Source: Statistics Denmark - StatBank.dk/ENE1HT"; processing must be stated. In the release package; held from the live set.

## Cross-check

Against `eurostat_electricity_production_annual` (Denmark, 1990 to 2024): wind (RA300), hydro (RA100) and solar photovoltaic (RA420) agree within 0.5 GWh in 102 of 105 year pairs. The three that do not:

| Year | Item | Eurostat, GWh | Statistics Denmark (here), GWh |
|---|---|---|---|
| 2018 | wind | 13,902 | 13,899 |
| 2022 | wind | 19,048 | 19,022 |
| 2022 | solar | 2,385 | 2,203 |

Production against Eurostat's gross production: below it in 31 of 35 years, by 0.4 to 7.6 per cent (1990: 24,012 against 25,982 GWh; 2024: 34,474 against 35,318), and above it in 2011, 2012, 2013 and 2017, by 1.0 to 6.6 per cent (2013: 37,033 against 34,743). The two publishers define production differently; neither file says how, and the gap is not one of own use alone. Use one publisher's series, not a mix.
