# Session 2323 report: Thailand not taken; Hong Kong's electricity (C&SD's Hong Kong Energy Statistics) in its place

24 October 2026, from 06:36 UTC, on lab-desktop (the data machine), the second session of `queue/done/108-day-10-november-data-malaysia-thailand-ecuador-kenya.md`, unattended. Precheck passed (`runs/c108/pre2323.out`). Model spend USD 0. Pulls: 15 of 15 to the web hosts, 5 to EIA's API (below).

## Read these first

- **Thailand is not taken.** None of its three sources can be used:
  - **EPPO (www.eppo.go.th):** its robots file allows the reader (read 506), but its website policy (read 511, a PDF) needs written permission. A new verdict, needs written permission in both columns:
    - Clause 2.2: the user may not change, distribute, transfer or make derivative works from the content without the owner's express permission.
    - Clause 3.3 forbids access by automated means (scripts) outside the channels EPPO provides; clause 3.5 forbids copying.
    - Its data API (data.eppo.go.th) needs a request for access (read 509).
    - EPPO's data files were not asked for.
  - **data.go.th**, Thailand's open data portal, refuses the reader at its robots file (HTTP 403, a security block; read 512). Not asked again.
  - **EGAT** publishes its system figures as graphs only (read 514). Its robots file disallows /home/wp-content/, where its files and website policy sit (read 513).
- **EIA routes looked at and left** (5 requests to api.eia.gov, `runs/c108/s2323/`):
  - Prime supplier sales (petroleum/cons/prim) end in March 2022.
  - Distillate sales by end use (petroleum/cons/821dsta) end in 2020.
  - U.S. net imports by country (petroleum/move/neti) is current, but it can be derived from two routes the ERW holds (imports by origin, exports by destination).
- **One public table in Thailand's place:** `censtatd_hk_electricity`, Hong Kong's electricity from the Census and Statistics Department's Hong Kong Energy Statistics. It is written, validated, archived, in coverage (sector power), and held from the live set and the release. 3,699 rows:
  - **table 915-91201:** local consumption a month by type of user (total, domestic, commercial, industrial, street lighting) and exports to the Chinese Mainland, January 1979 to August 2026;
  - **table 915-91203:** local generation, imports from and exports to the Mainland, industry own use and losses, and local consumption a quarter, 2013 to the second quarter of 2026.
  - Units: C&SD's terajoules times 1,000,000/3,600, giving MWh.
  - C&SD's years are the sums of its months and quarters (within 2 TJ), so they are not taken; neither is town gas.
- **License:** DATA.GOV.HK's terms (read 516) allow use "for both commercial and non-commercial purposes on a free-of-charge basis", with the source identified and attributed. A new verdict, may be public in both columns.
  - DATA.GOV.HK has no robots file (read 515).
  - www.censtatd.gov.hk's robots file allows every path and names ClaudeBot, anthropic-ai and Claude-Web to allow them (read 518).
- **A fault in `scripts/licenses.py` fixed:** its rule `Census` gave the Hong Kong table to the U.S. Census Bureau. It now reads `Census Bureau`, which still matches the Bureau's five tables and changes no other row.
- **Session 2322's table corrected:** `sources.csv` uses only `public` and `internal` as licenses, and session 2322 had written `CC BY 4.0`. Its source row, header and release row now read `public, CC BY 4.0`. The table was written again offline (the same rows), and its duplicated metadata rows were removed.

## The cross-check (`runs/c108/s2323/cross.py`, `cross.out`)

- **The months add up:** domestic plus commercial plus industrial plus street lighting equals the total within 1.8 TJ (rounding), 35 months over 1 TJ.
- **The quarters balance:** generation plus imports minus exports minus own use and losses equals local consumption within 1 TJ in all 54 quarters.
- **The tables agree:** the months' sums equal table 91203's quarterly local consumption within 1.3 TJ, and the exports within 1 TJ.
- **Against `owid_ember_electricity_annual`'s Hong Kong demand:** generation plus net imports is 0.3 to 2.2 per cent from Ember's, 2019 to 2024 (2024: 49.89 against 48.81 TWh). Local consumption is lower, because it leaves out the power companies' own use and losses (3.3 to 4.4 TWh a year).
- Exports to the Mainland are zero in every quarter from 2019.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.eppo.go.th | 6 | robots, two statistics pages, the API page, the disclaimer, the website policy |
| data.go.th | 1 | robots (403) |
| www.egat.co.th | 2 | robots, the statistics page |
| data.gov.hk, www.censtatd.gov.hk | 6 | two robots files, the terms, a catalogue search, two tables |
| api.eia.gov | 5 | a route list (3 calls), metadata and samples of three routes |

## Errors

- **The first trial stopped** because table 91203's years and first quarters start on the same day. The years are left out, being the quarters' sums.
- **A metadata patch met an unstaged edit** of `sources.csv`; it was staged and the patch applied in two parts.
- **Session 2322 wrote `CC BY 4.0` as a source license.** Corrected (above).

## Decisions made without you

- **Hong Kong in Thailand's place:** the nearest public grid source the ERW does not hold.
- **The EIA routes left,** two for being stale and one for being derivable.
- **C&SD's years and town gas left out.**
- **The Census rule narrowed** in `scripts/licenses.py`.

## For Samuel's ruling

- **EPPO's consent,** if Thailand's statistics are wanted: its website policy needs written permission for redistribution and for scripted access.

## Files

- New:
  - `warehouse/connectors/censtatd_hk_electricity.py`
  - `tests/test_session2323.py`
  - this report
- Changed:
  - `scripts/licenses.py` (the Census rule)
  - `warehouse/connectors/dosm_malaysia_electricity.py` (the license word)
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (506 to 518), `license_verdicts.csv` (EPPO, C&SD), `license_tables.csv`, `docs/licenses.md`
  - `docs/redivis/release-v1/`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c108/s2323/`, `runs/license_reads/s2323/`, `runs/s2323*`.
