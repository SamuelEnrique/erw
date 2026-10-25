# Electricity generation by fuel and the supply balance for each UK nation, 2004 to 2025 (DESNZ)

Energy Research Warehouse (ERW), method note written in session 2681 (chain 134) for a table first written on 25 October 2026 (session 2678).

Tables: `desnz_uk_nations_electricity_annual`

## Publisher and address

The Department for Energy Security and Net Zero (DESNZ) publishes "Electricity generation and supply in Scotland, Wales, Northern Ireland and England, 2004 to 2025 - data tables" with Energy Trends of September 2026, published 29 September 2026. The table reads `https://assets.publishing.service.gov.uk/media/6aba6c4afe72ed1e2b02f14b/Regional_Electricity_Generation_and_Supply_Timeseries_2026.xlsx`, listed on its gov.uk page, no key. Source id `desnz:electricity_generation_supply_nations_2026`. Connector: `warehouse/connectors/desnz_uk_nations_electricity.py` (session 2678), whose raw store is `warehouse/raw/desnz_regional/`. www.gov.uk's robots file closes only print and search paths (read 1392); the assets host has none (read 1393).

## Vintage and revision

Written by run `20261025T115017Z` (the write under the lock, offline), which read the workbook retrieved at 2026-10-25T11:46:03Z, last modified 28 September 2026. DESNZ republishes the whole series each year, with revisions.

## Shape and variables

Series, 4,167 rows, 200 entities, each year from 2004 to 2025, for the UK and each nation. `entity` `desnz:<nation>:<item>`, nation `uk`, `scotland`, `wales`, `northern_ireland`, `england`:
- **Table 2a, generation by fuel** (`generation`): the major power producers' rows `mpp_<fuel>` and the other generators' `other_<fuel>`, each with its total.
- **Table 1, the supply balance:**
  - `generated_mpp`, `generated_other`, `generated_total` (`generation`);
  - own use (`own_use`) and net supply (`net_supply`) of each;
  - `transfer_to_england`, `transfer_to_northern_ireland`, `transfer_to_europe` (`net_transfers`, net of receipts, as published), and `transfers_other_to_public` (`transfers`);
  - `transmission_losses`, `distribution_losses` (`losses`);
  - `consumption_public`, `consumption_autogenerators`, `consumption_total` (`consumption`);
  - `sales`; `statistical_difference`.

`unit` MWh (the tables' GWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` GB, GB-SCT, GB-WLS, GB-NIR or GB-ENG; `node` the row's label (note marks dropped).

**Figures:**
- UK generation was 393.9 TWh in 2004, 286.0 in 2024 and 293.6 in 2025. In 2025: Scotland 54.0, Wales 22.5, Northern Ireland 8.2, England 208.9.
- In 2025 Scotland's major producers made 27.3 TWh of wind, and its net transfer to England was 18.5 TWh. The UK's net transfer to Europe was -29.7 TWh, a net import.

## Reading the source

- The run stops at once, asking nothing, while `desnz_regional` or the assets host is paused.
- One request a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- Each table is read by its title and its header of "<year> <nation>" columns. A digit after a nation is dropped: Table 1 heads one column "2022 England6". Each row is read by its label.
- "[x]" and a blank cell have no row. Nothing is filled.
- **Not taken:**
  - Table 2a's "All generating companies" rows, a block DESNZ derives that does not add: fossil fuels miss coal, oil and gas by up to 1,250 GWh, and the total its parts by up to 7,875.
  - Table 2b (shares, per cent).
- **Kept as published:** Table 1, although its total generated misses its two parts in seven nation-years. Wales is +1,235 GWh and England -1,250 in 2020, Northern Ireland +15 in 2020, and England and the UK -96 in 2023 and -1,071 in 2024.
- **DESNZ's note 9:** the nations' totals do not sum exactly to the UK's.
- **Check:** a Table 2a block's fuels add to its total within 10 GWh (the largest gap is 7).
- The run stops for a nation, fuel or row not in the map, a row given twice or missing, or a check missed.

## License

Public. The page: "All content is available under the Open Government Licence v3.0, except where otherwise stated". DESNZ's verdict is on record (read 315): may be public. In the release package; held from the live set.

## Cross-check

Against `desnz_uk_electricity_quarterly` (Energy Trends 5.1, four quarters summed), the UK's total generated: 293.6 TWh in 2025 and 286.0 in 2024 in both.
