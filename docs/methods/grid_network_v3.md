# The grid network, version 3: replay, a shareable address, prices, trace the power

Version 3 of the network (`/network/v3`, in review) is the network of [`grid_network.md`](grid_network.md) with four
additions. Its look is unchanged: free-floating, a light background, carbon intensity as the sphere color, names on
hover, the four Watch buttons, the panel and the Batteries switch. The live page `/network` passes none of this and is
as it was.

## The replay: any day since 2019

**Source.** `eia930_daily_interchange`: EIA-930's daily interchange of every pair of balancing authorities, in MWh, by
EIA's Eastern day, from 2019-01-01. `warehouse/derived/network_daily.py` writes one file per year,
`site/public/network/daily_<year>.json`, and an index, `daily_index.json`. Nothing is written to `warehouse/output`;
the files are the site's, like the two stories.

**A frame is a day.** A pair's flow is the day's MWh over the hours of that Eastern day (24; 23 or 25 on the two days
the clocks change): the day's average MW, so that a day draws on the scale an hour draws on.

**Each pair is counted once**, by the network's own rule: read from the balancing authority whose code sorts first, as it
reported it; on a day it did not report, from the other's report with the sign flipped. A day neither reported is
blank, never filled.

**Screened days.** A pair-day further than 10 median absolute deviations, and at least 500 MWh, from the pair's own
median over its history is left blank. It is the screen of `ba_supply_monthly` (`ba_supply.screen`), applied for the
same reason: EIA's daily interchange holds days no tie can carry, and one such day would set the scale of a year. Each
year's file counts its screened pair-days, and the page prints the count.

**What a replayed day does not hold.** Demand: the warehouse holds no daily demand history, so the panel gives a day's
net imports in MW and no share of demand. The batteries: not held by day. Balancing authorities that reported in those
years and have no place in today's network are not drawn, and are named.

**Carbon intensity** is that day's (`carbon_intensity_daily`, `intensity_generation`), for the seven ISO balancing
authorities; elsewhere the sphere is grey, as on the live network.

**The controls.** A date picker (held to the first and last day of the replay) shows a day. "Play the year" plays the
days of the year shown, from the day shown to the year's last day and round again, at about five days a second.

## The address

The address holds the view (`view`: the live week, California's evening, a story, or `day`), the moment (`t`: an hour
of a story or of the live week, or a day), the grid selected (`grid`, its EIA code) and the switches (`batteries`,
`prices`, `trace`). Only what differs from the page as it opens is written, so the page's own address stays bare.

Opening an address restores its view without playing it: a shared link shows a moment. An hour of the live week that
has since left the rolling week cannot be shown; the page says so and shows the newest. Anything an address holds that
the page does not understand is ignored. While a view plays the address is not rewritten; it is written when it stops.

## Prices

The Prices switch is off by default. On, it draws a second ring, outside the batteries' ring, around each grid whose
main hub has a public real-time price held for the moment shown. The ring's weight follows the price: the square root
of the price's share of the highest price of the period shown, so that one scarcity hour does not turn every other
ring into a hair. A price at or below zero is the thinnest ring. The panel gives the number, and with the switch on,
the lowest and highest of the period shown.

**Which grids.** The live week and the stories: the hub prices the page already reads. The replay: the mean of the
real-time hourly prices of the Eastern day, only when every hour of that day is held; ERCOT from 2019, and CAISO,
ISO-NE, MISO, NYISO and SPP from September 2024, where the warehouse's price history begins. PJM never: its prices are
licensed. A hub is not a site: the price at a hub is not what power cost at every point of the grid.

## Trace the power

For the grid selected, over the period shown (every frame of the view: the live week, a story's window, or the year
of the replay):

1. **Its suppliers:** the neighbours whose net flow into it over the period is positive, largest first, each with its
   MWh and its share of what all of them supplied.
2. **Their suppliers:** for each of those, the neighbours whose net flow into it over the same period is positive (the
   grid selected is never listed), the four largest, each with its share of what that supplier took in.

A frame's MWh is its MW times its hours (one for an hour; the Eastern day's hours for a day). A frame a tie did not
report adds nothing.

**What it is not.** These are physical flows over ties, as each balancing authority reported them to EIA: not
contracts, and not where the power was generated. A supplier generates most of what it sends; listing its own
suppliers says only what flowed into it over the same period, never that their power is the power passed on. A tie
that carried power both ways counts by its balance over the period.

## Checks

- `tests/test_session93.py`: the builder on rows made for the test (the pair rule, the other side's report, a screened
  day, a 23-hour day, a price only for a complete day) and on the files as built (every array as long as its year, a
  frame equal to the table's row); the address, the day's hours, the ring's weight and the trace, run in Node; and that
  the live page passes nothing of version 3.
- `site/scripts/check-network-v3.mjs`: each addition in a real browser, and the live page as it was.
- `site/scripts/test-network.mjs` (session 68), unchanged, still passes on the live page.

## The replay's share of demand (session 109)

A replayed day of `/network/v3` now gives, for the grid chosen, its net imports as a share of its demand that day, and
each supplier's flow as a share of the same demand.

- **Demand** is `eia930_daily_demand` (`warehouse/connectors/eia930_daily_demand.py`, an approved pull of session 109):
  EIA's daily demand of every balancing authority, API route `electricity/rto/daily-region-data`, type D, EIA's Eastern
  day, from 2019-01-01. 190,512 rows for 71 respondents (balancing authorities and EIA's regions) to 2026-10-03, of a
  ceiling of 300,000. Public domain. EIA's terms (`https://www.eia.gov/about/copyrights_reuse.php`, read 4 October
  2026): "U.S. government publications are in the public domain and are not subject to copyright protection. You may
  use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that
  are on our website".
- **In the replay's files** a day's demand is its MWh over the hours of that Eastern day (24; 23 or 25 on the two days
  the clocks change): the day's average MW, the scale the flows are on. So a tie's average MW over the grid's average
  MW is that supplier's share of the day's demand. 54 of the network's balancing authorities have a demand.
- **A day's demand is used** when it is above zero and between half and twice the median of the six days around it
  (three before, three after, those held). 109 days of the history fail that and carry no demand and no share. EIA's
  daily demand is its own sum of the hours it holds: a day with hours missing at the source can be far off, and that is
  what the band catches. A day inside the band can still hold one impossible hour (`docs/methods/impossible_hours.md`):
  PJM's 224,345 MW of 13 July 2020 adds about 4 percent to that day.
- **What a share is not:** a share of the grid's supply (its own generation is not in the replay), nor a contract. The
  flows are physical, between neighbours.
- The live week's shares are as they were: hourly demand of the seven ISOs. The live page `/network` does not draw the
  replay and is unchanged.
