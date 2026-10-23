# Wind and solar PPA prices (Berkeley Lab)

Energy Research Warehouse (ERW), method note written in session 918 (chain 051) for a table first written on 23 October 2026.

Tables: `lbnl_ppa_prices`

## Publisher and address

Lawrence Berkeley National Laboratory (Berkeley Lab), two report data files, each linked from its page on LBNL's publications server (emp.lbl.gov answered HTTP 403 to the ERW's reader in session 253; eta-publications.lbl.gov serves the same files):

- Land-Based Wind Energy Technology Data Update, 2026 Edition (R. Wiser and others, August 2026), sheet "Wind PPAs by Plant": `https://eta-publications.lbl.gov/publications/land-based-wind-energy-technology-0`, file `/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx`.
- Utility-Scale Solar, 2025 Data Update (J. Seel, J. Mulvaney Kemp and others, October 2025), sheet "PPA Price by Project (PV only)": `https://eta-publications.lbl.gov/publications/us-utility-scale-solar-2025-data`, file `/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx`.

Connector: `warehouse/connectors/lbnl_ppa_prices.py` (session 915).

## Vintage and revision

Retrieved 2026-10-23 08:30 UTC (the same files session 253 saved on 13 October). A snapshot: each run replaces the table whole (ceiling: four requests, the two pages and the two files, 34 and 57 MB; `--offline` reads the saved ones). Each page must link one data file on its own host. LBNL publishes each report once a year; a new edition is a new page, so the connector's `FILES` needs the new page's address.

## Shape and variables

Events, one row a PPA (LBNL names no project). `event_id` `lbnl_ppa:<wind|solar>:<12 hex>`, a hash of the row's date, MW, term, region and price, with `-2` for a second identical row; `event_date` the PPA's execution date; `event_type` `ppa`; `mw` the contract capacity; `price` the PPA price levelized over its term (USD/MWh); `currency` USD; `x_technology`; `x_term_years`; `x_region` (CAISO, West (non-ISO), MISO, SPP, ERCOT, PJM, NYISO, ISO-NE, Southeast (non-ISO), Hawaii); `x_macro_region` (wind: West, Central, East; solar: Hawaii, West, Central, Northeast, Southeast); `x_price_unit`; `x_dollar_year` (wind 2025, solar 2024).

LBNL levelizes each contract over its full term after escalation and time-of-delivery factors, deflated with the GDP deflator and a 4 percent real discount rate. Solar PPAs are PV only, without PV+battery.

When written: 587 wind PPAs executed 1996 to March 2025 (62,327 MW, median 51.0 USD/MWh of 2025), 546 solar PPAs executed 2006 to June 2025 (41,550 MW, median 49.1 USD/MWh of 2024). Terms 3 to 35 years, median 20. Most PPAs by region: wind SPP 144, MISO 137, West (non-ISO) 127; solar CAISO 179, West (non-ISO) 148.

## Reading the sheets

- The row headed "PPA Execution Date" is found in the first 60 rows; the headings after it must be as read (wind: capacity, term, region, macro region and "Real 2025$/MWh"; solar: capacity, term, the ten regions, then the five consolidated regions), or the run stops.
- Wind gives a row's region and price in three columns. Solar gives the price in the column of its region and again in the column of its consolidated region; a row with no region or two stops the run. LBNL's `#N/A` is read as empty.
- The solar sheet's note says prices are in 2023 dollars, but its averages and the file's other price sheets are headed "2024 $/MWh"; the table takes 2024 and the header names the difference.
- Nothing is filled.

## License

Each file's copyright notice: "This work is openly licensed via CC BY 4.0" (Copyright The Regents of the University of California, through Lawrence Berkeley National Laboratory). Berkeley Lab's verdict in `license_verdicts.csv` (read 14) rests on the same statement in the Queued Up file.

## Cross-checks (sessions 915 and 918)

- Wind: the PPAs and their megawatts counted by execution year equal LBNL's "Wind PPA Average" sheet in 24 of 24 year groups (1996-99 to 2025). The rows' MW-weighted average is a little above LBNL's generation-weighted one (2015: 38.0 against 37.4; 2024: 71.6 against 70.0).
- Solar, outside Hawaii: the rows' MW-weighted average is within 5 percent of LBNL's generation-weighted average in 13 of 16 years, within 10 percent in 15.
- Session 918, against the code and the table: no event_id is repeated; every row has a price, a region and a consolidated region. Session 915's report gave the solar PPAs as ending in 2024; they run to June 2025 and the report is corrected.

## What it does not hold

- PV+battery PPAs ("PV+Battery Hybrid PPA Price"), concentrating solar ("PPA Price for CSP Plants"), and LevelTen's and Trio's price indices, which the same files hold.
- The projects' names or places.
