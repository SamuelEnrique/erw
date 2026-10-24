# Session 2421 report: Botswana's electricity a month from Statistics Botswana

24 October 2026, from 10:48 UTC, on lab-desktop (the data machine), a session of `queue/done/115-day-16-november-data-zambia-botswana-mongolia-cambodia.md`. Precheck passed (`runs/c115/precheck_2421.out`). Model spend USD 0.

Pulls: 4 requests of 15, all to www.statsbots.org.bw, 10 seconds apart (its crawl delay):
- its robots file, alone;
- the home page, which links the newest brief;
- the Electricity Generation and Distribution Stats Brief for the second quarter of 2026;
- the terms of use.

The trial and the write ran offline.

## Read these first

- **Botswana is taken from Statistics Botswana's quarterly electricity brief** (not held; no chain planned it). The Botswana Power Corporation was not needed: the bureau's brief has every month since 2016.
  - **Table:** `statsbots_botswana_electricity_monthly`, 383 figures, internal until session 2425's round writes the verdict (the terms read below are attribution only).
  - **Monthly series, MWh, January 2016 to June 2026:**
    - generation (local generation): 126 months;
    - imports: 126 months;
    - distribution: 125 months.
  - **The brief's one quarter by source** (the second quarter of 2026, freq `P3M`):
    - generation: coal 894,025, diesel 3,137, solar 97,361 MWh;
    - imports: Eskom 135,444, the SAPP markets 18,889, cross-border 28,858 MWh.
  - **The connector takes the newest brief from the home page,** so a later run reads the next quarter.
- **The checks:**
  - **Totals:** each year's months add to its printed quarters and total.
  - **Distribution:** each month's distribution equals its generation plus imports within 1.5 MWh, in 125 of 126 months.
  - **By source:** the quarter's sources add to its total, and its totals equal the monthly tables' quarter.
- **One cell left out:** the February 2026 distribution (292,427 MWh) is that month's generation printed again.
  - Generation plus imports is 344,839 MWh, and the first quarter's printed distribution total (1,122,208 MWh) agrees with that figure, not with 292,427.
  - The cell has no row and the header names it. The connector allows only a month printed as its generation; any other mismatch stops it.
- **Against `owid_ember_electricity_annual`'s Botswana demand:** distribution is 0.89 to 1.12 times Ember's demand from 2016 to 2024, and 0.999 in 2023.
- **License:** the bureau's terms of use say users "may utilise the information as they wish, provided that they acknowledge Statistics Botswana as the source of the basic data", and that they say the analysis is their own. That reads as public with attribution. The verdict is left to session 2425's round, as chain 110 did for Moldova.
- **Registered:**
  - the sector rule (`power`), the live-set hold;
  - the license tables (licenses check: 517 tables, 0 problems);
  - the test, `tests/test_session2421.py` (5 tests).

## Errors

- **The first parse read the table of contents as table 3.** It now takes each table's last title.
- **The first parse's quarter check stopped at the misprinted February** before the distribution identity could explain it. The sums are now checked after the identity, using generation plus imports for a month left out (that figure is never written).
- **Three of the test's first stop cases did not stop,** because the inputs were wrong (a difference within the tolerance, and a line that does not exist). Corrected.
- **A heredoc patch lost its backslashes** (a known trap on this machine). Redone with the Edit tool.

## Decisions made without you

- **Statistics Botswana over BPC:** monthly figures, and terms that allow reuse.
- **The quarter by source kept in the monthly table** as `P3M` rows, rather than a second table.
- **The February 2026 distribution left out,** not corrected.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/statsbots_botswana.py`, `tests/test_session2421.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c115/s2421/`, `runs/license_reads/s2421/`, `warehouse/raw/statsbots_botswana/`.
