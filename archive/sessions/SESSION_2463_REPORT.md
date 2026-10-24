# Session 2463 report: Côte d'Ivoire's electricity from the regulator, ANARE-CI

24 October 2026, from 12:56 UTC, on lab-desktop (the data machine), a session of `queue/done/119-day-19-november-data-kyrgyzstan-cote-divoire-jamaica-laos.md`. Precheck passed (`runs/c119/precheck_2463.out`). Model spend USD 0.

Pulls: 8 requests of 15:
- **www.cienergies.ci's robots address:** the name does not resolve.
- **www.anare.ci:** its robots file and the home page, which redirects to anare.ci.
- **anare.ci:** its robots file, asked before any other path of that host, then the generation, peak and consumption pages and the installed capacity page.

The trial and the write ran offline.

## Read these first

- **CI-ENERGIES' host does not resolve,** so Côte d'Ivoire is taken from the regulator, ANARE-CI (not held; no chain took it).
- **Both of ANARE-CI's hosts have a robots file of one line,** "User-agent: *", which disallows nothing and names no AI agent.
- **The table:** `anare_cotedivoire_electricity_annual`, 361 figures, 1960 to 2020, internal (the pages state no terms of reuse). From the three tables of the "Open Data" pages:
  - gross generation by kind: hydro, thermal and isolated plants (`generation_isolated`, 56 years: blank in 1986 to 1990);
  - national consumption by voltage: low voltage (BT), and high and medium voltage (HT/MT);
  - the system's peak demand, MW.
- **Units:** generation and consumption are in GWh, as the pages' charts are titled ("Production brute d'electricite (GWh)", "Consommation nat (GWh)"); written as MWh.
- **Not taken:**
  - the installed capacity page, which draws a chart with no table and no data in the page;
  - a total, which the pages do not give and none is computed.
- **2019 is printed twice** in the generation table with the same figures, so it is taken once. A year twice with different figures stops the run.
- **Against `owid_ember_electricity_annual`'s Côte d'Ivoire demand,** 2016 to 2020: the three kinds' sum is 1.11 to 1.20 times Ember's demand (the country exports power). Consumption, net of losses, is 0.71 to 0.80 of it. 2020: generation 11,210 GWh, consumption 8,024, Ember's demand 10,140.
- **Registered:**
  - the sector rule (`power`), the live-set hold;
  - the license tables (licenses check: 535 tables, 0 problems);
  - the test, `tests/test_session2463.py` (3 tests).

## Errors

- **None in the code.** One request (CI-ENERGIES) found nothing.

## Decisions made without you

- **ANARE-CI over CI-ENERGIES,** since the latter's host does not resolve.
- **The data to 2020,** as the regulator publishes it; nothing newer was found within the ceiling.

## For Samuel's ruling

- **ANARE-CI's terms:** none stated; a word from the regulator would settle whether the table can be public.

## Files

- New: `warehouse/connectors/anare_cotedivoire.py`, `tests/test_session2463.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c119/s2463/`, `runs/license_reads/s2463/`, `warehouse/raw/anare_cotedivoire/`.
