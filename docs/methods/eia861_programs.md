# EIA-861 demand response and dynamic pricing by utility

Energy Research Warehouse (ERW), method note written in session 877 (chain 047) for tables first written on 23 October 2026.

Tables: `eia861_demand_response`, `eia861_dynamic_pricing`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report, the demand response
file (`Demand_Response_<year>.xlsx`) and the dynamic pricing file (`Dynamic_Pricing_<year>.xlsx`; 2015 and 2016 are named
without the underscore), inside `f861<year>.zip`, page `https://www.eia.gov/electricity/data/eia861/`. The zips are the
ones `eia861_sales.py` saved in `warehouse/raw/eia861/` (rows retrieved 21 October 2026); session 868 made no request.
Connector: `warehouse/connectors/eia861_programs.py`, one connector for both files, as they share their form.

## Vintage and revision

Data years 2015 to 2025 when written (run `20261023T031259Z`). A run reads the years given with `--years` and writes
each table whole. 2015 to 2024 come from zips under EIA's `/archive/zip/`, 2025 from `/zip/`. EIA's robots file
disallows `/archive/` (session 666): such a year is read only from a zip already saved, never asked for.

Session 868 wrote the demand response table twice. A first write kept the figures on which two rows under one key
agreed; the connector now drops the whole record, and the second write holds 6 rows fewer (77,079 to 77,073). The
archive records the 6 keys deleted.

## Shape and variables

Series. `entity` `eia861_dr:<utility>:<state>:<balancing authority>` or `eia861_dp:<utility>:<state>:<balancing
authority>`; the balancing authority is empty before 2017, when EIA added the column, and in a few rows after. `ts_utc`
the data year's 1 January, `freq` `P1Y`, `geo` `US-<state>`, `node` the utility's name. EIA's own fields:
`x_utility_number`, `x_state`, `x_ba_code`.

The sectors are `residential`, `commercial`, `industrial`, `transportation` and `total`. A variable is
`<measure>_<sector>`.

`eia861_demand_response`:

| Variable | Unit | What it is |
|---|---|---|
| `customers_enrolled_<sector>` | `count` | customers enrolled in the program |
| `energy_savings_<sector>` | `MWh` | energy saved |
| `potential_peak_savings_<sector>` | `MW` | potential peak demand savings |
| `actual_peak_savings_<sector>` | `MW` | actual peak demand savings |
| `customer_incentives_<sector>` | `USD` | incentives paid to customers (EIA's thousand dollars times 1,000) |
| `other_costs_<sector>` | `USD` | all other costs (EIA's thousand dollars times 1,000) |

`eia861_dynamic_pricing`:

| Variable | Unit | What it is |
|---|---|---|
| `customers_enrolled_<sector>` | `count` | customers on a dynamic pricing program |

On every row of a utility in `eia861_dynamic_pricing`, the kinds of program EIA marks, by sector (residential,
commercial, industrial, transportation), Y, N or empty as EIA gives them: `x_tou_<sector>` (time of use pricing),
`x_rtp_<sector>` (real time pricing), `x_vpp_<sector>` (variable peak pricing), `x_cpp_<sector>` (critical peak
pricing), `x_cpr_<sector>` (critical peak rebate).

When written:

- `eia861_demand_response`: 77,073 rows, 533 utilities, 1,005 entities, 2015 to 2025. Actual peak savings, all
  utilities: 13,053 MW in 2015, 10,387 MW in 2020, 13,396 MW in 2025.
- `eia861_dynamic_pricing`: 33,157 rows, 907 utilities, 1,751 entities, 2015 to 2025.

2019 holds more rows than the years around it (13,590 demand response rows against 5,624 to 7,259 in the other years;
59 percent of them zero, against 23 to 31 percent). EIA gives no short-form file for 2019, and its 2019 files carry the
short-form utilities.

## Reading the sheets

- Every column is found by its stacked headings (a group, a measure, a sector), not by position. A heading carries right
  until the row names another. 2017 adds a balancing authority column and 2019 a Short Form column; the Short Form
  column is not taken.
- EIA's aggregates 88888 and 99999 are left out, as `eia861_sales.py` leaves them.
- A cell EIA leaves "." has no row. Nothing is filled.
- A row EIA gives twice with every field the same is kept once. Two rows under one utility, state and balancing
  authority with different values have no key: both are left out whole, not only the figures that differ, and named in
  the header (chain 030's rule). When written: Wabash Valley Power in Indiana (`eia861_dr:40211:IN:`) in 2015 and 2016,
  before EIA's balancing authority column. None in dynamic pricing.
- A heading the map does not know stops the run. The demand response file's "DSM Program" flags (grid-connected water
  heaters) are read past and named in the header.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`; `docs/licenses.md`: public,
agrees for both tables). Cite "U.S. Energy Information Administration, Form EIA-861".

## Cross-check (session 868)

Each row's total equals the sum of its sectors in 99.0 to 100 percent of rows. Customers enrolled agree exactly. Energy
savings, peak savings and incentives are about 1 percent apart where a sector is withheld.

## What it does not hold

- The demand response file's "DSM Program" flags.
- EIA's aggregates 88888 and 99999, and the 2015 and 2016 Wabash Valley Power records (two rows, two values, no key).
- A program's name or design: only the counts, savings and costs EIA gives, and the kinds of dynamic pricing it marks.
- Years before 2015 (the saved zips start at 2015).
