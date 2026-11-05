# What power plants paid for coal and natural gas, by state, a month (EIA, Form EIA-923)

Energy Research Warehouse (ERW), method note written in session 2004 (chain 056) for a table first written on 6 October 2026 (session 132).

Tables: `eia_power_plant_fuel_costs`

## Publisher and address

U.S. Energy Information Administration (EIA), electric power operational data, receipts and cost of fossil fuels (Form EIA-923; page cited `https://www.eia.gov/electricity/data/browser/`), through the EIA API v2 route `electricity/electric-power-operational-data`: `https://api.eia.gov/v2/electricity/electric-power-operational-data/data/?frequency=monthly&data[0]=cost-per-btu&data[1]=cost&facets[sectorid][]=98&facets[fueltypeid][]=COW&facets[fueltypeid][]=NG&start=2019-01`, sorted by period, location and fueltypeid, pages of 5,000. Sector 98 is the electric power sector; COW all coal products, NG natural gas. Source id `eia:electricity/electric-power-operational-data:cost`. Connector: `warehouse/connectors/eia_board.py` (session 132), one of its three tables. The key from `EIA_API_KEY` is sent apart from the address, so the address kept in `source_url` and in the raw files has none.

## Vintage and revision

January 2019 to July 2026 in the file on the data machine. Its header: rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261022T152428Z-github`, from the connector's run `20261022T150605Z`; "10,991 rows returned, 13,006 values", and 8,976 measures not written (13,006 plus 8,976 is 21,982, two measures for each of the 10,991 records). The rows' `retrieved_at` are 6 October 2026 (11,903 rows) and 22 October 2026 (1,103 rows).

Each run reads the whole history from January 2019, deletes the file and writes the table again, so EIA's revisions are taken. A table whose newest month is more than 150 days old is not written.

## Shape and variables

Series, 13,006 rows, 196 series over 98 entities. `entity` `eia:plant_fuel_cost:<location>:<COW|NG>`; `ts_utc` the month's first day; `freq` P1M; `node` EIA's name of the location (for example "Alaska", "East North Central"); `market` and `vintage` empty.

| Variable | Unit | Fuel | Rows | Series |
|---|---|---|---|---|
| `cost_per_mmbtu` | USD/MMBtu | coal and gas | 6,503 | 98 |
| `cost_per_short_ton` | USD/short_ton | coal | 2,941 | 45 |
| `cost_per_mcf` | USD/Mcf | gas | 3,562 | 53 |

- 58 locations: US (`geo` US), 47 states (`geo` `US-<state>`; Delaware, DC, Hawaii and Vermont have no row) and EIA's ten census divisions ENC, ESC, MAT, MTN, NEW, PCC, PCN, SAT, WNC and WSC (`geo` empty). Coal has 45 locations, gas 53.
- The U.S. series hold all 91 months.

## Reading the API

- The rows read must equal the total the API reports, or the table is not written.
- Each record carries two measures, `cost-per-btu` and `cost`. A measure that is empty, "W", "NA", "--", "null" or "None", or exactly 0 (EIA's figure for a state and month with no deliveries), is not written and is counted; any other value that is not a number stops the table. California's coal has no row.
- Units: "dollars per million Btu" is USD/MMBtu; `cost` in "dollars per short tons" is `cost_per_short_ton` and in "dollars per Mcf" `cost_per_mcf`; any other unit stops the table. An (entity, variable, ts_utc) given twice stops it.
- A negative cost is kept as EIA gives it: 14 rows, natural gas in New Mexico (August 2024, October 2025, March to May 2026), Arizona (April 2026) and Wyoming (February 2022).
- Ceiling: 1,500,000 rows returned in a run, counted from session 132's 1,300 rows of probes; past it the run stops. A page is tried up to four times; pages are 0.4 seconds apart.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (session 2004)

- The counts above were computed from the rows, read past the header lines.
- The two measures imply a heat content: for the U.S. coal, cost per short ton over cost per MMBtu is 18.52 to 19.48 MMBtu a short ton in all 91 months; for the U.S. gas, cost per Mcf over cost per MMBtu is 1.030 to 1.038 MMBtu an Mcf. July 2026: coal 47.33 USD a short ton and 2.4913 USD/MMBtu; gas 3.48 USD/Mcf and 3.3682 USD/MMBtu.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- Fuels other than coal and natural gas, the quantities received, and sectors other than the electric power sector (98).
- Plants: receipts and costs by plant are `eia923_fuel_receipts` (method note `eia923_receipts.md`).
- Months before 2019, and the states and months EIA withholds or gives as 0.
