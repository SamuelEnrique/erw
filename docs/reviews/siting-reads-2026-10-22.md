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
