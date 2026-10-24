# Session 2357 report: queue file 112 first; Pakistan closed, North Macedonia's electricity in its place (MakStat)

24 October 2026, from 08:02 UTC, on lab-desktop (the data machine), the first session of `queue/done/110-day-12-november-data-pakistan-bangladesh-morocco-kazakhstan.md`. Chain 059's agent took it when chain 105 landed (the owner's instruction: run the file the queue step prints). Model spend USD 0.

Pulls: 14 requests of 15:
- **Pakistan:**
  - nepra.org.pk's robots address (a Cloudflare challenge);
  - ntdc.gov.pk's robots address (HTTP 404);
  - NTDC's home page and its application bundle;
  - a publications archive address, which answered with the application's page.
- **CPPA-G:** www.cppa.gov.pk's robots address (a maintenance page).
- **MakStat:**
  - makstat.stat.gov.mk's robots address (HTTP 404);
  - three listings of MakStat's PxWeb API;
  - the table's metadata, twice (the first trial stopped on a month label);
  - one JSON-stat query by POST.

## Read these first

- **Queue file 112 written first and pushed to main alone** (`fe31a8c2`, with snapshots on both sides; the site answers 402):
  - `112-day-13-november-data-sri-lanka-nigeria-ghana-jordan.md`, sessions 2371 to 2384;
  - its rules are file 110's, with the hosts chains 105 and 109 closed added;
  - the four countries were found neither held nor planned on main.
  - 112 was the next free number (110 taken, 111 the code machine's); 2371 to 2384 were free on main and on the running chains' branches.
  - Chains 108's and 109's agents were told, and agreed to keep their own choices off those countries.
- **Pakistan is closed to the reader:**
  - NEPRA answers a Cloudflare challenge;
  - NTDC's site is a script application whose downloads by GET are plans (its monthly economic despatch) and annual reports in PDF, and its publications archive address does not exist;
  - CPPA-G's site is down for maintenance.

  The file's rule replaces a closed source with another public one.
- **In Pakistan's place: North Macedonia, from the State Statistical Office's MakStat** (not held; no chain planned it).
  - **Table:** `makstat_macedonia_electricity_monthly`, 3,669 figures, January 2012 to July 2026, in MWh as published. Internal until the licenses' round reads the office's terms.
  - **Variables (21):** imports, exports, gross inland consumption, gross and net production in total and by kind of plant (thermal, CHP and autoproducers, hydro, solar, wind, biogas), the energy branch's own use, distribution losses, available for final consumption and households.
  - **Access:** the PxWeb API answers the data only by POST. As chain 106's Latvian connector does, the connector sends one JSON-stat query by POST after the metadata's GET, and saves both together for offline runs. (This chain's earlier reports said the reader could not send POST; the shared fetch helper cannot, but a connector can, as here.)
- **MakStat writes some months as `2019_09` and one with a Cyrillic letter (`2026М01`).** The connector accepts the three forms and stops on any other.
- **The checks:**
  - **Net production against Eurostat's monthly net production for North Macedonia** (`eurostat_electricity_monthly`, entity `eurostat_elec:MK`): median ratio 1.0000 over 127 months, 90 within 0.1 percent, the range 0.987 to 1.189.
  - **The plants against MakStat's totals:** one month is off, gross January 2016 by 2,382 MWh (named in the header).
  - **Values that cannot be right, kept as published:** gross inland consumption is negative in 13 months from September 2022 to September 2025, down to -60,362 MWh; they are named in the header. Net production of CHP and autoproducers' thermal plants is negative in 39 months, which is their own use above their output.
- **Registered:**
  - the sector rule (`power`), the live-set hold, the license tables (licenses check: 496 tables, 0 problems);
  - the test, `tests/test_session2357.py` (3 tests).

## Errors

- **The first trial stopped on MakStat's month labels** (one request spent on the metadata). They are now read in their three forms.
- **The first name, `makstat_north_macedonia_electricity_monthly`, was over the validator's 40 characters;** it is now `makstat_macedonia_electricity_monthly`.

## Decisions made without you

- **Pakistan replaced by North Macedonia,** as the file's rule allows.
- **A query sent by POST,** as chain 106's connector does.
- **Gross inland consumption's negative months kept as published,** and named.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/makstat_macedonia.py`, `tests/test_session2357.py`, this report. On main: `queue/next/112-day-13-november-data-sri-lanka-nigeria-ghana-jordan.md`.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c110/`, `runs/license_reads/s2357/`.
