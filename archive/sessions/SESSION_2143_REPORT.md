# Session 2143 report: method notes for this chain's tables

24 October 2026, from 00:31 UTC, on lab-desktop (the data machine), chain 090, unattended. A helper agent drafted the notes in the chain's worktree while sessions 2144 to 2146 ran. This session checked them, recomputing the numbers it could. Model spend USD 0. Pulls: none.

## Read these first

- **Six notes, in the form of `docs/methods/ercot_4cp_intervals.md`,** each with its `Tables:` line, its Method cell set in `docs/coverage.md`, and a section "What it does not hold":
  - `docs/methods/wfigs_wildfires.md`:
    - 6,222 fires, 18 January 2015 to 21 October 2026.
    - Status: 4,513 out, 470 contained, 1,239 empty.
    - Final acres given for 493 fires, the general cause for 1,151.
    - The largest is Smokehouse Creek, 1,054,150 acres.
  - `docs/methods/gfz_kp_index_3h.md`:
    - 277,032 intervals; ap matches GFZ's Kp-to-ap table in every row.
    - 376 days at Kp 8- or more; 27 days and 31 intervals at 9o.
  - `docs/methods/epa_ghg_inventory_annual.md`:
    - 152 series of 33 years; every line sums to its total within 0.3 MMT.
    - It warns that Decision 61's `tCO2e` names the GHGRP's AR4 warming potentials, while the Inventory's tables name none.
  - `docs/methods/scripps_co2_mlo_monthly.md`: 818 months a variable, the 10 months marked -99.99 named, the peak 432.00 ppm (May 2026).
  - `docs/methods/doe_lead_energy_burden.md`:
    - 3,222 counties and 52 states; the median state burden 2.59 percent, Puerto Rico's the highest in every bracket.
    - It warns that LEAD's county codes drop the leading zero (318 counties have four digits, San Francisco is `doe_lead:6075`). A join to five-digit FIPS adds it back.
  - `docs/methods/afdc_station_counts_annual.md`:
    - In 44 place-years AFDC's three charging levels do not sum to its ports.
    - All 3,060 values the table shares with chain 092's `afdc_ev_charging_state_annual` (the EV columns from 2014) are equal.
- **Checked by this session** (`runs/c090/`): the LEAD zips' total, 7,841,647,083 bytes; the 24 uneven AFDC totals, all in the 2013 sheet; the two EPA variables that keep a footnote letter; and the Kp values of 10 May and 10 October 2024, 8.667 (9-).

## Contradictions found, acted on

1. **Session 2135's report** named 10 May and 10 October 2024 "8+"; the rows give 8.667, which is 9-. Corrected.
2. **EPA's footnote letters:** the docstring and session 2136's report said the letters are dropped; the code drops them after Combustion, Total, HFCs and Percent only. So Table 2-11's "Stationary Sourcesa" keeps its letter, and `power:ch4:stationary_sourcesa` and `power:n2o:stationary_sourcesa` carry it (66 rows). The words are corrected. The names are left as written: a new name would break the series once it is on Redivis. **For a code session**, with a rename if wanted.
3. **EPA's national variables** have no basis before their slug (`total_gross_emissions_sources` and the two others). The docstring now says so; the written header's wording stays until the next run.
4. **LEAD's size:** "7.4 GB" in session 2140's report was the folder's size as `du` prints it. The zips total 7.84 GB (7.30 GiB). Corrected.
5. **AFDC's uneven totals** are all in the 2013 sheet, not spread over "2007 to 2013". The docstring and session 2141's report are corrected.
6. **The Scripps header** said MKO covers "the months after" the eruption; the rows hold MKO for December 2022 to February 2023 only. The header's code is corrected for the next run. The file contradicts itself too: its opening says sampling moved to Maunakea from December 2022, its station column gives three months.
7. **WFIGS's page limit** (a 21st page that still says more remain stops the run) is now in the docstring.
8. **WFIGS was written twice** (runs `20261023T231224Z` and `20261023T231301Z`); session 2134's report now says so.
9. **The LEAD docstring's "read 261"** is main's read of the submission page (session 2108). It was GFZ's robots file on the branch before the merge; since the merge it is right as written.
10. **`runs/c090/s2134/cross.py`'s docstring** said the plants of the latest year; it reads every year (the data machine's file, not in git).

Read numbers in the notes are the merged record's (302 on, after chain 092's landing).

## Decisions made without you

- **The notes drafted by a helper agent and checked here.**
- **No variable renamed after its upload** (item 2).

## For Samuel's ruling

- None new.

## Files

- New: the six notes, this report.
- Changed: `docs/coverage.md` (six Method cells); `warehouse/connectors/epa_ghg_inventory.py`, `afdc_stations.py`, `wfigs_wildfires.py`, `scripps_co2_mlo.py` (words only); the reports of sessions 2134, 2135, 2136, 2140 and 2141.
