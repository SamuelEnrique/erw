# The datacenter tracker's rollups

Energy Research Warehouse (ERW), method note written in session 2236 (chain 156) for the table it adds.

Tables: `datacenter_tracker_rollups`

## Sources and builder

The ERW builds this table from its own `datacenter_projects` (the facilities the scored news names, `docs/methods/datacenter_projects.md`). The builder is `warehouse/derived/datacenter_tracker_rollups.py`, run by the daily sequence after the facilities as `datacenter_tracker_rollups`. No model is called and no request is made.

## What a row is

The series shape: one group, one variable, one day.

- **`entity`**: `grid:<grid>` (the facility's `grid`: a grid operator its stories name, else the grid that serves most of its state, `grid_basis` saying which; `grid:none` for a facility with neither), `state:<postal code>` (`state:none`), `operator:<name>` (the operator, else the developer, joined to one name as `warehouse/deals/counterparties.py` joins the deals' counterparties; `operator:none`), and `tracker:all`.
- **`variable`**: `facilities`; `facilities_with_mw`; `facilities_without_mw`; `mw_stated`, the sum of the MW the group's stories state; `mw_stated_planned`, `mw_stated_under_construction`, `mw_stated_operating`, `mw_stated_withdrawn` and `mw_stated_none` by the facility's `status`.
- **`unit`**: count or MW. **`ts_utc`**: the day the rollup was built, 00:00 UTC; `freq` P1D.

## The rules

- **A sum is of the MW the stories state**, of any basis (`mw_basis`: IT load, total, a tenant's share, a phase, or unstated): the sum of a group mixes bases, and the page says so beside it. The facilities that state no MW are counted beside the sum (`facilities_without_mw`), never added as zero.
- **A group whose facilities state no MW has no sum**: the row is not written, so a reader sees the count without a number.
- **The grid read from a state is a reading, not a fact of the story**: `grid_basis` state. A state split between grids is not given one.

## On 6 November 2026 (read from the table of 5 November, 163 facilities)

45 facilities state MW (26,636 MW summed, of every basis); 132 have no grid (no US state stated, or a state split between grids); ERCOT 11 facilities (4 with MW, 457 MW), PJM 10 (1, 18 MW), MISO 4 (none with MW).

## License

As `datacenter_projects`: license needed since 21 October 2026. Its own row of `warehouse/metadata/license_status.csv` is written once the data machine has built the table and `coverage.csv` holds it (session 410's test holds every row of the file to a table of coverage); until then no live set, page or download reads it.

## What it does not hold

- A facility no scored story names (the operators' own site lists and the queues are in `datacenter_facilities`, held whole); a MW no story states; a share of a facility's MW in a grid it straddles.
