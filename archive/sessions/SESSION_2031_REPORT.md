# Session 2031 report: ethanol's and biodiesel's plants (EIA's biofuels capacity reports)

23 October 2026, from 18:53 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, unattended. Model spend USD 0. Pulls: 9 requests of 15 (below).

## Read these first

- **One table written, validated, archived, in coverage (sector products, public), in the release package, both holds:** `eia_biofuel_plants`, an entities table, one row a plant and year: 511 plant years, as of 1 January 2026 (189 fuel ethanol, 45 biodiesel and 19 renewable diesel fuel and other biofuels plants, from EIA's combined U.S. Biofuels Plant Production Capacity report of 24 September 2026) and as of 1 January 2025 (191, 48 and 19, from the three single-fuel reports of September 2025). Each row: the facility (2026) or the city (2025, whose sheets name no facility), the operator as EIA writes it, the state and PADD, and the capacity as published in million gallons a year and thousand barrels a day ("(s)", less than 0.5, kept). Four 2025 renewable diesel rows are refineries co-processing renewable feedstock and petroleum (EIA's footnote 1), marked `x_coprocessing` yes.
- **The plant list is published,** so the table is the entities table the chain file asked for, not a series by state. The capacities stay in `x_` columns: an entity's `capacity_mw` is power, and a plant's yearly gallons are not.
- **Two years only:** earlier issues sit under www.eia.gov's `/archive/`, which its robots file disallows; the chain's rule holds it.
- **The cross-check** against the tables EIA's own pages print: for 2025, all 51 states (with the District of Columbia) of the ethanol and the biodiesel pages agree with the plants summed by state, in plants and in MMgal/yr. For 2026, every PADD's plant counts agree for all three fuels; the capacity in Mb/d computed once from the plants' MMgal/yr agrees within 1 Mb/d (PADD 2's ethanol 1,137 against 1,136; the U.S. total 1,203 against 1,202 for ethanol and 129 against 128 for biodiesel), which is EIA's rounding of each plant's figure.

## The pulls

1. `www.eia.gov/robots.txt` (read 202): disallows `/archive/` and site machinery. 2. The fuel ethanol capacity page. 3. The biodiesel capacity page. 4. The combined biofuels capacity page. 5. The renewable diesel capacity page. 6 to 9. The four workbooks, saved in `warehouse/raw/eia_biofuels_capacity/` and reused by the write (`--offline`).

The terms are EIA's (read 1, public).

## Decisions made without you

- **A plant's id is its place among its year, fuel and state** in EIA's workbook (`eia_biofuel:<year>:<fuel>:<state>:<n>`): EIA publishes no plant number, and a 2025 plant cannot be joined to its 2026 row without matching names, which the session did not do.
- **The 2025 respondents' footnote mark ("1") taken off the name** and kept as `x_coprocessing`.
- **The years the workbooks are as of are the connector's arguments** (`--combined-year 2026`, `--single-year 2025`, the defaults), read from each page's title; the workbooks' own sheets do not all print it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_biofuels_capacity.py`, `tests/test_session2031.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (202), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c058/s2031/`, `runs/license_reads/s2031/`, `runs/s2031*`, `warehouse/raw/eia_biofuels_capacity/`.
