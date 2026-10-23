# eGRID subregions: capacity, generation, emissions and resource mix (EPA)

Energy Research Warehouse (ERW), method note written in session 2009 (chain 056) for a table first written on 23 October 2026 (session 985, chain 055).

Tables: `egrid_subregions_annual`

## Publisher and address

U.S. Environmental Protection Agency (EPA), Emissions & Generation Resource Integrated Database (eGRID2023, revision 2), the subregion sheet SRL23 of the workbook `https://www.epa.gov/system/files/documents/2025-06/egrid2023_data_rev2.xlsx`, listed on `https://www.epa.gov/egrid/download-data`. Connector: `warehouse/connectors/egrid_subregions.py` (session 985), which reads the workbook `egrid.py` saves (`warehouse/raw/egrid/`).

## Vintage and revision

eGRID2023 (data year 2023), the workbook last modified 16 June 2025. A snapshot (no request while the saved workbook is on the machine).

## Shape and variables

Series, 540 rows: the 27 subregions times 20 variables, one year. `entity` `egrid:<subregion acronym>`; `ts_utc` 2023-01-01; `freq` P1Y; `geo` empty; `node` the subregion's name. Variables: nameplate_capacity (MW), net_generation (MWh), co2_emissions and co2e_emissions (tCO2: eGRID's short tons times 0.90718474), co2_rate, co2e_rate and co2_rate_nonbaseload (kgCO2/MWh: eGRID's lb/MWh times 0.45359237), and share_coal, share_oil, share_gas, share_nuclear, share_hydro, share_biomass, share_wind, share_solar, share_geothermal, share_other_fossil, share_other_unknown, share_renewables and share_nonrenewables (ratio: the resource mix as a fraction). 4,191.0 TWh and 1,458.5 million tCO2 in all.

## Reading the sheet

- A field not in the sheet, or a subregion given twice, stops the run; eGRID's "--" has no row. Nothing is filled.

## License

Public: a work of the U.S. government (EPA; `license_verdicts.csv`).

## Cross-checks (sessions 985 and 2009)

- Against `egrid_power_plants` (the same workbook's plant sheet) summed by subregion: net generation, CO2 and nameplate capacity within 0.5 percent in all 27 subregions; the totals 4,191.0 TWh and 1,458.5 million tCO2 both ways.
- Session 2009, against the code: `FIELDS` gives the variables, units and factors above; the counts computed from the rows.

## What it does not hold

- eGRID's state, balancing authority, NERC region and U.S. sheets, the other pollutants as their own series, and earlier eGRID years.
