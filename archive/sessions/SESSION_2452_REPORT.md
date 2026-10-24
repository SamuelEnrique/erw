# Session 2452 report: method notes for this chain's three country tables, every point acted on

24 October 2026, from 12:50 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/118-day-18-november-data-rwanda-senegal-azerbaijan-uzbekistan.md`, unattended. The notes were drafted by a helper beside sessions 2453 to 2460 and checked here. Precheck passed (`runs/c118/pre2452.out`). Model spend USD 0. Pulls: none.

## Read these first

- **Which tables had no note:** as chain 114's session 2410 found, every held table outside the running chains has a note. The only tables with none were this chain's three country tables, `rura_rwanda_electricity_quarterly`, `statsaz_azerbaijan_electricity_annual` and `siat_uzbekistan_electricity_annual`. The own choices' notes follow in session 2457.
- **Three method notes** in `docs/methods/`, each checked as session 960 checked its notes, against the code, the table and the saved sources. The helper found every row of the three tables equal to the sources. The Method cells are set.
- **Every point was acted on:**
  - **Rwanda:**
    - neither "Regional shared HPP" nor "Imports" is defined, and RURA's own mix counts the regional line as hydro;
    - sales include exports: generation less exports is RURA's supply to the national grid, domestic sales fall 16 to 19 per cent short of it, and the reports give no losses;
    - the categories grow over the reports: street lights and exports from Q1 2022, Nasho's own use from Q2 2023. Q3 and Q4 2021's exports are given only in a figure and are not taken;
    - header line 1 now ends with the last quarter's last month;
    - session 2448's report named a capacity for Shema Power that no saved file gives; it is corrected.
  - **Azerbaijan:**
    - the docstring's node is now what the table holds;
    - "-" is "not applicable" and "0.0" "the least number", as the Committee's page says;
    - table 5.4's fuel-fired and CHP part leaves out the autoproducers, which the balance's fuel lines hold; neither autoproducers nor "by generator" is defined;
    - header line 2 no longer lists transformation input, which has no rows (19 of the balance's 59 lines are "-" in every year);
    - session 2450's report is corrected on the years its cross-check compared.
  - **Uzbekistan:**
    - only indicator 440's page was read for the license, and the files carry none;
    - the page's source line names the Statistics Agency, and the header now does too;
    - the consumption indicator's own name is quoted; it is undefined and 19 to 24 per cent below production in most years;
    - 2018's consumption is flagged; the files' notes stop at 2023; the largest unallocated parts are named;
    - session 2451's report is corrected on the license pages.
  - **"Not read" for RURA in `docs/licenses.md`** means no verdict, as for AMM; nothing was changed.
  - **The three tables were written again offline,** with the same rows.
  - **The notes' read numbers** were renumbered with session 2457's merge mapping, from 763 to 805 to 784 to 826.

## Errors

- **Sessions 2448, 2450 and 2451's reports and the three connectors' headers carried the slips above.** Each is corrected in place and says so.

## Decisions made without you

- None beyond acting on the points.

## For Samuel's ruling

- None new.

## Files

- New:
  - `docs/methods/rura_rwanda_electricity_quarterly.md`, `statsaz_azerbaijan_electricity_annual.md`, `siat_uzbekistan_electricity_annual.md`
  - this report
- Changed:
  - `warehouse/connectors/rura_rwanda.py`, `statsaz_azerbaijan.py`, `siat_uzbekistan.py`
  - sessions 2448, 2450 and 2451's reports
  - `docs/coverage.md` (Method cells), the coverage and archive manifest rows
- On the data machine only: `runs/c118/s2452/` (the drafts, the helper's check scripts and `POINTS.md`, `act.py`, `renumber_notes.py`).
