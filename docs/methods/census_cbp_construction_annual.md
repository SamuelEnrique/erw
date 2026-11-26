# The construction trades by state, a year, 2012 to 2023: establishments, employment and payroll (Census Bureau, County Business Patterns, NAICS 2362 and 238)

Energy Research Warehouse (ERW), method note written in session 10000 (chain 701) for a table first written on 26 November 2026, at data request 7 of `docs/state/data_requests_forecast.md` (chain 740's `/impact`: the construction earnings of a datacenter, payroll per employee of the trades that build it, by state).

Tables: `census_cbp_construction_annual`

## Publisher and address

U.S. Census Bureau, County Business Patterns (CBP), the state files: one zip a year, `https://www2.census.gov/programs-surveys/cbp/datasets/<year>/cbp<yy>st.zip`, the same files `census_cbp_hosting_annual` is read from (`docs/methods/census_cbp_hosting_annual.md`). Two industries are kept: NAICS 2362, nonresidential building construction (the files print it `2362//`), and NAICS 238, specialty trade contractors (`238///`), each state's line for all legal forms (`lfo` "-").

Connector: `warehouse/connectors/census_cbp_construction.py`: `[--offline] [--out-dir DIR] [--first YEAR] [--last YEAR]`. It reads the files `census_cbp_hosting.py` saved under `warehouse/raw/census_cbp_hosting/` (one copy of each document), so its first run on 26 November 2026 made no request; a year not saved there is asked once, two seconds apart, and saved in the same store. www2.census.gov's robots file names only some crawlers, none of them every reader.

## Shape and variables

Series, 3,672 rows: 51 areas (the 50 states and DC) for each of 12 years, 2 industries and 3 variables. `entity` `census_cbp_2362:<postal code>` or `census_cbp_238:<postal code>`, `node` the postal code, `geo` `US-<code>`, `freq` P1Y, `ts_utc` 1 January of the year, `market` blank. Variables:

- `establishments` (count);
- `employment` (count, the pay period including 12 March);
- `annual_payroll` (USD, the Bureau's thousands times 1,000).

Extra columns: `x_naics` (2362 or 238), `x_emp_noise` and `x_ap_noise` (the Bureau's noise flags: G low, H moderate, J high; D and S where a figure is withheld), `x_naics_vintage` 2017 (2012 to 2021) or 2022 (2022 and 2023).

## What it is not

- Payroll per employee (annual_payroll over employment) is the reader's division, not a column: the table holds what the Bureau printed.
- NAICS 238 is every specialty trade (electrical, plumbing, concrete, roofing and the rest), not only the trades on a datacenter's site; NAICS 2362 is all nonresidential building, not datacenters alone.
- A figure the Bureau withholds is kept as printed, with its flag. Nothing is filled.

## Checks

- The run of 26 November 2026 matched the 2023 file read by hand for Texas: NAICS 2362, 66,104 employees, payroll 6,200,944 thousand dollars, 3,980 establishments.
- The validator: pass (series, 102 entities, 3 variables, 2012 to 2023).

## License

May be public (the Census Bureau, as for `census_cbp_hosting_annual`; `warehouse/metadata/license_verdicts.csv`); its name is not to imply endorsement. Cite the U.S. Census Bureau, County Business Patterns.
