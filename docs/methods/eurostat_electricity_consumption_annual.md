# European electricity consumption by sector, the energy sector's use and losses, 1990 to 2025 (Eurostat's nrg_cb_e)

Energy Research Warehouse (ERW), method note written in session 2759 (chain 139) for a table first written on 25 October 2026 (session 2757).

Tables: `eurostat_electricity_consumption_annual`

## Publisher and address

Eurostat (the Statistical Office of the European Union), "Supply, transformation and consumption of electricity" (nrg_cb_e, `https://ec.europa.eu/eurostat/databrowser/view/nrg_cb_e/default/table`). The table reads two files from Eurostat's SDMX 2.1 dissemination API, with no key:
- the data, every balance item of electricity (SIEC E7000) in GWh: `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/nrg_cb_e/A..E7000.GWH.?format=SDMX-CSV&compressed=false&startPeriod=1990`;
- the NRG_BAL codelist, for the balance items' names.

Source id `eurostat:nrg_cb_e`. Connector: `warehouse/connectors/eurostat_electricity_consumption.py` (session 2757), whose raw store is `warehouse/raw/eurostat_electricity_consumption/`. ec.europa.eu's robots file disallows the old SDMX path, the search pages and two language paths, leaves `/eurostat/api/dissemination/` open, and names no Claude agent (read 1507).

## Vintage and revision

Written by run `20261025T222857Z` (the write under the lock, offline), which read the file retrieved at 2026-10-25T22:25:36Z; Eurostat's last update, as the file gives it (no time zone), 22/10/26 23:00:00. Eurostat revises the energy balances each year, and the latest year's sectors arrive after its totals: 2025 so far gives the totals only.

## Shape and variables

Series, 15,667 rows, 40 areas (`entity` `eurostat_electricity_consumption:<geo>`), twelve variables, 1990 to 2025, in MWh (Eurostat's GWh times 1,000):
- `available_for_final_consumption` (AFC), `final_consumption` (FC), `energy_sector_use` (NRG_E), `losses` (LOSS), `statistical_differences` (STATDIFF);
- final consumption's energy use by sector: `industry` (FC_IND_E), `transport` (FC_TRA_E), `commercial_public_services` (FC_OTH_CP_E), `households` (FC_OTH_HH_E), `agriculture_forestry` (FC_OTH_AF_E), `fishing` (FC_OTH_FISH_E), `other_not_specified` (FC_OTH_NSP_E).

`ts_utc` the year's 1 January; `freq` P1Y; `geo` ISO alpha-2 (Eurostat's EL is GR), blank for EU27_2020; `node` "<geo> electricity, <the NRG_BAL name>"; `x_geo_code`, `x_nrg_bal`, `x_flag` and `x_conf_status` Eurostat's codes and flags.

**In this dataset Eurostat's final consumption (FC) includes the energy sector's own use:** FC equals NRG_E plus the seven sectors. A user wanting final consumption as other datasets define it subtracts `energy_sector_use`.

The file's other 51 balance items are not written: production and trade (held in `eurostat_electricity_production_annual` and `eurostat_electricity_trade_annual`), the transformation input, the branches of industry, transport and the energy sector, and the loss items' parts.

Countries kept: the EU's members, EFTA's and the official candidates, with EU27_2020, as `eurostat_electricity_production_annual` keeps them. The United Kingdom, Kosovo and the euro area aggregate are left out.

## Reading the source

- A header not Eurostat's; a unit, frequency, product or balance item not expected; a value not a number; or a key given twice stops the run.
- A blank has no row; zeros are kept (2,972); nothing is filled.
- **Checks:**
  - AFC equals FC plus STATDIFF within 1 GWh in all 1,326 country years. A miss stops the run.
  - FC equals NRG_E plus the seven sectors within 1 GWh in 1,260 of 1,289 country years that give all eight. The other 29 (EU27_2020 14, France 14, Austria 1, the largest Austria's 2024 by 3,944.1 GWh) are kept as Eurostat publishes them and listed in the run log.

## License

Public with acknowledgement: Eurostat's copyright notice, the verdict on record (read 280, session 2123). Cite: Eurostat, nrg_cb_e. In the release package; held from the live set.

## Cross-check

Against `ssb_norway_electricity_monthly` (Statistics Norway's monthly electricity balance, each year's twelve months summed), Norway, GWh:

| Year | Item | SSB | Eurostat (here) | Difference |
|---|---|---|---|---|
| 2020 | net consumption against final consumption | 125,410 | 125,545 | +0.1% |
| 2024 | net consumption against final consumption | 130,068 | 128,971 | -0.8% |
| 2020 | households | 40,483 | 39,884 | -1.5% |
| 2024 | households | 40,856 | 39,054 | -4.4% |

The households differ by definition (SSB's "consumption in households" is not Eurostat's household sector). SSB's "grid loss and statistical difference" is not Eurostat's losses, and is not compared.
