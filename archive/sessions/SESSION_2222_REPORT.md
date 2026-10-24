# Session 2222 report: six more held-but-undescribed tables get their notes

24 October 2026, from 02:10 UTC (the notes drafted by a helper beside sessions 2218 to 2221, checked and finished from 02:37 UTC), on lab-desktop (the data machine), the thirteenth session of `queue/done/098-day-2-november-data-price-indexes-reservoirs-rooftops.md`, unattended. Model spend USD 0. Pulls: none; the helper ran one `git fetch --dry-run` against GitHub, which changed no ref.

## Read these first

- **Six tables without a method note,** after a search of the notes on this branch, on main and on chains 097's and 099's branches (by Tables line, file name or a body describing the table). Each now has one, checked as session 960 checked its notes, and its Method cell in coverage links it:

  | Table | Rows | Span | First written |
  |---|---|---|---|
  | `census_cbp_hosting_annual` | 1,836 | 51 areas, 2012 to 2023 | session 2160 |
  | `eia860m_retired_generators_all` | 7,334 | retired 1972-11 to 2026-08 | session 133 |
  | `isone_interconnection_queue` | 1,751 | queue dates 1996 to 2025-01-14 | session 8 |
  | `isone_zone_prices_history` | 1,075,024 | 2019-01-01 to 2026-09-01 | session 140 |
  | `iso_zone_prices_history` | 1,665,645 | NYISO and SPP from 2019, CAISO ZP26 from 2023-06-26 | session 140 |
  | `pjm_rpm_capacity_prices` | 234 | 18 areas, 2007/08 to 2028/29 | session 7 |

  Chain 099's agent was told; its session 2228 takes other tables.
- **Acted on:**
  - **Census:** the docstring said a withheld figure carries flag N. No row does; the withheld zeros carry D or S, and the docstring now says so.
  - **EIA-860M retired:** the docstring and header said the table has the two-year table's columns. It lacks `energy_capacity_mwh`, so 54 storage units have no MWh here, and both now say so.
  - **ISO-NE queue:** queue id 1093 (New Brunswick) had `geo` US-NB.
    - `iso_queues.py` now writes a geo only for a U.S. state's or DC's code. This also clears CAISO's US-MX, found in chain 094's notes.
    - The queues' next Monday run writes it.
  - **PJM capacity prices:** the docstring said ISO-NE's and MISO's prices "are not collected". `iso_all_capacity_prices` holds them: ISO-NE 26 rows, MISO 130. It also holds PJM's same 234 prices under its own variable and market names (`pjm_bra`, `capacity_price`), so a join of the two tables on either finds nothing. The docstring now says so.
- **Recorded, not changed** (no request, or not this session's to change):
  - NYISO's and ISO-NE's license lines predate the license record's ruling of 21 October.
  - ISO-NE's and NYISO's and SPP's zone histories are not refreshed where the tables are held.
  - The ISO-NE queue's blank operator and in-service columns.
  - The census NAICS vintage column.
- **Corrections to session 2160's report** (chain 090):
  - "California, Texas and Virginia lead both": Virginia is fourth in 2023 employment, behind New York.
  - The Spearman 0.56 includes a "US" row of sites with no state; without it the figure is 0.65.
  - The 2012 national employment sum counts four withheld states as zero.
  - The zips are 10.2 to 11.9 MB, not "12 MB".
  - Sessions 7, 8, 133 and 140's figures hold.

## Checks that passed (the helper's, `runs/c098/s2222/`)

- Every table's row count and range match its header, and no key is twice.
- Census: session 2160's cross-check reruns identical, and the saved zips reproduce the rows.
- EIA-860M: all 249 rows of the two-year table are present and agree; no generator is also operating.
- ISO-NE queue: all 1,282 of Berkeley Lab's ISO-NE ids are present, with capacity within 0.5 MW for 1,164 of 1,226.
- The zone histories match the six-week tables to the cent where they overlap; NYISO real time is within 0.15 of the 15-minute table's hourly mean in all 11,660 zone hours.
- PJM: all 234 prices equal `iso_all_capacity_prices`.
- The tests of the changed connectors pass (sessions 121, 133, 140, 206, 207, 321, 65, 89, 2160).

## Errors

- **The Method cells' build ran on main's validator and main's copies,** which turned `usbr_crsp_reservoirs_daily`'s validator cell to "blocked" (its units are on this branch's validator) and `pjm_rpm_capacity_prices`' last run back to this machine's 10 October file. Both rows were put back as committed, with only their Method cells new.

## Decisions made without you

- **The six tables picked** by the helper's search, none planned by chains 097's or 099's files.
- **A non-U.S. code leaves geo blank** rather than being written as another country's code, since the data standard's geo for a Canadian province was not checked here.

## For Samuel's ruling

- None new.

## Files

- New: `docs/methods/census_cbp_hosting_annual.md`, `eia860m_retired_generators_all.md`, `isone_interconnection_queue.md`, `isone_zone_prices_history.md`, `iso_zone_prices_history.md`, `pjm_rpm_capacity_prices.md`, this report.
- Changed: `warehouse/connectors/census_cbp_hosting.py`, `eia860m_retired_all.py`, `capacity_prices.py` (docstrings), `iso_queues.py` (the geo rule), `docs/coverage.md` (seven Method cells, `usbr_crsp_reservoirs_daily`'s among them).
- On the data machine only: `runs/c098/s2222/`, `runs/c098/s2222_*`.
