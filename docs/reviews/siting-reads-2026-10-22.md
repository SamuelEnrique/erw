# The All grids tab's reads, 22 October 2026

Energy Research Warehouse (ERW), session 716 of chain 050, on samueloldlaptop (the code machine), 22 October 2026 at about 11:30 UTC. Session 580's read timer (`lib/supabase.ts`, on when the server starts with `ERW_READ_TIMING=1`) was on for the whole run, on a local production build of `wip/715-allgrids` (which holds sessions 700 to 715) served at `http://localhost:3715`.

## The tab reads nothing from the database

- **Every address of the tab answered with no read of the database**: 0 lines of `[erw-read]` across the nine addresses below, three times each, and three more first requests after a fresh start.
  - The tab reads only the site's own files: the hub and zone price files of "Your load", `site/data/siting/*.json`, and "Your load"'s rules, waits, demand and large-load files.
  - `tests/test_session716.py` holds that no file of the tab imports the site's database reader.
- **The timer was on**: "Your load" (`/cost-of-power`), requested twice in the same run, made 80 requests, 40 distinct reads (below).
- **No index is needed by the tab**, so session 580's unapplied migration (`warehouse/supabase/migrations/036_slow_read_indexes.sql`) is unchanged.

## The build

`npm run build` of the whole site on this machine: **64 s**, then **32 s** with a warm cache: under the 90 s asked. The tab is server-rendered at each request (`/cost-of-power` is dynamic), so it adds no page to the build.

## Each address's answer, in milliseconds

On this machine, with the internal cookie, the server warm, three tries each; then the first request after a fresh start ("cold"), which computes every row once (the results are kept in the process: `lib/siting.ts`'s memo).

| Address | Warm, ms (three tries) | HTML, MB |
|---|---|---|
| `/cost-of-power?view=allgrids` | 129 / 120 / 118 | 1.73 |
| `/cost-of-power?view=allgrids&rows=nodes` | 184 / 181 / 175 | 0.32 |
| `/cost-of-power?view=allgrids&profile=flexible` | 138 / 98 / 91 | 1.57 |
| `/cost-of-power?view=allgrids&profile=electrolyzer` | 92 / 98 / 97 | 1.57 |
| `/cost-of-power?view=allgrids&profile=industry` | 127 / 113 / 98 | 1.49 |
| `/cost-of-power?view=allgrids&sort=allin&a=ercot%3AHB_HUBAVG&b=nyiso%3AN.Y.C.` | 120 / 116 / 118 | 1.76 |
| `/cost-of-power?view=allgrids&rows=nodes&nsort=energy&ndir=desc` | 181 / 176 / 167 | 0.32 |
| `/cost-of-power?view=allgrids&rows=nodes&node=ercot%3A7RNCHSLR_ALL` | 168 / 166 / 166 | 0.34 |
| `/cost-of-power?view=allgrids&profile=electrolyzer&strike=20` | 104 / 91 / 93 | 1.57 |
| cold: the node list, then the hub table, then the electrolyzer | 679, 641, 224 | 0.32, 1.73, 1.57 |

**The hub table's page is heavy: 1.73 MB of HTML.** Its 48 rows carry about 15 tips each, many of them a few hundred characters, and the server's payload for the browser repeats them. On this machine it answers in about 120 ms; on a phone over a slow network the transfer is the cost. Shorter tips (the method once per column, the row's own figures in its tip) would roughly halve it. This is listed for Samuel's ruling, not changed: the tips' words are the page's sources.

## The twenty slowest reads of "Your load", for comparison

From `node site/scripts/slow-reads.mjs` on the server's log: 80 requests, 40 distinct reads. The milliseconds are the timer's, on a quiet database. None is the tab's.

| # | ms | table | filter | order | offset | rows |
|---|---|---|---|---|---|---|
| 1 | 19 | carbon_intensity_hourly | entity=eia930:ERCO, intensity_demand | ts_utc | 11000 | 0 |
| 2 | 19 | carbon_intensity_hourly | the same | ts_utc | 12000 | 0 |
| 3 | 7 | price_years_by_window | ercot:LZ_NORTH, datacenter_flat_rt_* | variable | 0 | 20 |
| 4 | 7 | price_years_by_window | ercot:LZ_NORTH, datacenter_hours_rt_* | variable | 0 | 20 |
| 5 | 5 | carbon_intensity_monthly | eia930:ERCO, intensity_demand | ts_utc | 0 | 87 |
| 6 | 5 | ercot_rtm_price_adders | ercot:system, rtorpa_mean, from 2025-10-01 | ts_utc | 2000 | 0 |
| 7 | 5 | ercot_rtm_price_adders | the same | ts_utc | 3000 | 0 |
| 8 | 5 | ercot_rtm_price_adders | the same | ts_utc | 4000 | 0 |
| 9 | 4 | ercot_large_load_status | ercot:large_load | ts_utc | 0 | 38 |
| 10 | 3 | carbon_intensity_hourly | eia930:ERCO, intensity_demand | ts_utc | 0 | 1000 |
| 11 | 3 | carbon_intensity_hourly | the same | ts_utc | 3000 | 1000 |
| 12 | 3 | carbon_intensity_hourly | the same | ts_utc | 4000 | 1000 |
| 13 | 3 | carbon_intensity_hourly | the same | ts_utc | 7000 | 1000 |
| 14 | 3 | scarcity_hours_by_grid | iso:ercot, the twelve months | ts_utc, variable | 1000 | 1000 |
| 15 | 3 | scarcity_hours_by_grid | the same | ts_utc, variable | 7000 | 1000 |
| 16 | 3 | scarcity_hours_by_grid | the same | ts_utc, variable | 9000 | 1000 |
| 17 | 2 | carbon_intensity_hourly | eia930:ERCO, intensity_demand | ts_utc | 2000 | 1000 |
| 18 | 2 | carbon_intensity_hourly | the same | ts_utc | 1000 | 1000 |
| 19 | 2 | carbon_intensity_hourly | the same | ts_utc | 6000 | 1000 |
| 20 | 2 | carbon_intensity_hourly | the same | ts_utc | 8000 | 1000 |

Two reads ask a page past the end of the table (offsets 11,000 and 12,000 of the hourly carbon, and 2,000 to 4,000 of the adders, 0 rows): the paging asks once more than it needs. They are "Your load"'s, not this chain's, and are listed for whoever next touches `lib/datacenter/answers.ts`.

## Again (session 739, chain 062)

On a build of `wip/738-allgrids` (chain 062's sessions 722 to 738: the spread, the filter and the download, the kind words, the zone line, the second card, the tip's box in `tokens.css`), 22 October 2026 at about 16:50 UTC, the server started with `ERW_READ_TIMING=1`.

- **The tab still makes no read of the database**: 0 `[erw-read]` lines across ten addresses, three times each (the six of 716 that still exist, and the node list by spread, the link's address, the headroom sort for NYISO). "Your load", asked four times in the same run, wrote 120 lines (40 distinct reads), so the timer was on.
- **The answers**: the hub table 142 ms warm (1,236 ms the first time after the start), the node list 187 to 230 ms, a node's panel 190 ms. 716 measured 166 to 168 ms for the panel.
- **The build**: about 70 seconds (compiled in 16.1 s, TypeScript 27.2 s, 282 static pages), as at 716.
- **The page**: the hub table 1.59 MB of HTML, from 1.82 at 716, after session 737's change.

The twenty slowest reads of "Your load" (`node site/scripts/slow-reads.mjs`, 240 requests, 40 distinct reads): the slowest 27 ms (`scarcity_hours_by_grid`), then 9 and 8 ms (`price_years_by_window`, `ercot_rtm_price_adders`), then the hourly carbon pages at 3 to 5 ms. The same tables as 716's list, none slower than 30 ms. No index is needed; migration 036 stays as it is. The full list: `runs/chain_062/slow739.md` on this machine.

## Again (session 761, chain 063)

On a build of `wip/760-allgrids` (chain 063's 744 to 760: the node's intraday swing, the sort line's case), 22 October 2026 at about 19:30 UTC, the server started with `ERW_READ_TIMING=1`.

- **The tab still makes no read of the database**: 0 `[erw-read]` lines across six addresses, three times each (the hub table, the node list, the list by intraday swing, a node's panel, the flexible profile, the headroom sort for NYISO). "Your load", asked three times, wrote 120 lines.
- **The answers**: the hub table 148 to 175 ms warm (1,179 ms first), the node list 200 to 246 ms, a node's panel 185 to 201 ms, the headroom sort 42 to 52 ms.
- **The build**: compiled in 14.0 s, TypeScript 29.0 s, about 70 seconds in all.
- **The pages**: the hub table 1,584,788 bytes, unchanged since 737. The node list 340,129 bytes, from 319,756 at 737: the swing column, 20 KB.

## Again (session 783, chain 064)

On production (chain 064's 766 to 777 served since 21:30 UTC), 22 October 2026 at about 21:43 UTC.

- **The tab still makes no read of the database**: chain 064 added no server read (772's class filter and 777's hand-over work in the browser), `tests/test_session716.py` holds on this branch, and session 761's timed run (0 read lines) stands for the server's code.
- **The pages**: the hub table 1,585,500 bytes (unchanged since 737); **the node list 226,915 bytes**, from 340,129 at 761, after 777's hand-over column by column; the third card 41,388 bytes.

## Again (session 972, chain 065)

On production (chain 065's 788 to 799 served since 23:59 UTC), 23 October 2026 at about 00:10 UTC.

- **The tab still makes no read of the database**: chain 065 added no server read (793's download works in the browser from the props the table already had; 794's pair and 795's "settles at the same prices" line read `site/data/siting/nodes.json`, a file of the build), `tests/test_session716.py` holds on this branch, and session 761's timed run (0 read lines) stands for the server's code.
- **The pages**:
  - the hub table 1,596,087 bytes, from 1,585,500 at 783: 793's download, 10.6 KB;
  - the node list 226,920 bytes, unchanged;
  - two nodes as A and B (BBREEZE_1_2 with PALACIOS_RN) 1,642,603 bytes: the hub table's page and the two panels with 794's chart and month table, 46.5 KB more.
