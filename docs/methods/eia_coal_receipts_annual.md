# Coal receipts at power plants, mine to plant

Energy Research Warehouse (ERW), method note written in session 877 (chain 047) for a table first written on 23 October 2026.

Tables: `eia_coal_receipts_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), coal receipts at power plants (Form EIA-923), API v2, route
`coal/shipments/receipts`:
`https://api.eia.gov/v2/coal/shipments/receipts/data/?frequency=annual&data[]=quantity&data[]=price&data[]=heat-content&data[]=sulfur-content&data[]=ash-content&start=2008`,
in pages of 5,000. EIA's browser page: `https://www.eia.gov/coal/data/browser/`. Connector:
`warehouse/connectors/eia_coal_receipts.py` (session 875). The API key is read from the environment and is redacted in
every address the table records.

Why this route (session 870): the route `coal/shipments/by-mine-by-plant` (69,067 annual records, 2008 to 2025) gives
several records for one mine, plant, supplier, coal type and year, with different quantities, prices and qualities, and
no field that tells them apart: 16,078 records, about 23 percent, among them the largest flows. By chain 030's rule such
records have no key, so session 870 wrote no table. The receipts route carries the contract type and the transport mode,
and with them nearly every record has a key.

## Vintage and revision

Years 2008 to 2025, retrieved 2026-10-23T03:39:59Z. A snapshot: each run reads the route again from 2008 and replaces the
table whole, so a value EIA revises is replaced. `vintage` is empty. Ceiling 15 requests a run (3 seconds apart; a page
saved in `warehouse/raw/eia_coal_receipts/` is reused unless `--fresh`). Session 875 made 12 requests (the trial's 12
pages); the write reused them (0 requests).

## Shape and variables

Series. Key `entity`, `variable`, `ts_utc`. `entity`
`eia_coal_receipt:<mineMSHAId>:<plantId>:<supplier>:<coalRankId>:<contractType>:<transportationMode>`, EIA's codes and the
supplier's name as a slug (an empty part is `none`). `ts_utc` the year's 1 January, 00:00:00Z; `freq` `P1Y`; `geo`
`US-<plant state>`; `market` empty; `node` the mine, the supplier and the plant by name.

Variables and units:

- `quantity`: short_ton, the coal received.
- `price`: USD/short_ton, EIA's average delivered price.
- `heat_content`: Btu/lb, the coal's heat content per pound. `Btu/lb` joined the unit vocabulary by Decision 52
  (session 870, `docs/datastandard.md`).
- `sulfur_content`, `ash_content`: pct by weight.

A value EIA leaves empty or withholds has no row; nothing is filled. A unit not in the connector's map stops the run.

Rank `TOT` is EIA's sum of the ranks beside it (`x_rank` "All"). Leave it out of a sum over ranks, or the coal is counted
twice. In 2020, TOT is 419.4 million short tons = 130.6 bituminous + 241.4 subbituminous + 43.9 lignite + 3.5 waste coal.

`x_*`, EIA's own fields: `x_msha_id` (the mine's MSHA id), `x_mine_state`, `x_mine_county`, `x_mine_basin`,
`x_mine_type`, `x_plant_id` (EIA's plant code, as in `eia860_plants_annual`), `x_plant_state`, `x_supplier`, `x_rank`,
`x_contract_type`, `x_transport_mode`.

Records without a key: a row EIA gives twice with every field the same is kept once. Where one key and year carry two
different values, every record under it is left out whole, not summed or chosen (chain 030's rule). The header counts
104 such keys, the figure the session report gives as 104 of 57,066 records (0.2 percent). The table holds 56,858
mine-plant-year records of EIA's 57,066.

When written: 270,547 rows; 27,749 entities; 1,129 mines; 471 plants in 47 states; 1,205 suppliers; 18 years.
Rows a variable: quantity, heat_content, sulfur_content and ash_content 56,858 each, price 43,115 (EIA withholds the
rest). Records by rank: TOT 28,409, BIT 16,589, SUB 10,971, WC 498, LIG 387, ANT 4. By contract type: contract purchase
40,113, spot-market purchase 14,807, new contract 1,772, none given 166. By transport mode: rail 37,441, river 11,226,
truck 7,286, tramway or conveyor 787, tidewater piers 58, water 28, Great Lakes 18, pipeline 12, none given 2.

## License

Public: a work of the U.S. government. EIA's terms (record 1 of the license reads, `docs/licenses.md`): its data "are in
the public domain and are not subject to copyright protection". Verdict in `docs/licenses.md`: public. Cite "U.S. Energy
Information Administration, Form EIA-923".

## Cross-check (session 875)

- The TOT receipts' quantity-weighted price against EIA's electric power sector delivered price
  (`eia_coal_delivered_price_annual`, U.S.): within 1.1 percent every year from 2016 to 2025 (2020: 36.52 against 36.13
  USD/short_ton); 2.2 to 13 percent below in 2008 to 2015, when more prices were withheld.
- The table links the mines of `eia_coal_mine_production_annual` to the plants of `eia860_plants_annual` and
  `eia923_plant_fuel_annual`.

## What it does not hold

- The records under the 104 keys with two different values, left out whole.
- Prices EIA withholds (no row, not filled).
- Months: only annual records are read.
- Years before 2008 (the connector starts at 2008).
- The by-mine-by-plant route's records, which have no key (session 870).
