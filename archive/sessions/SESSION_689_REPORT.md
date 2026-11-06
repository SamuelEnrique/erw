# Session 689 report: EIA-861M's aggregates of 2017 to 2021 leave the table

23 October 2026, from 00:14 UTC, on lab-desktop (the data machine), a session of `queue/done/045-evening-22-october-data-resumed.md`. Model spend USD 0. No ruling of the owner on these rows was found (the chain's "unless the owner has ruled otherwise").

## Read these first

- **`eia861m_utility_sales_monthly` now holds sampled utilities only: 1,051,488 rows (from 1,145,088), 369 utilities, January 2017 to July 2026.** The 93,600 rows that left are EIA's aggregates of the 2017 to 2021 files: "Adjustment <year>" (utility number 0, EIA's estimate of the utilities outside the monthly sample) and "Total EPM" (88888, its state totals), 9,360 rows of each a year. Every other row is unchanged (checked: the old table's rows of real utilities equal the new table's, `retrieved_at` apart).
- **The rule:** `eia861m_sales.py` leaves out rows by EIA's aggregate numbers (0, 88888, 99999) as well as by name. A scan of all ten saved workbooks (2017 to 2026, both sheets) found every aggregate numbered 0 or 88888, under five names ("Adjustment <year>", "Total EPM", "US Total EPM" to 2021; "State Adjustment <year>", "State Total", "US Total" since). 99999 is in none of them; it is in the rule because the chain named it.
- **The cross-check:** in every month from January 2017 to July 2026, the new table's sampled utilities of the 50 states and DC, plus EIA's adjustment rows, equal EIA's own U.S. total row of the same file, for total sales, revenue and customers (0.0000% apart at the worst month of every year and measure).
- Written under the data lock from the saved files (`--offline`, no request), validated (exit 0), coverage rebuilt `--only`, archived (archive run `20261023T001900Z-local`: 0 rows new, **93,600 keys deleted**, so a restore gives the new table).

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| none | 0 of 0 | the saved workbooks of `warehouse/raw/eia861m/` |

## Decisions made without you

- 99999 is kept in the rule though no file has it (the chain named it; it removes nothing today).
- The Stanford Redivis draft still holds the old table (1,145,088 rows, the aggregates in it): this session had no Redivis requests. Its re-upload (about 5 requests) goes to the next Redivis session with the 47 tables of session 688's reconcile.
- `licenses.py tables` also picked up the daily run's newer header of `energy_deals` and `energy_deals_evidence` (Heatmap News now among their sources): kept, as it describes the files on this machine.

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session689.py` (3 tests), this report. Changed: `warehouse/connectors/eia861m_sales.py`, `docs/methods/eia861m_utility_sales_monthly.md`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/tables.csv`. On the data machine only: `runs/c045/s689/` (the scan, the trial, the cross-check), `runs/s689_*`.
