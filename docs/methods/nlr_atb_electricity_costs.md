# NLR (formerly NREL) Electricity Annual Technology Baseline: projected costs by technology and year

Energy Research Warehouse (ERW), method note written in session 675 (chain 043) for tables first written on 21 or 22 October 2026.

Tables: `nlr_atb_electricity_costs`

Connector: `warehouse/connectors/nlr_atb_costs.py` (session 487, the owner's instruction of 21 October 2026).

## Publisher and report

National Laboratory of the Rockies (NLR, formerly NREL), 2025 Electricity Annual Technology Baseline (ATB) v1.0.0. Source code `nlr:atb_electricity`; the report's page is `https://atb.nrel.gov/electricity/`. The connector reads the ATB's flat file in the Open Energy Data Initiative's public bucket:

- the bucket's listing, `https://oedi-data-lake.s3.amazonaws.com/?list-type=2&prefix=ATB/electricity/parquet/`, to find the newest year and version;
- the file, `https://oedi-data-lake.s3.amazonaws.com/ATB/electricity/parquet/2025/v1.0.0/ATBe.parquet` on 21 October 2026.

## Vintage and revision rule

- The newest ATB the bucket lists: the highest year, then the highest version. A year whose dollar year is not recorded in the connector stops the run (only 2025, in 2023 dollars, is recorded), so a new ATB is read only after a person records its dollar year.
- `vintage` is the file's Last-Modified time, 2026-09-01T22:22:25Z; retrieved 2026-10-21. `x_atb_version` is "2025 v1.0.0".
- Written with `ip.write_snapshot`: a run replaces the whole table. A new ATB year replaces the 2025 rows; the year is also in the entity id (`nlr_atb_2025:`).
- Ceiling: two requests (the listing, asked fresh each run, and the file; a file already in `warehouse/raw/nlr_atb_costs/` is reused).

## Shape and columns

Series shape, with the ATB's own fields after the standard columns: `entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_technology, x_techdetail, x_techdetail2, x_resourcedetail, x_scale, x_scenario, x_display_name, x_default, x_maturity, x_case, x_crp_years, x_dollar_year, x_atb_version`.

- `entity`: `nlr_atb_2025:<technology>:<detail>:<scenario>`, lower case: the ATB's technology; its techdetail, techdetail2, resourcedetail and scale joined (a detail that repeats an earlier detail is left out); and its scenario (advanced, moderate, conservative). Example: `nlr_atb_2025:biopower:dedicated:biopower:utility:advanced`.
- `ts_utc`: the projection year's 1 January, 2023 to 2060; `freq` `P1Y`; `geo` `US`; `node` the ATB's display name.
- Variables and units (rows in the table):
  - `capex`, `USD/kW` (19,844);
  - `occ`, overnight capital cost, `USD/kW` (19,844);
  - `fixed_om`, `USD/kW-year` (20,528);
  - `variable_om`, `USD/MWh` (5,399);
  - `fuel`, `USD/MWh` (393);
  - `lcoe`, `USD/MWh` (14,496);
  - `capacity_factor`, `ratio` (14,496).
- 95,000 rows, 20 technologies, 547 entities. The technologies, as the ATB names them: Biopower, CSP, Coal_FE, Coal_Retrofits, CommPV, Commercial Battery Storage, DistributedWind, Geothermal, Hydropower, LandbasedWind, NaturalGas_FE, NaturalGas_Retrofits, Nuclear, OffShoreWind, Pumped Storage Hydropower, ResPV, Residential Battery Storage, Utility-Scale Battery Storage, Utility-Scale PV-Plus-Battery, UtilityPV.

## Which rows of the ATB

The ATB's default view only, as session 312 read its workbook: the R&D cost case (no tax credits; `x_case` `R&D`) and a 30-year cost recovery period (`x_crp_years` 30). The rows repeat for each recovery period wherever the value does not depend on it (CAPEX, O&M), so one period is enough, and 30 years exists for every technology. Values are in the ATB's dollar year, 2023 dollars (`x_dollar_year`), as the ATB gives them.

## License

ERW verdict: public. Header: "License: public with credit (NLR data terms; cite "NLR (formerly NREL), 2025 Electricity Annual Technology Baseline")." The connector notes NLR's terms were read on 19 October 2026 and kept in `warehouse/raw/nlr_atb/terms/`: use and copy without fee, the notice kept and DOE/NLR credited.

## Cross-check

None in the connector. An (entity, variable, ts_utc) given twice stops the run, and so does a file with no R&D row at 30 years.

## What it does not hold

- No cost case other than R&D (so no case with tax credits) and no recovery period other than 30 years.
- Nothing converted, filled or interpolated; a blank value has no row.
- No other ATB metric: only CAPEX, OCC, fixed O&M, variable O&M, fuel, capacity factor and LCOE.
- No earlier ATB edition; the table is one edition at a time.
