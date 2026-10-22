# EPA eGRID: every US power plant's capacity, generation, emissions and emission rates

Energy Research Warehouse (ERW), method note written in session 674 (chain 043) for a table first written on 21 October 2026.

Tables: `egrid_power_plants`

Connector: `warehouse/connectors/egrid.py` (session 486, the owner's instruction of 21 October 2026).

## Publisher and report

U.S. Environmental Protection Agency (EPA), Emissions & Generation Resource Integrated Database (eGRID2023), plant sheet PLNT23.

- Page: `https://www.epa.gov/egrid/download-data`
- File: `https://www.epa.gov/system/files/documents/2025-06/egrid2023_data_rev2.xlsx`

The connector reads the page and takes the newest `egrid<year>_data*.xlsx` it links, not the `_metric` workbook (the same data in metric units). It reads the sheet `PLNT<yy>`, whose first row holds eGRID's long names and second row its codes. Ceiling: two requests (the page and the workbook); a workbook already in `warehouse/raw/egrid/` is reused.

## Vintage and revision rule

One data year, the newest eGRID the page links: eGRID2023, data year 2023 (`vintage` eGRID2023, `data_year` 2023). The table is written by `write_snapshot`: a later run replaces the whole table, so when EPA publishes a newer eGRID the table moves to that year and the earlier year is not kept in it. The connector has no year option.

## Shape

Entities (`docs/datastandard.md`), one row per plant: 12,612 plants, 1,303,569 MW of nameplate, 4,191.0 TWh of net generation (the header's totals).

- `entity_id`: `egrid:<ORISPL>`, the plant's DOE/EIA ORIS code (the same number as `eia860:<plant id>` in the EIA-860 tables).
- `entity_type` plant; `name` PNAME; `geo` US-<state>; `lat`, `lon` LAT, LON; `capacity_mw` NAMEPCAP, nameplate in MW; `status` and `status_date` empty (eGRID lists the plants of its data year and gives no status); `operator` the utility's name (UTLSRVNM).
- eGRID's own fields, the ERW's name then eGRID's code: `data_year` YEAR; `plant_id` ORISPL; `state` PSTATABB; `county` CNTYNAME; `fips_state` FIPSST and `fips_county` FIPSCNTY (zero-padded to 2 and 3 digits); `transmission_owner` OPRNAME; `utility_id` UTLSRVID; `sector` SECTOR; `balancing_authority` BACODE; `balancing_authority_name` BANAME; `nerc_region` NERC; `egrid_subregion` SUBRGN; `iso_rto` ISORTO; `units` NUMUNT; `generators` NUMGEN; `primary_fuel` PLPRMFL; `primary_fuel_category` PLFUELCT; `coal_flag` COALFLAG; `chp_flag` CHPFLAG; `capacity_factor` CAPFAC.
- Annual quantities, units as eGRID gives them: `heat_input_mmbtu` PLHTIAN (MMBtu); `net_generation_mwh` PLNGENAN (MWh); `nox_tons` PLNOXAN, `so2_tons` PLSO2AN, `co2_tons` PLCO2AN, `co2e_tons` PLCO2EQA (short tons); `ch4_lbs` PLCH4AN, `n2o_lbs` PLN2OAN, `hg_lbs` PLHGAN (pounds).
- Rates: `nox_rate_lb_mwh` PLNOXRTA, `so2_rate_lb_mwh` PLSO2RTA, `co2_rate_lb_mwh` PLCO2RTA, `co2e_rate_lb_mwh` PLC2ERTA (lb/MWh); `heat_rate_btu_kwh` PLHTRT (Btu/kWh).
- Generation by fuel, MWh: `gen_coal_mwh` PLGENACL, `gen_oil_mwh` PLGENAOL, `gen_gas_mwh` PLGENAGS, `gen_nuclear_mwh` PLGENANC, `gen_hydro_mwh` PLGENAHY, `gen_biomass_mwh` PLGENABM, `gen_wind_mwh` PLGENAWI, `gen_solar_mwh` PLGENASO, `gen_geothermal_mwh` PLGENAGT, `gen_other_fossil_mwh` PLGENAOF, `gen_other_purchased_mwh` PLGENAOP.

A field the reader needs and cannot find stops the run, and so does a plant code given twice.

## License

ERW verdict: public (`docs/licenses.md`). The header's License line: public, a work of the U.S. government; cite "U.S. EPA, eGRID2023". The connector records EPA's sentence that data it produces is by default in the public domain unless otherwise specified (read in session 311, record 55 of `license_reads.csv`).

## Cross-check

None in the connector. Session 486's report: net generation 4,191.0 TWh against EIA's 2023 figure of about 4,178; CO2 1,607.7 million short tons (about 1,458 million metric); 97.5% of eGRID's plant codes are in `eia860m_operating_generators`. Session 510 compared `eia923_plant_fuel_annual` for 2023 with this table plant by plant: of the 10,609 plants over 1 GWh in both, a median ratio of 1.0000 and 99.9% within 1%.

## What it does not hold

- Emissions are EPA's: measured (EPA's Clean Air Markets data) or estimated by EPA from fuel use and emission factors. The `*_src` fields that say which, plant by plant, are not taken.
- Plant status and dates: eGRID gives none.
- Units and generators one by one, and eGRID's other sheets (state, subregion and balancing authority totals): only the plant sheet is read.
- More than one data year (see the revision rule).
- A cell eGRID leaves blank is empty here; nothing is filled.
