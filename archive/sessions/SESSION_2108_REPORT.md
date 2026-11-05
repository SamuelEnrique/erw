# Session 2108 report: what households spend on energy (EIA's SEDS residential sector, in place of BEA)

23 October 2026, from 21:35 UTC, on lab-desktop (the data machine), a session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`. Model spend USD 0. Pulls: 12 requests of 15. These were apps.bea.gov's robots file; data.openei.org's robots file (404), LEAD's submission page, its data dictionary and two sizes asked by HEAD; api.eia.gov's robots address (403, no robots file); and 5 pages of EIA's API. Also 3 to Supabase for the lock.

## Read these first

- **BEA was not pulled:** apps.bea.gov's robots file disallows `/` and allows only some paths (`/api/`, `/iTable/`, `/regional/bearfacts/` and others), not `/regional/zip/`, where the SAPCE downloads are. BEA's API needs a UserID the ERW does not hold (no BEA key in the environment), and none was signed up for. **apps.bea.gov's `/regional/zip/` joins the hosts not asked**; session 2119 writes it into chain 079's rules.
- **DOE's LEAD Tool (data.openei.org submission 6219, CC BY 4.0) is a gap for a later chain, not taken:** households' energy spending and burden by income, tenure and building. But it comes as 52 state zips, and California's alone is 913 MB (Vermont's 28 MB), beyond this session's ceiling and the machine's memory rule. A later session can take it with a ceiling of about 60 requests, reading each zip from disk in chunks; its data dictionary was read (`runs/license_reads/s2108/`).
- **In their place, EIA's State Energy Data System, the residential sector. One series table, `eia_seds_residential_annual`:** 20,020 rows, 11 series for the 50 states, DC and the nation, 1990 to 2024. The series are households' energy expenditures in total and by source (electricity, natural gas, all petroleum, distillate fuel oil, HGL, kerosene, wood), the sector's consumption (TBtu) and average price (USD/MMBtu), and the resident population (a count). `eia_seds_state_energy` held only all sectors' expenditures; this table does not repeat its series. EIA's API answered in 5 requests.
- **The cross-check** (`runs/c069/s2108/cross.py`): SEDS's residential electricity expenditures against EIA-861's residential revenue summed to the state (`eia861_utility_sales`, every utility and part), 510 state-years from 2015 to 2024. The median ratio is 1.014, and SEDS is never below EIA-861 (5th percentile 1.000). The widest gap is South Dakota, about 1.33. That gap fits the utilities that file EIA-861's short form, which `eia861_utility_sales` does not hold and SEDS's estimates include; this session did not test that cause. In 2024 the nation's households spent USD 333.3 billion on energy: 244.4 on electricity, 63.6 on natural gas, 23.7 on petroleum and 1.6 on wood. The sources sum to the total, and the total is USD 980 per person. Spending per residential electricity customer is lowest in Ohio and Illinois, which are retail choice states. EIA-861 there probably counts a customer under both energy-only and delivery-only service, so per-customer figures there should not be read alone.
- **Values scaled by code, rounded to six decimals** (512.3 million dollars is 512,300,000, not 512,299,999.99999994); the test holds it.
- **Registered:** the sector rule (`power;gas;oil`), the live set's hold and the release's storage hold, the release package's rows, the license tables (licenses check 0 problems, release check 0 differences); no row twice. The test: `tests/test_session2108.py` (3 tests).

## Errors

- **A raw-save line written by mistake** into the connector's request function (the raw store records every request itself); removed before the trial.

## Decisions made without you

- **EIA's SEDS in place of BEA** (a public source on a host the ERW already reads, the same question: households' energy spending by state), and LEAD left for a session with room for it.
- **From 1990,** as `eia_seds_state_energy`, not 2010.
- **A table of its own,** not more series in `eia_seds_state_energy`, which pages may read.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_seds_residential.py`, `tests/test_session2108.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c069/s2108/`.
