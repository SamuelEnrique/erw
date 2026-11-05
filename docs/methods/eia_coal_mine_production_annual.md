# Coal production and employees by mine

Energy Research Warehouse (ERW), method note written in session 694 (chain 045) for a table first written on 23 October 2026.

Tables: `eia_coal_mine_production_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Annual Coal Report, mine-level production (Form EIA-7A and MSHA Form
7000-2), through EIA's API v2, route `coal/mine-production`:
`https://api.eia.gov/v2/coal/mine-production/data/?frequency=annual&data[]=production&data[]=average-employees&data[]=latitude&data[]=longitude&data[]=operating-company&data[]=refuse-flag&start=2001`
(the key is never written). Connector: `warehouse/connectors/eia_coal_mine_production.py`. Page:
`https://www.eia.gov/coal/data.php`.

## Vintage and revision

Annual, 2001 to 2024 when written (EIA's route ends at 2024). A snapshot: each run replaces the table whole, so EIA's
revisions arrive at the next run with `--fresh` (a page saved in `warehouse/raw/eia_coal_mine_production/` is reused
otherwise; `--offline` asks nothing). Ceiling 12 requests; session 694 used 8 for the trial's eight pages of 5,000, and the
write reused them.

## Shape and variables

Series. `entity` `eia_coal_mine:<mineMSHAId>:<coalRankId>:<mineTypeId>`: one mine by the Mine Safety and Health
Administration's number, with EIA's rank (`BIT`, `SUB`, `LIG`, `ANT`, `PRP` a preparation plant) and mine type (`SUR`,
`UND`, `REF` refuse recovery). A preparation plant can report as surface and as underground in one year, so the rank and
type are in the key. `ts_utc` the year's 1 January, `freq` `P1Y`; `geo` `US-<state>`, with EIA's coal regions inside a
state put in their state (`KYE` and `KYW` Kentucky, `PAA` and `PAB` Pennsylvania anthracite and bituminous, `WVN` and
`WVS` West Virginia); `node` the mine's name.

| Variable | Unit | EIA's column |
|---|---|---|
| `production` | `short_ton` (Decision 50) | `production` |
| `employees` | `count` | `average-employees` |

EIA's own fields, as given: `x_msha_id`, `x_state` (EIA's code, the regions above kept), `x_county`, `x_supply_region`,
`x_rank`, `x_mine_type`, `x_status` (Active; Active, men working, not producing; Temporarily closed; Permanently
abandoned; Mine closed by MSHA; and two rarer), `x_operator` (EIA's operating company, cut at 30 characters by EIA),
`x_latitude`, `x_longitude` (empty on 12,817 rows), `x_refuse` (`Yes` for refuse recovery).

When written: 72,852 rows (37,485 production, 35,367 employees), 4,665 mines, 5,455 series. 12,589 production rows are
0, as EIA gives them (preparation plants, which process mined coal, and mines idle all year). In 2024, 524 mines
produced; the largest, North Antelope Rochelle (Wyoming), 59.8 million short tons.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`). Cite "U.S. Energy
Information Administration, Annual Coal Report".

## Cross-check (session 694)

Against `eia_coal_production_annual` (EIA's state aggregates, all ranks and all mine types): the mines' production
summed by year equals EIA's U.S. total exactly in every year 2001 to 2024 (512.5 million short tons in 2024). By state
and EIA region, 655 state-years in both: a median ratio of 1.0000, 93.1 percent within 1 percent and 80.2 percent within
0.1 percent; the widest are Pennsylvania anthracite (`PAA`, 1.31 in 2001, 1.05 to 1.11 in later years) and Arkansas in
2001 (1.21), where EIA's aggregate places some mines' coal in another region than the mine's own row.

## What it does not hold

- EIA's labor hours and productivity: the vocabulary's `hour` is an hour of the day, not a quantity of work (session 685).
- A figure EIA leaves empty (an employee count, most often) has no row; nothing is filled.
- Shipments from a mine to a plant (route `coal/shipments`), reserves and prices by mine.
- The mine's owner where it differs from its operating company.
