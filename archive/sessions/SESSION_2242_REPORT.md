# Session 2242 report: six held-but-undescribed tables get their notes

24 October 2026, from 03:35 UTC (the notes drafted by a helper beside sessions 2243 to 2250, checked and finished from 03:56 UTC), on lab-desktop (the data machine), the fifth session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Six tables without a method note,** after a search of the notes on this branch, on main and on chains 097's and 099's branches, now have one each. They were checked as session 960 checked its notes, and their Method cells link them.

  | Table | Rows | Span |
  |---|---|---|
  | `eia860m_operating_generators` | 28,605 | vintage 2026-08, 1,417,946.5 MW |
  | `eia860m_planned_generators` | 2,316 | planned 2026-08 to 2039-12, 288,721.1 MW |
  | `eia860m_retired_generators` | 249 | retired 2025-01 to 2026-08, 6,620.1 MW |
  | `eia930_daily_total_interchange` | 212,461 | 2019-01-01 to 2026-10-22, 83 respondents |
  | `isone_rtm_zone_prices_hourly` | 11,664 | 2026-08-26 to 2026-10-22, 9 locations |
  | `ercot_zone_prices_history` | 2,481,384 | 2015 to 2026-10-18 |

- **Acted on:** the three EIA-860M tables' connector said that earlier vintages are in git history (the tables left git in session 9) and that it writes only when the vintage changes. Every run on the GitHub runner writes, since the runner holds no tables. `eia860.py`'s docstring and header now say both; the rows are unchanged.
- **Recorded, not changed:**
  - **EIA-930's daily total interchange has no row for 46 days** (2025-11-06 to 12-10 and 12-21 to 12-31). EIA's API returned none, and the saved monthly files mean those days are not asked again.
  - **ISO-NE's real-time hourly table:** a preliminary report given the final report's address, four days missing, and no license line. ISO-NE's terms ask for written permission, and the license record governs.
  - **ERCOT's load-zone history asks `/misapp` and `/misdownload`,** which ERCOT's robots file disallows. So do ERCOT's other connectors. This is the standing question "ERCOT's robots file" in every recent chain's note, for the owner; nothing is changed here.
  - EIA's rows without a generator id or a technology, and the first-retrieval times the archive keeps.
- **Corrections to earlier reports** (the helper's checks):
  - **Session 68:** "EIA's total interchange equals the sum of CAISO's ties within 1 MWh on all 307 common days" holds today on 123 of 311 days. The rest differ by 2 to 15 MWh, all from 2025-12-17 on.
  - **Session 140:** its USD 29.55 million comes from the rounded 33.73; the unrounded mean gives USD 29.54 million.
  - Sessions 5's and 8's figures hold.

## Checks that passed (the helper's, `runs/c101/s2242/`)

- Every table was read past its counted header lines, with no key twice, and its counts and spans match its header.
- The EIA-860M operating and planned tables match `energy_projects` exactly. All 249 retired generators are in `eia860m_retired_generators_all`, with the same dates and capacities.
- ISO-NE's hourly prices are within USD 0.02 of the mean of the four quarter hours of `isone_rtm_zone_prices` in 9,720 hours, and agree to the cent with `isone_zone_prices_history` where both hold.
- ERCOT's 7,684 intervals shared with `ercot_rtm_node_prices` agree to the cent.

## Errors

- **The six notes were swept into session 2250's commit** by its `git add`, before this session checked them. The committed text matched the drafts, and the action lines and Method cells are added here.
- **The Method cells' build ran on main's copies** and changed other cells of the six rows. Only the Method cells were kept (`runs/c101/keep_method_cells.py`).

## Decisions made without you

- **The six tables picked** by the helper's search, none planned by chains 097's, 099's or 102's files.

## For Samuel's ruling

- None new ("ERCOT's robots file", as before).

## Files

- New: `docs/methods/eia860m_operating_generators.md`, `eia860m_planned_generators.md`, `eia860m_retired_generators.md`, `eia930_daily_total_interchange.md`, `isone_rtm_zone_prices_hourly.md`, `ercot_zone_prices_history.md` (committed with session 2250's), this report.
- Changed: `warehouse/connectors/eia860.py` (docstring and header text), `docs/coverage.md` (six Method cells).
- On the data machine only: `runs/c101/s2242/`.
