# Electricity demand and power sector emissions by country and region, a year (Ember, through Our World in Data)

Energy Research Warehouse (ERW), method note written in session 2129 (chain 079) for a table first written on 23 October 2026 (session 2126, `archive/sessions/SESSION_2126_REPORT.md`; the source and its license were read in session 2125).

Tables: `owid_ember_electricity_annual`

## Publisher and address

Our World in Data, energy dataset, from its catalog (no key): the data, `https://catalog.ourworldindata.org/energy/owid_energy/owid_energy.csv` (9,081,888 bytes, 130 columns), and its codebook, `https://catalog.ourworldindata.org/energy/owid_energy/owid_energy.codebook.csv` (130 rows, each column's unit and sources). The two columns taken are Ember's yearly electricity data (global and European, 2026) as Our World in Data compiles them. Source ids `owid:energy` and, for the producer, `ember:yearly_electricity`. Files saved under `warehouse/raw/owid_energy/`.

Connector: `warehouse/connectors/owid_energy.py` (session 2126): `[--offline] [--out-dir DIR]`, two requests (codebook, data). Every run checks the codebook first: a taken column whose sources are no longer exactly Ember's two data sets, or whose unit changed, stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `coverage.csv` gives the sectors power and carbon.

## Vintage and revision

One run, `20261023T230815Z`, from the data retrieved at 2026-10-23T23:07:14Z; `vintage` 2026-09-30T14:42:02Z in every row, the file's last-modified time. A later run replaces rows by their key and keeps rows it does not restate.

## Shape and variables

Series, 12,406 rows:

| `variable` | From the column | `unit` | Rows | Entities | Years |
|---|---|---|---|---|---|
| electricity_demand | electricity_demand_twh, times 1,000,000 | MWh | 6,378 | 239 | 1990 to 2025 |
| electricity_emissions | electricity_emissions_mtco2eq, times 1,000,000 | tCO2e | 6,028 | 239 | 2000 to 2025 |

`entity` `owid_energy:<ISO alpha-3>` for 214 entities, and `owid_energy:<name in snake case>` for 25: Our World in Data's regions and income groups (africa, asia, europe, european_union_27, north_america, oceania, south_america, world, the four income groups), Ember's regions named "(Ember)" (africa_ember, asean_ember, asia_ember, eu_ember, europe_ember, g20_ember, g7_ember, latin_america_and_caribbean_ember, middle_east_ember, north_america_ember, oceania_ember, oecd_ember), and Kosovo, which has no ISO code in the file. `node` the name as Our World in Data gives it (one per entity); `x_iso_code` and `x_owid_column`; `geo`, `market` blank; `freq` P1Y.

Demand rows a year: 35 from 1990 to 1999 (European countries and aggregates), 236 to 238 from 2000 to 2023, 221 in 2024, 106 in 2025.

## Placing values in time

`ts_utc` is the year's 1 January, UTC; the value is the calendar year's total.

## What is and is not filled

- Of the dataset's 130 columns, three draw on Ember alone (the codebook: electricity_carbon_intensity_gco2eq_per_kwh, electricity_demand_twh, electricity_emissions_mtco2eq). Two are taken; the carbon intensity is left out for want of a CO2-equivalent intensity unit in the data standard. The other 127 columns draw on sources without a verdict in the license record and are not taken.
- Values as published, multiplied by 1,000,000 and rounded to 3 decimals; a blank cell has no row; nothing is filled. 24 demand and 48 emissions rows are zero.

## License

Header: "License: public: Our World in Data's work is CC BY 4.0; Ember's data are CC BY 4.0. Cite: Ember (2026), Yearly Electricity Data; processed by Our World in Data." `license_verdicts.csv` records Ember (read 133) and Our World in Data (read 284), both "may be public". `docs/licenses.md`: "may be public", flag public, ERW verdict public.

## Checks (session 2129)

The figures in this note were computed from the rows of `warehouse/output/owid_ember_electricity_annual.csv`, read past its 11 header lines, and from the saved data file and codebook (scripts in `runs/c079/s2129/`).

- 12,406 rows, `ts_utc` from 1990-01-01T00:00:00Z to 2025-01-01T00:00:00Z, as the header states. No (entity, variable, ts_utc) twice; no negative value.
- World against the sum of the ISO-coded entities: demand 1.0005 (2000), 1.0001 (2010), 0.9998 (2020), 0.9960 (2023), 0.9964 (2024); emissions 0.9996, 0.9996, 0.9995, 0.9976, 0.9976. In 2025, with 90 countries reported, the countries sum to 0.9325 of World's demand and 0.9175 of its emissions.
- World demand: 30,930,230,000 MWh in 2024 and 31,772,350,000 in 2025; United States 4,404,830,000 MWh in 2024 and 4,535,810,000 in 2025.
- Session 2126's cross-check (`runs/c079/s2126/cross.py`), run again: its output is identical to the saved `cross.out`.
  - Demand over EIA's generation plus net imports (`eia_international_electricity_annual`), 2015 to 2024: United States 0.998 to 1.000; Canada 1.019 to 1.071; Mexico 0.875 (2021) to 1.070 (2022).
  - United States power sector emissions over EIA's power sector CO2 (`eia_power_co2_state_annual`, `eia_power_co2:US:ALL`): 1.015 (2015: 2,062.0 Mt CO2e against 2,031.5 Mt CO2) rising to 1.096 (2024: 1,685.2 against 1,537.1), with 1.072 in 2020 above 1.066 in 2021 and 2022. Ember counts CO2 equivalent, EIA CO2 alone.

## Where the description and the data disagree

1. **Two or three Ember columns.** The docstring says "Two draw on Ember alone ... and are taken" and then names "The third Ember-only column". The codebook holds three columns sourced from Ember alone.
2. **Why the other columns are left out.** Header line 3: "The dataset's other columns draw on sources the license record holds no verdict for and are not taken." One of them, electricity_carbon_intensity_gco2eq_per_kwh, draws on Ember alone and is left out for its unit.
3. **A country keyed as a region.** The docstring keys "owid_energy:<ISO 3166-1 alpha-3 code>, or owid_energy:<the region's name in snake case> for a region or aggregate". Kosovo, a country without an ISO code in the file, is `owid_energy:kosovo`.

## The session report against the table

Every figure of `SESSION_2126_REPORT.md` checked against the table, the saved files and the rerun cross-check holds: 12,406 rows; demand 1990 to 2025, 6,378 rows; emissions 2000 to 2025, 6,028 rows; 239 countries and regions; last modified 30 September 2026; 130 columns, three of them Ember's alone; the 9.1 MB file; United States demand 4,404,830,000 MWh in 2024 and 0.998 to 1.000 of EIA's; Canada 1.019 to 1.071; Mexico 0.875 to 1.070; emissions 1.015 (2015) to 1.096 (2024). Its reading that "the gap widens" holds from end to end, not year by year (2021 and 2022 sit below 2020). None found that does not hold.

Acted on in session 2129: the docstring now says three columns draw on Ember alone and two are taken, and names Kosovo's key; the header now says the carbon intensity was left for its unit; the table was written again offline, its rows unchanged.

## What it does not hold

- Generation by fuel, capacity, carbon intensity, or any column of the dataset drawn on the Energy Institute, population series or historical sources.
- Months or hours.
