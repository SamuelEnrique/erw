# Session 553 report: coal receipts not pulled (no key EIA gives is unique); the delivered price by state and sector in their place

21 October 2026, from 22:09 UTC, on lab-desktop (the data machine), a session of `queue/done/030-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **Coal receipts at power plants (route `coal/shipments/receipts`): probed, not pulled.** EIA's records are by plant, mine, contract, transport mode, supplier and rank: 1,372 in 2024.
  - With all eleven fields EIA gives, 4 of them still repeat with two different prices. E C Gaston's contract coal from Town Creek, for one, appears at 162.05 and 159.85 a ton.
  - No field tells the two apart, so neither can be written without inventing a key. A weighted average would be a figure of mine, not EIA's.
- **In its place, by the chain's rule: EIA's average delivered price of coal by state or region and consuming sector** (route `coal/consumption-and-quality`, the Quarterly Coal Report), unique on its two fields. `warehouse/connectors/eia_coal_delivered_price.py` writes `eia_coal_delivered_price_annual`.
  - 3,213 rows: 228 series, 2000 to 2025, in `USD/short_ton`. Many of EIA's figures are withheld and have no row.
  - Locations: states, census divisions and the U.S. Sectors: utilities, independent producers with and without CHP, electric power, commercial, coke plants and other industrial. The header says a sum takes one level.
  - EIA's quantities (short tons) and qualities are not taken.
- **Cross-check** (`runs/s553/crosscheck.py` on the data machine): the electric power sector's price by state against `eia_power_plant_fuel_costs`' coal cost per short ton. 151 state-years (2019 to 2025): median ratio 1.000, middle half 0.996 to 1.002.
- **Held** from `/data` and Redivis v1. Sector rule (`coal`). Tests: `tests/test_session553.py`, 4.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 6 of 30 | the receipts route and a 2024 page; the consumption and quality route and a 2024 page; the trial (2) |

## For Samuel's ruling

- Whether coal receipts by plant and mine are wanted, with their repeated records kept as EIA gives them (a row number in the key), or not at all.

## Files

- New: `warehouse/connectors/eia_coal_delivered_price.py`, `tests/test_session553.py`, this report. Changed: the shared metadata, holds and package.
