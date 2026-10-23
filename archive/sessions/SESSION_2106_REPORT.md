# Session 2106 report: oil and gas on public lands (BLM's oil and gas statistics), and chain 079's file

23 October 2026, from 21:13 UTC, on lab-desktop (the data machine), the first session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`, run by chain 057's agent (the owner's instruction for that run: run the file the queue step prints). Model spend USD 0. Pulls: www.blm.gov, 3 requests of 15 (the robots file in a call of its own, the statistics page, the workbook), and 3 to Supabase for the lock.

## Read these first

- **The next file first:** `queue/next/079-day-28-october-data-quakes-credits-rates-world-renewables.md` (sessions 2120 to 2133, machine: data), committed alone in the detached worktree `erw-c069q` and pushed with `HEAD:main` (`c24a284b`, 21:15 UTC); `git status -sb` showed nothing ahead. 079 was the next free number (060 to 078 and 080 to 088 taken); 2120 to 2133 were free. Its sources: the USGS's earthquake catalog (the induced earthquakes of Oklahoma and its neighbours), the IRS's residential energy credits by state, Berkeley Lab's retail price and cost trends, IRENA's capacity statistics, Our World in Data's energy dataset, and one of the session's choosing. Snapshots `q079-before` and `q079-after`: **0 differences** in all 25 pages (a queue file only; nothing a page reads).
- **One series table, `blm_oil_gas_statistics_annual`:** 12,500 rows, the 50 states BLM lists, fiscal years 2001 to 2025, the ten tables of BLM's workbook "All Fed O&G Statistics by Year by State" (FY 2025's, its sheets as of 1 October 2025): leases in effect, acres under lease, new leases issued, acres newly leased, producing leases, producing acres, applications for permit to drill approved, wells spud, producible and service well bores, and completions. ts_utc is the fiscal year's first day (FY 2025 begins 1 October 2024); x_fiscal_year keeps BLM's year. Federal only: BLM's notes say Indian leases and wells are not included.
- **Checked as read:** in every table and every year the states sum to BLM's total row, and each total equals the Summary sheet's; the total rows are checked and not kept. The workbook's address is read from the statistics page (the latest fiscal year's "All Fed" workbook), not written into the code.
- **A new unit, `acre` (Decision 63),** in `docs/datastandard.md` and the validator together. Chain 067's Decision 61 (`tCO2e`) is on its own branch, so this one is numbered after it; the write ran with the branch's validator copied in and main's put back.
- **The cross-check** (`runs/c069/s2106/cross.py`), against ONRR's federal onshore oil and gas produced in each state (`onrr_production_annual`, oil in barrels and gas at 6 Mcf a barrel, for ranking only): BLM's producing leases rank the states as ONRR's production does (Spearman 0.95 in 2015, 0.96 in 2020, 0.95 in 2024), the well bores at 0.93 to 0.94 and the wells spud at 0.77 to 0.81. New Mexico, Wyoming, Colorado, North Dakota and Utah lead both. Nationally, BLM's wells spud fell from 5,343 in FY 2007 to 847 in FY 2016, while ONRR's federal onshore production rose from 701 to 1,366 million barrels of oil equivalent between 2007 and 2025. Idaho has ONRR production but no BLM well bores; Indiana, Maryland (and, earlier, Arizona and Tennessee) have well bores but no ONRR production. Both are small, and the note says so.
- **Registered:** the sector rule (`oil;gas`), the live set's hold and the release's storage hold; the release package's rows (1 table, 10 variables), `license_tables.csv` and `docs/licenses.md` (licenses check: 0 problems; release check: 0 differences). No row twice in sources, coverage, the archive manifest, `docs/coverage.md` or the license tables. The table's method note is for session 2116.
- **The test:** `tests/test_session2106.py` (5 tests, a workbook built in BLM's form): Table 3's "FY  2020" header with two spaces, the fiscal year's start, the four ways the run stops, the workbook's address found on the page, the unit, the sector and the holds.

## Errors

- **The chain's worktree was first made inside the main checkout** (`git -C erw worktree add erw-c069` read the path against `erw`); moved at once with `git worktree move` to `../erw-c069`, before any file was written in it.
- **The first trial stopped on Table 3's headers** ("FY  2020", two spaces); the year columns are now matched with one or more spaces, in the Summary as in the tables, and the test holds it.

## Decisions made without you

- **The branch cut from chain 066's** (`wip/2056-2069-data`, unlanded, its check run in progress), so chain 066's tables and verdicts are under this chain's; this session added no license read.
- **ts_utc the fiscal year's first day,** with x_fiscal_year kept, as the standard's period-start rule gives it.
- **BLM's total rows checked and not kept,** so a sum over states does not count them twice.
- **The table held public** (in the release's storage hold, as ONRR's are), its verdict BLM's of session 956 (read 159, may be public).

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/blm_oil_gas_stats.py`, `tests/test_session2106.py`, this report; on main, `queue/next/079-day-28-october-data-quakes-credits-rates-world-renewables.md`.
- Changed: `docs/datastandard.md`, `warehouse/validate/erw_validate.py`, `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/` (README, tables, variables).
- On the data machine only: `runs/c069/` (the probe, the seeding helper, the trial, the cross-check, the outputs).
