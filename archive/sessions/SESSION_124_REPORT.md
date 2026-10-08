# Session 124 report: the network, version 3, to launch-ready

**Done, merged and on production since 13:46 UTC.** Vercel did not build this session's own merge; the next merge, 56 minutes later, carried it (see "The live pages"). The live `/network` was not replaced and reads as it did (snapshot below). No model call, no request to any publisher.

**Verdict: ready to open, once two things are decided by you.** The page now opens on a complete hour and says which; its trace agrees with two cases worked by hand; its replay survives its worst days; it works at phone width; MISO is shown as paused. What stands between it and replacing `/network` is not code: four parts of the live page are not on this one yet, and MISO's price would disappear. Both are in the table "What replacing it would change".

## Read these first

1. **A rule of the warehouse was hiding the storm.** The replay leaves out a pair-day that is far from the pair's own median: "a day no tie can carry". Worked by hand for Winter Storm Uri, that rule had removed:
   - **MISO to SPP on 15, 16 and 17 February 2021.** 95,060 MWh on the 15th by MISO's report and 95,390 by SPP's. Two operators, 0.3 percent apart.
   - **Mexico to Texas on 12, 13 and 14 February 2021.** 6,861, 7,465 and 9,061 MWh. The hourly record shows 382 MW in hour after hour, the level the same tie reached on the 11th and the 15th, which the rule accepts.
   - The replay held 2,676 MWh from Mexico to Texas for the whole storm. EIA's table holds 26,065.
2. **It is not only Uri.** Of the 2,732 pair-days the rule leaves out, the other operator also reported 2,604, and in **1,911 the two reports agree within 5 percent** (1,901 within 1 percent). Seven in ten of the days the rule calls impossible are confirmed by a second meter. The January 2024 storm is among them (MISO to SPP, 104,833 MWh on the 14th).
3. **The replay now keeps a day the record confirms**; 815 stay out. This is the replay only. The same rule feeds `ba_supply_monthly`, which the live page reads, and I did not touch it: see "Held for your approval".
4. **The trace now agrees with the hand-worked cases to a hundredth of a point.**
   - California over 2021: 56,993,006 MWh in from nine suppliers by hand; BPAT 21.05 percent, LDWP 20.58, SRP 19.83, NEVP 15.09, AZPS 10.94, BANC 6.25, IID 4.52, WALC 1.61, PACW 0.12. The trace: the same.
   - Texas, 12 to 19 February 2021: SPP 84.6 percent (142,209 MWh), Mexico 15.4 (25,957 MWh). The trace: the same, after point 3.
5. **Four things in the trace were wrong or misleading, and are fixed.**
   - In the replay it covered the whole year whatever day was shown. Texas "during Uri" read "SPP 100 percent" because it was all of 2021. It now covers the day, its month or the year.
   - It said "365 days" for 2025, of which 47 hold no flow. It now says how many days of the period hold a flow.
   - Under Texas it said "CEN supplied by CISO, 100 percent": Mexico's operator is one name in EIA's file, but its California tie and its Texas ties do not connect inside Mexico. Nothing is traced through it now, and the page says why.
   - It reads each tie once by the network's rule, which is not always the grid's own report (BANC to California: 3,559,578 MWh by BANC, 3,297,404 by California). The page now says which reading it uses.
6. **The page opens on a complete hour.** The newest hour of the week is held by few pairs. The live week now opens on the newest hour every reporting pair holds, and says which. On the local build with the 13:05 UTC refresh: 2 October 06:00 UTC, held by all 155 pairs of the week; the newest hour of all, 4 October 03:00, holds 154 of them. An hour earlier the week still held a 156th pair (Southwestern Power Administration with SPP), silent since 26 September: it was named and not waited for, and has since left the week. Read on production at 13:48 UTC: the same sentence, the same figures.
7. **The replay through its hardest days: nothing broke that a visitor would see as an error, and two things were wrong.** A day for which EIA's file is blank drew an empty network with no word; it now says so (47 such days in late 2025; the replay's last day holds 29 of 149 pairs and says so). And, by the code's reading, a year's file that arrived late could replace a newer day asked for after it; a guard now prevents it, and three years asked for in a row show the last.
8. **Phone and slow machine.** At 390 px nothing is wider than the screen and the panel sits under the network. With the processor slowed six times the live week and the stories hold 52 to 56 frames a second; the replay playing a year drops to 14, with a longest frame of 0.4 seconds. Measured, not fixed: that drawing code is the live page's.
9. **MISO is shown as paused, in words.** No price ring and no price in its panel, in the live week, the stories and the replay; the panel and the fold say why. Its flows, demand and carbon are EIA's and are shown.

## Held for your approval

**The same rule in `ba_supply_monthly`.** The live page's twelve-month figures come from that table, which leaves out a balancing authority's day when one of its pairs is screened.

- **No number on a live page would move today.** Of the confirmed days, 12 were reported by one of the seven ISOs, and none is in the last twelve months:

  | Pair | Days | The two reports, MWh |
  |---|---|---|
  | MISO with SPP | 15, 16, 17 February 2021 | 95,060 and 95,390; 71,165 and 71,213; 83,377 and 83,217 |
  | MISO with SPP | 14, 15, 16 January 2024 | 104,833 and 104,724; 75,438 and 75,479; 84,711 and 84,885 |
  | PJM with CPLW | 23 January 2025 | 7,627 and 7,961 |

- **What would change:** the table's rows for MISO and SPP in February 2021 and January 2024 and for PJM in January 2025 (days held, net imports, shares), and Texas's February 2021 if the hourly test were used there too.
- **I did not build it.** The table is one session 118 holds, and its figures before and after belong in one place with that session's. The rule to apply is in `network_daily.py` (`confirmed`), tested.
- **Until then** the method page says the replay and the monthly table read these days differently.

**MISO's price in the replay's files.** The page shows none. The files (public at `/network/daily_2024.json` to `2026`) still hold MISO's daily mean price from September 2024, as they did before the pause. Removing it is one line in the builder and changes what the daily run writes; it is the same question as the pause itself, so it is yours.

## What replacing `/network` with this page would change for a visitor

Not done. If `/network` passed the `v3` prop:

| | `/network` today | With version 3 |
|---|---|---|
| The hour it opens on | the newest hour, which few pairs hold | the newest complete hour, named, with the pairs that have stopped |
| A day since 2019 | not there | a date picker and "Play the year" |
| Prices | the hub price in the panel | the same, a Prices switch and a ring; **no price for MISO**, which the live page shows today |
| Trace the power | not there | two steps; in the replay over a day, its month or its year |
| The address | always `/network` | holds the grid, the moment and the switches |
| The "Newest hour" line, the three measures of imports, "How fresh each layer is", the note on California's break | on the page | **not on version 3's page**; it links to `/network` for them, and would link to itself |
| The live week's numbers in the panel | as now | the same figures for the hour shown; the hour shown first is earlier |

So before a swap: move those four parts across, and decide MISO's price. The checked numbers (demand, carbon, the twelve months) are read the same way by both.

## What changed in the code

- **`site/lib/networkV3.ts`** (pure functions): `completeHour`, `monthSpan`, `PAUSED_PRICE`, `ISLANDS`; `trace` returns how many frames hold a flow and traces nothing through an island.
- **`site/app/network/Network.tsx`** (shared with the live page): every change is behind the `v3` prop. Without it the page opens on `snap.hours.length - 1` as before and a price is the view's own. A test holds the gating lines, and the live page's own browser test passes on the build.
- **`site/app/network/v3/page.tsx`**: the complete-hour line, the kept days, MISO, the trace's words.
- **`warehouse/derived/network_daily.py`**: `confirmed` (the two tests), `pairs_held` and `pairs_usual` per year, `last_complete` and the counts in the index. All eight years rebuilt; the newest the daily way. The daily run will use it from today.
- **`docs/methods/grid_network_v3.md`**: a section for all of the above, with the table of what a swap would change.

## The live pages

**Update, 13:48 UTC: on production, and nothing unmeant moved.** Session 125's merge (`b2f09c5`, 13:45 UTC) was built by Vercel at 13:46 and carries this session's code.

- `before-124` (12:43:28 UTC) against `after-124b` (13:47:23 UTC), 25 pages, 4,037 checked numbers: **38 differences, all of them the clock.**
  - `/`: 32. The price board's newest real-time price of five hubs (ERCOT 70.17 to 43.02, California 54.24 to 52.18, New York 38.05 to 29.66, SPP 29.99 to 23.62, New England 56.28 to 20.40 USD/MWh, each an hour later), their interval lines, and three lines giving a table's age in days (5.8 to 5.7, 5.7 to 5.6, 4.7 to 4.6). Expected: the 15-minute prices.
  - `/network`: 6. "refreshed 12:05 UTC" to "13:05 UTC" and the demand's newest hour, 10:00 to 11:00 UTC, in three lines each way. Expected: the hourly refresh.
  - The other 23 pages: 0.
- `before-125` (13:38:03) against `after-125` (13:47:09), around the build itself: **0 differences** on all 25 pages.
- `/network/v3` on production opens on 2 October 06:00 UTC, "the newest hour that every one of the 155 reporting pairs holds", and renders in the internal view; a visitor finds it closed.

What follows is as written at 13:30 UTC, before that build.

**The deploy has not reached production.** One push, `task/124-network-v3`: run 37311550214, checks passed, merged to main as `e511e2e` at 12:49:56 UTC.

- **Vercel had not built that commit at 13:30 UTC.** GitHub shows no deployment and no Vercel status for it; each of the eight merges before it today had a deployment within three minutes. Vercel's status feed reports all systems operational. I have no access to Vercel's dashboard and did not look for a way around it.
- **So production serves session 123's build.** `/network/v3` there is the page as it was before this session. Everything this report says of the new page was measured on the local build of the merged code.
- **The next push to main deploys both.** Session 125's push follows; its report carries the snapshot of this deploy. If nothing has built by then, the dashboard's Deployments tab will show why (a daily limit of the plan is my guess, not a finding).

**Snapshots.** `before-124` at 12:43:28 UTC and `after-124` at 13:02:13 UTC, 25 pages, 4,037 checked numbers: **0 differences** on every page. That shows nothing moved on a live page; it is not yet the "after" of this deploy, since the deploy had not happened. A third, `after-124b`, is taken by a watcher when production first serves the new page (it waits until 13:53 UTC).

**What the deploy should change on a live page: nothing.** The shared component's changes are behind the `v3` prop, a test holds the gating lines, and the live page's own browser test passes on the local build. On the local build `/network` reads as on production, apart from the hourly refresh.

## Decisions made without you

- **"Complete for every pair" means every pair that is reporting.** A pair silent for the last 48 hours of the week is named and left out of the test. Waiting for it would have opened the page on 26 September.
- **Five percent** for two reports to count as one flow; 1,901 of the 1,911 agree within one.
- **The hourly test** applies only where EIA's hourly record is on the machine (the two event windows). It keeps six pair-days.
- **I changed a file the live page imports.** There is no other way: version 3 is that component with a prop. The gating is tested, and the snapshot shows the live page's text and numbers unmoved.
- **The trace opens on the month** of the day shown in the replay. A year hid the event; a day is often one tie.
- **The replay's slowness is reported, not repaired.**

## Errors, and what caught them

| What | Caught by | Now |
|---|---|---|
| The existing browser check expected a ring on MISO and the trace over a year | the check itself (31 now pass) | updated for the paused hub and the trace's period |
| My new check counted ties at exactly zero as flows to draw | its first run (8 of 24 failed) | a tie at zero is held and has nothing to draw |
| My new check looked for the fold's words in a closed fold | the same | reads the text whether the fold is open or not |
| Four older tests pinned the prop's type, the page's call and a file's keys | the tests | updated, each with a note |
| The newest year's file lost a key the daily build writes | session 114's test | rebuilt the daily way |

## Tests

`tests/test_session124.py`, 23 tests: the complete hour (a late pair, a stopped pair, a hole, none); the trace (Mexico, frames held, a month's span); the two hand-worked cases against the table; MISO to SPP kept and in the file; the builder's two tests on made rows, and what they must not keep; the files' counts; the gating of the shared component; the page's words.

In a real browser on the local build: `check-network-v3.mjs` 31 checks; `check-network-v3-hard.mjs` 24 checks (the hardest days, a phone, a slowed processor); the live page's own `test-network.mjs` passes.

Full suite: 1,249 tests, exit 0. Site build exit 0. Route check exit 0 (16 live, 107 in review).

## What is left

1. **Your two decisions**: the rule in the monthly table; MISO's price in the files.
2. **Move the four parts of the live page across** before any swap (half a day).
3. **The replay on a slow machine**: rebuild only what changed from one day to the next. It touches the drawing code both pages share, so it wants its own session with the live page's frame times measured before and after.
4. **The replay's last days are thin** (29 of 149 pairs on the newest): EIA fills them over days. The page says so; the date picker could stop at the last complete day instead.
5. **The two sides of a tie.** The trace says which side it reads. Showing both where they differ by more than a few percent would need the other side's figures in the replay's files (about twice their size).
