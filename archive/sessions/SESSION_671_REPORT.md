# Session 671 report: connection durations, derived

22 October 2026, on lab-desktop (the data machine), a session of `queue/done/043-night-23-october-data-redivis-gaps.md`. Model spend USD 0. Pulls: none.

## Read these first

- **`interconnection_durations` (3,098 completed projects) and `interconnection_durations_summary` (1,365 rows) are written**, from `lbnl_interconnection_queue` with no request: request date to operation date in months (days / 30.4375), by project, and by grid and year of operation with medians, quartiles and a five-year median. Validated, archived, in coverage (derived, public), method `docs/methods/interconnection_durations.md`.
- **For the five years to 2025:** the U.S. median is 56.8 months (964 projects); ERCOT 45.6, West 47.1, Southeast 54.4, PJM 69.1, SPP 70.1, CAISO 95.1. ISO-NE has no row (the file gives it no operation date); MISO's last year is 2024 and NYISO's 2023.
- Left out and counted in the header: 1,643 operational requests without a request or an operation date, and 48 whose operation date is before the request date.
- **A new unit, `month`**, joins the validator and the data standard (Decision 49). Both holds are in. Tests: `tests/test_session671.py`.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| none | 0 | the queue table held |

## Decisions made without you

- `month` was added to the unit vocabulary rather than writing the durations in years: the time-to-connect column is read in months.
- The summary's `projects_5y` and `median_months_5y` were added beside the year's own figures, so a grid with few completions in a year still has a steady figure.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/derived/interconnection_durations.py`, `docs/methods/interconnection_durations.md`, `tests/test_session671.py`, this report. Changed: `warehouse/validate/erw_validate.py`, `docs/datastandard.md`, the metadata and release files as in session 667.
