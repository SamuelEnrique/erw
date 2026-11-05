# Session 2295 report: India's power supply position (the Central Electricity Authority, in place of Grid-India)

24 October 2026, from 05:32 UTC, on lab-desktop (the data machine), a session of `queue/done/105-day-8-november-data-mexico-india-peru-korea.md`. Model spend USD 0.

Pulls: 12 requests of 15:
- grid-india.in's and www.grid-india.in's robots addresses (each reset the connection);
- cea.nic.in's robots file (allows every path);
- a wrong address (HTTP 404);
- CEA's home page and its Power Supply Position (Energy) page;
- six March reports (PDF).

The trial and the write ran offline.

## Read these first

- **Grid-India is closed:** both of its hosts reset the connection at their robots files, so nothing else was asked.
- **India's figures come from the Central Electricity Authority instead.** Its monthly Energy Power Supply Position reports are PDFs (no Excel is offered). Each March report's second block gives the fiscal year's totals by state, region and All India.
- **One series table, `cea_india_psp_annual`:** 777 figures, fiscal years 2020-21 to 2025-26, for 49 states, regions and All India. It holds energy required, supplied and not supplied, in MWh (CEA's MU of net energy times 1,000).
  - Names printed over two lines are joined, and "Others" carry their region.
  - Places CEA marks "#" (Lakshadweep and Andaman-Nicobar; the second added by session 2353) are kept but left out of their region's sum, as CEA leaves them.
- **The checks:**
  - **The regions sum to All India** in every year, to CEA's rounding.
  - **A region's line can hold more than its listed states.** CEA marks such regions "##". From 2022-23 to 2024-25 (corrected by session 2353: the earlier reports carry no ## mark) the consumption it does not show by state is folded into the region; 2025-26 lists it as "Others", entities drawing power directly from ISTS (since session 2353 their own `x_kind`, other_entities). The gaps are named in the header, up to 11,314 MU (the Western Region, 2024-25).
- **The cross-check** (`runs/c105/s2295/cross.py`):
  - All India's energy supplied grew from 1,271 TWh (2020-21) to 1,707 TWh (2025-26).
  - The shortfall fell from 0.38 percent to 0.03 percent.
  - CEA's figures are 81 to 85 percent of Ember's India demand for the calendar year the fiscal year starts in. CEA counts the grid's energy, net, and Ember counts more (captive generation, for one).
- **License: internal** until the licenses' round (session 2299) reads CEA's terms.
- **Registered:** the sector rule (`power`), the live-set hold, the license tables (licenses check: 0 problems). The test is `tests/test_session2295.py` (3 tests).

## Errors

- **The first trials stopped on two of CEA's conventions:** Lakshadweep left out of its region's sum (marked "#"), and regions holding more than their states (marked "##"). Both are now read as CEA prints them.
- **One request went to a guessed address,** and the dashboard's address was sent with doubled percent signs; it answered all the same.
- **The test's first fixture had the wrong order for a split name;** corrected.

## Decisions made without you

- **CEA in place of Grid-India,** as the chain's rule allows when a host bars the reader.
- **Fiscal years from the March reports,** six requests, rather than 80 monthly PDFs.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/cea_india_psp.py`, `tests/test_session2295.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c105/s2295/`.
