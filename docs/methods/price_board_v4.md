# The price board, version 4

Table `price_board_stats`, built by `warehouse/derived/price_board_v4.py`; and `eia_all_futures_prices`, pulled by
`warehouse/connectors/eia_futures.py`. Page: `/board/v4`, in review. Session 127. The earlier boards
([the price board](price_board.md), `/board` and `/board/v3`) are untouched.

## What it holds

Every energy price the warehouse holds as a daily series, 22 of them, and 11 spreads:

| Group | Prices | From |
|---|---|---|
| Power, day-ahead and real time | the main hub of ERCOT (hub average), CAISO (SP15), NYISO (New York City zone), SPP (North hub) and ISO-NE (internal hub): 10 | `ercot_hub_prices_daily`, `iso_hub_prices_history` |
| Natural gas | Henry Hub | `eia_fuel_spot_prices` |
| Crude oil | WTI at Cushing, Brent | `eia_fuel_spot_prices` |
| Refined products | gasoline (New York Harbor, Gulf Coast, Los Angeles), diesel (New York Harbor, Gulf Coast, Los Angeles), jet fuel (Gulf Coast), heating oil (New York Harbor), propane (Mont Belvieu): 9 | `eia_product_spot_prices` |

A power price is the mean of a complete local operating day at the hub: a day short of one interval is not a day.
A fuel price is EIA's daily spot price by trading day. Nothing is filled.

**Not read.** MISO's hub is in `iso_hub_prices_history` and is not read: its prices are paused
([the MISO pause](miso_pause.md)) and no figure is made from them. PJM's prices are not held.

## The figures

For each price, as `<measure>_<figure>` (measure `spot`, `da` or `rt`):

| Figure | What it is |
|---|---|
| `last` | the newest day held and its value (`ts_utc` is the day) |
| `change_1d` | against the day held before it |
| `change_1w`, `change_1m`, `change_1y` | against the newest day held at least 7, 30 and 365 days before the last, when that day is no more than 6 days older than that. `x_from` is that day. Otherwise the move is not held and no row is written |
| `range_low_1y`, `range_high_1y`, `range_days_1y` | the lowest and the highest value of the 365 days ending on the last day, and how many of those days are held; written when at least 180 are |
| `range_position_1y` | where the last value sits between the two: 0 the low, 1 the high |

A percent beside a move is shown on the page only where the price cannot be negative (the fuels).

## The spreads

Each is a daily series with the same figures.

| Measure | Formula | Unit |
|---|---|---|
| `spark_spread_7` | hub day-ahead daily mean - 7.0 MMBtu/MWh x Henry Hub | USD/MWh |
| `da_minus_rt` | hub day-ahead daily mean - real-time daily mean, on days both are held | USD/MWh |
| `crack_321` | (2 x U.S. Gulf Coast conventional regular gasoline + 1 x U.S. Gulf Coast ultra-low sulfur No. 2 diesel) x 42 / 3 - WTI at Cushing, on days all three are held | USD/bbl |

**The spark spread is indicative.** The heat rate of 7.0 MMBtu/MWh is an assumption, about a combined-cycle gas plant,
the same one `price_board_spreads` has used since session 7. Henry Hub is in Louisiana: it is not the gas a plant in
Texas, California, New York, the Plains or New England burns, and the local price can stand far from it (the
regional hubs are not held: below). The gas price is the operating day's, else the newest trading day's up to 4 days
before it, the trader view's rule; EIA publishes its spot prices about a week behind, so the newest spark spread is
older than the newest power price.

**The crack spread** turns the two products from dollars a gallon to dollars a barrel (42 gallons), weights two
barrels of gasoline and one of diesel, divides by three and takes off the crude: what three barrels of crude earn as
products, per barrel, before any cost of refining.

## The pull, and what EIA does and does not publish

Approved: EIA's daily spot and futures series through its open data API, 2019 to today, ceiling 600,000 rows, USD 0.
Rows returned: **21,312**, the session's probe included.

- **The daily spot series were already held.** EIA's API holds 11 daily spot series (route `petroleum/pri/spt`, and
  Henry Hub on `natural-gas/pri/fut`). All 11 have been in the warehouse since session 7, back to 1986, in
  `eia_fuel_spot_prices` and `eia_product_spot_prices`. Nothing more of them was pulled.
- **EIA publishes no daily crude grade beyond WTI and Brent.** The route's daily series are those two.
- **EIA's futures end on 5 April 2024.** Its pages say: "Futures prices after April 5, 2024, are not available". The
  API's newest day for crude oil, heating oil, RBOB gasoline and natural gas contracts 1 to 4 is 2024-04-05; its
  propane and older gasoline contracts ended in 2009 and 2006. The sixteen that reach 2024 were pulled from 2019:
  `eia_all_futures_prices`, 21,240 rows, a closed history. There is no current natural gas futures price to set
  beside Henry Hub from a free source.

## EIA's terms, quoted

From `https://www.eia.gov/about/copyrights_reuse.php`, read 5 October 2026:

> U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.

and, under "Protected materials":

> You may see on our website documents, illustrations, photographs, or other information resources contributed or licensed by private individuals, companies, or organizations that may be protected by U.S. and foreign copyright laws. Transmission or reproduction of protected items beyond that allowed by fair use as defined in the copyright laws requires the written permission of the copyright owners.

EIA asks for an acknowledgment: "Source: U.S. Energy Information Administration" with the publication date. Its open
data page says: "EIA data is provided free of charge and should be used in compliance with our Copyrights and Reuse Policy."

**The notices on these series.** EIA's definitions pages name where each comes from, and say nothing more:

| Series | EIA's page says |
|---|---|
| Daily spot prices of crude oil and products | "Sources: Refinitiv, an LSEG business" |
| Henry Hub spot | "Spot Price: Refinitiv, an LSEG business." |
| Futures | "Crude oil futures: New York Mercantile Exchange (NYMEX)"; "Futures Prices: New York Mercantile Exchange (NYMEX)."; "Official daily closing prices at 2:30 p.m. from the trading floor of the New York Mercantile Exchange (NYMEX)" |

None of these notices forbids republishing in so many words. None says the series is EIA's own either, and the
"protected materials" passage is general.

**How the tables are marked, and why.**

- `eia_all_futures_prices`: **internal**, by this session's reading, for a person to rule. The prices are an
  exchange's settlement prices, the exchange licenses them, and EIA stopped republishing them. That is three reasons
  to hold them back and no words that require it. Nothing on the board shows them.
- `eia_fuel_spot_prices` and `eia_product_spot_prices`: **public**, as they have been since session 7. This session
  did not change that. EIA names a commercial provider as their source too. If the reading that holds the futures
  back is right, a person should rule on these as well; they are read by pages that were live until 5 October 2026.
- `price_board_stats`: public, derived from public tables.

## What is named in the plan and not held

No free source gives these, and nothing stands in for them on the board. Each row is shown greyed with the source
that would supply it.

| Price | The source that would supply it |
|---|---|
| Regional natural gas hubs | S&P Global Commodity Insights (Platts) or Natural Gas Intelligence |
| TTF | ICE Endex or LSEG |
| JKM | S&P Global Commodity Insights (Platts) |
| Uranium | UxC or TradeTech |
| Carbon allowances by the day | ICE |
| Lithium | Fastmarkets or Benchmark Mineral Intelligence |
| NYMEX futures after 5 April 2024 | CME Group |

The warehouse does hold monthly averages from the IMF for European gas, Japan's LNG and uranium
(`fred_imf_commodity_prices`), and the quarterly auction results of California and RGGI (internal). A monthly average
is not a daily price, and the board does not show one as if it were.

PJM's prices need a license the ERW does not hold. MISO's are paused since 4 October 2026. The page says both in the
words `/board/v3` already uses.

## The daily refresh

`warehouse/refresh_board_v4.sh` runs the builder and the validator under `warehouse/health.py`. It is written and
not scheduled. The tables the builder reads are already refreshed by the daily run, so switching it on is one step in
`warehouse/run_daily.sh` after `price_board`, and, when the page opens, a live-set rule for `price_board_stats` so the
page reads the live set and not the site's own copy.
