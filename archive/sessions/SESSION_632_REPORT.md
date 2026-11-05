# Session 632 report: crude oil imports by origin, destination and grade: 29 pages saved, nothing written

22 October 2026, from 05:08 UTC, on lab-desktop (the data machine), a session of `queue/done/040-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **Nothing written yet.** `warehouse/connectors/eia_crude_imports_detail.py` reads EIA's route `crude-oil-imports` (Form EIA-814, company level imports), monthly, from 2011, origins that are countries. It stopped at offset 145,000: EIA answered HTTP 502 and, asked again after 60 seconds, 504.
  - 29 pages (145,000 records, 2011 to about the middle of 2024) are saved in `warehouse/raw/eia_crude_imports_detail/` on the data machine. A later run reuses them.
  - About 5 or 6 pages are left. This session had 5 requests left under its ceiling while EIA was answering with errors, so it stopped rather than end on a second partial run.
- **The route** (probed): facets `originId`, `originType`, `destinationId`, `destinationType`, `gradeId`, from 2009-01, about 2,000 records a month, in thousand barrels.
  - The origins are countries (690 a month in January 2026) and EIA's sums of them (regions, OPEC and non-OPEC, the world). Only countries are taken.
  - The destinations nest: refinery, refinery state, refinery PADD, port, port state, port PADD, the U.S. The grades are light sweet, light sour, medium, heavy sweet and heavy sour.
  - Country origins hold 191,815 records from 2009, beyond 40 requests, so the table starts in 2011. 2009 and 2010 are left for an early window.
- **The table, once written**: `eia_crude_imports_detail_monthly`, entity `eia_crude_imports:<originId>:<destinationId>:<gradeId>`, variable `imports` (`kbbl`). No key repeats in the January 2026 page.

## Decisions made without you

- **Session 636 ("one more source") finishes this table** from the 29 saved pages, under its own ceiling of 20: the remaining pages, then the cross-check (the countries' U.S. destination summed by month against `eia_crude_imports_by_country`) and the write. Crude imports by destination are a public source the ERW does not hold.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 35 of 40 | the metadata, a January 2026 page, the count of country origins, the trial (29 answered, 3 answered with errors: 502 at offset 125,000 asked again and answered; 502 and 504 at offset 145,000) |

## Files

- New: `warehouse/connectors/eia_crude_imports_detail.py`, this report.
