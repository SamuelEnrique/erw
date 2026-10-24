# Session 2284 report: six held-but-undescribed tables get their notes

24 October 2026, from 05:20 UTC (the notes drafted by a helper beside sessions 2285 to 2292, checked and finished from 05:44 UTC), on lab-desktop (the data machine), the fifth session of `queue/done/104-day-7-november-data-portugal-italy-japan-argentina.md`, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Six tables without a method note, after a search of 1,542 notes** on this branch, main and chains 102's and 103's branches, now have one each, checked as session 960 checked its notes, with their Method cells.

  | Table | Rows | Span |
  |---|---|---|
  | `iso_dam_hub_prices` | 23,016, 19 hubs | 2026-08-26 to 2026-10-24 (MISO to 3 October) |
  | `eia930_all_demand` | 21,792, 8 respondents | 2026-08-26 to 2026-10-22 |
  | `eia930_all_generation` | 115,272, 17 variables | the same |
  | `eia930_all_history` | 60,084, 7 balancing authorities | January to June 2018 |
  | `eia930_daily_demand` | 191,785, 71 respondents | 2019-01-01 to 2026-10-22 |
  | `eia930_daily_interchange` | 952,530, 390 pairs | 2019-01-01 to 2026-10-21 |

  Two are borderline: `eia930_daily_demand` has one paragraph in `grid_network_v3.md`, and `eia930_all_history` one bullet in `events.md`. Neither is a method note.
- **Acted on:**
  - `eia930_daily_demand`'s connector said "every balancing authority". Its respondents include EIA's regions and US48, and five regions repeat a balancing authority's values, so a sum over entities double counts.
  - `eia930_daily_interchange`'s said "every pair of balancing authorities". Its pairs include Canadian and Mexican neighbours that do not report.
  - Both docstrings and headers now say so. The rows are unchanged.
- **Recorded, not changed** (no request; for the connectors' next change):
  - **`iso_dam_hub_prices`:** CAISO's and SPP's forward days have no vintage, and SPP's 15 October 2026 is missing. There is no License line (the license record governs MISO's rows), and `config.yaml` says 30 days where the table holds 59.
  - **The 30-day EIA-930 tables:**
    - Their titles say "every balancing authority" where they hold the seven ISOs and US48.
    - ERCO and NYIS lack 26 August without a gap row.
    - ISNE has three hours of all-zero fuels beside its total.
    - Other notes say "about 30 days", where the tables hold 58.
  - **`eia930_all_history`:** the docstring promises gap rows the code does not write, and three places give three dates for EIA's first workbook.
- **Report figures:** none fails. Sessions 29's, 62's and 109's counts were of the tables then; they have grown with EIA's late reports.

## Checks that passed (the helper's, `runs/c104/s2284/`)

- No key is twice in any table, and the consolidated tables' counts match their members' header lines.
- An independent pull (`iso_zone_prices_history`) matches `iso_dam_hub_prices` on all 2,400 shared hours.
- Hourly demand summed over each Eastern day equals EIA's daily figure on every whole day for the seven ISOs. US48 matches on only 2 of 57 days.
- NYISO's zones match EIA's NYIS demand to 0.2 MW on average, and ERCOT's load to 95 MW, both with the hour as the hour's end.
- The generation table's batteries match `eia930_all_storage` on 6,866 of 6,888 shared hours.

## Errors

- **The helper's notes for session 2289 were staged with these** by a broad `git add`; unstaged before the commit.

## Decisions made without you

- **The six tables picked** by the helper's search.

## For Samuel's ruling

- None new.

## Files

- New: `docs/methods/iso_dam_hub_prices.md`, `eia930_all_demand.md`, `eia930_all_generation.md`, `eia930_all_history.md`, `eia930_daily_demand.md`, `eia930_daily_interchange.md`, this report.
- Changed: `warehouse/connectors/eia930_daily_demand.py`, `eia930_daily_interchange.py` (docstrings and headers), `docs/coverage.md` (six Method cells).
- On the data machine only: `runs/c104/s2284/`.
