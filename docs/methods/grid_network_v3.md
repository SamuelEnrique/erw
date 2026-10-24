# The grid network, version 3: replay, a shareable address, prices, trace the power

**Since session 168 (9 October 2026) version 3 is the network page: it stands at `/network`, and `/network/v3` redirects there.** Where this note says `/network/v3`, read `/network`; where it says "the live page" or "`/network` today", read the page that stood there until session 168 (kept, unrouted, in `site/app/_retired/network-original`). The folded sections of both pages are in [`grid_network.md`](grid_network.md), "What stood on the page face until session 168".

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

## To launch-ready (session 124)

### The newest complete hour

EIA's interchange arrives pair by pair. The newest hour of the live week is usually held by a few pairs only, and a
network drawn on it shows flows that are simply not in yet as flows that are absent.

- **The live week now opens on the newest hour that every reporting pair holds** (`completeHour` in
  `site/lib/networkV3.ts`), and the page says which hour, how many pairs report, and how many of them the newest
  hour of all holds. Later hours stay on the slider.
- **A pair that has held nothing in the last 48 hours of the week has stopped reporting.** It is named, with its
  last hour, and is not waited for: one such pair would hold the page a week behind. (On 5 October 2026 one of the
  156 pairs, the Southwestern Power Administration with SPP, had been silent since 26 September.)
- The replay's index has `last_complete`: the newest day that holds nine tenths of its year's usual pairs. The
  replay's newest day held 29 of 149 pairs when this was written; the page says so on the day.

### Days the rule would leave out, and the record confirms

The replay leaves out a pair-day that stands further than 10 median absolute deviations (at least 5,000 MWh) from
the pair's own median: "a day no tie can carry". Worked by hand for Winter Storm Uri, that rule removed the days
that matter most:

| Pair | Days | What the record shows |
|---|---|---|
| MISO to SPP | 15 to 17 February 2021 | 95,060 MWh on the 15th by MISO's report, 95,390 by SPP's: two operators, 0.3 percent apart |
| Texas from Mexico | 12 to 14 February 2021 | 6,861, 7,465 and 9,061 MWh. EIA's hourly record: 382 MW in hour after hour, the level the same tie reached in hours of the 11th and the 15th, days the rule accepts. The days are unusual for how long the tie ran full, not for how much it carried |

Of the 2,732 pair-days the rule leaves out, the other balancing authority also reported 2,604, and in 1,911 the two
reports agree within 5 percent (1,901 within 1 percent). Two operators' figures for one flow that agree are not a
fault of either.

**The replay now keeps a screened pair-day that the record confirms**, by either of two tests
(`warehouse/derived/network_daily.py` `confirmed`):

1. both sides reported the day and their figures agree within 5 percent (1,911 pair-days);
2. only one side reports, EIA's hourly record of the day is held whole, and no hour is above the largest hour the
   same tie carried on days the rule accepts, by more than 1 percent (6 pair-days: Texas from Mexico above).

815 pair-days stay out. With the days kept, the trace for Texas over 12 to 19 February 2021 agrees with the same sum
worked by hand from `eia930_daily_interchange` to a hundredth of a point: SPP 84.6 percent (142,209 MWh), Mexico
15.4 percent (25,957 MWh). Before, the replay held 2,676 MWh from Mexico for the whole storm.

**This is the replay's reading only.** The monthly supply table (`ba_supply_monthly`), which the live page reads,
applies the rule as it stands. Changing it there is held for a person: see the session's report.

### Trace the power, checked by hand

- **California over 2021**, each tie read once by the network's rule, from `eia930_daily_interchange` with pandas:
  56,993,006 MWh in from nine suppliers; the trace gives 56,992,955 (the file holds a day's average MW to one
  decimal) and every share agrees to two decimals: BPAT 21.05 percent, LDWP 20.58, SRP 19.83, NEVP 15.09, AZPS
  10.94, BANC 6.25, IID 4.52, WALC 1.61, PACW 0.12.
- **The two sides of a tie do not always agree.** Read as California itself reported each tie, BANC is 3,297,404
  MWh, not 3,559,578 (BANC's own report, which the rule reads because its code sorts first), and BPAT 12,043,590,
  not 11,999,086. The page says which reading the trace uses and that the panel's twelve months use the other.
- **The period.** In the replay the trace used to cover the whole year whatever day was shown, so February 2021
  could not be isolated: Texas over 2021 read "SPP 100 percent". It now covers the day shown, its month (as it
  opens) or the year.
- **Days that hold nothing.** The trace used to say "365 days" for 2025, of which 47 hold no flow at all. It now
  says how many days of the period hold a flow for the grid.
- **Nothing is traced through Mexico.** Under Texas the second step read "CEN supplied by CISO, 100 percent": the
  Mexican operator is one name in EIA's file, but its tie to California and its ties to Texas belong to systems that
  do not connect inside Mexico.

### The hardest days, a phone, a slow machine

`site/scripts/check-network-v3-hard.mjs`, in a real browser, 24 checks: the first day, a leap day, the 23-hour and
25-hour days, the peaks of two winter storms, two days EIA's file is blank for, the replay's last day; three years
asked for in a row (the last asked for is the one shown: a year's file that arrives late no longer replaces it); a
year played across the blank weeks of late 2025; the trace on Texas in February 2021 and on a blank day; MISO's
panel.

At 390 px the page is no wider than the screen and the panel sits under the network. Frame rate at 390 px, a
headless browser drawing with software, the processor slowed by DevTools:

| | As it is | Slowed 4 times | Slowed 6 times |
|---|---|---|---|
| The live week, turning | 57 a second | 57 | 56 |
| Texas during Uri, playing | 56 | 55 | 52 |
| The replay, playing a year | 57 | 32 | 14 (longest frame 0.4 s) |

The replay is the heavy view: every day it rebuilds the flows and every sphere. On a machine six times slower than
this one a year still plays, in jumps. It was measured, not rebuilt: the drawing code is shared with the live page.

### MISO

MISO's own files are paused since 4 October 2026 ([`miso_pause.md`](miso_pause.md)). On this page MISO has no price
ring and its panel shows no price, in the live week, the stories and the replay; the panel and the fold say why. Its
flows, demand and carbon are EIA's and are shown. The replay's files still hold MISO's daily mean price from
September 2024 (they did before the pause, and the live page reads its hourly price); removing it from the files is
for the person reviewing MISO's terms.

### What replacing `/network` with this page would change for a visitor

Not done: `/network` is as it was. If the live page passed the `v3` prop, a visitor would see:

| | `/network` today | With version 3 |
|---|---|---|
| The hour the page opens on | the newest hour of the week, which few pairs hold | the newest hour every reporting pair holds, named, with the pairs that have stopped |
| A day since 2019 | not there | a date picker and "Play the year" |
| Prices | the hub price in the panel | the same, a Prices switch and a ring; **no price for MISO** (the live page shows one today) |
| Trace the power | not there | two steps, over the view, or a day, its month or its year in the replay |
| The address | always `/network` | holds the grid, the moment and the switches: a view can be shared |
| "Newest hour" line, the three measures of imports, "How fresh each layer is", the note on California's break | on the page | **not on version 3's page**, which links to `/network` for them. They would have to move across first, or the link would point at itself |
| The numbers in the panel for the live week | as now | the same figures, for the hour shown; the hour shown by default is earlier |

The checked numbers of the live page (demand, carbon, the twelve months) are read the same way by both. The one
figure a visitor would lose is MISO's price; the one that would differ on opening is every flow, because the hour
differs.

## The day carried from grid to grid (chain 077, 23 October 2026)

On the Grid tool the replay lives on the Network tab of `/grid`, and its address words are kept there as `net` (the view: `day`, a story, California's evening) and `t` (the day or hour), beside the tool's own `grid`, `view` and `shape`. Until chain 077 a reader who picked a day and then another grid lost the day: the picker's links were the grid's bare address. Now:

- **The grid picker carries the replay's day** on the Gravity tab (session 1153) and on the Network tab (the orchestrator's fix after session 1161's walk, commit `35d2c31c`): when the address holds `net=day`, each grid's link carries `net=day` and its `t` (`site/lib/carry.ts`, `KEEP_DAY`; drawn by `site/components/tool/CarryLink.tsx` through the shared `ToolPicker`'s optional `carry`, which follows the component's `replaceState` through `useSearchParams`; the server's first render carries it too). The network reads `net=day&t` at load and opens on that day; the gravity shape draws no day (it holds no generation by day) but keeps it in the address. The Mix and Clean tabs' pickers carry nothing.
- **Only a day is carried by the picker**, not an hour of the live week nor a story (session 1153's choice; the map's links below carry both).
- **A grid clicked on the map carries the whole moment** (session 1156): one of the seven ISO grids is a link to its own Network tab in the Map shape, with `net` set to the view shown (any view but the live week) and `t` to its day or hour (`carryMoment` in `site/lib/networkMap.ts`).

Decisions (chain 077):

- **The day, not the hour or the story, is what a picker carries**: a day since 2019 is the replay's shareable moment and the same day for every grid, and an hour of the live week leaves the rolling week within days ("The address" above). The owner may ask for the hour and the story too; it is a change of the carry's rule (`KEEP_DAY`), not of the page.
- **The carry is a shared piece** (`ToolPicker`'s `carry`), set on two tabs only; a picker without it draws as before.
- **The map's link carries more than the picker** because a click on the map is a move inside the same moment; the picker is a change of grid, read as a new start except for the day.

## The outside grids' demand in the replay (chain 078, 24 October 2026)

Chain 078 in this note (sessions 1164 to 1177): 1170 (this section). The replay's held hub prices (session 1167) are in `grid_network.md`, "The Exchange blocks under the gravity shape".

Session 1170, the Grid pack's blind spot 11 (`docs/reviews/packs/grid.md`, section 6): in the live week only the seven ISO grids have a demand, so a balancing authority such as BPAT has no share of demand; the replay's files hold EIA's daily demand (`eia930_daily_demand`, session 109 above) for 54 balancing authorities across the years (52 in each year's file to 2025, 54 in 2026's). The Grid tool now draws a picked day's figures on the server, from the replay's committed file, wherever the address names a day (`net=day&t=<day>`):

- **The Network tab** (`grid_network_<grid>`, first in the panel, `data-grid-replay-day="<BA>"`): for the balancing authority the address names (`node`, else the grid's own), any of the network's, BPAT as well as the seven ISO grids: the day's demand, its net export or import over the ties with a flow that day (signed from its side, positive when power left it) and how many ties held a flow, each the day's MWh over the hours of EIA's Eastern day, the day's average MW, written whole. Where the file holds no demand for it that day the cell says "not held" in the tool's one look (`Missing`), the reason on hover: the file holds no demand for that balancing authority at all (CENACE, BC Hydro), or the day's is blank (session 109's band, or not reported).
- **The Gravity tab** (`grid_gravity_<grid>`, one line under the table, `data-gravity-day`): the day's demand of the grid in view, keyed the same way, and that the shape still draws the live hour: it is sized by net generation (ruling 1a), held by hour for the live week only. The Lower 48's demand is "not held": the files hold each balancing authority's, not the whole's. The window sentence above the table, when a day is in the address, names it and says the line under the table gives its demand; without a day it reads as before.
- **The keys.** The demand is `fmt|n0|file|public/network/daily_<year>.json|demand.<BA>.@<day>`: session 1166's `file|` kind, now reading the replay's files under `site/public/network/` as well as `site/data/`, with one more path segment, `@<day>`, the element at that day's place in the file's own `days` (`site/scripts/check-file.mjs`). The net exchange and the ties are `fmt|n0|netday|export|<BA>|<day>` (or `netday|import`, a positive number) and `netday|ties|<BA>|<day>`: a new kind, since a sum over the file's links is not a path; check-values recomputes it from the same committed file with the page's rule (`netdayValue` in `site/lib/gridReplay.ts`). Neither daily table is in the live set (`warehouse/supabase/live_set.yaml`; an anon read on 24 October 2026 returned no rows for either), so each key is checked against the file alone, and check-values says so on its line.
- **On 2021-02-15** (the Uri storm), from `daily_2021.json`: BPAT's demand 7,930 MW (7,929.6 in the file), a net export of 8,121 MW (8,120.9) over its 18 ties, more than its own demand that day; ERCO's demand 50,152 MW (50,151.8), a net import of 886 MW over its 2 ties (CENACE 107.1 MW in, SPP 779.2 MW in). The node test `site/scripts/test-grid-replay.mjs` recomputes every key of every balancing authority of that day.
- **Held grids.** EIA-930's daily demand and interchange are public for every grid (`site/data/license_status.json`): nothing drawn here is held; the replay's hub prices stay as session 1167 left them, "license needed" where held, and are not in these panels.

Decisions (chain 078, session 1170):

- **The figures are the day in the address when the page was opened.** The server draws them; a day picked in the replay moves the address (the component's `replaceState`), and the page opened again, or a grid picked in the picker (which carries the day), draws that day. The note under the panel says so.
- **The day is held to the replay's first and last day, as the component holds it** (`clampDay`); an address that asks for a day outside says which day it opens on.
- **The Network tab's day is the node's, not only the grid's**, as the task names it: `grid=ercot&node=BPAT&net=day&t=2021-02-15` shows BPAT's day above ERCOT's hour. The Lower 48 without a node shows no day.
- **Whole MW**, behind `fmt|n0|`: the file holds one decimal; the browser's panel writes whole MW. The net is the sum of the file's one-decimal flows held to one decimal, so the page and the check compute the same number.
- **A new kind for the net, `netday|`, beside `file|`**: the instruction asked for the same kind; a single path cannot hold a sum of up to 18 ties, so the net reads the same committed file through a kind of its own, as `net|export` reads the snapshot for the hour.
- **The server reads the file from `site/public/network/`** (`site/lib/gridReplayFile.ts`), and `next.config.ts` traces those files into `/grid`'s function (`outputFileTracingIncludes`); a file that cannot be read is said, never filled.
- **The gravity table's own sentence keeps its words without a day**; with a day it says "no figure in this table is that day's", since the line under it is.
- **check-methods reads a `file|` path ending at `@<day>` as the figure of its last name that is not an instance** (`demand`); every other path reads as before.

## The replayed day in chain 091 (24 October 2026)

Chain 091 in this note (sessions 1178 to 1189): 1181 (a file not read), 1182 (its file), 1183 (its anchor), 1184 (its method link), 1185 (the Lower 48's demand); written by session 1188 from their reports. Each rule in full is in `grid_network.md`, in the section of the session's name.

- **A year's file not read (session 1181)**: on the Gravity tab the day's demand said "not held" when the year's committed file could not be read on the server; it now says "could not be read" (the Network tab's block already did).
- **Its file (session 1182)**: `erw_grid_replay_<BA>.csv`, named for the balancing authority shown: the day's demand, net exchange and ties.
- **Its anchor (session 1183)**: `#replayed-day`, opened with its state by `/grid?grid=ercot&view=network&net=day&t=2021-02-15&node=ERCO`.
- **Its method (session 1184)**: the line "Method: ..." at the block's foot opens the section above, "The outside grids' demand in the replay (chain 078, 24 October 2026)" (`METHOD_REPLAY` in `site/lib/gridAnchors.ts`); the words said when the year's file could not be read carry no link.
- **The Lower 48's demand stays "not held" (session 1185)**: the replay's files hold 54 balancing authorities, not US48; of the live set only `event_window_daily` holds US48 by day, for the COVID window (March 2019 to May 2020), which is not the replay's rule.

Decisions (chain 091):

- **The file is named for its node, not for a grid**: the block is drawn on the Network tab of whichever grid the address names, and session 1170's call is pinned word for word, so the block is not told the grid (session 1182).
- **The heading "The outside grids' demand in the replay (chain 078, 24 October 2026)" is a link target**, its id held to `METHOD_REPLAY` by `site/scripts/test-grid-methods.mjs`: a rename is made with the constant (session 1184).
- **No other table is read for the Lower 48's day**: a demand from another window or rule would be a figure the replay does not hold (session 1185).
