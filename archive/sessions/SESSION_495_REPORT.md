# Session 495 report: EIA-861, the years before 2025, and a fault found in the reader

21 October 2026, from 17:48 UTC, on lab-desktop (the data machine), the seventh session of `queue/done/022-evening-21-october-sources.md` (run before 494, which needs the lock). Model spend USD 0.

## Read these first

- **A fault in session 485's reader, found and fixed before any table was written.** `eia861_sales.py` read EIA's sheet by column position, as 2025 lays it out. 2019's sheet holds an extra "Short Form" column after the balancing authority, so a positional read shifted every 2019 figure by one column. The 2019 trial ran without complaint (51,066 rows), which is why the headings of every year were compared with 2025's: 2015 and 2016 only spell "BA_CODE" differently, and 2019 has the extra column.
  - The reader now finds every column by its heading, the sector from the first row and the measure from the second.
  - A missing heading stops the run, and only the sheets that exist are read.
  - Tests: `tests/test_session485.py`, 7 (with 2019's layout and a missing heading).
- **2015 to 2025, rebuilt with the new reader** (in a scratch folder; 0 requests, the saved page and zips reused): every year's rows as before except 2019, now 55,427.

  | Year | Utilities | Rows |
  |---|---|---|
  | 2015 to 2018 | 2,096 to 2,127 | 38,631 to 42,386 |
  | 2019 | 3,179 | 55,427 |
  | 2020 to 2025 | 1,521 to 1,536 | 34,207 to 36,476 |

  2019 holds the short-form utilities as observed rows, which later years mark imputed. That is EIA's marking, kept.
- **Cross-check, every year, against EIA's monthly state retail sales** (parts A, B and D, states only): 97% to 99% (2019 99.4%, 2025 96.9%), the gap being the imputed and withheld rows left out.

## To finish (session 489's part, when the lock is free)

`eia861_sales.py --year <y>` for 2015 to 2025 (0 requests), the validator, `build_coverage.py --only '^eia861_utility_sales$'`, `archive.py write --tables '^eia861_utility_sales$'`.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.eia.gov | 20 of 22 | the page and a zip for each of 2015 to 2024 (the first pass); the second pass 0 |

## Decisions made without you

1. The reader rewritten to read by heading, with the years' own layouts kept as EIA publishes them.

## Files

- Changed: `warehouse/connectors/eia861_sales.py`, `tests/test_session485.py`. New: this report.
