# Austria's electricity a month from 2023 (Statistics Austria's monthly electricity statistics)

Energy Research Warehouse (ERW), method note written in session 2801 (chain 142) for a table first written on 26 October 2026 (session 2795).

Tables: `statat_austria_electricity_monthly`

## Publisher and address

Statistics Austria (STATISTIK AUSTRIA), "Monthly electricity statistics", four yearly OpenDocument spreadsheets: `https://www.statistik.at/fileadmin/pages/99/MEle<year>.ods`, 2023 to 2026. They are listed on the energy balances page, `https://www.statistik.at/en/statistics/energy-and-environment/energy/energy-balances`.

Source id `statat:monthly_electricity_statistics`. Connector: `warehouse/connectors/statat_electricity_monthly.py` (session 2795), whose raw store is `warehouse/raw/statistik_austria/`. It reads each file's `content.xml` by streaming, with the standard library (session 2764's reader, copied in). www.statistik.at's robots file was read in its own request (read 1596), as before. Session 2795 took this source in place of CPS Energy, whose robots file disallows Anthropic's agents by name.

## Vintage and revision

Written by run `20261026T030737Z`, which read the four files retrieved from 03:04:45 to 03:05:01 UTC on 26 October 2026. The 2026 file runs to July 2026. Each year's file is replaced as Statistics Austria revises it; the next run reads the current files whole.

## Shape and variables

Series, 793 rows, 12 entities, January 2023 to July 2026:
- `entity` `statat_mele:at` for the country's totals, or `statat_mele:at:<source>` for net production by source:
  - conventional thermal and its five fuels (coal, oil, natural gas, combustible renewables, other combustible fuels);
  - hydro, with pure and mixed hydro;
  - wind;
  - solar, from 2025.
- `variable`:
  - `net_production`;
  - `imports` and `imports_from_eu`;
  - `exports` and `exports_to_eu`;
  - `pumped_storage_use`;
  - `losses` (transmission and distribution);
  - `consumption` (calculated).
- `unit` MWh (the files' GWh times 1,000); `ts_utc` the month's first day at 00:00:00Z; `freq` P1M; `geo` AT; `node` the year and the row's label.

**Figures:** net production was 5,412,400 MWh in January 2023 and 5,485,045 MWh in July 2026.

## Reading the source

- "of which" is dropped from the labels. A "." (not available) has no row, and a "-" is read as zero.
- **Compared every month within 0.15 GWh:**
  - the total against its sources, only in years whose file lists solar (2023's and 2024's files list none, and their totals include it);
  - conventional thermal against its fuels;
  - hydro against pure and mixed;
  - the production sheet's total against the summary sheet's.

  **Two differences are kept as published:** conventional thermal in May 2024, and the summary sheet's total in May 2026, 45.9 GWh above the production sheet's.
- A row not in the expected structure, or a value not a number, stops the run. Nothing is filled.

## License

Statistics Austria's general terms, section 10: reproduction and distribution with the source cited and edits stated (the verdict on record, read 1518, session 2764). Credit: STATISTIK AUSTRIA; edited by the ERW (GWh written as MWh, reshaped). In the release package; held from the live set.

## Cross-check

Against `econtrol_austria_electricity_monthly` (E-Control, Austria's regulator), its whole-grid rows (`Importe | Ges`, entity `econtrol:at:999033`, and `Exporte | Ges`, `econtrol:at:999025`), GWh. E-Control's public-grid rows (`Oef`) are smaller and are not these:

| Month | Imports (here) | Imports (E-Control) | Exports (here) | Exports (E-Control) |
|---|---|---|---|---|
| January 2023 | 2,837.1 | 2,837.1 | 1,659.6 | 1,659.6 |
| July 2026 | 2,584.2 | 2,584.2 | 1,857.1 | 1,857.1 |

Of the 86 monthly imports and exports compared, 77 agree within 0.05 GWh, the files' rounding to 0.1 GWh. Statistics Austria compiles these files from E-Control's and Eurostat's statistics. **Nine, all in 2024, differ by more:** the largest is imports in September 2024, 1,586.7 GWh here against 1,590.3 GWh at E-Control (3.6 GWh, 0.2 per cent), then December 2024's imports (0.6 GWh). These are read as E-Control's later revisions, and both are kept as published. What this table adds is its own balance lines (pumped storage, losses, consumption, trade with the EU) and the solar row.
