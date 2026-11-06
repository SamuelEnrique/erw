# EIA Electric Power Annual, chapter 8: heat rates and operating costs

Energy Research Warehouse (ERW), method note written in session 905 (chain 049) for tables first written on 23 October 2026.

Tables: `eia_power_costs_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Electric Power Annual, chapter 8, four workbooks on the page
`https://www.eia.gov/electricity/annual/`: `xls/epa_08_01.xlsx` (Table 8.1, average operating heat rate by energy
source), `xls/epa_08_02.xlsx` (Table 8.2, average tested heat rate by prime mover and energy source), `xls/epa_08_03.xlsx`
(Table 8.3, revenue and expense statistics for major U.S. investor-owned electric utilities) and `xls/epa_08_04.xlsx`
(Table 8.4, average power plant operating expenses for those utilities). Retrieved 23 October 2026, 06:55:42 to 06:55:43
UTC. Four requests, the connector's ceiling; the workbooks are saved in `warehouse/raw/eia_epa_costs/` and reused with
`--offline`. EIA's robots file allows `/electricity/annual/` (read by session 895, with the annual's page). Connector:
`warehouse/connectors/eia_epa_costs.py`, one connector for the four tables.

## Vintage and revision

Data years 2015 to 2025 when written (run `20261023T065738Z`). A run reads the four workbooks and writes the table whole,
one snapshot; `vintage` is empty. The first write replaced no earlier file (the previous file held 0 rows).

## Shape and variables

Series. `entity` one of four forms: `eia_epa:heat_rate:<energy source>` (table 8.1),
`eia_epa:tested_heat_rate:<prime mover>:<energy source>` (table 8.2), `eia_epa:iou_finance:<line path>` (table 8.3, the
line's parents joined with ".") and `eia_epa:iou_plant_expense:<plant type>` (table 8.4). `ts_utc` the year's 1 January,
`freq` `P1Y`, `geo` `US`, `market` empty. `node` is the line as EIA words it in table 8.3, and in the other tables the
source, prime mover or plant type with the measure (`Coal, average operating heat rate`, `Nuclear, fuel expense`).

| Variable | Unit | What it is |
|---|---|---|
| `heat_rate` | `MMBtu/MWh` | average operating heat rate by energy source (EIA's Btu per kWh divided by 1,000) |
| `tested_heat_rate` | `MMBtu/MWh` | average tested heat rate by prime mover and energy source (the same) |
| `amount` | `USD` | a line of table 8.3 (EIA's million dollars times 1,000,000) |
| `operation_expense` | `USD/MWh` | a plant type's operation expense (EIA's mills per kWh, the same number) |
| `maintenance_expense` | `USD/MWh` | its maintenance expense (the same) |
| `fuel_expense` | `USD/MWh` | its fuel expense (the same) |
| `total_expense` | `USD/MWh` | its total expense (the same) |

The energy sources are `coal`, `petroleum`, `natural_gas` and `nuclear`; the prime movers `steam_generator`,
`gas_turbine`, `internal_combustion` and `combined_cycle`; the plant types `nuclear`, `fossil_steam`, `hydro_electric`
and `gas_turbine_and_small_scale`. Table 8.3's 21 lines: `utility_operating_revenues` (`electric_utility`,
`other_utility`); `utility_operating_expenses` (`electric_utility`, `other_utility`), the electric utility's
`operation`, `maintenance`, `depreciation` and `taxes_and_other`, operation's `production` (`cost_of_fuel`,
`purchased_power`, `other`), `transmission`, `distribution`, `customer_accounts`, `customer_service`, `sales` and
`administrative_and_general`; and `net_utility_operating_income`.

When written: 550 rows, 39 entities, 2015 to 2025, every entity in all 11 years. `heat_rate` 44 rows, `tested_heat_rate`
110 (10 pairs of prime mover and source), `amount` 231, `operation_expense`, `maintenance_expense` and `total_expense` 44
each, `fuel_expense` 33 (no hydro-electric row). In 2025: total expense 23.89 USD/MWh at a nuclear plant, 42.12 at fossil
steam, 28.22 at gas turbine and small scale; operating heat rate 10.443 MMBtu/MWh for nuclear and 7.781 for natural gas.

## Reading the sheets

- Table 8.1: the third row must read Year, Coal, Petroleum, Natural Gas, Nuclear, or the run stops. A row is read when its
  first cell is a four-digit year.
- Table 8.2: the third row must read Prime Mover and the same four sources. A year row opens a block, and a row naming one
  of the four prime movers is read into it; any other line in a block that does not begin "Note" stops the run.
- Table 8.3: the row "Description" gives the year of each column. A line's depth is the number of dots EIA indents it
  with, divided by six, and the entity is the path of the line and its parents, so a sum takes one level. Lines beginning
  "Notes" or "Total may" are passed. The lines are taken as found: no list of them is checked.
- Table 8.4: two blocks (operation and maintenance, then fuel and total), each a row of groups over a row of plant types
  under "Year". A heading not in that form, or a count of blocks other than two, stops the run.
- A value EIA withholds ("W") or does not have ("--", "NA") has no row. Nothing is filled.
- A key (entity, variable, ts_utc) given twice stops the run.

## License

Public: a work of the U.S. government (EIA, record 1 of `license_reads.csv`; `docs/licenses.md`: public, agrees). Cite
"U.S. Energy Information Administration, Electric Power Annual".

## Cross-check (session 903)

Table 8.3's parts sum to their totals in all 11 years: revenues, electric expenses, and production; every parent line
agrees with its parts within 1 million dollars, EIA's last digit. EIA notes that missing or erroneous respondent data may
leave the table's subtotals slightly out.

Table 8.1's 2025 heat rates against EIA-923's 2025 plants (session 897's table), fuel used for electricity over net
generation: nuclear 10.443 against 10.445 MMBtu/MWh; natural gas 7.781 against 7.636, about 2 percent apart. EIA does not
state how it weights the annual figure, so the gap is reported as found.

## What it does not hold

- Any table of the Electric Power Annual but 8.1 to 8.4.
- A hydro-electric fuel expense, and tested heat rates for coal or nuclear under a gas turbine, internal combustion or
  combined cycle: no row in any year.
- A single utility, plant, state or region: table 8.3 is the major investor-owned utilities together, table 8.4 their
  average, and `geo` is `US` throughout.
- Years before 2015 (none in the workbooks as read).
