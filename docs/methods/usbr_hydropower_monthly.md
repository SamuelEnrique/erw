# Reclamation's hydropower plants, a month (the Bureau of Reclamation's plant performance data)

Energy Research Warehouse (ERW), method note written in session 2009 (chain 056) for a table first written on 23 October 2026.

Tables: `usbr_hydropower_monthly`

## Publisher and address

U.S. Bureau of Reclamation (USBR), Power Resources Office, "Active USBR Facilities, Operated and Maintained by Reclamation, Monthly and Annual Performance Data", `https://www.usbr.gov/power/data/Plant_Data_11_2025.xlsx`, linked from its Reports and Data page `https://www.usbr.gov/power/data/data.html` (the workbook's name carries its month; the connector reads the page for it). Connector: `warehouse/connectors/usbr_power.py` (session 2003). www.usbr.gov's robots file disallows only `/pn-bin` and `/gp-bin`.

The chain asked for Reclamation's RISE (data.usbr.gov): its robots file disallows `/rise/api` and the time series queries, the only ways RISE serves its data, so this workbook was taken instead. The page's "10 year monthly generation by facility.xlsx" answered HTTP 404.

## Vintage and revision

The workbook generated 7 November 2025 (monthly sheet) and 12 November 2025 (annual sheet): October 2013 to September 2025, Reclamation's fiscal years 2014 to 2025 (Anderson Ranch's last row is dated October 2025). Reclamation's note: "Facility data is considered PROVISIONAL and is subject to revision." A snapshot (ceiling two requests).

## Shape and variables

Series, 31,702 rows, 55 plants, 220 series. `entity` `usbr_plant:<facility>`; variables installed_capacity (MW, Reclamation's kW over 1,000; 7,933 rows), gross_generation (MWh, its kWh over 1,000; 7,933), auxiliary_use (7,918) and net_generation (7,918); `ts_utc` the month's first day; `freq` P1M; `geo` empty (the workbook gives no state); `node` the facility as Reclamation names it; `x_region` Reclamation's region (MB, CPN, UCB, CGB, LCB), from the annual sheet.

## Reading the workbook

- The heading rows must be as read (the annual sheet's "Plant Capacity (kWh)" is its own label for kW); the two sheets must list the same 55 facilities; a month must be MM/YYYY; an (entity, variable, ts_utc) given twice stops the run.
- 932 months of net generation are below zero (a month a plant used more than it made, as for a pump-generating plant), kept as written. An empty cell has no row (Lewiston's 15 months from January 2024 to May 2025 with no auxiliary use or net generation). Nothing is filled.
- The annual sheet is not written: its net generation is checked against the sum of each fiscal year's months (October to September); 659 of 660 plant fiscal years agree within 0.1 percent.

## License

Public: Reclamation's Disclaimer page defers to the Department of the Interior's notice (reads 172 and 159 of `license_reads.csv`): "materials produced by federal agencies are in the public domain".

## Cross-checks (sessions 2003 and 2009)

- 52 of the 55 plants match a Reclamation-owned plant of `ornl_eha_hydropower_plants` by name (not Boise River Diversion, Judge Francis Carr and Mt. Elbert); 47 of those within 10 percent of ORNL's capacity.
- January to September 2025 net generation against `eia923_plant_fuel_monthly` by the EIA plant id ORNL gives: 46 of 50 within 5 percent (Grand Coulee 12,360,602 and 12,270,940 MWh; Glen Canyon 2,229,877 and 2,230,280; Shasta 2,063,176 and 2,063,178). Hoover differs (2,313,685 against 1,603,965): EIA reports the Arizona and Nevada plants separately. Two pump-generating plants matched their main plant's EIA id by name and are not comparisons.
- Session 2009, against the code: `MONTHLY`, `ANNUAL` and `VARS` give the headings and variables above; the counts computed from the rows.

## What it does not hold

- Reclamation's reservoir, release and water data (RISE), and plants it owns but others operate.
