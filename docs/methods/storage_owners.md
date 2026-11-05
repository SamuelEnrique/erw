# Who owns the batteries: method

Tables: `storage_owners_monthly`

Built in session 87 for the review page `/storage/owners` ("Who owns the batteries"), since session 239 the owners tab of `/storage` (`/storage?tab=owners`; the old address redirects). One table:

| Table | Tier | What |
|---|---|---|
| `storage_owners_monthly` | derived | Operating and planned battery storage by the company that reports each plant and by grid: MW, MWh, average duration, units, rank and share; and per grid the count of companies and the share of the largest |

Code: `warehouse/derived/storage_owners.py`. No pull. It reads the two EIA-860M tables of the newest inventory, `eia860m_operating_generators` and `eia860m_planned_generators`. How much has been built, month by month and by duration, is the neighbouring table: [`storage_buildout.md`](storage_buildout.md).

## What is counted

The same units as the build-out table, so the two agree:

- **A battery** is a generator whose prime mover is `BA` (EIA's "Batteries"), in plants of 1 MW and above. Pumped hydro, flywheels and compressed air are not counted.
- **Operating** is EIA's operating inventory, statuses `OP`, `SB`, `OS` and `OA`. **Planned** is EIA's planned inventory, every status from approvals pending to under construction.
- **The grid** of a unit is its balancing authority code where that is one of the seven ISOs (`CISO`, `ERCO`, `ISNE`, `MISO`, `NYIS`, `PJM`, `SWPP`); every other code, and no code, is `outside_isos`; `us` is every unit, Puerto Rico included.
- **MW** is nameplate power. **MWh** is EIA's Nameplate Energy Capacity. **Hours** is MWh over the MW of the units that report energy, omitted (never zero) where none does. The planned inventory has no energy column, so no planned MWh is written.

For each grid the operating MW and MWh here equal the newest month of `storage_buildout_monthly` (`tests/test_session87.py`).

## What an owner is

**EIA-860M names one company for each plant, its "Entity": the company that reports the plant to EIA.** It is the plant's owner or its operator, and for batteries it is very often a project company formed for one plant.

- The table keys an owner by EIA's Entity ID (`eia860:utility:<id>`) and carries EIA's Entity Name in `x_owner`. In the inventory of August 2026 every Entity ID has one name and every name one ID; the builder fails if an ID ever carries two names.
- **No parents.** EIA-860M does not say who owns a project company, and nothing here merges names. A developer with ten project companies is ten owners. So the share of the largest five or ten is a floor on how concentrated ownership really is, not a measure of it.
- **No shares.** Who owns what fraction of a plant is in the annual EIA-860 (Schedule 4), which this table does not read. A plant counts whole for the company that reports it.

## The table

A `series` table, one inventory month (`freq P1M`). Variables are `<grid>_<metric>`, also in `x_grid` and `x_metric`.

| Entity | Metrics |
|---|---|
| `eia860:utility:<id>` (a company) | `operating_mw`, `operating_mwh`, `operating_hours`, `operating_units`, `operating_rank` (its position by operating MW in the grid, 1 the largest; equal MW ordered by name, so a rank is given once), `operating_share_pct` (of the grid's operating MW), `planned_mw`, `planned_units` |
| `iso:<grid>`, `us:outside_isos`, `us:total` | `operating_mw`, `operating_mwh`, `operating_hours`, `operating_units`, `owners_operating`, `planned_mw`, `planned_units`, `owners_planned`, `top5_share_pct`, `top10_share_pct` |

A company has a metric only where it has a unit: there are no zero rows. MW and MWh are summed as whole ten-thousandths, so a total carries no float noise; a share is rounded half up to two decimals, a duration to four.

## The page and the live set

The table is public (EIA-860M is in the public domain). It was first held out of the live set (`catalogue_hold`); since session 102 it is loaded under `review_hold` (`warehouse/supabase/live_set.yaml`): in Supabase, read by Ask, and in no count a visitor sees (session 281 corrected this line, which still said it was held out). The review page therefore reads `site/data/storage_owners.json`, a copy of the table's newest month written by the builder (`--snapshot`); every number in it is a row of the table, which a test checks.

## Checks

`tests/test_session87.py`: the builder on made-up units (sums, grids, ranks and ties, shares, a company with planned units only, the omitted duration, an Entity ID with two names); the table against `storage_buildout_monthly`; each grid's companies summing to the grid; the snapshot against the table; the page's model.

## Checks against the table (session 2424)

Counted from `warehouse/output` by `runs/c115/s2424/check_tables.py`: `storage_owners_monthly` 9,540 rows, one inventory month (August 2026, `freq P1M`), 948 entities (9,450 rows of companies `eia860:utility:<id>`, 70 of grids `iso:<grid>`, 20 of `us:outside_isos` and `us:total`), 108 variables over 9 grids (`x_grid`), units MW, MWh, MWh/MW, count and pct, no key given twice, every value a number. As the table section above describes. The Tables line was added so that the finder of held tables with no note sees it.
