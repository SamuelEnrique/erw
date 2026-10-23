# Session 2030 report: the renewable fuels' credits (EPA's RIN generation)

23 October 2026, from 18:41 UTC, on lab-desktop (the data machine), the third session of `queue/done/058-day-24-october-data-outages-fuels-mines-vehicles.md`, unattended. Model spend USD 0. Pulls: 9 requests of 15 (below).

## Read these first

- **Two tables written, validated, archived, in coverage (sectors products and carbon, public), in the release package, both holds:**
  - `epa_rfs_rins_monthly`: the RINs generated and the renewable fuel's batch volume in gallons, a month by D code (D3 cellulosic biofuel, D4 biomass-based diesel, D5 advanced biofuel, D6 renewable fuel, D7 cellulosic diesel, by the names EPA's fuel type file gives them), July 2010 to September 2026, 1,632 rows.
  - `epa_rfs_fuel_annual`: the same two figures a RIN year by D code and fuel category (ethanol, biodiesel, renewable diesel, biogas, renewable jet fuel and the rest, 32 fuels as EPA names them), 2010 to 2026, 568 rows.
- **The source:** the "Historical Monthly Data" CSV files of EPA's Public Data for the Renewable Fuel Standard page (from the EPA Moderated Transaction System). EPA re-issues each file every month with the whole history (`rindata_sep2026.csv` and `fuelproduction_sep2026.csv`, last modified 14 October 2026); the connector takes the newest link from each listing page, so the next run takes October's. The RIN generation page itself shows only an interactive dashboard (`edap.epa.gov`), which was not asked. EPA's bulk file API was not asked (no key).
- **A new unit, `gal`** (Decision 59), added to `docs/datastandard.md` and the validator together; until this chain lands, a write, a Method-cell run or an upload of these tables runs with the branch's validator copied in.
- **The cross-check** against `eia_oxygenate_production_monthly`'s U.S. fuel ethanol plant production (thousand barrels at 42 gallons): EPA's D6 volume a year is 0.92 to 1.00 of EIA's from 2011 to 2024 (2011 0.977, 2015 0.991, 2020 0.928, 2024 0.918) and 0.888 in 2025. D6 counts the renewable fuel that generated a RIN; ethanol produced and exported generates none, and the gap widens in the years exports grew. That reason was not tested here.
- **`test_session205`'s bound on the license record raised by 20** (chain 056's reads 168 to 174 and this chain's 196 to 205 passed it by one), with room for chain 057's reads at the merge.

## The pulls

1. `www.epa.gov/robots.txt` (read 205): disallows only site machinery, admin, user and search paths. 2. The RINs Generated Transactions page. 3. Public Data for the Renewable Fuel Standard. 4 and 5. The two listing pages (by fuel type, by month). 6 and 7. The two September 2026 files. 8 and 9. The connector's trial: the two listing pages again (the connector reads them fresh), the files reused.

The terms are EPA's (read 55, public).

## Decisions made without you

- **Two tables, not one:** the monthly file has no fuel; the fuel type file has no month.
- **The D codes' names from EPA's own file,** never a list typed into the connector; a code the file does not name stops the run.
- **The latest year kept, partial** (to September 2026), and said in both headers.
- **`runs/c058/write_table.sh` changed:** with `VALIDATOR=branch` the branch's validator now stays in through the coverage build, since `build_coverage.py` writes the validator's status into each row. The first write left `epa_rfs_rins_monthly`'s row "blocked (1 errors)" (main's validator does not know `gal`); `runs/c058/coverage_rows.sh` (new, under the data lock) rebuilt both rows with the branch's files, and both say pass.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/epa_rfs_rins.py`, `tests/test_session2030.py` (4 tests), this report.
- Changed: `docs/datastandard.md` (Decision 59), `warehouse/validate/erw_validate.py`, `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `tests/test_session205.py` (the bound), `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (205), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c058/s2030/`, `runs/c058/coverage_rows.sh`, `runs/license_reads/s2030/`, `runs/s2030*`, `warehouse/raw/epa_rfs_rins/`.
