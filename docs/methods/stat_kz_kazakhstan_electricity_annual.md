# Kazakhstan's electricity a year, 2022 to 2025, from the fuel and energy balances (the Bureau of National Statistics)

Energy Research Warehouse (ERW), method note written in session 2667 (chain 133) for a table first written on 25 October 2026 (session 2664).

Tables: `stat_kz_kazakhstan_electricity_annual`

## Publisher and address

The Bureau of National Statistics of the Agency for Strategic Planning and Reforms of the Republic of Kazakhstan publishes a fuel and energy balance each year, in physical terms. The table reads the electricity column of each English edition's sheet "1":

`https://stat.gov.kz/api/iblock/element/<id>/file/en/` (2022 75937, 2023 205511, 2024 411633, 2025 411634)

Each address answers with the file under `/upload/iblock/` on the same host. The editions are listed on the Energy Statistics page (`https://stat.gov.kz/en/industries/business-statistics/stat-energy/`). No key. Source id `stat_kz:fuel_energy_balance_physical`. Connector: `warehouse/connectors/stat_kz_kazakhstan_electricity.py` (session 2664), whose raw store is `warehouse/raw/stat_kz/`. stat.gov.kz's robots file closes Bitrix's system paths and some query parameters (read 1362).

## Vintage and revision

Written by run `20261025T103039Z` (the write under the lock, offline), which read the four workbooks retrieved from 10:27 to 10:29 UTC on 25 October 2026. The 2025 edition was published on 3 August 2026; the next is due on 2 August 2027.

## Shape and variables

Series, 84 rows, 21 entities, 2022 to 2025. `entity` `statkz:kz:<item>`:
- **Generation:**
  - `output` (the transformation sector's electricity), and its four plant classes `tpp_main`, `tpp_secondary`, `chpp_main` and `chpp_secondary`;
  - `hydro`, `solar`, `wind` and `biogas` (primary production).
- **Trade:** `imports`; `exports` (stored as a positive quantity, the balance printing it negative).
- **Use:**
  - `own_use` (the energy sector's own needs) and `losses`;
  - `consumption` (final energy consumption) and its sectors `industry`, `transport`, `other`, `households`, `services` and `agriculture`.
- `statistical_difference`.

`unit` MWh (the balance's million kWh times 1,000); `ts_utc` the year's first day; `freq` P1Y; `geo` KZ; `node` the row's label as the edition gives it.

The output was 113.6 TWh in 2022 and 2023, 118.7 in 2024 and 123.8 in 2025. Wind grew from 2.3 TWh to 5.2. In 2025: hydro 10.4, solar 2.3, imports 5.1, exports 3.5, final consumption 87.1.

**The plant classes are not comparable across 2024 and 2025.** The 2025 edition puts most output under electricity plants of main activity (71.5 TWh), the earlier editions under CHP plants (82.3 TWh in 2024).

## Reading the source

- The run stops at once, asking nothing, while `stat_kz` or stat.gov.kz is paused.
- Four requests a run, saved and reused unless `--fresh`; `--offline` asks nothing.
- **Each sheet is checked for:**
  - its title ("... for <year> in physical terms"), the year the workbook was asked for;
  - its column headers: electricity and the four renewables, in million kWh.
- **Each row is found by its label within its section** (total supply, the transformation sector's exit, final consumption).
  - The editions name the same rows differently. 2025 says "Imports (+)", "Statistical differences" and "Electricity plants (TPP)". 2022 to 2024 say "import", "Statistical discrepancies" and "Power plants (TPP) ... - electricity generation".
  - A row found under none of its names stops the run.
- **Checks,** each within 1 million kWh and passing in every year:
  - the plant classes add to the output;
  - output, imports, exports, own use and losses make the energy available;
  - available less the statistical difference is the final consumption;
  - industry, transport and the other sectors add to it.

Nothing is filled. Not read: the 2021 edition (element 37685), in GWh and with the IEA's row names.

## License

Public. The Bureau's conditions for the use of official statistical information (read 1364): "Users may use official statistical information for any purposes (including reusing it in full) freely, free of charge, perpetually, and without territorial restrictions, including copying, publishing, distributing with a reference to the source". Verdict: may be public. In the release package; held from the live set.

## Cross-check

Against `eia_world_electricity_annual`'s Kazakhstan, in TWh:
- **Generation:** 2022 113.6 against 113.59; 2023 113.6 against 113.17; 2024 118.7 against 122.79.
- **Trade:** imports and exports agree to 0.01 TWh in 2022 (3.69 and 2.24) and 2023 (4.78 and 2.71).
