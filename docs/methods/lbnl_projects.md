# Solar projects and wind plants' capacity factors (Berkeley Lab)

Energy Research Warehouse (ERW), method note written in session 946 (chain 053) for tables first written on 23 October 2026.

Tables: `lbnl_solar_projects`, `lbnl_wind_capacity_factors`, `lbnl_wind_costs`, `lbnl_wind_turbine_orders`

## Publisher and address

Lawrence Berkeley National Laboratory (Berkeley Lab), the two report data files `lbnl_ppa_prices.md` describes, read from the copies `lbnl_ppa_prices.py` saves (`warehouse/raw/lbnl_ppa_prices/`):

- Utility-Scale Solar, 2025 Data Update (October 2025), sheet "Individual_Project_Data": `https://eta-publications.lbl.gov/sites/default/files/2025-10/2025_utility-scale_solar_data_update.xlsx`. Connector: `warehouse/connectors/lbnl_solar_projects.py` (session 939).
- Land-Based Wind Energy Technology Data Update, 2026 Edition (August 2026), sheet "Capacity Factor in 2025 by COD": `https://eta-publications.lbl.gov/sites/default/files/2026-08/data_file_land-based_wind_energy_technology_update_2026_edition_public_0.xlsx`. Connector: `warehouse/connectors/lbnl_wind_capacity_factors.py` (session 944).

Each connector asks nothing while the saved file is on the machine (ceiling one request otherwise).

## Vintage and revision

The solar file retrieved 2026-10-23T08:30:21Z (last modified 15 October 2025); the wind file the same morning. Snapshots, replaced whole by a run. LBNL publishes each report once a year at a new address; the connectors' `URL` then needs the new file's.

## Shape and variables

`lbnl_solar_projects` (entities, 1,775 projects: 1,759 PV, 16 CSP; 112,820 MW-AC; 48 states): `entity_id` `lbnl_solar:<EIA ID as LBNL writes it>`, its suffixes (`ret`, `a`, `b`) kept as LBNL writes them, not interpreted, or `lbnl_solar:none-<name>` for the 3 without an id; `entity_type` `plant`; `name`; `geo` `US-<state>`; `lat`, `lon`; `capacity_mw` the AC capacity; `status` empty (LBNL lists projects that reached commercial operation); `status_date` LBNL's solar commercial operation date (1984 to 2024; many a month's last day). The rest are LBNL's columns, renamed with their units: region, irradiance (`ghi_kwh_m2_day`), technology and sub-type, DC capacity, inverter loading ratio, mount, tracking, tilt, azimuth, hybrid configuration (198 projects: PV+Storage 160, PV+Fossil 16, PV+Geothermal 5 and others), storage technology, coupling, year, MW and MWh, the 2024 energy and capacity value, LCOE without and with federal tax credits and the levelized PPA price (425 projects), all in 2024 USD/MWh, the offtaker, and `cf_<year>` the capacity factor of each year 2008 to 2024 (a fraction).

`lbnl_wind_capacity_factors` (series, 1,210 plants): `entity` `lbnl_wind:<EIA plant code>`; `variable` `capacity_factor`; `unit` `ratio` (a fraction); `ts_utc` 2025-01-01; `freq` `P1Y`; `geo` `US`; `node` "EIA plant <code>"; `x_cod` LBNL's commercial operation year or period (1998-99, 2000-01, 2002-03, 2004-05, then each year to 2024); `x_repower` partial repower (101), full repower (22) or empty. Median 0.319, from 0.037 to 0.624. LBNL names no project.

## Reading the sheets

- Solar: the headings must be as read; an id given twice stops the run; a blank stays blank.
- Wind: the project block is the sheet's columns K to N (capacity factor, COD, EIA plant code, repower), found by its heading row ("Factor", "COD", "Code", "Repower" under "2025 Capacity"); the summary block to its left is not taken. A heading not as read or a plant code given twice stops the run; a plant without a value would be left out (none when written).
- Nothing is filled.

## License

Each file's copyright notice: "This work is openly licensed via CC BY 4.0"; Berkeley Lab's verdict in `license_verdicts.csv` (read 14).

## Cross-checks (sessions 939, 944 and 946)

- Solar against EIA (session 939): 1,772 projects carry an EIA id (1,767 plants); 1,740 are in `uspvdb_solar_facilities` and 1,755 have PV generators in `eia860m_operating_generators`; the AC capacity equals EIA-860M's PV nameplate within 5 percent at 1,637 of 1,750 plants (109,926 and 110,626 MW in all).
- Wind against EIA (session 944): every plant is in `eia860_wind_generators` (2025); for the 1,209 plants with twelve months of 2025 net generation in `eia923_plant_fuel_monthly`, generation over EIA-860 nameplate times 8,760 hours equals LBNL's figure within 0.01 at 1,138 (median difference 0.000); the capacity-weighted fleet figure is 0.340 by LBNL and 0.336 by EIA.
- Session 946, against the code and the tables: no id is repeated in either; the solar `status_date` is LBNL's own date column, not built from its year; the counts above computed from the rows.

## What they do not hold

- The wind file's other sheets (turbine sizes, curtailment, the regional costs and the O&M points; its prices and costs are `lbnl_wind_costs`, below) and its "REC Prices" sheet, monthly certificate prices by state from Marex Spectron, a broker: whether LBNL's license covers a broker's prices is a question for the owner (session 940).
- Wind capacity factors of years before 2025, or by project name.
- The solar file's PV+battery PPAs, which are `lbnl_hybrid_ppa_prices` (`lbnl_ppa_prices.md`).

## Wind turbine prices and project costs (session 952; added by session 960)

`lbnl_wind_costs` and `lbnl_wind_turbine_orders`, from the same 2026 wind data file, sheets "Wind Turbine Prices", "CapEx Over Time" and "Wind LCOE Over Time". Connector: `warehouse/connectors/lbnl_wind_costs.py` (`--table` each); no request while `lbnl_ppa_prices`' saved file is on the machine. All in real 2025 dollars (`x_dollar_year` 2025).

`lbnl_wind_costs` (series, 119 rows): `entity` `lbnl_wind_cost:<what>:<whose>`.

| Entity | Rows | What |
|---|---|---|
| `turbine_price:vestas`, `:sgre`, `:nordex` | 21, 9, 10 | the makers' global average turbine prices (USD/kW) at LBNL's mid-year dates (30 June; Vestas from 2005, the others from 2016); `geo` empty |
| `turbine_price:lbnl` | 20 | LBNL's average turbine price a year, 2006 to 2025 (1,751 to 1,101 USD/kW, its low 990 in 2020); `geo` US |
| `capex:us` | 31 | the capacity-weighted installed cost of each commercial operation year's projects, 1983 to 2025 (USD/kW; 2,133 in 2015, 1,583 in 2022, 2,096 in 2025), `x_sample` the projects |
| `lcoe:us` | 28 | the generation-weighted levelized cost, 1998 to 2025 (USD/MWh; 107 in 1998, 39.8 in 2022, 52.1 in 2025), `x_sample` and `x_sample_mw` |

A year LBNL gives a sample but no cost has no row. LBNL calls EIA's 2024 and 2025 cost estimates preliminary.

`lbnl_wind_turbine_orders` (events, 122): the reported U.S. turbine orders, February 1997 to July 2016, each with its price (USD/kW; median 1,741). `event_id` `lbnl_turbine_order:<12 hex of the date and price>`, a second identical row `-2`; `event_type` `turbine_order`; LBNL names no buyer, maker or size.

Not taken: "Recent CapEx by Region" (it does not say which years' projects it averages) and "O&M Over Time" (about 215 projects' average O&M costs, with no project and no date beyond the COD year, some suppressed by LBNL).

Cross-checks (sessions 952 and 960): the installed cost against `nlr_atb_electricity_costs`' land-based wind (moderate case, dollars of 2023): 2023's 6 percent under the ATB's base year, 2024's within 2 percent of its class 4 default, 2025's 9 percent over its projection; LBNL's LCOE of 2023 to 2025 inside the ATB's range across wind classes. Session 960, against the code: `TURBINE_BLOCKS` gives the four price blocks; the counts computed from the rows.
