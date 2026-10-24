# Session 2254 report: New Zealand's generation and demand (the Electricity Authority's EMI)

24 October 2026, from 03:53 UTC, on lab-desktop (the data machine), a session of `queue/done/102-day-5-november-data-poland-belgium-new-zealand-columbia.md`. Model spend USD 0.

Pulls: 12 requests of 15:
- www.emi.ea.govt.nz's robots address (HTTP 404, no file);
- its Generation datasets page and the `Generation_MD` listing;
- its Wholesale reports page and the Generation tag page;
- the Generation trends report's page;
- www.ea.govt.nz's robots file (allows every path) and the Authority's copyright statement;
- four report CSVs: generation and demand, for New Zealand and by island, monthly from 2015.

www.mbie.govt.nz was not asked. The trial and the write ran offline.

## Read these first

- **One series table, `emi_nz_generation_demand_monthly`:** 846 monthly figures, January 2015 to September 2026, of New Zealand's grid generation and demand, for the country and for each island, in MWh (EMI's GWh times 1,000). They come from EMI's reports "Generation trends" (W_GG_C) and "Demand trends" (W_GD_C), in their CSV downloads.
- **Generation by fuel is not in it.** These reports' only dimension is the region. EMI's fuel split is in its half-hourly files by unit (`Generation_MD`, one a month from August 1997, 350 files), more than the ceiling allows; that is for a later session with its own ceiling. The report list that might hold a fuel report is built by script and could not be read.
- **License: public.** The Authority's copyright statement (on www.ea.govt.nz) says its "copyright material is licensed for re-use under the Creative Commons Attribution (CC-BY) 4.0 international licence", with attribution to the Electricity Authority. The verdict is recorded in session 2257's round.
- **Checks:**
  - each CSV must state its report, region type, monthly scale and GWh;
  - every period must be a calendar month;
  - no month may be given twice for a region;
  - the islands must agree with New Zealand within 1 percent.
- **They agree to rounding from 2015 to May 2026.** From June 2026, New Zealand's generation exceeds the two islands' by 1.6 to 9.9 GWh a month (up to 0.24 percent). These are EMI's own figures, kept and named in the header. The dollar columns (NZD) are not taken.
- **The cross-check** (`runs/c102/s2254/cross.py`, whole years):
  - EMI's grid demand is 94 to 96 percent of Ember's demand for New Zealand (41.6 against 43.3 TWh in 2025);
  - grid generation runs 3.3 to 3.6 percent above grid demand every year;
  - the South Island generates 1.6 to 4.4 TWh a year more than it uses, sent north.
- **Registered:**
  - the sector rule (`power`);
  - both holds;
  - the release package's rows;
  - the license tables (licenses check: 0 problems; release check: 0 differences).

  No row is given twice. The test is `tests/test_session2254.py` (4 tests).

## Errors

- **The first trial stopped on the islands' sum,** which differs from June 2026. The check now stops only past 1 percent and names the months.
- **Requests spent finding the reports:** the Generation tag page is built by script and gave no report codes.

## Decisions made without you

- **Monthly totals by region** in place of generation by fuel, which the reports do not give within the ceiling.
- **The table public** under the Authority's CC BY 4.0 statement.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/emi_nz.py`, `tests/test_session2254.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c102/s2254/`.
