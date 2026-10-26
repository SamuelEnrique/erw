# European households' electricity by end use, 2010 to 2024 (Eurostat's nrg_d_hhq)

Energy Research Warehouse (ERW), method note written in session 2801 (chain 142) for a table first written on 26 October 2026 (session 2798).

Tables: `eurostat_household_electricity_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Disaggregated final energy consumption in households, quantities" (nrg_d_hhq, `https://ec.europa.eu/eurostat/databrowser/view/nrg_d_hhq/default/table`). The table reads one file from Eurostat's SDMX 2.1 dissemination API, with no key: electricity's (SIEC E7000) households' balance items in GWh, `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_d_hhq/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990`.

Source id `eurostat:nrg_d_hhq`. Connector: `warehouse/connectors/eurostat_household_electricity.py` (session 2798), whose raw store is `warehouse/raw/eurostat_household_electricity/`. The balance items' names are the NRG_BAL codelist's, read by session 2798 and written in the connector. ec.europa.eu's robots file leaves `/eurostat/api/dissemination/` open and names no Claude agent (read 1597).

## Vintage and revision

Written by run `20261026T031957Z` (the write under the lock, offline), which read the file retrieved at 2026-10-26T03:16:41Z. Eurostat's last update, as the file gives it (no time zone), is 09/06/26 11:00:00. Eurostat revises the energy balances, and so this breakdown, each year.

## Shape and variables

Series, 3,150 rows, 38 areas, 2010 to 2024:
- `entity` `eurostat_household_electricity:<geo>`.
- `variable`: `total` (FC_OTH_HH_E, the households' energy use of electricity) and its six end uses, `space_heating`, `space_cooling`, `water_heating`, `cooking`, `lighting_appliances` (lighting and electrical appliances) and `other_end_use`.
- `unit` MWh (Eurostat's GWh times 1,000); `ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (Eurostat's EL is GR), blank for EU27_2020.
- `node` "<geo> households' electricity, <the NRG_BAL name>"; `x_geo_code`, `x_nrg_bal`, `x_flag` and `x_conf_status` Eurostat's codes and flags.

**Figures:** the EU27's households used 712,357,936 MWh of electricity in 2024. Of it:
- lighting and electrical appliances 391,097,146 MWh (54.9 per cent);
- space heating 113,873,225 (16.0);
- cooking 88,318,640 (12.4);
- water heating 80,980,292 (11.4);
- space cooling 22,335,982 (3.1);
- other end uses 15,752,651 (2.2).

Germany's households used 132,438,000 MWh in 2024.

## Reading the source

- **The six end uses make the total** within 0.001 GWh in all 444 country years that give all seven items. A difference above 1 GWh would stop the run.
- **A country year whose seven items are all zero is not written** (97 of them): no country's households use no electricity. These are the years a country did not report the split: 18 countries a year in 2010 to 2012, 17 in 2013 and 2014, 5 in 2015, 3 in 2016, 1 in 2017, none from 2018. The run log lists each. The other 370 zeros are kept, 291 of them other end uses and 78 space cooling.
- **The EU27_2020 aggregate before 2016 sums only the members that reported the split.** Its total is 34 to 37 per cent under the households' figure in `eurostat_electricity_consumption_annual` in 2010 to 2014, and 3 per cent under in 2015. Only from 2016 does the EU's figure stand for the whole Union.
- Countries kept: as `eurostat_electricity_consumption_annual` keeps them; the United Kingdom, Kosovo and the euro area aggregates are left out.
- The run stops, asking nothing, while Eurostat is paused. It also stops, filling nothing, on:
  - a header not Eurostat's;
  - a unit, frequency, product or balance item not expected;
  - a value not a number;
  - a key given twice.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_d_hhq. In the release package; held from the live set.

## Cross-check

The households' total against `eurostat_electricity_consumption_annual`'s `households` (nrg_cb_e, FC_OTH_HH_E), in the 451 country years both give: 392 agree within 1 GWh and 416 within 1 per cent. The rest are the EU aggregate's early years (above) and a few countries' later vintages:

| Country | Year | Here, GWh | nrg_cb_e, GWh | Difference |
|---|---|---|---|---|
| Germany | 2024 | 132,438.0 | 132,438.0 | 0 |
| EU27_2020 | 2012 | 451,044.7 | 718,455.7 | 37.2 per cent under |
| EU27_2020 | 2016 | 699,905.1 | 703,041.1 | 0.4 per cent under |
| North Macedonia | 2024 | 2,182.3 | 3,150.3 | 30.7 per cent under |
| Turkey | 2024 | 69,772.6 | 74,639.5 | 6.5 per cent under |
| Croatia | 2024 | 6,409.4 | 6,818.0 | 6.0 per cent under |

nrg_d_hhq was last updated on 9 June 2026 (as its file gives it), nrg_cb_e on 22 October 2026. The two are kept as each publishes them.
