# Session 2363 report: Europe's oil a month (Eurostat), a source of the session's own choosing

24 October 2026, from 08:45 UTC, on lab-desktop (the data machine), a session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Model spend USD 0.

Pulls: 8 requests of 20:
- **Serbia:** data.stat.gov.rs's robots address (HTTP 404) and its database's English home page.
- **Eurostat:**
  - ec.europa.eu's robots file;
  - the query for nrg_cb_oilm (answered with a job key);
  - the NRG_BAL codelist;
  - the job's status, twice;
  - its data, once (156 MB).

The trial and the write ran offline.

## Read these first

- **Why Eurostat's monthly oil supply:**
  - The ERW held Eurostat's monthly electricity, its gas imports, and since chain 108 its monthly gas balance, but not oil.
  - EIA's petroleum tables cover the United States only.
  - **Serbia was looked at first:** its statistics office's database holds energy only as annual statistics, and Eurostat's monthly electricity table already holds Serbia, so it was set aside.
- **One series table, `eurostat_oil_monthly`:** 457,009 figures, public.
  - **Coverage:** January 2016 to September 2026, 35 European countries and the EU27 aggregate.
  - **Products, seven of the file's 33:** crude oil, oil products in all, motor gasoline, gas oil and diesel oil, kerosene-type jet fuel (each without its biofuel portion), fuel oil and LPG.
  - **Flows:** every one the file gives, 26 balance items: imports, exports, indigenous production, refinery intake and output, gross inland deliveries, stock change, bunkers, road transport and the rest.
  - **Unit:** `t`, Eurostat's thousand tonnes times 1,000 (Decision 56).
  - **License:** Eurostat's verdict is on record, reuse with acknowledgement.
- **The United Kingdom is left out** by Eurostat's terms, as in the other Eurostat tables, and named in the header.
- **Eurostat's extract is too large to be answered at once.** Eurostat queues it and returns a job key; the connector asks the status and then the data from Eurostat's asynchronous API by GET. The extract is saved for offline runs.
- **`vintage` is empty.** Eurostat's "LAST UPDATE" is printed as `23/10/26 23:00:00`, its clock unstated, so it goes in the header instead.
- **The checks:**
  - **Members against the EU:** crude oil imports summed over the members that report equal Eurostat's EU27 figure in all 126 months; all 27 report in 107 of them (corrected by session 2366: Eurostat's EU row is the reporting members' sum).
  - **Scale:** the EU imported 469.2 Mt of crude oil in 2024.
- **Registered:**
  - the sector rule (`oil`), the live-set hold;
  - the release package's held list and its rows in `docs/redivis/release-v1/` (the release check passes);
  - the license tables (licenses check: 505 tables, 0 problems; flag and verdict agree, public);
  - the test, `tests/test_session2363.py` (3 tests).
- **Not in the Stanford draft yet:** session 2366 uploads it.

## Errors

- **The first trial put Eurostat's "LAST UPDATE" in `vintage`,** which the validator warned is not ISO 8601. It is now empty, and the date is in the header.
- **The write's metadata patch did not apply** (`runs/c110/s2363/write.out` ends "fail=1": the main checkout lagged main); the table's own rows were put in by `runs/c102/add_own_rows.py` (added by session 2366).

## Decisions made without you

- **Eurostat's monthly oil supply,** seven products, after Serbia was found to hold only annual figures.
- **The other 26 products** (the parts of these and the biofuel shares) not taken: they would have quadrupled a 157 MB table.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eurostat_oil_monthly.py`, `tests/test_session2363.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`;
  - `docs/redivis/release-v1/`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c110/s2363/`, `runs/license_reads/s2363/`, `runs/s2363_*`.
