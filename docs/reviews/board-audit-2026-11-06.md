# The price board audit, 6 November 2026

Energy Research Warehouse (ERW), session 1600 (chain 165, the old laptop's second window). Every public price, cost, charge, capacity and carbon series the warehouse holds, against what `/board` draws today; the gap as a numbered list; the held series with their publisher and the hold's words; the board's data file and builder; the daily run's `board` step. This file is the chain's faults file: every numbered row carries a state, and each later session marks the rows it closes.

Read on: `site/data/board.json` as origin's main holds it (built `2026-11-05T17:41:31Z`, 992,917 bytes), `warehouse/metadata/coverage.csv` on origin's main, `warehouse/derived/board_page.py`, `docs/methods/price_board.md`, and the tables in this machine's `warehouse/output` (the old laptop's copies, last refreshed 2 to 22 October 2026: their entities and variables were read from them, their dates are not the warehouse's newest; the coverage's dates are).

## 1. What the board draws today

1,200 rows in 20 groups: 1,106 with values, 94 placeholders. Columns of a row: latest value and date, the day, week, month and year moves, the 7-day and 30-day means, the 30-day low and high, the last 30 points (with hover), the one-year range, and on four groups the futures column ("licensed source needed").

| Group | Rows with values | Placeholders | Newest date drawn | Tables |
|---|---:|---:|---|---|
| power | 22 | 66 (NYISO 22, ISO-NE 18: license needed; MISO 16: paused; PJM 10: licensed) | 2026-10-30 | `ercot_all_hub_prices_history`, `iso_hub_prices_history`, the rolling hub and zone tables |
| peak | 30 | 0 | 2026-10-30 | the same |
| spark | 15 | 2 | 2026-10-31 | the hub rows, `eia_fuel_spot_prices`, `eia_power_plant_fuel_costs` |
| da_rt | 31 | 0 | 2026-10-29 | the hub rows |
| battery | 62 | 0 | 2026-10-30 | the hub rows |
| as | 43 | 4 | 2026-10-30 | `ercot_as_prices`, `caiso_as_prices`, `nyiso_as_prices`, `spp_as_prices` |
| gas | 1 | 7 | 2026-10-27 | `eia_fuel_spot_prices` |
| gasprices | 255 | 0 | 2026-07-01 | `eia_gas_prices_state_monthly` |
| crude | 44 | 1 | 2026-10-27 | `eia_fuel_spot_prices`, `eia_crude_stream_prices` |
| products | 9 | 2 | 2026-10-27 | `eia_product_spot_prices` |
| oilspreads | 2 | 0 | 2026-10-27 | the product and crude rows |
| world | 9 | 0 | 2026-09-01 | `wb_commodity_prices_monthly` |
| retailfuel | 40 | 0 | 2026-10-26 | `eia_regional_retail_fuel_prices` |
| heating | 140 | 0 | 2026-10-19 | `eia_heating_fuel_prices_weekly` |
| retailpower | 248 | 0 | 2026-08-01 | `eia_retail_electricity_prices` |
| plantfuel | 143 | 5 | 2026-08-01 | `eia_power_plant_fuel_costs` |
| metals | 5 | 2 | 2026-09-01 | `imf_commodity_prices` |
| rates | 3 | 0 | 2026-10-28 | `frb_treasury_yields` |
| carbon | 4 | 3 | 2026-09-14 | `carb_lcfs_credit_prices`, `carb_auction_allowance_prices` |
| other | 0 | 2 | | |

Rows by step: 706 monthly, 216 daily, 182 weekly, 2 quarterly, 94 placeholders without a step.

## 2. Every public price, cost, charge, capacity and carbon series held, against the board

Sub-annual series only: the board draws daily, weekly, monthly and quarterly rows (the method note's rule since session 1117; annual tables are named in section 4). Granularity is the table's own; "newest" is `coverage.csv`'s `ts_max` on origin's main.

| Table | License | Series (this machine's copy) | Unit | Step | Newest | On the board |
|---|---|---|---|---|---|---|
| `ercot_all_hub_prices_history` | public | 6 hubs, DA hourly, RT 15-minute | USD/MWh | PT1H, PT15M | 2026-10-31 | power, peak, da_rt, battery, spark |
| `iso_hub_prices_history` | public; NYISO, ISO-NE, MISO rows held | main hubs and NP15, ZP26 | USD/MWh | PT1H, PT15M | 2026-11-07 | the same (held grids blank) |
| `iso_dam_hub_prices`, `iso_rtm_hub_prices` | public; MISO held | every hub of CAISO, ERCOT, SPP | USD/MWh | PT1H, PT15M | 2026-11-07, 2026-11-05 | the same |
| `nyiso_dam_zone_prices`, `nyiso_rtm_zone_prices` | license needed (NYISO) | 11 zones | USD/MWh | PT1H, PT15M | 2026-11-07, 2026-11-05 | placeholders |
| `isone_dam_zone_prices`, `isone_rtm_zone_prices`, `isone_rtm_zone_prices_hourly` | license needed (ISO-NE) | hub and 8 zones | USD/MWh | PT1H, PT15M | 2026-11-07, 2026-11-05 | placeholders |
| `iso_zone_prices_history` | public; NYISO held | CAISO ZP26, NYISO's 11 zones, SPP South day-ahead | USD/MWh | PT1H, PT15M | 2026-11-03 | not read: the same series come from the rolling tables (gap 26) |
| **`ercot_zone_prices_history`** | public | **ERCOT's 8 load zones day-ahead (LZ_AEN, LZ_CPS, LZ_HOUSTON, LZ_LCRA, LZ_NORTH, LZ_RAYBN, LZ_SOUTH, LZ_WEST), 4 in real time (Houston, North, South, West)** | USD/MWh | PT1H, PT15M | 2026-11-01 | **not drawn (gap 1)** |
| `ercot_hub_prices_daily` | public, derived | the hubs' daily means | USD/MWh | P1D | 2026-11-06 | not drawn: the board computes the same days from the hourly rows |
| **`ercot_rtm_price_adders`** | public | **the real-time adders: RTORPA, RTOFFPA, RTORDPA (mean and max of the hour, last value 2025-12-05 on this machine), RTRDPA (to 2026-10-18 here)** | USD/MWh | PT1H | 2026-11-01 | **not drawn (gap 6)** |
| **`node_basis_summary`** | public, derived | **ERCOT's nodes against the hub average by month: day-ahead basis p10 to p90, the 4-hour spread, by technology (all, gas, solar, wind, storage)** | USD/MWh | P1M | 2026-11-01 | **not drawn (gap 4)** |
| `node_basis_daily` | public, derived | each node's daily basis | USD/MWh | P1D | 2026-11-04 | not drawn: nodes, one row each would be thousands (gap 4 summarizes them) |
| **`ercot_storage_node_basis`** | public, derived | **ERCOT's storage nodes against the hub by week: spread at the node and at the hub, medians, p10 and p90** | USD/MWh | P1W | 2026-09-28 | **not drawn (gap 4)** |
| `ercot_rtm_node_prices`, `ercot_node_prices_hourly` | public; internal | nodes | USD/MWh | PT15M, PT1H | 2026-11-05 | not drawn (nodes) |
| `ercot_as_prices`, `caiso_as_prices`, `spp_as_prices` | public | reserves and regulation, day-ahead hourly | USD/MW-hour | PT1H | 2026-10-31, 2026-11-06, 2026-10-04 | as |
| `nyiso_as_prices` | license needed (NYISO) | | USD/MW-hour | PT1H | 2026-10-05 | placeholder |
| `ercot_as_prices_daily`, `ercot_as_prices_monthly` | public, derived | roll-ups of `ercot_as_prices` | USD/MW-hour | P1D, P1M | 2026-10-30, 2026-10-01 | not drawn: roll-ups of rows drawn |
| **`ercot_4cp_intervals`** | public | **ERCOT's four coincident peak intervals a year, 2018 to 2025, with the system load** | MW | PT15M | 2025-09-04 (2018 to 2025 in coverage) | **not drawn (gap 7)** |
| `eia_fuel_spot_prices` | public | Henry Hub, WTI, Brent | USD/MMBtu, USD/bbl | P1D | 2026-11-03 | gas, crude |
| `eia_product_spot_prices` | public | nine product spots | USD/gal | P1D | 2026-11-03 | products, oilspreads |
| `eia_crude_stream_prices` | public | first purchase, landed, F.O.B., refiner acquisition | USD/bbl | P1M | 2026-09-01 | crude |
| **`eia_crude_first_purchase_prices`** | public | **2 series: F002038__3, F003075793** | USD/bbl | P1M | 2026-08-01 | **not drawn; whether they repeat a crude stream row is not checked (gap 13)** |
| `eia_regional_retail_fuel_prices` | public | gasoline regular and diesel: US, PADDs, states, cities | USD/gal | P1W | 2026-11-02 | retailfuel |
| **`eia_retail_fuel_prices`** | public | **US diesel, US gasoline regular, US gasoline all grades (EMM_EPM0)** | USD/gal | P1W | 2026-11-02 | **not drawn; all grades is no row of the board (gap 12)** |
| `eia_heating_fuel_prices_weekly` | public | heating oil and propane, residential and wholesale | USD/gal | P1W | 2026-10-19 | heating |
| `eia_gas_prices_state_monthly` | public | citygate, homes, commercial, industrial, electric power by state | USD/Mcf | P1M | 2026-07-01 | gasprices |
| **`eia_lng_exports_monthly`** | public | **the export price at 8 terminals (Cameron, Calcasieu Pass, Cove Point, Corpus Christi, Elba Island, Freeport, Plaquemines, Sabine Pass) and the export volume at 9 (and Golden Pass)** | USD/Mcf, MMcf | P1M | 2026-08-01 | **not drawn (gap 9)** |
| **`eia_gas_trade_monthly`** | public | **US LNG exports and imports, pipeline trade with Canada and Mexico, by month** | MMcf | P1M | 2026-07-01 | **not drawn (gap 9)** |
| **`eia_gas_storage_weekly`** | public | **working gas in storage: Lower 48 and the five regions, salt and nonsalt** | Bcf | P1W | 2026-10-16 | **not drawn (gap 8)** |
| `eia_power_plant_fuel_costs` | public | coal and gas delivered to plants by state | USD/MMBtu, USD/short ton | P1M | 2026-08-01 | plantfuel, the dark spread |
| `eia_retail_electricity_prices` | public | by state and sector | USD/MWh | P1M | 2026-08-01 | retailpower |
| `imf_commodity_prices` | public | uranium, lithium, cobalt, nickel, copper | USD | P1M | 2026-09-01 | metals |
| `wb_commodity_prices_monthly` | public (CC BY 4.0) | crude (4), coal (2), gas US and Europe, LNG Japan | USD | P1M | 2026-09-01 | world |
| `frb_treasury_yields` | public | 2, 10, 30 years | percent | P1D | 2026-11-04 | rates |
| `carb_lcfs_credit_prices` | public | weekly credit price, all and Type 1 | USD/t CO2e | P1W | 2026-09-14 | carbon |
| `carb_auction_allowance_prices` | public | current and advance auction settlement | USD/t CO2e | P3M | 2026-08-01 | carbon |
| `epa_rfs_rins_monthly` | public | RINs generated and batch volume by D code (no price) | count, gal | P1M | 2026-09-01 | not drawn: volumes, no RIN price is held (gap 19) |
| `cftc_cot_positions` | public | positions in WTI, Henry Hub and products futures | contracts | P1W | 2026-10-20 | not drawn: positions, not prices (gap 24) |
| `eia_steo_forecasts` | public | EIA's monthly forecasts, prices among them | | P1M | 2027-12-01 | not drawn: a forecast, not a price (gap 25) |
| `bcrp_peru_hydrocarbons_monthly` | public | Peru | | P1M | 2026-08-01 | not drawn: outside the board's markets |
| `hub_price_comparison`, `cost_of_power_*`, `merchant_revenue_monthly`, `price_years_by_window` | license needed (held grids) or public, derived | the other pages' computations | | P1M | | not drawn: other tools' figures |
| `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads` | public, derived | the first board's tables | | P1D | 2026-11-07 | read by `/grid`, not by `/board` |

## 3. The gap, numbered

State: **open** until a session closes it; each closing session writes its number and the test that proves it.

| # | Gap | Group | Session | State |
|---:|---|---|---|---|
| 1 | ERCOT's load zones: 8 day-ahead, 4 real time (`ercot_zone_prices_history`), with on-peak, off-peak, battery spread and day-ahead less real time as the hubs have | power | 1601 | closed in 1601 (`tests/test_board_1601.py`) |
| 2 | The real-time row's interval is not stated: "real time" says nothing of ERCOT's 15-minute, CAISO's 15-minute mean of 5-minute or SPP's 5-minute prices, nor that the row is a daily mean of complete hours | power, peak, da_rt, battery | 1601 | closed in 1601 (`tests/test_board_1601.py`) |
| 3 | No hub-to-hub spread: ERCOT North less Houston, West less North, South less Houston; CAISO NP15 less SP15; SPP North less South; across grids where both are public (ERCOT hub average less SPP North, CAISO SP15 less ERCOT hub average). Asked in `docs/reviews/trader-path.md`, step 15 | spreads | 1606 | open |
| 4 | ERCOT's node basis: no row summarizes it (`node_basis_summary`, `ercot_storage_node_basis`); the node view is `/cost-of-power` | power | 1601 | closed in 1601 (`tests/test_board_1601.py`) |
| 5 | Capacity prices: one placeholder for four operators; none of `iso_all_capacity_prices`' rows is public (the table is internal), so a placeholder for each operator with its auction and publisher | other | 1601 | closed in 1601 (`tests/test_board_1601.py`) |
| 6 | ERCOT's real-time price adders (`ercot_rtm_price_adders`, public): no row; three of the four end on 5 December 2025 in this machine's copy, so their rows must say when they stop | power | 1601 | closed in 1601 (`tests/test_board_1601.py`) |
| 7 | ERCOT's 4CP: the year's four peaks are held (`ercot_4cp_intervals`) and drawn nowhere on the board; the Texas delivery charges (`texas_delivery_charges`) are internal | cost group | 1604 | open |
| 8 | Gas in storage, weekly (`eia_gas_storage_weekly`): no row; the week's position is what a gas trader reads first | gas | 1602 | open |
| 9 | LNG: the export price by terminal and the export volumes (`eia_lng_exports_monthly`, `eia_gas_trade_monthly`) are not drawn; LNG feedgas by the day is not held | gas | 1602 | open |
| 10 | Regional gas hubs: four placeholders (Waha, SoCal Citygate, Algonquin, Chicago); Houston Ship Channel, Transco Zone 6 New York, Dominion South and the Northwest are not named | gas | 1602 | open |
| 11 | TTF and JKM by the day: placeholders as they should be; their World Bank months are in the world group and no row says so beside them | gas | 1602 | open |
| 12 | US retail gasoline, all grades (`eia_retail_fuel_prices`, EMM_EPM0): no row | retailfuel | 1603 | open |
| 13 | `eia_crude_first_purchase_prices`: two series not checked against the crude stream rows | crude | 1603 | open |
| 14 | Crack spreads by product: only the two 3-2-1 cracks; no gasoline crack, no diesel crack, no heating oil crack | oilspreads | 1607 | open |
| 15 | Coal by basin: placeholders (S&P Global) as they should be; the coal rows of the world group are not named beside them | plantfuel | 1603 | open |
| 16 | The PADD series: drawn in retail fuel and heating; the spot products are New York Harbor, Gulf Coast and Los Angeles only (EIA's daily set) | products | 1603 | no gap: noted |
| 17 | RGGI's row says "held internal while the publisher's terms are reviewed" with status `not_held`, and names no publisher: a held series must print "licensed source needed" and name the publisher (RGGI, Inc.) | carbon | 1604 | open |
| 18 | ISO-NE's ancillary row: the same, status `not_held`, no publisher named | as | 1604 | open |
| 19 | RIN prices: none held; EPA's RIN volumes are held. A placeholder that names the source | carbon | 1604 | open |
| 20 | Uranium: the IMF's month is drawn and the daily spot is a placeholder (UxC, TradeTech) | metals | 1604 | no gap: noted |
| 21 | Retail electricity: drawn by state and sector, newest month August 2026 | retailpower | | no gap |
| 22 | The moves: day, week, month and year are drawn; year to date is not | all | 1608 | open |
| 23 | The trend line: the last 30 points; the chain asks for the last ninety days (or the step's equivalent) | all | 1609 | open |
| 24 | CFTC positions: not a price; not drawn | | | out of scope: for a ruling |
| 25 | EIA's STEO price forecasts: not a market price; not drawn | | | out of scope: for a ruling |
| 26 | `iso_zone_prices_history` is not read by the builder: its CAISO ZP26 and SPP South day-ahead reach back further than the rolling tables (ZP26 and SPP South have no one-year range on the board) | power | 1601 | closed in 1601 (`tests/test_board_1601.py`) |
| 27 | The spark spread uses Henry Hub for every grid; no regional gas price is held to replace it (licensed); the heat rate is stated, its source is not | spark | 1606 | open |
| 28 | The ERCOT 4CP exposure: needs the year's peaks and a load shape; the peaks are held (gap 7) | spark | 1606 | open |
| 29 | The LNG netback: needs a destination price and shipping and regasification costs; only the World Bank's monthly Japan LNG and Europe gas are held, no freight | oilspreads | 1607 | open |

## 4. Not drawn, by the board's rule

Annual tables: `eia_coal_prices_annual`, `eia_coal_delivered_price_annual`, `eia_coal_trade_price_annual`, `eia_coal_price_rank_annual`, `eia_power_costs_annual`, `ercot_peak_premium_annual`, `pjm_rpm_capacity_prices` (internal, by delivery year). Contracts by signing date: `lbnl_ppa_prices`, `lbnl_hybrid_ppa_prices`. Tariffs as events: `utility_large_load_tariffs`. The day-ahead alert days: `caiso_dam_alert_day_hub_prices`.

## 5. The held series: publisher and the hold's words

| Row or rows | Status on the board | Publisher | The hold's words (as the builder writes them) |
|---|---|---|---|
| MISO, every hub, both markets; MISO's spark and dark; MISO's reserves | paused | MISO | "MISO's terms forbid automated access to its site, so the ERW stopped asking for its prices on 4 October 2026 until a person has reviewed the terms. No MISO value is shown." |
| PJM, five hubs, both markets; PJM's spark and dark; PJM's reserves | licensed | PJM | "PJM publishes its prices under a license and an account the ERW does not hold. Source that would supply them: PJM Data Miner, under PJM's data license." |
| NYISO and ISO-NE, every hub and zone, and every row built from them | licensed (`warehouse/metadata/license_status.csv`, from 21 October 2026) | NYISO, ISO-NE | `ls.note(grid)`: the publisher's sentence read in session 205 asks for written permission |
| NYMEX futures, contracts 1 to 4 (Henry Hub, WTI, RBOB, heating oil) and the futures column | licensed | CME Group | "EIA's NYMEX contracts 1 to 4 end on 5 April 2024 ... Source that would supply the curve: CME Group." |
| Waha, SoCal Citygate, Algonquin Citygate, Chicago Citygate | licensed | S&P Global Commodity Insights (Platts), Natural Gas Intelligence | "Source that would supply it: ... daily indices." |
| TTF, daily | licensed | ICE Endex, LSEG | "Source that would supply the daily price: ICE Endex or LSEG. ..." |
| JKM, daily | licensed | S&P Global Commodity Insights (Platts) | "Source that would supply the daily price: ..." |
| Coal spot by basin (5) | licensed | S&P Global | "EIA shows the week's coal spot prices with S&P Global's permission and says the history is proprietary and cannot be released." |
| Uranium, daily; lithium, daily | licensed | UxC, TradeTech; Fastmarkets, Benchmark Mineral Intelligence | "Source that would supply it: ..." |
| European carbon (EUA) | licensed | ICE Endex | |
| Renewable energy credits | licensed | S&P Global Commodity Insights, ICE | |
| Capacity prices (PJM, NYISO, ISO-NE, MISO) | licensed | each operator | "Auction results are held internal while each operator's terms are reviewed." |
| Energy equities | licensed | an exchange data vendor | |
| RGGI auction | not_held (gap 17) | RGGI, Inc. | "The auction results are held internal while the publisher's terms are reviewed; not shown." |
| ISO-NE reserves and regulation | not_held (gap 18) | ISO-NE | "Held internal while ISO-NE's terms are reviewed; not shown." |

## 6. The data file and the builder

`site/data/board.json`, one line of JSON: `built`, `sources` (each row's source written once, a row points at it by index), `heat_rate` 7.0, `coal_heat_rate` 10.5, `gas_back_days` 4, `slack_days` 6, `groups` (id, title, filters, `curve`), `rows`, `week` (31 hubs), `spikes` (40). A row with values: `id`, `group`, `label`, `at`, `code`, `unit`, `freq`, `tags`, `source`, `status`, `last {t, v}`, `moves {d, w, m, y}` each `{t, v, ch, pct}`, `range {lo, hi, n, pos}`, `avg7`, `avg30`, `lo30`, `hi30`, `spark {t0, d, v}` (30 points), and where they apply `hourly`, `hub`, `formula`, `inputs`, `curve`, `also`. A placeholder: `id`, `group`, `label`, `at`, `code`, `unit`, `freq` "", `tags`, `status`, `note`. Beside it: `site/public/board/s/<id>.json` (a row's whole history) and `site/public/board/h/<id>.json` (a hub's hours).

`warehouse/derived/board_page.py`, `build()`: the hourly store of every price table from 2019 (`hourly_store`), `build_power` (hubs and zones, on-peak and off-peak, battery, day-ahead less real time; held grids as placeholders; MISO and PJM listed), `build_as`, `build_fuels` (gas, crude, products, retail fuel, plant fuel, retail electricity, metals, rates, carbon, capacity and equities), `build_world`, `build_gas_prices`, `build_heating`, `build_spreads` (spark, heat rate, dark, the two cracks), `build_week`; `write_site` writes the files. Every table is asked for first (`here()`): one absent is noted and its rows are not built, and `page_keep.py` keeps the rows held.

The page (`site/app/board/page.tsx`, `site/components/board/BoardView.tsx`, `site/lib/board.ts`) draws `groups` and `rows` as they come: a new row or group in the file is drawn in the existing form with no change to the page.

## 7. The daily run's board step

- The runner: `warehouse/run_daily.sh`, step `board` (`warehouse/health.py run --step board -- bash warehouse/refresh_board.sh`: the four connectors, the validator, then `page_keep.py board`, which runs the builder into a temporary folder and takes a row only where it is no older and no shorter than the held one), then the board's tests (`tests.test_session132`, `240`, `1118`, `1139`): a board they refuse is put back as committed.
- The data machine: `warehouse/run_data_machine.sh`, step `dm_board_page` (`page_keep.py board`, on the machine that holds ERCOT's history), then the group `dm_test_board`.
- Last built: the file on main says `2026-11-05T17:41:31Z` (the data machine's run of 5 November, commit `3709610b6`); the runner's run of 6 November (`e2794ff06`) built it again, and session 2885 (`06434e862`) put back the rows that run had thinned.
- A new group or row reaches the page only through a daily run's build: this chain changes the builder, and its rows appear on the page the first day a data machine runs it after the branch lands.
