# Brazil's hydro, thermal, wind and solar generation, load and net interchange an hour, by subsystem and for the national system, 2020 to 22 October 2026 (ONS's open data)

Energy Research Warehouse (ERW), method note written in session 2247 (chain 101) for a table first written on 24 October 2026 (session 2240 of chain 101, its report `archive/sessions/SESSION_2240_REPORT.md`).

Tables: `ons_brazil_balance_hourly`

## Publisher and address

Operador Nacional do Sistema Eletrico (ONS), Brazil's system operator, open data (Dados Abertos), dataset "Balanco de Energia nos Subsistemas", page `https://dados.ons.org.br/dataset/balanco-energia-subsistema` (read 371). The page describes it as the load and supply of energy verified hourly by subsystem, the supply being the generation of hydro, thermal, wind and photovoltaic plants, in MWmed. The files, one a year:

- `https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/balanco_energia_subsistema_ho/BALANCO_ENERGIA_SUBSISTEMA_<year>.csv`, 2020 to 2026.

Each is semicolon-separated UTF-8, one line an hour and subsystem: `id_subsistema;nom_subsistema;din_instante;val_gerhidraulica;val_gertermica;val_gereolica;val_gersolar;val_carga;val_intercambio`. ONS's data dictionary (read 373, `DicionarioDados_Balanco_Energia_Subsistema.json`) calls `din_instante` "Data de Referencia" and each value the verified value "em MWmed"; it states no time zone. Source id `ons:balanco_energia_subsistema`.

Session 2240's probe (`runs/c101/s2240/probe.csv`) made 11 requests. `dados.ons.org.br`'s robots file disallows `/api/` and dataset history and asks a crawl delay of 10 seconds (read 370); the dataset page is allowed. The bucket has no robots file (read 372, HTTP 404). The seven files (HTTP 200, 3,719,822 to 5,127,029 bytes) are saved in `runs/license_reads/s2240/` (04 to 10) and seeded into `warehouse/raw/ons_balance/20261024T032446Z_probe/`; the trial and the write read them offline.

Connector: `warehouse/connectors/ons_balance.py` (session 2240): `[--first 2020] [--last 2026] [--offline] [--out-dir DIR]`, one request a year. A header not ONS's, a subsystem not named, a stamp not in ONS's form, a value that is not a number or an hour given twice stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it.

## Vintage and revision

One run, `20261024T032831Z`, written offline from the seven files retrieved from 2026-10-24T03:25:26Z to 03:25:29Z (`retrieved_at` is each file's): "This run wrote 1790640 rows: 1790640 new, 0 replacing earlier rows ...; 0 rows are kept from earlier runs." `vintage` is each file's Last-Modified: 2020 2024-10-20T14:55:51Z, 2021 2024-10-20T14:56:38Z, 2022 2024-10-20T14:57:21Z, 2023 2025-07-28T13:30:26Z, 2024 2025-07-28T13:31:29Z, 2025 2026-01-31T22:01:09Z, 2026 2026-10-23T22:00:22Z. The dataset page gives its last update as "outubro 23, 2026, 22:00 (UTC)".

ONS, the dataset page: "Os dados disponibilizados fazem parte de um processo de consistencia recorrente e, portanto, podem ser atualizados apos a sua publicacao" (the data are part of a recurring consistency process and may be updated after publication; accents dropped here). Files for years long past were rewritten in 2024 and 2025. A later run merges by (entity, variable, ts_utc): a revised value replaces the old one, but an hour ONS later blanks writes no row, so the earlier value would be kept.

## Shape and variables

Series, 1,790,640 rows, five entities of 358,128 rows each: `ons:N` (`node` NORTE), `ons:NE` (NORDESTE), `ons:S` (SUL), `ons:SE` (SUDESTE/CENTRO-OESTE) and `ons:SIN` (SISTEMA INTERLIGADO NACIONAL); six variables; `unit` MW, the hour's mean; `freq` PT1H; `geo` BR; `market` blank; `x_brasilia_hour` ONS's stamp. Every entity holds all 59,688 hours of the span in every variable: no blank, nothing filled.

| Entity | Variable | Mean | Lowest | Highest |
|---|---|---|---|---|
| ons:N | hydro | 7,999.868 | 275.271 | 19,532.703 |
| ons:N | thermal | 1,881.857 | 155.507 | 4,363.925 |
| ons:N | wind | 196.984 | 0 | 424.059 |
| ons:N | solar | 263.163 | 0 | 3,657.644 |
| ons:N | load | 7,056.411 | 1,364.251 | 11,422.408 |
| ons:N | net_interchange | 3,285.183 | -5,989.947 | 14,146.508 |
| ons:NE | hydro | 3,863.426 | 1,186.933 | 8,903.974 |
| ons:NE | thermal | 1,125.993 | 134.798 | 5,263.779 |
| ons:NE | wind | 9,339.223 | 140.500 | 22,681.452 |
| ons:NE | solar | 1,920.433 | -0.156 | 17,944.117 |
| ons:NE | load | 12,099.696 | 7,262.283 | 18,156.972 |
| ons:NE | net_interchange | 4,168.434 | -8,047.675 | 15,300.016 |
| ons:S | hydro | 7,937.909 | 136.934 | 16,129.770 |
| ons:S | thermal | 1,204.810 | 19.000 | 2,519.903 |
| ons:S | wind | 689.338 | 5.500 | 2,065.188 |
| ons:S | solar | 590.866 | 0 | 7,525.684 |
| ons:S | load | 12,675.482 | 5,755.558 | 22,737.443 |
| ons:S | net_interchange | -2,250.695 | -12,484.777 | 8,425.681 |
| ons:SE | hydro | 27,573.270 | 12,290.537 | 49,700.321 |
| ons:SE | thermal | 6,192.228 | 2,193.996 | 12,525.058 |
| ons:SE | wind | 27.719 | 0 | 264.952 |
| ons:SE | solar | 2,526.796 | 0 | 28,883.740 |
| ons:SE | load | 41,346.114 | 21,658.253 | 62,149.885 |
| ons:SE | net_interchange | -5,021.651 | -16,172.031 | 7,167.823 |
| ons:SIN | hydro | 47,374.474 | 18,216.904 | 87,875.710 |
| ons:SIN | thermal | 10,404.892 | 4,415.886 | 22,751.102 |
| ons:SIN | wind | 10,248.166 | 158.500 | 25,064.762 |
| ons:SIN | solar | 5,301.179 | 0 | 52,925.009 |
| ons:SIN | load | 73,177.704 | 40,358.310 | 106,148.660 |
| ons:SIN | net_interchange | 180.742 | -2,766.580 | 2,700.750 |

MW, rounded to 3 decimals.

- **Net interchange** is positive for an export, as the header says: in the North, generation less load averages 3,285.5 MW against a mean interchange of 3,285.2. SIN's, the national system's, can only be with neighbouring countries; it is 0 in 29,304 hours.
- **Solar at night.** Values are as published: SIN's solar averages 8 to 17 MW in each clock hour from 19:00 to 04:00, and is exactly 0 in only 4,970 hours; NE's solar is -0.156 MW at 2026-09-22T22:00:00Z, the only negative generation value.
- Values keep ONS's digits, with floating-point tails (the North's hydro 5,244.15799999 MW at 2020-01-01T04:00:00Z).

In 2025 (Brasilia days), SIN: load 697.374 TWh; hydro 403.838, wind 115.361, solar 91.833 and thermal 89.381 TWh; net interchange 3.040 TWh.

## Placing values in time, and what is filled

`ts_utc` is ONS's `din_instante` plus three hours, taken as Brasilia time (UTC-3, no daylight saving since 2019) and as the hour's start; `x_brasilia_hour` keeps the stamp (0 rows where `ts_utc` is not it plus three hours). The first hour is 2020-01-01 00:00 Brasilia (03:00Z), the last 2026-10-22 23:00 (2026-10-23T02:00:00Z); header line 1's "2026-10-23" is that last hour's UTC date.

ONS states no time zone, so the zone is the session's inference, from the solar peak. Checked on the table (`ons.py`):

- SIN's mean solar by clock hour peaks at hour 11 (15,894 MW) and 12 (15,707) in every year 2020 to 2026, and is above 2 percent of its peak from hour 6 to hour 17 in every year; the North, Northeast and Southeast peak at 11, the South at 12.
- The centre of SIN's solar output, weighting each hour's middle by its mean, falls at 11.91 on ONS's clock, 11:55, if a stamp is the hour's start. Mean solar noon on a UTC-3 clock lies between about 11:20 and 12:20 for longitudes 35 to 50 degrees west. A UTC clock would put the centre at 08:55 local time. A stamp marking the hour's end would put it at 10:55, earlier than mean solar noon anywhere in that span: the start fits better.
- SIN's load is lowest at hour 4 and highest at hour 19.
- Every entity holds every hour from first to last once: no hour of the clock is skipped or given twice in seven years, as a clock with daylight saving would do.

A blank has no row; there is none. Nothing is filled.

## License

Header: "License: public, CC BY (the dataset page): credit to ONS, changes noted (reshaped from wide to long, the hour placed in UTC; no value changed). Cite: ONS, Dados Abertos." `docs/licenses.md` and `warehouse/metadata/license_verdicts.csv`: read 371 (session 2240, the dataset page's legal notice), "Ao acessar este site e/ou utilizar as informacoes provenientes dele, sera considerado que voce aceitou os termos e condicoes da LICENCA CC-BY, que permite que os reutilizadores distribuam, modifiquem, adaptem e desenvolvam o material sobre os dados, desde que seja dado o credito apropriado ao criador(ONS) e que informe quais alteracoes foram feitas." (accents dropped here), verdict "may be public", if the ERW sells anything "may be public"; the table's row: flag public, "agrees", ERW verdict public.

## Checks (session 2247)

The figures in this note were computed from the rows of `warehouse/output/ons_brazil_balance_hourly.csv`, read past its 10 header lines (counted), and from the saved page and dictionary, read only (scripts `runs/c101/s2247/ons.py` and `ons2.py`, outputs beside them).

- 1,790,640 rows, `ts_utc` from 2020-01-01T03:00:00Z to 2026-10-23T02:00:00Z, as header line 10 states; 59,688 hours for each entity, as header line 3 states, and every hour of the span; no (entity, variable, ts_utc) twice; no blank value; unit MW throughout.
- The trial's table (`runs/c101/s2240/trial/ons_brazil_balance_hourly.csv`) has the same rows past its header, byte for byte.
- Session 2240's cross-check (`runs/c101/s2240/cross.py`), run again from the main checkout with the written table as argument 1: its output is identical to the saved `cross.out`, which was run on the trial. SIN's load against Ember's Brazilian demand (`owid_ember_electricity_annual`): 0.8523 (2020), 0.8834, 0.8733, 0.8927, 0.9157 and 0.9150 (2025: 697.374 against 762.12 TWh). The four subsystems less SIN, largest gap: hydro 0.003 MW, load 0.005, thermal 9.749, solar 592.526, net interchange 1,551.320, wind 15,423.332. Generation less load less net interchange, largest gap 23,140.318 MW over 298,440 subsystem hours. Wind and solar, 10.7 percent of SIN's generation in 2020, 29.6 percent in 2025.
- Net interchange against generation less load (`ons2.py`): within 1 MW in 287,439 of 298,440 entity hours (96.31 percent); beyond it in 2,110 (N), 2,421 (NE), 1,834 (S), 2,196 (SE) and 2,440 (SIN). All 11,001 are in January to May 2026 (3,308, 2,996, 2,364, 1,408 and 901 entity hours a month), but 24 hours of the South in September 2022; none from June 2026.
- The four subsystems against SIN, more than 1 MW apart: wind 293 hours, solar 166 and thermal 97, all in January to May 2026; net interchange 24 hours, all in September 2022; hydro and load never.

## Where the description and the data disagree

None found that the rows contradict. Compared: the header's and docstring's entities, variables, unit, hour counts, span, sign of net interchange, "a blank has no row" and the two statements on ONS's inconsistencies, against the rows; the dictionary's columns and "MWmed", and the dataset page's sentence on revision, against the docstring. Two precisions:

- The docstring and header say net interchange equals generation less load in "about 96% of the hours, not all", and that the four subsystems sum to SIN "except in some hours, most of them in 2026". The breaks are not scattered: they fall in January to May 2026 (the year whose file ONS last rewrote) and in 24 hours of September 2022. A reader who needs the balance to close can use every hour before 2026 but those 24, and every hour from June 2026.
- The hour as the stamp's start, like the zone, is the session's inference; the solar centre (11:55 on ONS's clock) supports both.

Nothing to change in the connector. Session 2247's report corrects session 2240's two figures (the subsystems' 1,834 to 2,421 hours; the load ratio to Ember is not rising every year).

## The session report against the table

Every figure of `SESSION_2240_REPORT.md` checked against the table, the saved page and dictionary and the rerun cross-check holds (2020 to 22 October 2026, 1,790,640 rows, five entities, six measures in MW, "MWmed", solar peaking at 11:00 to 12:00 on ONS's clock, about 96 percent of hours within 1 MW and 1,834 to 2,440 hours an entity beyond it, the subsystems apart from SIN mostly in 2026 and wind up to 15,423 MW, 0.852 to 0.916 of Ember's demand, 697.374 against 762.12 TWh, wind and solar 10.7 to 29.6 percent, 11 requests), except:

- "1,834 to 2,440 hours a subsystem": the range counts SIN, which is not a subsystem; the four subsystems give 1,834 to 2,421.
- "SIN's load a year is 0.852 to 0.916 of Ember's ... rising": not every year; 2022 (0.8733) is below 2021 (0.8834) and 2025 (0.9150) below 2024 (0.9157).

## What it does not hold

- Generation by plant, the isolated systems outside SIN, generation behind the meter, ONS's other open datasets, hours before 2020, and 23 October 2026 on (the 2026 file, last modified at 22:00Z on 23 October, ends at 23:00 on 22 October, Brasilia time).
