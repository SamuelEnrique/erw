# County population, and each county's balancing authority and EIA region

Energy Research Warehouse (ERW). Session 7802, chain 401 part C, tables 4 and 5. Internal tier: registered, validated, archived and in coverage; read by no page and not in the live set. Public data (U.S. Census Bureau, U.S. Energy Information Administration).

## `census_county_population` (series)

- Entity `census:county:<state FIPS><county FIPS>`, five digits. Unit `count`.
- `population_census_2020`, `ts_utc` 2020-04-01: the 2020 census population as the Bureau's 2010 to 2020 intercensal county files print it (`YEAR` 12, "4/1/2020 Census population", from the 2020 Modified Age and Race Census file).
- `population_estimate`, `ts_utc` 1 July of each year, `freq` P1Y: 2018 and 2019 from the same intercensal files (`YEAR` 10 and 11); 2020 to 2025 from the vintage 2025 county totals (`POPESTIMATE2020` to `POPESTIMATE2025`). `x_product` says which. The two products are as published: the intercensal estimates are on 2020 boundaries and consistent with the 2020 census; vintage 2025 is the current series from the 2020 estimates base. They are not spliced or adjusted, so a reader comparing 2019 with 2020 compares two products.
- Connecticut: vintage 2025 counts its nine planning regions (09110 to 09190), the intercensal files its eight former counties (09001 to 09015). Each is kept under its own code; neither is mapped onto the other.
- Files: `https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/intercensal/county/asrh/cc-est2020int-agesex-<state FIPS>.csv` (the 50 states and the District of Columbia; the file layout is `CC-EST2020INT-AGESEX.pdf` on the same server) and `https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/counties/totals/co-est2025-alldata.csv`. The robots file of www2.census.gov refuses no request of this kind and names no AI agent (read 18 November 2026). api.census.gov answered the robots request with a firewall page and was not used.

## `eia_county_region` (entities)

Each county of the lower 48 and the District of Columbia (every code `census_county_population` holds there), with its balancing authority and EIA region. Read from tables the warehouse holds; no request is made.

- **Which utilities serve a county:** EIA-861's Service Territory sheets as `utility_service_territories` holds them (data year 2025). EIA gives no share of a county and no boundary; a utility serves a county when EIA lists the pair.
- **Each utility's balancing authority:** its `x_ba_code` in that state in EIA-861's sales file and delivery-only file (`eia861_utility_sales` and `eia861_delivery_only`, data year 2025). The delivery-only file matters: the wires utilities of competitive areas (CenterPoint in Houston, Oncor in Dallas) file there and not in the sales file.
- **One balancing authority:** that one. **More than one:** the county is marked shared (`x_shared` Y) and every one is listed in `x_bas` with its serving utilities' customers in the state and how many utilities.
- **The primary (the rule that was taken):** the balancing authority whose serving utilities have the most total retail customers in the state, counting parts A (bundled) and C (delivery) of EIA-861, or the utility's other parts where it files neither; ties by the code. Statewide customers stand in for the county's load because EIA gives no county split; a large utility serving a sliver of a county can win it. **The other rule that was open:** the balancing authority with the most serving utilities in the county, kept in `x_ba_by_count` for a reader who prefers it. Recorded under "Decisions made without Samuel" in session 7802's report.
- **The region:** the primary balancing authority's region in the newest EIA-930 six-month BALANCE file (`Region`); `x_regions` lists every listed balancing authority's region.
- **County names:** EIA-861 writes a county's name ("Anderson", "Baltimore City"); it is matched to the Bureau's ("Anderson County", "Baltimore city") after both are read without accents, lowercased, with "county", "parish", "borough", "census area", "municipality" and "city and borough" dropped, "saint" read as "st", and points, apostrophes, hyphens and spaces removed. A territory row that matches no county of its state is counted in the header and listed in the run log, never guessed. On 18 November 2026 one did not match: Virginia's "Bedford City", which became part of Bedford County in 2013.
- **A county with no balancing authority:** written, with `x_basis` saying why (EIA-861 lists no utility for it, or its utilities name none). Connecticut's planning regions are among them: EIA-861 lists the former counties.

## Build

    python warehouse/connectors/census_county_population.py
    python warehouse/derived/eia_county_region.py

Both under the data lock. Not in the daily run: the county estimates change once a year (a new vintage each spring) and EIA-861 once a year (each autumn).
