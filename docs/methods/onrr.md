# Federal and Native American production and revenue (the Office of Natural Resources Revenue)

Energy Research Warehouse (ERW), method note written in session 960 (chain 054) for tables first written on 23 October 2026.

Tables: `onrr_production_monthly`, `onrr_production_annual`, `onrr_revenue_monthly`

## Publisher and address

U.S. Department of the Interior, Office of Natural Resources Revenue (ONRR), Natural Resources Revenue Data, downloads (`https://revenuedata.doi.gov/downloads/`), three CSV files served from `https://revenuedata.onrr.gov/downloads/`: `monthly_production.csv`, `calendar_year_production.csv`, `monthly_revenue.csv`. Connector: `warehouse/connectors/onrr.py` (session 951), one `--table` each or all three. The site is drawn in the browser; the files' names were read from its page chunks (session 951's report). Both hosts' robots files disallow only `/patterns/`.

## Vintage and revision

The three files were last modified by ONRR on 21 October 2026 and retrieved on 23 October. Snapshots: each run replaces its table whole (ceiling three requests; `--offline` reads the saved files). ONRR revises recent months; the monthly production file is revised later than the annual (session 951's cross-check).

## Shape and variables

Series. `x_*` keep ONRR's own fields: land class and category, state, county, FIPS code, offshore region, and in the revenue table the revenue type, mineral lease type, commodity and product.

- `onrr_production_monthly` (2,264 rows, 8 series, January 2003 to July 2026): `entity` `onrr_production:<federal|native_american>:<onshore|offshore>:<oil|gas|coal>`; `variable` production; `unit` bbl, Mcf or short_ton (ONRR's tons); `freq` P1M; `geo` US. Native American lands are onshore only.
- `onrr_production_annual` (15,068 rows, 830 series, 2003 to 2025): federal lands by county or offshore region (Alaska, Gulf of America, Pacific), the energy products only: oil, gas, coal and three of its kinds, and geothermal electricity (ONRR's kilowatt hours over 1,000, as MWh). `entity` `onrr_production:<class>:<category>:<FIPS code>_<county name>` or `:<offshore region>`, then `:<product>`; `freq` P1Y; `geo` US-<state>, empty for offshore rows and rows ONRR gives no state.
- `onrr_revenue_monthly` (413,554 rows, 5,047 series, January 2003 to August 2026): `entity` `onrr_revenue:<class>:<category>:<place>:<revenue type>:<lease type>:<commodity>:<product>`, `none` where ONRR leaves a part empty; `variable` revenue; `unit` USD; `freq` P1M; `geo` US-<state> or empty (20,303 rows: offshore, not tied to a lease, or Native American revenue ONRR gives no state for). Royalties are 245 billion dollars of the 298 held, bonuses 43, rents 5.

## Reading the files

- Headings must be as read; a commodity of the monthly file not in the map stops the run; a key given twice stops it.
- One FIPS code can carry two of ONRR's county names (Kenai (Post) and Kenai (Pre), 02122): the name is part of the key, so they stay two places.
- The annual file's minerals (salt, potash, soda ash, gold and the rest) and geothermal's direct use and steam are left out, being in units the ERW has no word for and outside its energy scope.
- A negative revenue (29,103 rows) is ONRR's adjustment of an earlier month and is kept. Nothing is filled.

## License

A work of the U.S. Department of the Interior: "Generally, materials produced by federal agencies are in the public domain and may be reproduced without permission" (the Department's notice, read 159 of `license_reads.csv`; verdict "may be public", session 956). Cite ONRR, Natural Resources Revenue Data.

## Cross-checks (sessions 951 and 960)

- ONRR's annual federal offshore Gulf of America oil and gas against `boem_ogor_lease_production_monthly` summed by year: within 0.5 percent in all 23 years (2024: 656.2 million barrels in both). ONRR's monthly offshore figure also holds the Pacific and Alaska.
- Federal onshore coal summed from the annual file equals the monthly file's within 0.04 percent in every year; oil and gas within 1 percent in 21 of 23 years.
- Session 960, against the code and the tables: the counts above computed from the rows; the eight monthly series are the eight ONRR gives (no Native American offshore).

## What they do not hold

- Production by lease or by company, and revenue by company (ONRR's "federal revenue by company" is a separate download, not taken).
- Disbursements to states, tribes and funds (ONRR's disbursement files), and production by disposition.
- The minerals and geothermal direct use (above).
