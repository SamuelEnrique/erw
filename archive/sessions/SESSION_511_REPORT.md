# Session 511 report: Form EIA-861M, each sampled utility's monthly sales

21 October 2026, from 19:27 UTC, on lab-desktop (the data machine), the second session of `queue/done/026-night-21-october-sources.md`. Model spend USD 0.

## Read these first

- **`warehouse/connectors/eia861m_sales.py`: the monthly sales, revenue and customers of the utilities in EIA's monthly sample**, by state and sector, as the series table `eia861m_utility_sales_monthly`.
  - 180,161 rows: 354 utilities, January 2025 to July 2026.
  - Read from `sales_ult_cust_2025.xlsx` (Last-Modified 24 February 2026) and `sales_ult_cust_2026.xlsx` (24 September 2026). Both sheets are read: States and Territory.
- **Read by heading** (session 495's lesson). Entity `eia861m:<utility>:<state>`. Variables `<sector>_sales` (MWh), `<sector>_revenue` (USD, from EIA's thousand dollars) and `<sector>_customers`. Every row carries EIA's data status ("Preliminary" in both files) in `x_data_status`.
- **Real data only.** EIA estimates the utilities outside its sample as one row a state, "State Adjustment". Its "State Total" and "US Total" rows include those estimates. None of the three is a utility, and none is taken.
- **Robots and terms**: EIA's pages are allowed, and EIA's terms are record 1 of `license_reads.csv` (public).
- **Cross-check against `eia861_utility_sales`, 2025** (`runs/s511/crosscheck.py` on the data machine): each utility-state with all twelve months, summed, against the annual form's total sales, summed over its parts.
  - 600 utility-states are in both. The median ratio is 1.0000; 81.2% are within 2% and 86.7% within 10%.
  - Some differ widely: utility 60025 has ratios from 4.3 to 7.3, and three Massachusetts and Ohio utilities 0.07 to 0.09. The totals are 2,449 TWh against 3,050 TWh.
  - The cause was not established here. The annual form's parts (energy-only and delivery-only service) are one possible reason, and it is left for a later session.
- **Written under the data lock** with `--offline`, from the trial's saved page and files (0 requests). Validator, coverage and archive exited 0.
- **Held** from `/data`'s catalogue and from Redivis v1 until uploaded. Not in the live set.
- Sector rule (`power`). Tests: `tests/test_session511.py`, 7, on real rows of the 2025 sheet.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.eia.gov | 6 of 6 | the probe: the page and the 2025 and 2026 files; the trial: the same three again (the probe's were not saved in `warehouse/raw`); the write 0 |

## Decisions made without you

1. 2025 and 2026 only, so that the ceiling of six held; earlier years (2017 on) can be added by a later run.
2. `--offline` added, so that a write after a trial asks nothing.

## For a later session

- The 13% of utility-states whose monthly sum and annual total differ by more than 10%: read the annual form's parts and service types for them.

## Files

- New: `warehouse/connectors/eia861m_sales.py`, `tests/test_session511.py`, this report. Changed: `warehouse/metadata/build_coverage.py` (with session 510's commit), `docs/coverage.md`, `docs/licenses.md`, `docs/redivis/release-v1/`, `warehouse/metadata/{coverage,archive_manifest,sources,license_tables}.csv`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`.
