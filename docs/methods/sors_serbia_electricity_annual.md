# Serbia's balance of electricity, a year (SORS's Energy Balances, table 1)

Energy Research Warehouse (ERW), method note written in session 2527 (chain 123) for a table first written on 24 October 2026 (session 2525).

Tables: `sors_serbia_electricity_annual`

## Publisher and address

The Statistical Office of the Republic of Serbia (SORS), its bulletin "Energy Balances, 2024" (final data, February 2026), table 1, "Balance of Electricity in 2024": `https://publikacije.stat.gov.rs/G2026/pdf/G20265730.pdf`. One GET, no key. Source id `sors:energy_balances_2024`. Connector: `warehouse/connectors/sors_serbia_electricity.py` (session 2525). www.stat.gov.rs, data.stat.gov.rs and publikacije.stat.gov.rs have no robots file (reads 964, 965, 967).

## Vintage and revision

2024, written by run `20261024T192418Z` (the write under the lock, offline), which read the bulletin saved at 2026-10-24T19:20:48Z. `vintage` is its last-modified time, 2026-02-26T07:42:33Z. Each year's bulletin has its own address; the connector reads the 2024 one.

## Shape and variables

Series, 36 rows, 20 entities. `entity` `sors:rs:<item>`; `unit` MWh (SORS's GWh, printed to three decimals, times 1,000); `ts_utc` 2024-01-01; `freq` P1Y; `geo` RS; `node` and `x_label` the row's Serbian label.

| `variable` | Items | 2024, TWh |
|---|---|---|
| `primary_production` | solar, wind, hydro (the table's first three columns) | 0.16, 1.35, 10.51 |
| `imports`, `exports`, `gross_available` | total | 6.94, 6.42, 0.52 (imports less exports) |
| `transformation_input` | total, pumped_storage | 0.51 |
| `gross_production` | total, hydro, wind, solar, thermal, chp, autoproducers | 37.49 (thermal 23.22) |
| `own_use` | total and eleven branches (thermal 2.39, coal mines 0.63, refineries 0.31) | 3.96 |
| `losses` | total | 3.98 |
| `available_final`, `final_consumption` | total; industry, construction, transport, households, agriculture, other_consumers | 29.55 (households 13.23, industry 9.56) |

A section's total holds its rows: a sum over entities takes one level.

## Reading the source

- The run stops at once, asking nothing, while `sors_energy_balances` or publikacije.stat.gov.rs is paused.
- One request a run (timeout 180 seconds); `--offline` reads the saved bulletin.
- **The page:** the one that holds table 1's title, "GWh" and the losses row. Each line is a label and four cells (solar, wind, hydro, electricity), "-" for none, a decimal comma.
- **Labels:** a footnote mark ("1)", "2)") is dropped, and a label beginning with a Latin E is read with the Cyrillic Е (the bulletin prints "Eнергија" so).
- **Sections:** the input to transformation, production by transformation, own use in the energy sector, and final consumption for energy purposes set the variable of the plant, branch and sector rows under them; a single row (imports, exports, gross available, losses, energy available for final consumption) ends a section.
- **Rows not taken:** those the balance prints with only "-" for electricity (stock changes, bunkers, the other energy products' branches); one of them holding a figure stops the run.
- The run stops, and no file is written, for: no such page, a row not in the map, a row before its section, a figure of another form, a key given twice.

Nothing is filled.

## License

Public. SORS's copyright page (read 966): "Files and statistical data from this website may be downloaded, reproduced, distributed, shared, and used for commercial and non-commercial purposes (unless otherwise indicated), provided that any changes to the data are clearly indicated and the Statistical Office of the Republic of Serbia (SORS) is cited as the source of the original data." Verdict (session 2525): may be public. The header states the scaling to MWh and cites SORS. Held from the live set; in the next Stanford draft.

## Cross-checks (session 2525)

- Each section's parts sum to its total.
- `eia_world_electricity_annual`, Serbia, 2024: imports and exports equal SORS's to the MWh; EIA's generation 36.99 TWh against SORS's gross production 37.49 TWh.

## What it does not hold

- Years before 2024 (earlier bulletins); monthly figures; the other energy products' balances; prices (RSD).
