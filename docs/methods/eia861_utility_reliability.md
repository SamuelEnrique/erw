# EIA-861 distribution reliability by utility

Energy Research Warehouse (ERW), method note written in session 695 (chain 045) for a table first written on 23 October 2026.

Tables: `eia861_utility_reliability`

## Publisher and address

U.S. Energy Information Administration (EIA), Form EIA-861 Annual Electric Power Industry Report, the reliability file
(`Reliability_<year>.xlsx` inside `f861<year>.zip`, sheets `Reliability_States` and `Reliability_Territories`), page
`https://www.eia.gov/electricity/data/eia861/`. The zips are the ones `eia861_sales.py` saved in `warehouse/raw/eia861/`
on 21 October 2026; session 695 made no request. Connector: `warehouse/connectors/eia861_reliability.py`.

## Vintage and revision

Data years 2015 to 2025 when written. A run reads the years asked (`--years`), or the newest the page links, and merges
them into the table on (entity, variable, ts_utc), so a later year adds to the table and a year read again replaces its
own rows. The header's "Years held" line names every year the file holds. EIA's robots file disallows `/archive/`, where
EIA moves older years' zips (session 666): such a year is read only from a zip already saved, never asked for.

## Shape and variables

Series. `entity` `eia861_reliability:<utility number>:<state>`, one distribution utility in one state (1,288 when
written, 1,215 utilities). `ts_utc` the data year's 1 January, `freq` `P1Y`, `geo` `US-<state>`, `node` the utility's
name. A utility reports under the IEEE 1366 standard, under its own ("other") method, or both.

| Variable | Unit | What it is |
|---|---|---|
| `ieee_saidi_with_med`, `ieee_saidi_without_med`, `ieee_saidi_minus_los` | `minute/customer` | SAIDI: minutes of sustained interruption per customer in the year |
| `ieee_saifi_with_med`, `ieee_saifi_without_med`, `ieee_saifi_minus_los` | `interruption/customer` | SAIFI: sustained interruptions per customer |
| `ieee_caidi_with_med`, `ieee_caidi_without_med`, `ieee_caidi_minus_los` | `minute/interruption` | CAIDI: minutes per interruption |
| `ieee_customers` | `count` | the customers the IEEE figures cover |
| `other_saidi_*`, `other_saifi_*`, `other_caidi_*` (`with_med`, `without_med`) | as above | the same indices by the utility's other method |
| `other_customers` | `count` | the customers the other figures cover |

`with_med`: all events, major event days included. `without_med`: major event days left out. `minus_los`: major event
days included, interruptions caused by a loss of supply (upstream generation or transmission) removed; IEEE only.

EIA's own fields: `x_utility_number`, `x_state`, `x_ownership`, `x_ieee_auto_recorded` and `x_other_auto_recorded`
(outages recorded automatically, Y or N), `x_ieee_highest_voltage_kv` and `x_other_highest_voltage_kv` (the highest
distribution voltage, kV), `x_other_inactive_included`, `x_other_momentary` (whether momentary interruptions are
counted under the other method).

Units: Decision 51 (`docs/datastandard.md`) added `minute/customer`, `interruption/customer` and `minute/interruption`.

When written: 90,705 rows.

## Reading the sheets

Every column is found by its headings. The layout changed twice: 2019 adds a Short Form column; from 2021 a third
heading row names the events ("All Events (With Major Event Days)", "Without Major Event Days", "Loss of Supply Removed
(With Major Event Days)") above headings like "SAIDI (minutes per year)". From 2015 to 2020 the events are in the
heading itself ("SAIDI With MED"), and EIA labels the IEEE loss-of-supply CAIDI "CAIDI Minus MED"; it stands where 2021
on puts that CAIDI, and is read as `ieee_caidi_minus_los`. A cell EIA leaves "." has no row; nothing is filled.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`). Cite "U.S. Energy
Information Administration, Form EIA-861".

## Cross-check (session 695)

Against EIA's own State Totals sheet (2023 to 2025), the utilities' IEEE figures weighted by their IEEE customers, by
state (51 states and DC):

| Year | Customers within 1% | SAIDI within 1% | SAIFI within 1% |
|---|---|---|---|
| 2023 | 98% | 100% | 80% (90% within 5%) |
| 2024 | 96% | 100% | 80% (92% within 5%) |
| 2025 | 61% | 69% | 63% |

2023 and 2024 agree. In 2025 EIA's State Totals cover fewer customers than its utility rows in several states (Missouri:
1,335,817 IEEE customers in the totals against 2,780,993 in the utility rows, which match 2024's 2,767,867), so the
2025 totals are not the sum of the 2025 rows; the table holds the utility rows as EIA gives them.

## What it does not hold

- EIA's State Totals sheet (an aggregate), and its "Any Standard" columns.
- A utility that reports no reliability figures (most small utilities file the short form without them).
- Momentary interruptions as a count: EIA gives only whether they are counted.
- Years before 2015 (the saved zips start at 2015; earlier zips are under `/archive/`).
