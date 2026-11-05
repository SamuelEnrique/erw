# Croatia's transmission network a year from 2017 (HOPS, Elektroenergetski podaci)

Energy Research Warehouse (ERW), method note written in session 2829 (chain 144) for a table first written on 26 October 2026 (session 2823).

Tables: `hops_croatia_annual`

## Publisher and address

HOPS (Hrvatski operator prijenosnog sustava), Croatia's transmission system operator. Its page "Elektroenergetski podaci" (`https://www.hops.hr/elektroenergetski-podaci`) holds one table of the transmission network's yearly figures.

Source id `hops:elektroenergetski_podaci`. Connector: `warehouse/connectors/hops_croatia.py` (session 2823), whose raw store is `warehouse/raw/hops_croatia/`. www.hops.hr and hops.hr have no robots file (HTTP 404, reads 1641 and 1642).

## Vintage and revision

Written by run `20261026T065052Z` (offline), which read the page retrieved at 2026-10-26T06:49:59Z: 2017 to 2025. HOPS adds a year when it closes one.

## Shape and variables

Series, 126 rows, 9 years:
- `entity` `hops:hr`, or `hops:hr:<source>` for production (hydro, thermal, wind, solar).
- `variable`:
  - `generation`, the transmission network's production by source and its total;
  - `imports` (into Croatia, half of Krško's output included), `exports` and `net_imports`;
  - `energy_carried`, the energy carried on the transmission network;
  - `peak_load` and `minimum_load`, with the day and hour the page prints;
  - `consumption` (on the network, losses not included), `losses`, and `direct_customer_delivery` (to customers connected to the transmission network).
- `unit` MWh (the page's GWh times 1,000), or MW for the two loads (the page's MWh/h, the hour's mean).
- `ts_utc` the year's 1 January; `freq` P1Y; `geo` HR; `x_label` the page's row (in Croatian); `x_day` and `x_hour` for the loads.

**Figures:**
- 2024: production 11,924,000 MWh, imports 13,010,000, exports 7,951,000; peak load 3,363 MW (17 July 2024, at 20h).
- Wind: 1,088,000 MWh in 2017, 2,883,000 in 2025.

## Reading the source

- A dot is the page's thousands separator ("4.809" GWh is 4,809 GWh).
- **The page's balances, within 1 GWh: 20 of 36 hold.**
  - Every year, the sources make the total, and imports less exports make the net.
  - **From 2018 the energy carried exceeds both production plus imports and consumption, losses plus exports, by the same amount:** 102 GWh in 2018, rising to 372 in 2025. It is an inflow the page does not name. It is kept as published, counted, and listed in the run log, not given a row of its own.
- Nothing is filled. The run stops on no table, a header not of years, a row not in the expected structure, or a value not a number.

## License

**Internal.** HOPS's terms page (`https://www.hops.hr/odredbe-i-uvjeti`, read 1645) covers the use of personal data only, with a copyright line ("© 2026. Hrvatski operator prijenosnog sustava d.d."). It gives no terms of reuse, so the table waits for HOPS's terms or its written permission (session 2825's report).

## Cross-check

Against `eurostat_electricity_production_annual` (all of Croatia, gross), MWh:

| Year | Source | HOPS (transmission network) | Eurostat | Share |
|---|---|---|---|---|
| 2019 | hydro | 5,606,000 | 5,826,100 | 0.962 |
| 2022 | hydro | 4,712,000 | 5,459,700 | 0.863 |
| 2024 | hydro | 5,847,000 | 6,727,000 | 0.869 |
| 2024 | wind | 2,419,000 | 2,576,600 | 0.939 |
| 2024 | solar | 46,000 | 820,000 | 0.056 |

The transmission network carries most hydro and wind, but little solar, which is mostly on the distribution network.
