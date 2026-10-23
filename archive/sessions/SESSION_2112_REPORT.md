# Session 2112 report: the 1603 grants (the Treasury's payments in lieu of tax credits)

23 October 2026, from 22:29 UTC, on lab-desktop (the data machine), a session of `queue/done/069-day-27-october-data-public-lands-sunlight-spending-streams.md`. Model spend USD 0. Pulls: home.treasury.gov, 3 requests of 15 (the robots file in a call of its own, the program page, the awardee list), and 3 to Supabase for the lock.

## Read these first

- **One events table, `treasury_1603_awards`:** 10,012 awards, USD 26,157,401,498 funded, from 1 September 2009 to 10 November 2017. The source is the Treasury's awardee list "as of March 1, 2018" (`/system/files/216/Website-Awarded-as-of-3.1.18.xlsx`, its address read from the program page). One row an award: the business as the Treasury names it (`parties`), the state or territory (`entity_ids` and `x_state`, 54 of them with DC, PR, GU and VI), the technology as named (`x_technology`), the amount funded (`x_funded_usd`) and the award date. `price` stays empty (it is per MWh in the standard), as `doe_grip`'s awards are held. `event_id` is a hash of the row's five fields, so it is stable.
- **The cross-check:** the awards sum to the list's Total row exactly (USD 26,157,401,498), and the program page reports "over $26 billion". The page also counts "109,766 clean energy projects", while the list holds 10,012 awards: an award can cover several projects, and the header says so. By technology, wind took USD 12.89 billion in 434 awards and solar electricity USD 9.56 billion in 8,050. By year the peak was 2012 (USD 6.40 billion). California led the states (USD 7.05 billion), then Texas (1.99). The median award is USD 85,030.
- **One award date is an Excel serial number** in the Treasury's file (40940, Shemron Properties LLC, New York), read as 1 February 2012 and counted in the header.
- **The license is not settled** (session 2111: the Treasury's site states no terms of reuse), so the table is held from the Stanford draft and the release, as the Drought Monitor's is. The question is under session 2111's "For Samuel's ruling".
- **Registered:** the sector rule (`power;deals`), the live set's hold and the release's storage hold, the release package's rows (held), the license tables (licenses check 0 problems, release check 0 differences); no row twice. The test: `tests/test_session2112.py` (4 tests).

## Errors

- **The test's expected date was wrong by a day** (I took serial 40940 for 31 January 2012; it is 1 February, as 40909 is 1 January); the connector was right, the test corrected.

## Decisions made without you

- **The amount in an x column, `price` empty,** as `doe_grip.py` does.
- **The table written while its license is unsettled,** held from the draft and the release until a ruling.

## For Samuel's ruling

- None new (session 2111's question on the Treasury covers it).

## Files

- New: `warehouse/connectors/treasury_1603.py`, `tests/test_session2112.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c069/s2112/`.
