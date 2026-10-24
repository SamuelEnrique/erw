# Session 2252 report: Poland's power balance (PSE), and chain 103 written

24 October 2026, from 03:34 UTC, on lab-desktop (the data machine), the first session of `queue/done/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`. Chain 059's agent took the file when chain 097 landed, under the owner's instruction for this run (run the file the queue step prints). Model spend USD 0.

Pulls: 10 requests of 15:
- api.raporty.pse.pl's robots address (HTTP 404, the app's page) and www.pse.pl's robots file, each in a call of its own;
- the API's root (404), its OData metadata address (404), the app's script bundle (for the reports' labels) and its OpenAPI description;
- one day of the report as a probe;
- three calendar years (2024, 2025 and 2026 to date).

The trial and the write ran offline. Also Supabase, for the locks and the archive.

## Read these first

- **The next file first:** `queue/next/103-day-6-november-data-south-africa-chile-colombia-taiwan.md` (sessions 2266 to 2279: Eskom, Chile's Coordinador Electrico Nacional, Colombia's XM, Taipower) was written, committed alone and pushed to main (`febc55cd`) before any other work, with snapshots. The site answered 402 on both sides.
  - 103 was the next free number on main and the running branches.
  - Mexico's CENACE was not chosen: chain 068 found it reachable only through a form.
  - Chain 101's agent has since reported that Eskom's portal reserves its data, and that Taipower's files are reachable only through data.gov.tw, whose robots file answered 500. Session 2265 updates the file with both (`runs/c102/q103_updates.md`).
- **One series table, `pse_poland_balance_15min`:** 909,219 figures, Poland's power balance a quarter hour from PSE's report his-wlk-cal ("Wielkosci podstawowe"), from 21:45 UTC on 13 June 2024 (the report's first period) to 21:45 UTC on 23 October 2026, in MW. The 14 variables are:
  - demand;
  - the scheduled units' generation (total, JGw 1 and 2, storage JGm 1 and 2 and its charging, wind and solar JGz 2, JGa);
  - the units outside the balancing market;
  - wind and solar;
  - the cross-border exchange balance, parallel and non-parallel.

  Each field is named by PSE's own English label, found in its reports app's script bundle. The API publishes no metadata.
- **The times:** each figure is keyed by PSE's UTC period. The local days of the clock changes have 92 and 100 quarter hours, and PSE's local stamps repeat ("02a") where the clock goes back. No UTC period is given twice.
- **Not taken:**
  - the business day in progress at retrieval (96 quarter hours, which PSE lists empty ahead);
  - PSE's jgo, jgz1 and jgz3, empty in every year;
  - the blank figures, counted in the header;
  - prices (PLN).
- **One request returns a whole year** (Data API builder, `$first=40000`). The connector stops if an answer fills its page.
- **The cross-check** (`runs/c102/s2252/cross.py`, months with all their quarter hours):
  - against Eurostat's monthly figures for Poland (chain 099's `eurostat_electricity_monthly`): demand 0.94 to 1.13 of the supply available for the internal market (median 1.04), solar 0.88 to 1.41 (median 1.03), wind 0.58 to 1.04 (median 0.93; March 2026's 0.58 is the outlier);
  - PSE's 2025 demand is 158.4 TWh, 91 percent of Ember's 174.3 TWh. PSE's is the transmission system's demand, without the generation used where it is made.
- **License: internal** until the licenses' round (session 2257) reads PSE's terms. Neither the API nor its app names any terms.
- **Registered:** the sector rule (`power`), the live-set hold, the license tables (licenses check: 0 problems). No row is given twice. The test is `tests/test_session2252.py` (4 tests).

## Errors

- **The first trial stopped on a figure in jga,** which the probe of 2024 had shown empty in all but one quarter hour. `jga` is taken.
- **Two requests went to addresses that do not exist** (the API's root and `$metadata`).

## Decisions made without you

- **Chain 102 taken beside chains 099 and 101,** under the owner's instruction for this run. Chain 101's agent had written the file, and was told.
- **Decisions 73 and 74 left to chain 101** (`degAPI`, `Btu/ft3`). This chain's start at 75.
- **The quarter hours kept as published,** not summed to hours.

## For Samuel's ruling

- None new. The live site's 402 stands (session 2189).

## Files

- New: `warehouse/connectors/pse_poland.py`, `tests/test_session2252.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On main: `queue/next/103-day-6-november-data-south-africa-chile-colombia-taiwan.md`.
- On the data machine only: `runs/c102/`.
