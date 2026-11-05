# EIA-923 monthly net generation and fuel consumed by plant

Energy Research Warehouse (ERW), method note written in session 905 (chain 049) for tables first written on 23 October 2026.

Tables: `eia923_plant_fuel_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-923, Schedules 2, 3, 4 and 5, page 1: the workbook
`EIA923_Schedules_2_3_4_5_M_<month>_<year>_<date>.xlsx`, sheets "Page 1 Generation and Fuel Data" and "Page 1 Puerto
Rico", inside the yearly zip `f923_<year>.zip`, page `https://www.eia.gov/electricity/data/eia923/`. The connector asks
for the zip directly at `xls/f923_<year>.zip`, one request a year; the page is not asked for. When written:
`https://www.eia.gov/electricity/data/eia923/xls/f923_2025.zip` (retrieved 2026-10-23T06:29:28Z), saved in
`warehouse/raw/eia923_monthly/` and reused. Connector: `warehouse/connectors/eia923_monthly.py`.

## Vintage and revision

January to December 2025 when written (run `20261023T063207Z`, workbook `EIA923_Schedules_2_3_4_5_M_12_2025_Final.xlsx`).
A run reads the years given with `--years` and writes the table whole.

Only years EIA keeps outside `/archive/` are read. The page read in session 897 links 2008 to 2024 under `/archive/`,
which EIA's robots file disallows (session 666), and only 2025 and 2026 (to date) outside it. An older year answers 404
at `xls/` and stops the run; it is not sought under `/archive/`. Session 897 fetched the 2026 zip only through a probe,
and the ceiling was spent before the connector could save it: a later run takes it with one request
(`--years 2025 2026`).

## Shape and variables

Series. `entity` `eia923m:<plant id>:<reported prime mover>:<reported fuel type code>:<nuclear unit id>`, the last part
empty for none (EIA's "." is read as none). `ts_utc` the month's first day, `freq` `P1M`, `geo` `US-<plant state>`
(`US-PR` for Puerto Rico), `node` the plant's name. EIA's own fields, as EIA gives them: `x_operator_id`,
`x_operator_name`, `x_nerc_region`, `x_ba_code`, `x_sector_name`, `x_chp` (combined heat and power, Y or N),
`x_mer_fuel_type`, `x_respondent_frequency` (M, A or AM when written). `market` and `vintage` are empty.

| Variable | Unit | What it is |
|---|---|---|
| `net_generation` | `MWh` | net generation (EIA's Netgen) |
| `fuel_consumed` | `TBtu` | fuel consumed in all (EIA's Tot_MMBtu times 0.000001) |
| `fuel_consumed_electric` | `TBtu` | the part of the fuel consumed to make electricity (EIA's Elec_MMBtu times 0.000001) |

Fuel is in TBtu as `eia923_plant_fuel_annual` gives it.

When written: 660,531 rows, 14,091 plants, 18,617 entities (94 with a nuclear unit), 220,177 rows of each variable,
2025-01 to 2025-12. `geo` `US-PR`: 2,874 rows, 47 plants. `net_generation` is below zero in 11,196 rows, as EIA gives
it. One entity, `eia923m:8825:ST:RFO:` (36 rows), has no state and no name in the table: its `geo` is `US` and its
`node` empty.

## Reading the sheets

- The heading row is the one, among the first ten, whose first cell is "Plant Id". Every column is found by its heading,
  not by position.
- A monthly heading is a figure and a month ("Netgen January"); a month EIA cuts short ("Septembe") is read. The 36
  monthly figures taken are Netgen, Tot_MMBtu and Elec_MMBtu; fewer than 36 stops the run. Quantity, Elec_Quantity and
  MMBtuPer_Unit are read past.
- The year-to-date totals, Physical Unit Label, Census Region, NAICS Code, EIA Sector Number and Reserved columns are
  read past. A heading not in the form read stops the run, as does a missing plant, name, state, prime mover, fuel or
  year column.
- Only rows whose YEAR is the year asked are taken.
- Plant 99999, EIA's "State-Fuel Level Increment" (an aggregate by state and fuel, not a plant), is left out, as the
  EIA-861 connectors leave EIA's 99999 out.
- A month EIA has not yet reported ("."), or leaves empty, has no row. Nothing is filled.
- A row EIA gives twice with every field the same is kept once. A key EIA gives twice with two different values has no
  key: both records are left out whole and named in the header (chain 030's rule). None when written.
- A row found in both sheets stops the run.

## License

Public: a work of the U.S. government (EIA, record 1 of `license_reads.csv`). Cite "U.S. Energy Information
Administration, Form EIA-923".

## Cross-check (session 897)

`eia923_plant_fuel_annual` ends in 2024, so the two do not overlap. Against `eia_state_generation_monthly` instead: the
plants' net generation summed by state and month equals EIA's state figure within 0.5 percent in 567 of 624
state-months, and within 2 percent in 606. The U.S. in 2025: 4,428.9 TWh here against 4,441.4 TWh. The left-out state
increments are part of the gap.

## What it does not hold

- The physical quantities (each fuel in its own unit), the heat content per unit and the energy storage sheet.
- The year-to-date totals, Census Region, NAICS code and EIA sector number.
- EIA's state-level increments (plant 99999).
- Years other than 2025 when written: 2008 to 2024 sit under `/archive/`, which is not asked for, and 2026 waits for a
  later run.
