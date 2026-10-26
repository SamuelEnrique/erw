# European industry's electricity by NACE activity, 2017 to 2024 (Eurostat's nrg_d_indq_n)

Energy Research Warehouse (ERW), method note written in session 2815 (chain 143) for a table first written on 26 October 2026 (session 2818).

Tables: `eurostat_industry_electricity_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Energy consumption in industry by NACE Rev. 2 activity, quantities" (nrg_d_indq_n, `https://ec.europa.eu/eurostat/databrowser/view/nrg_d_indq_n/default/table`). The table reads two files from Eurostat's SDMX 2.1 dissemination API, with no key:
- electricity (SIEC E7000) in GWh, every activity and country, `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_d_indq_n/A.GWH.E7000..?format=SDMX-CSV&compressed=false`. The key is freq.unit.siec.nace_r2.geo, read from the dataset's structure (read 1627).
- the NACE_R2 codelist.

Source id `eurostat:nrg_d_indq_n`. Connector: `warehouse/connectors/eurostat_industry_electricity.py` (session 2818), whose raw store is `warehouse/raw/eurostat_industry_electricity/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1625).

## Vintage and revision

Written by run `20261026T053156Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T05:28:27Z. Eurostat's last update, as the file gives it (no time zone), is 27/08/26 23:00:00.

## Shape and variables

Series, 8,307 rows, 34 areas, 55 activities, 2017 to 2024:
- `entity` `eurostat_industry_electricity:<geo>:<NACE code>`. The codes are TOTAL; mining (B07-B09 except energy products, and its parts); the manufacturing divisions C10 to C33 and some groups (pulp C1711, the chemical groups C201 to C206, glass C231, cement C235, aluminium C2442); aggregates of divisions (C10-C12, C25-C28 and others); construction (F and F41 to F43).
- `variable` `electricity_consumption`; `unit` MWh (Eurostat's GWh times 1,000).
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (EL is GR), blank for EU27_2020; `node` "<geo> industry electricity, <the NACE name>"; `x_nace_r2`, `x_flag` and `x_conf_status`.

**The activities overlap** (divisions, their groups, and aggregates of divisions): do not sum them.

**Figures, Germany 2024 (MWh):**

| Activity | Code | MWh |
|---|---|---|
| Industry | TOTAL | 190,603,000 |
| Chemicals | C20 | 43,345,000 |
| Basic metals | C24 | 31,682,000 |
| Food, drink and tobacco | C10-C12 | 17,953,000 |
| Paper | C17 | 15,230,000 |
| Aluminium | C2442 | 5,140,000 |

## Reading the source

- **Zeros for splits not reported** (as in `eurostat_household_electricity_annual`) are not written. They are counted in the header and listed in the run log:
  - 42 country years whose every value is zero (several countries in 2017 to 2019);
  - 529 groups whose children are all zero under a positive parent (Austria's chemicals, 3,408 GWh in 2020, with its six groups 0).

  4,199 observations in all.
- **Each group's children against its parent,** within 0.5 GWh: 1,835 of 1,851 hold. The 16 others are kept as published.
- 1,104 other zeros are kept. 488 confidential observations (status C) have no row. Nothing is filled.
- The run stops, asking nothing, while Eurostat is paused. It also stops on:
  - a header not Eurostat's;
  - a frequency, unit, product or activity not expected;
  - a value not a number, or negative;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_d_indq_n. In the release package; held from the live set.

## Cross-check

TOTAL against `eurostat_electricity_consumption_annual`'s `industry` (nrg_cb_e, FC_IND_E), in the 191 country years both give:
- 123 agree within 0.1 per cent (Germany 2024: 190,603 GWh in both), and 140 within 1 per cent.
- 11 differ by more than 5 per cent: Estonia 2017 to 2020 (27.3 per cent under in 2020), Italy 2021 (8.6 per cent over), Greece 2020, Georgia 2024, the Netherlands 2017 to 2019 and Serbia 2020. These are the two datasets' vintages, kept as published.
