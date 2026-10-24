# Session 2375 report: method notes for the two tables without one, every point acted on

24 October 2026, from 09:00 UTC, on lab-desktop (the data machine), the fifth session of `queue/done/112-day-13-november-data-sri-lanka-nigeria-ghana-jordan.md`, unattended. The notes were drafted by a helper beside sessions 2376 to 2383 and checked here. Precheck passed (`runs/c112/pre2375.out`). Model spend USD 0. Pulls: none.

## Read these first

- **Which tables had no note:**
  - As chain 108's session 2326 found, every held table outside the running chains is described in a note, under its own name or a family note's.
  - The only tables with no note at all were this chain's two from sessions 2371 and 2373: `ceb_srilanka_electricity_annual` and `energycom_ghana_electricity_annual`.
  - Chain 110's session 2361 was told the six FERC EQR tables are in `eqr_buyers.md` and `eqr_terms.md`.
- **Two method notes,** in `docs/methods/`, each checked as session 960 checked its notes, against the code, the table, the PDFs and the cross-checks. The Method cells are set.
- **Every point was acted on:**
  - **CEB:**
    - `generation_ipp_ncre_rooftop_solar` is rooftop solar's energy exported to the network, printed under the producers. It is not producer output, and rooftop solar has no capacity row (1,141 MW in 2024 and 1,935 MW in 2025 on the summary page). The header and docstring now say so.
    - The tolerance is stated in CEB's printed units.
    - The page is named as the PDF's third, printed page 1.
    - Session 2371's report is corrected: small islands and rooftop solar are generation rows only, and the dashboard has 21 scripts, not "a dozen".
    - Written again offline.
  - **Ghana:**
    - The bulletin's footnote 8 says total generation includes imports. Table 3.7's total holds none: it is hydro plus thermal plus other renewables, and the bulletin's energy transmitted is that total plus imports in 2000 to 2006. The header now says so.
    - The system peak has two definitions in the bulletin, so the system peak less Ghana's is not export load; the header says so.
    - The tables are named by title and printed page.
    - Session 2373's report is corrected on imports and on 2025's total (27.945 TWh), and its cross-check's docstring now names Ghana.
    - Written again offline.
  - **"Not read" in `docs/licenses.md`** for both publishers means no verdict, which an internal table under unstated terms does not have (as REN's since chain 104). Nothing was changed.

## Errors

- **Sessions 2371 and 2373's reports and headers carried the errors above;** each is corrected in place and says so.
- **The offline rewrites left duplicate metadata rows;** each table's newest was kept.

## Decisions made without you

- **No note for tables already described in family notes.**

## For Samuel's ruling

- None new.

## Files

- New:
  - `docs/methods/ceb_srilanka_electricity_annual.md`, `docs/methods/energycom_ghana_electricity_annual.md`
  - this report
- Changed:
  - `warehouse/connectors/ceb_srilanka.py`, `energycom_ghana.py`
  - sessions 2371 and 2373's reports
  - the coverage (Method cells), sources and archive manifest files
- On the data machine only: `runs/c112/s2375/` (the helper's scripts in `notes/`), `runs/c112/s2373/cross.py`.
