# EIA-861 distribution systems and distributed generation by utility

Energy Research Warehouse (ERW), method note written in session 891 (chain 048) for tables first written on 23 October 2026.

Tables: `eia861_distribution_systems`, `eia861_distributed_generation`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report, the distribution
systems file (`Distribution_Systems_<year>.xlsx`, a States and a Territories sheet) and the distributed generation file
(`Non_Net_Metering_Distributed_<year>.xlsx`, the generators on distribution systems that are not net metered; its
utility-level sheets only), inside `f861<year>.zip`, page `https://www.eia.gov/electricity/data/eia861/`. The zips are
the ones `eia861_sales.py` saved in `warehouse/raw/eia861/` (rows retrieved 21 October 2026); session 883 made no
request. Connectors: `warehouse/connectors/eia861_distribution_systems.py` and
`warehouse/connectors/eia861_distributed_generation.py`, one for each file, each written on its own. The session's second
slot was meant for the dynamic pricing file; chain 047's session 868 had already written it (`eia861_dynamic_pricing`),
so the slot took the distributed generation file. The net-metered generators are in `eia861_net_metering`.

## Vintage and revision

`eia861_distribution_systems`: data years 2015 to 2025 when written (run `20261023T043627Z`).
`eia861_distributed_generation`: data years 2016 to 2025 when written (run `20261023T043744Z`). 2015's distributed
generation file has another form (technology totals without sectors, and a separate dispersed generation sheet) and is
not taken; the connector refuses a year before 2016. A run reads the years given with `--years` and writes its table
whole. 2015 to 2024 come from zips under EIA's `/archive/zip/`, 2025 from `/zip/`. EIA's robots file disallows
`/archive/` (session 666): such a year is read only from a zip already saved, never asked for.

Utilities a year in `eia861_distribution_systems`: 1,815 to 1,821 from 2015 to 2018, 2,833 in 2019, 1,223 to 1,236
from 2020, the year EIA moved the small utilities to the short form (sessions 881 and 882). 2019 holds more rows than
the years around it in both tables (distribution systems 5,996 against 2,415 to 3,939; distributed generation 36,608
against 8,245 to 17,935).

## Shape and variables

Series. `ts_utc` the data year's 1 January, `freq` `P1Y`, `geo` `US-<state>`, `node` the utility's name.

`eia861_distribution_systems`: `entity` `eia861_ds:<utility>:<state>`; EIA's balancing authority column, where it gives
one, is read past. EIA's own fields: `x_utility_number`, `x_state`.

| Variable | Unit | What it is |
|---|---|---|
| `distribution_circuits` | `count` | the utility's distribution circuits in the state |
| `circuits_voltage_optimization` | `count` | the circuits with voltage or VAR optimization |

`eia861_distributed_generation`: `entity` `eia861_dg:<utility>:<state>:<balancing authority>`; the balancing authority
is empty where EIA gives none. EIA's own fields: `x_utility_number`, `x_state`, `x_ba_code`, `x_capacity_type`.

The technologies are `pv`, `battery`, `wind`, `hydro`, `fuel_cell`, `internal_combustion`, `combustion_turbine`,
`steam`, `other` and `total`; the sectors `residential`, `commercial`, `industrial`, `transportation`,
`direct_connected` and `total`.

| Variable | Unit | What it is |
|---|---|---|
| `number_of_generators` | `count` | generators not net metered |
| `total_capacity` | `MW` | their total capacity |
| `capacity_backup_only` | `MW` | capacity used for back-up only |
| `capacity_utility_owned` | `MW` | capacity the utility owns |
| `<technology>_capacity_<sector>` | `MW` | capacity by technology and sector; `battery` is EIA's "Storage", later "Battery" |
| `battery_energy_<sector>` | `MWh` | EIA's "Battery Energy (MWh)", kept apart from the battery capacity |

`x_capacity_type` is EIA's column "Type": `AC` (130,236 rows), `DC` (19,872 rows) or nothing (29,053 rows), whether the
utility gives the capacity in alternating or direct current. Session 883 wrote it as `x_data_type`, described as A actual
and E estimated; this note's reading found the values, and session 891 renamed the column, corrected the header and the
docstring, and wrote the table again (run `20261023T053132Z`; the same rows and figures).

When written:

- `eia861_distribution_systems`: 34,947 rows, 2,862 utilities, 3,035 entities, 2015 to 2025. All utilities: 204,884
  circuits in 2015 and 206,255 in 2025; those optimized rose from 44,006 to 59,566.
- `eia861_distributed_generation`: 179,161 rows, 705 utilities, 750 entities, 70 variables, 2016 to 2025. All
  utilities: 2,143 MW in 2016, 6,922 MW in 2025 (3,897 MW solar, 939 MW and 2,937 MWh of batteries).

## Reading the sheets

- Distribution systems: each column is found by its heading, not by position. A heading the map does not know stops the
  run. A Short Form column is read past.
- Distributed generation: every column is found by its stacked headings (a technology, a sector), not by position, with
  the reader of `eia861_programs.py`. The technology headings are read as prefixes, the longer first, so "Battery Energy"
  is not read as "Battery". EIA's 2016 file has a title row over the headings. Each sheet must give the ten technology
  totals and at least 64 figures; else the run stops. A heading the map does not know stops the run. A Short Form column
  is read past.
- Distributed generation sheets: `Utility_Level-States` and `Utility_Level-Ter` in 2016, `States` and `Territories` from
  2017 to 2022, `States_ Utility Level` and `Territories` from 2023. The `States- State Level` sheet (no utility) is
  not read; EIA gives it in 2023, 2024 and 2025.
- "Storage" and "Battery" read as one technology, `battery`, in MW. EIA's heading is "Storage" from 2016 to 2022 and
  "Battery" from 2023, beside the new "Battery Energy (MWh)"; `battery_energy_` holds 2023, 2024 and 2025. The session
  883 report and the first header gave 2025 for the change; session 891 corrected the header.
- EIA's aggregates 88888 and 99999 are left out, as `eia861_sales.py` leaves them; in the distributed generation file
  99999 holds EIA's "State Adjustment" rows.
- A cell EIA leaves "." (and, in distribution systems, a blank cell) has no row. Nothing is filled.
- A row EIA gives twice with every field the same is kept once. Two rows under one key (utility and state; utility,
  state and balancing authority for distributed generation) with different values have no key: both are left out whole
  and named in the header (chain 030's rule). When written, none in either table.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`; `docs/licenses.md`: public,
agrees for both tables). Cite "U.S. Energy Information Administration, Form EIA-861".

## Cross-check (session 883)

- Circuits with optimization never exceed the circuits (15,914 of 15,914 records).
- Distributed generation: the technologies sum to the total in 4,884 of 4,884 records, the solar sectors to solar's
  total in 4,010 of 4,010, and the total capacity equals the technologies' total in 4,869 of 4,872.
- 2025's utilities summed by state against EIA's own state-level sheet: 6,884 MW against 6,864, apart by EIA's "State
  Adjustment" rows (utility 99999), which the table leaves out as every EIA-861 table does.

## What it does not hold

- 2015's distributed generation file (another form) and EIA's state-level distributed generation sheets.
- EIA's aggregates 88888 and 99999, the "State Adjustment" rows among them.
- Net-metered generators (in `eia861_net_metering`).
- A balancing authority for the distribution circuits.
- A single generator or circuit: only each utility's counts and capacity by state.
- Years before 2015 for distribution systems (the saved zips start at 2015), before 2016 for distributed generation.
