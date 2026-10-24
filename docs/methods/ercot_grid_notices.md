# ERCOT's grid notices: method

Energy Research Warehouse (ERW), session 322 (the owner's default of 19 October 2026 for the morning note's item 9). The table is `ercot_grid_notices` (events); the code is `warehouse/connectors/ercot_grid_notices.py`. Tier: source. License: public (ERCOT's terms, read 2 of `warehouse/metadata/license_reads.csv`). Credit: Electric Reliability Council of Texas (ERCOT).

## 1. Question

On which days did ERCOT call on supply or demand across its grid: an Energy Emergency Alert, rotating outages, a conservation appeal, a watch? `grid_stress_days` counts a CAISO day by its notices as well as its price (session 297's rule). Until this table, ERCOT was judged by price alone, so 24 December 2022 (Winter Storm Elliott) was not a stress day (session 306).

## 2. Where ERCOT keeps its notices

ERCOT publishes no single history of its notices. Three of its pages were read on 19 October 2026, after its robots file (which disallows none of them):

| Page | What it holds | Read |
|---|---|---|
| News releases, `https://www.ercot.com/news/releases?year=YYYY` | every release from 2010; the grid-condition ones announce EEAs, rotating outages, conservation appeals, Power Watches (2011), Weather Watches and Voluntary Conservation Notices (TXANS, from May 2023), and some Operating Condition Notices | every year's listing, and each release whose title names a grid condition or the weather |
| Operations messages, `https://www.ercot.com/services/comm/mkt_notices/opsmessages?m=MM&y=YYYY` | the control room's messages: Advisory, Watch, OCN, Emergency Notice, EEA, and routine operational lines | the six months ERCOT serves (May to October 2026). December 2022 answered with an empty list: no earlier month is served |
| Market notice archive, `https://www.ercot.com/services/comm/mkt_notices/archives` | market, settlement and outage notices, from 19 October 2023 only | read once; not used: it holds no operating conditions |

## 3. Rows

- **One row per notice and Central day it covers.** A release that names its days covers those ("Requests Conservation Monday, January 15"; "Winter Weather Watch Through Sun., Feb. 6"; "a Weather Watch from January 20-23"; an OCN "between Thursday, December 22 through Monday, December 26"), read from the title, else the first two paragraphs; the dateline ("Austin, TX, Sept. 4, 2019") is not a covered day. A release that names none covers the day it was issued. A control-room message covers the day it was issued, or the days an OCN or Watch names (at most 14 days ahead).
- **`event_type`** from the notice's own words, in this order: `update` (a release or message that ends or cancels a notice), `rotating_outages` and `eea3`, `power_watch` (2011's Power Watch and Power Warning), `eea2`, `eea1` (named in the title, or the first paragraph saying ERCOT issued, declared, entered or is in an EEA), `voluntary_conservation`, `weather_watch`, `conservation_appeal` (the title, or the text asking for conservation and not saying it is not asking), `ocn_weather` and `ocn` (an Operating Condition Notice, for extreme weather or not), and `statement` (a release on the grid that announces no notice). Control-room messages keep their own type (`advisory`, `watch`, `ocn`, `emergency_notice`, `emergency_test`); the routine "Operational Information" and DC tie lines are not kept.
- **`x_counts`**: `yes` for a system-wide call on supply or demand, the kinds `grid_stress_days` counts as it counts CAISO's notices: an EEA level, rotating outages, a conservation appeal or Voluntary Conservation Notice, a Power or Weather Watch, an OCN for extreme weather, and a release ending an emergency (the emergency was in effect that day). `no` for a notice for the Rio Grande Valley only, an Advisory or Watch on the control room's own tools (a geomagnetic disturbance, a study that did not solve), a test, a statement and other updates.
- **`x_text`**: the release's title and first two paragraphs, or the message, as ERCOT wrote them (its terms ask that the contents not be modified). Some of ERCOT's pages carry a replacement character for an apostrophe or a dash; it is kept as served.

## 4. What it holds (19 October 2026)

178 rows, 2 February 2011 to 15 October 2026; 120 of them count, on 100 days. By type, counted: conservation appeals 39, Weather Watches 44, Power Watches 10, OCNs for extreme weather 11 (5 from the release of 16 December 2022, 6 from the control room's OCN of 19 August 2026), Voluntary Conservation Notices 4, rotating outages 2, EEA 1 and EEA 2 one each, and 8 updates ending an emergency.

**Elliott.** ERCOT's release of 16 December 2022 says: "Earlier today, ERCOT issued an Operating Condition Notice (OCN) ... that temperatures will meet ERCOT's criteria of 25 degrees or lower in the Austin/San Antonio and the Dallas Fort-Worth areas between Thursday, December 22 through Monday, December 26." Those five days are notice days; ERCOT issued no conservation appeal or EEA for Elliott in its releases.

## 5. Limits

- Before May 2026 the control room's own messages are not served; an Advisory, Watch or OCN of an earlier day is in the table only where a release announced it. A day may have had a notice the table does not hold.
- The classification reads words, not a code ERCOT assigns. Each counted row can be checked against its `x_text` and its `source_url`.
- The daily window of the operations messages is six months, so each run keeps the rows it read before (the table only grows).

## 6. On the Grid tool: the notice state (session 1174, 24 October 2026)

The table's first page. The Mix tab of `/grid?grid=ercot` opens on the panel `grid_ercotnotice_ercot` (`site/components/grid/ErcotNoticeState.tsx`, `site/lib/ercotNotices.ts`), as CAISO's opens on its alerts (`california_reliability.md`, "On the Grid tool: the alert state"). The rows are read once per render (`site/lib/gridErcotNotices.ts`: `event_id`, `event_date`, `event_type` and three fields of `extra`, `x_counts`, `x_region` and `retrieved_at`; `x_text` is not asked for, since no panel draws ERCOT's words).

- **A call** is a row with `x_counts` `yes` (section 3): a system-wide call on supply or demand, as `grid_stress_days` counts it. Its kinds, each a group of the keys: `eea` (`eea1`, `eea2`, `eea3`, `rotating_outages`), `conservation` (`conservation_appeal`, `voluntary_conservation`), `watch` (`weather_watch`, and 2011's `power_watch`) and `ocn` (`ocn_weather`); a counted `update` (a release ending an emergency) is a call of no kind. `other` is every row with `x_counts` `no` (the control room's Advisories and Watches on its own tools, tests, statements, other updates, notices for the Rio Grande Valley only), named apart and never marked. `any` is every row.
- **Today** is the Central day the page was drawn. The table covers a day when it holds a notice of that day or a later one. For a day it covers, the panel says which calls are in force, or that none is; for a later day it says the day is not held yet, with the table's newest notice day (`ercotn|last|any|<today>`) and the day the ERW last read ERCOT's pages (`ercotn|read`, the UTC day of the newest `retrieved_at`: each read rewrites every row's) beside it, so "none today" is never said past what the table holds. On 23 October 2026 (Central) the newest notice is 2026-10-15 (an Advisory), read on 2026-10-19.
- **The last call** (`ercotn|last|call|<today>`: 2026-08-25, the OCN for extreme heat of 20 to 25 August 2026) and the days with one this year (`ercotn|ndays|call|<year>-01-01|<today>`: 10 in 2026); then the last day of each kind (`ercotn|last|<kind>|<today>`): an EEA 2023-09-06 (EEA 2), a conservation appeal 2024-01-16, a Weather Watch 2026-01-27, an OCN 2026-08-25.
- **Not calls, named apart:** the last such day (`ercotn|last|other|<today>`: 2026-10-15) and their days this year (`ercotn|ndays|other|<year>-01-01|<today>`: 19 in 2026).
- **The notice days on the scarcity strip** (ERCOT, `scarcity_hours_by_grid.md`): a triangle under each day of the strip with a call that Central day, each cell's hover naming the day's notices; the counts `ercotn|ndays|call|<first day>|<last day>` and `ercotn|ndays|other|<first day>|<last day>` under it. The window of 1 to 30 September 2026 holds no call day (0), so nothing is marked; the Advisories of 15, 28 and 29 September (3 days) are named, not marked.
- **The monthly mix** (`mixp=month`, ERCOT): a month with a call day is marked on the chart, its days in the mark's name; the call days of the months drawn are one count (`ercotn|ndays|call|<first month>|<last day of the newest month>`). The 24 months drawn on 24 October 2026 (September 2024 to September 2026, December 2025 not built) hold 22 call days in four months: January 2025 (Weather Watches, 6 to 10 and 20 to 23 January), February 2025 (19 to 21), January 2026 (24 to 27) and August 2026 (the OCN of 20 to 25).

### Check keys

- `ercotn|last|<group>|<day>`: the newest Central day on or before `<day>` with a row of the group, written as the date (YYYY-MM-DD).
- `ercotn|ndays|<group>|<from>|<to>`: the distinct Central days from `<from>` to `<to>`, both included, with a row of the group.
- `ercotn|read`: the UTC day of the newest `retrieved_at` of the rows.
- A group is `any`, `call`, `eea`, `conservation`, `watch`, `ocn` or `other`. check-values reads every row of the table once (with the same three fields of `extra`) and recomputes each key by the page's own rule (`site/lib/ercotNotices.ts`, `ercotnValue`); `site/scripts/test-ercot-notices.mjs` holds the rule on a fixture of every real row (`site/scripts/fixtures/ercot_notices.json`, read 24 October 2026, without `x_text`).

### Decisions (session 1174, chain 078)

- **A kind of key of its own, `ercotn|`, not CAISO's `awe|`:** `awe|last` and `awe|ndays` carry no table word and their groups are CAISO's notice types; ERCOT's groups need `x_counts` and `x_region` as well as the type. The two rules are kept apart, each with its file, its test and its read.
- **A call is the method's own `x_counts`**, so the panel, the strip and the monthly marks mean the days `grid_stress_days` counts for ERCOT, not a new list of types.
- **The state stands first on ERCOT's Mix tab**, as CAISO's does on its tab: it moves the blocks below it down the page; no figure's value or key changes.
- **The day the pages were read is said beside the newest notice.** ERCOT's control room's messages are read with the news releases on the data machine, by hand (no schedule runs the connector), so a week can pass with no new row; the read day tells a reader why, without the page claiming that the days between were quiet.
- **The notice's Central day is set on the strip's column of the same date** (the strip's days are Central standard time days; in summer the two share 23 of their 24 hours), as CAISO's Pacific days are.
- **Only three fields of `extra` are read** (PostgREST's `extra->>`), about 48 KB for 178 rows in place of about 156 KB with ERCOT's words; the page draws none of the words.
- **`ercot:news_releases` and `ercot:operations_messages` stay under `sources_hold`** and the table under `review_hold` (`warehouse/supabase/live_set.yaml`): every page is in review, so nothing a visitor counts changes. When the Grid tool opens, both come off with it.
