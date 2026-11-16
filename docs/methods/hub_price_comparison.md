# Where power is cheap: hub and zone prices compared

One derived table, `hub_price_comparison`, behind the page `/prices/compare` ("Where power is cheap", in review),
built by `warehouse/derived/price_compare.py`. No request is made: the builder reads price tables the warehouse
already holds.

Tables: `hub_price_comparison` (named here by session 2960).

**A hub is not a site.** A hub or zone price is an average over many points of a grid. The price at one substation
differs from it by congestion and losses, and what a buyer pays adds delivery, capacity and other charges. The table
compares markets; it does not price a location.

## Inputs

| Table | What it gives |
|---|---|
| `iso_hub_prices_history` | day-ahead and real-time prices from September 2024 at six main hubs: CAISO SP15 and NP15, ISO-NE Internal Hub, NYISO N.Y.C., SPP North, and MISO Indiana (not used: below) |
| `ercot_all_hub_prices_history` | ERCOT's six trading hubs, day-ahead and real-time, from 2015 |
| `iso_dam_hub_prices`, `iso_rtm_hub_prices` | the daily run's hubs since late August 2026: CAISO 3, ERCOT 6, SPP 2 (and MISO 8, not used) |
| `isone_dam_zone_prices`, `isone_rtm_zone_prices`, `isone_rtm_zone_prices_hourly` | ISO-NE's eight load zones and its hub, since late August 2026 |
| `nyiso_dam_zone_prices`, `nyiso_rtm_zone_prices` | NYISO's eleven zones, since late August 2026 |
| `carbon_intensity_daily` | each grid's carbon intensity of generation by day (EIA-930 emissions; California by the warehouse's join) |

A row held in two tables is read once, from the first of the list.

## What is not derived, and why

- **MISO's hubs (8): held, not shown.** MISO's terms of use forbid automated access and say "You are not permitted to
  modify, publish, transmit, participate in the transfer or sale of, reproduce, create derivative works of, distribute,
  publicly perform, publicly display or in any way exploit any of the materials or content on this Website". Pulls of
  MISO are paused pending a review of those terms by a person ([`miso_pause.md`](miso_pause.md)). Until that review
  this table derives nothing from MISO's prices. The builder reads `warehouse/metadata/paused_sources.csv`: when the
  pause is lifted, MISO's hubs are compared on the next build.
- **Any price table marked internal** in `coverage.csv` is left out the same way, by name. None of the tables above
  is internal today.
- **PJM: not held.** The warehouse has no PJM hub or zone energy price; PJM's prices are licensed.

The page lists each of these by name with the reason and no number.

## The two windows

In each grid's own local time, ending with the last calendar month that every hub of the history holds to its end:

- **Twelve months** (`freq P1Y`, `ts_utc` the first day of the window): the hubs with a year of history. Eleven as
  built: ERCOT's six, CAISO SP15 and NP15, ISO-NE Internal Hub, NYISO N.Y.C., SPP North.
- **The last whole month** (`freq P1M`): every hub and zone held. Thirty-one as built.

The zones are in the month and not in the year because the warehouse has pulled them only since late August 2026.

## The measures

For each market, `dam` (day-ahead) and `rtm` (real-time), over the hours held in the window:

| Variable | Unit | Meaning |
|---|---|---|
| `<m>_avg_price` | USD/MWh | the mean of the hourly prices |
| `<m>_negative_hours_share_pct` | percent | the share of hours with a price below zero |
| `<m>_above_200_hours_share_pct` | percent | the share of hours with a price above USD 200 per MWh |
| `<m>_day_spread_top4_bottom4` | USD/MWh | on the average day (the mean price of each local hour of the day over the window), the mean of its four dearest hours less the mean of its four cheapest. The four need not be next to each other |
| `<m>_hours_held`, `<m>_hours_in_window` | count | |

and for the hub's grid:

| Variable | Unit | Meaning |
|---|---|---|
| `grid_carbon_intensity` | kgCO2/MWh | the mean of the daily carbon intensities of generation held in the window |
| `grid_carbon_days_held` | count | |

**An hour of real-time price** is the mean of its four 15-minute prices (themselves means of the operator's
five-minute prices), and is held only when all four are. ISO-NE's real-time price is held two ways, as 15-minute means
and as ISO-NE's own hourly report; the one that holds more of the window is used, whole, never mixed with the other.

**When a figure is not written.** A market of a hub, when fewer than 95 percent of the window's hours are held (as
built: ISO-NE's real-time price over the twelve months, 8,112 of 8,760 hours; SPP South's real-time price for the
month). The grid's carbon intensity, when fewer than 90 percent of the window's days are held (as built: SPP over the
twelve months, 236 of 365 days). Nothing is filled.

**The carbon intensity is the grid's, not the hub's:** every hub of a grid carries the same figure. It is the average
generation of the balancing authority, not the marginal plant.

## What the table does not hold

Nodal prices; delivered prices; any price of PJM or MISO; zones over twelve months; a forecast.

## Rebuilding

```bash
python warehouse/lock.py run --task "hub price comparison" --minutes 15 -- <python> warehouse/derived/price_compare.py --snapshot
python warehouse/derived/price_compare.py --out-dir DIR      # a trial: nothing in warehouse/output
```

The table is rebuilt whole each run: the windows move with the last whole month.

## The replication (session 7012, chain 301)

`replication/compare/replicate.py` recomputes every figure of `site/data/price_compare.json` from the tables above by
this note alone (their order, each grid's local time, the four quarters of a real-time hour, ISO-NE's better-held form,
the 95 and 90 percent floors): 578 of 578 equal on the file rebuilt on 16 November 2026. It found one fault, now fixed:
an hour of real time whose four prices sum to zero is an hour of zero, and the builder rounds its mean to 9 places so the
float sum's noise does not count it as negative (`docs/reviews/price-compare-faults-2026-11-16.md`). `replicate.do`
rebuilds five ERCOT figures of the twelve months in Stata, its expected values at its top.

## Checks

`tests/test_session96.py`: the measures on prices made for the test (the mean, the two shares, the spread of a known
average day, an hour of real time only from four quarter hours, a window with too few hours not written, the hours of
a window across a clock change); a paused publisher's hubs are named and carry no row; the table as built against the
price tables for two hubs, computed again by hand; the site's copy equal to the table; and the page's choices and its
ordering, run in Node. `site/scripts/check-prices-compare.mjs`: every number the page shows, against the site's copy.

## The cross-checks (session 7018, chain 301)

The comparison is computed from the operators' own prices; no second public publisher of the same hub averages is held (ICE's indices, as EIA republishes them, are internal). What stands:

| Check | Result |
|---|---|
| Every figure of the page's file recomputed from the price tables by this note (the replication) | 578 of 578 equal, after one fault fixed (an hour of zero counted below zero) |
| The board's EIA closes for the same months beside the World Bank's monthly averages (fuels, not power) | `docs/methods/price_board.md`, "The cross-checks" |

Not yet read: the operators' own annual market reports (ERCOT's and CAISO's average day-ahead hub prices for a year), which would set a published yearly average beside the twelve months.

## The decisions on the page (session 7018, chain 301)

The page draws these at its foot (`site/lib/decisions.ts`, `COMPARE_DECISIONS`), each choice's default and source on hover:

1. A hub or zone price is an average over many points of a grid: the price at one substation differs by congestion and losses, and a buyer pays delivery and capacity on top. The page compares markets, not locations. **Default:** Hubs and zones only; no nodal or delivered price. **Source:** The operators' hub and zone definitions; docs/methods/hub_price_comparison.md, its opening paragraph. (session 96)
2. Two windows, each in the grid's own local time: the twelve months and the last whole month, both ending with the last calendar month that every hub of the history holds to its end, so no hub is compared over a month another lacks. **Default:** Twelve months and the last whole month, ending with the last month every hub holds. **Source:** docs/methods/hub_price_comparison.md, "The two windows". (session 96)
3. A market of a hub is written when at least 95 percent of the window's hours are held, and a grid's carbon intensity when 90 percent of its days are; below that the cell names what is held, and nothing is filled. **Default:** 95 percent of the hours; 90 percent of the days for carbon. **Source:** docs/methods/hub_price_comparison.md, "When a figure is not written". (session 96)
4. A real-time hour is the mean of its four 15-minute prices, themselves means of the operator's five-minute prices, and counts only when all four are held; ISO-NE's two real-time series are never mixed, the one holding more of the window is used whole. **Default:** Four 15-minute means an hour, all four held; one ISO-NE series a window. **Source:** The operators' real-time prices; docs/methods/hub_price_comparison.md, "The measures". (session 96)
5. The share of hours below zero counts an hour whose mean, rounded to nine places, is below zero, so an hour of four prices that sum to exactly zero is not negative. **Default:** Below zero after rounding the hour's mean to nine places. **Source:** docs/reviews/price-compare-faults-2026-11-16.md, row 1; warehouse/derived/price_compare.py, hourly(). (sessions 96 and 7012)
6. The share of hours priced above USD 200 per MWh is the page's measure of scarce hours: one round threshold for every grid, not each operator's own scarcity signal. **Default:** USD 200 per MWh on every grid. **Source:** The page's own choice; docs/methods/hub_price_comparison.md, "The measures". (session 96)
7. The day spread is taken on the average day of the window: the mean price of each local hour of the day, then the mean of its four dearest hours less the mean of its four cheapest, which need not be next to each other. **Default:** Four dearest less four cheapest hours of the average day. **Source:** docs/methods/hub_price_comparison.md, "The measures": what four hours of storage could shift on an average day. (session 96)
8. The carbon intensity beside a hub is its grid's average generation by day, the same figure for every hub of a grid, not the marginal plant's and not the hub's own. **Default:** The grid's average carbon intensity of generation. **Source:** EIA-930's hourly emissions by balancing authority, California by the warehouse's join. (session 96)
9. MISO's hubs are held and not shown while its terms are reviewed, and PJM's prices are not held at all: each is named with the reason and no number. **Default:** MISO held without a figure; PJM not held. **Source:** MISO's terms of use (docs/methods/miso_pause.md); PJM's market data license. (session 96)

## What waits for the owner (session 7018)

- MISO's hubs (its terms, under review) and PJM's prices (a license).
- Whether a grid's own scarcity signal should stand beside the round USD 200 threshold.

## Sign-off

- Signed off by:
- Date:
- Items of the section above ruled, and how:
