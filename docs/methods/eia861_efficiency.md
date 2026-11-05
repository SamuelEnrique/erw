# EIA-861 energy efficiency programs by utility

Energy Research Warehouse (ERW), method note written in session 891 (chain 048) for tables first written on 23 October 2026.

Tables: `eia861_energy_efficiency`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report, the energy efficiency
file (`Energy_Efficiency_<year>.xlsx`, sheets `Energy Efficiency_States` and, from 2016, `Energy Efficiency_Territories`),
inside `f861<year>.zip`, page `https://www.eia.gov/electricity/data/eia861/`. The zips are the ones `eia861_sales.py`
saved in `warehouse/raw/eia861/` (rows retrieved 21 October 2026); session 881 made no request. Connector:
`warehouse/connectors/eia861_efficiency.py`, a connector of its own that imports the stacked-heading reader of
`eia861_programs.py`, so that a run writes only this table. The ERW's state table from EIA stands beside it
(`eia_energy_efficiency_state_annual`).

## Vintage and revision

Data years 2015 to 2025 when written (run `20261023T042716Z`). A run reads the years given with `--years` and writes
the table whole. 2015 to 2024 come from zips under EIA's `/archive/zip/`, 2025 from `/zip/`. EIA's robots file
disallows `/archive/` (session 666): such a year is read only from a zip already saved, never asked for.

Utilities reporting fall from 653 in 2019 to 417 in 2020: EIA moved the small utilities to the short form (EIA-861S)
from 2020, which carries no efficiency figures. The table holds what EIA holds.

## Shape and variables

Series. `entity` `eia861_ee:<utility>:<state>:<balancing authority>`; the balancing authority is empty where EIA gives
none (when written, 3 of the 590 entities of 2015). `ts_utc` the data year's 1 January, `freq` `P1Y`, `geo` `US-<state>`, `node` the utility's
name. EIA's own fields: `x_utility_number`, `x_state`, `x_ba_code`, and `x_website` (EIA's Website column).

The sectors are `residential`, `commercial`, `industrial`, `transportation` and `total`. A variable is
`<group>_<measure>_<sector>`. The group is `annual` for EIA's "Reporting Year Incremental" headings (the reporting year's
incremental savings or costs) and `life` for its "Incremental Life Cycle" headings (the same programs over their life).

| Variable | Unit | What it is |
|---|---|---|
| `annual_energy_savings_<sector>`, `life_energy_savings_<sector>` | `MWh` | energy savings |
| `annual_peak_savings_<sector>`, `life_peak_savings_<sector>` | `MW` | peak demand savings |
| `annual_customer_incentives_<sector>`, `life_customer_incentives_<sector>` | `USD` | customer incentives (EIA's thousand dollars times 1,000) |
| `annual_other_costs_<sector>`, `life_other_costs_<sector>` | `USD` | all other costs (EIA's thousand dollars times 1,000) |
| `weighted_average_life_<sector>` | `year` | EIA's weighted average life, in years; the four sectors, no total |

When written: 187,850 rows, 734 utilities, 794 entities, 44 variables, 2015 to 2025. All utilities' first-year energy
savings (`annual_energy_savings_total`): 26.1 TWh in 2015, 28.2 in 2020, 24.2 in 2025; customer incentives
(`annual_customer_incentives_total`): USD 3.45 billion, 3.15 billion and 4.36 billion.

2019 holds more rows than the years around it (30,536 against 13,741 to 18,731 in the other years) and more utilities
(653).

## Reading the sheets

- Every column is found by its stacked headings (a group, a measure, a sector), not by position, with the reader of
  `eia861_programs.py`. The group headings are read as prefixes, since EIA writes "Cost" in 2015 and "Costs" later.
- Each sheet must give 44 figures (four measures in two groups for five sectors, and the weighted average life for four);
  else the run stops. A heading the map does not know stops the run. A Short Form column is read past.
- EIA's aggregates 88888 and 99999 are left out, as `eia861_sales.py` leaves them.
- A cell EIA leaves "." has no row. Nothing is filled.
- A row EIA gives twice with every field the same is kept once. Two rows under one utility, state and balancing
  authority with different values have no key: both are left out whole and named in the header (chain 030's rule). When
  written, none.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`; `docs/licenses.md`: public,
agrees). Cite "U.S. Energy Information Administration, Form EIA-861".

## Cross-check (session 881)

Against `eia_energy_efficiency_state_annual` (EIA's state profiles, by API), the utilities summed by state and year:

- First-year energy savings within 1 percent in 255 of 255 state-years (253 within 0.1 percent).
- Life cycle savings within 1 percent in 509 of 509; customer incentives in 249 of 249.
- Peak savings within 1 percent in 248 of 252. The four apart are small states' totals of a few MW (the report names
  Alaska 2018 and 2019, Delaware 2017), where EIA's rounding of single utilities shows.

## What it does not hold

- The small utilities from 2020: EIA's short form carries no efficiency figures.
- A total of the weighted average life across sectors.
- A program's name or design: only the savings, costs and life EIA gives.
- EIA's aggregates 88888 and 99999.
- Years before 2015 (the saved zips start at 2015).
