# European data centres' electricity consumption, 2020 to 2024 (Eurostat's isoc_env_ict_nrg)

Energy Research Warehouse (ERW), method note written in session 2801 (chain 142) for a table first written on 26 October 2026 (session 2799).

Tables: `eurostat_data_centre_electricity_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Data centres' electricity consumption" (isoc_env_ict_nrg, `https://ec.europa.eu/eurostat/databrowser/view/isoc_env_ict_nrg/default/table`). The table reads the whole dataset from Eurostat's SDMX 2.1 dissemination API, with no key: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/isoc_env_ict_nrg?format=SDMX-CSV&compressed=false`. That is electricity (SIEC E7000) consumed by data centres (NACE Rev. 2 "DATAC"), in GWh.

Source id `eurostat:isoc_env_ict_nrg`. Connector: `warehouse/connectors/eurostat_data_centres.py` (session 2799), whose raw store is `warehouse/raw/eurostat_data_centres/`. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1598). Session 2799 found the dataset in Eurostat's dataflow list (2,950 datasets).

**It is the ERW's first measured data-centre consumption.** The ERW's other data-centre tables hold projects, operators' sites and queue positions, not use.

## Vintage and revision

Written by run `20261026T032717Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T03:25:03Z. Eurostat's last update, as the file gives it (no time zone), is 27/07/26 11:00:00. The collection began with reference year 2020, and countries have joined it year by year.

## Shape and variables

Series, 85 rows, 32 areas, 2020 to 2024:
- `entity` `eurostat_data_centres:<geo>`; `variable` `electricity_consumption`.
- `unit` MWh (Eurostat's GWh times 1,000); `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (Eurostat's EL is GR).
- `node` "<geo> data centres' electricity consumption"; `x_geo_code`, `x_flag` and `x_conf_status` Eurostat's codes and flags.

Countries a year: 5 in 2020, 6 in 2021, 21 in 2022, 26 in 2023, 27 in 2024. Eurostat gives no EU aggregate.

**Figures, 2024:**

| Country | MWh |
|---|---|
| Germany | 20,000,000 |
| Ireland | 6,969,000 |
| the Netherlands | 5,092,643 |
| France | 4,348,256 |

Ireland's data centres used 3,027,000 MWh in 2020.

## Reading the source

- **11 confidential observations** (status C, no value) have no row: Italy 2022 to 2024, Serbia 2020 to 2024, Malta 2023 and 2024, and Bulgaria 2024.
- **28 zeros are kept as Eurostat prints them,** and the header names the countries that give one. **Some cannot be measured absences:** Denmark's 2020 to 2022, for one, while large data centres operate there, and Poland's 2022 and 2023, before 459,342 MWh in 2024. Treat a zero as "none reported", not "none used". Nothing is filled.
- Countries kept: the EU's members, EFTA's and the official candidates (none other is in the file so far).
- The run stops, asking nothing, while Eurostat is paused. It also stops, filling nothing, on:
  - a header not Eurostat's;
  - a unit, frequency, product or activity not expected;
  - a value not a number, or negative;
  - a period not a year;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, isoc_env_ict_nrg. In the release package; held from the live set.

## Cross-check

Against each country's final electricity consumption in `eurostat_electricity_consumption_annual` (nrg_cb_e, FC):

| Country | Year | Data centres, GWh | Share of final consumption |
|---|---|---|---|
| Ireland | 2020 | 3,027.0 | 10.5 per cent |
| Ireland | 2024 | 6,969.0 | 21.2 per cent |
| the Netherlands | 2024 | 5,092.6 | 4.7 per cent |
| Germany | 2024 | 20,000.0 | 4.2 per cent |
| France | 2024 | 4,348.3 | 1.1 per cent |

The share is this note's, not a column of the table. Germany's figures (17,900, 18,000 and 20,000 GWh) are given rounded, as Eurostat prints them.
