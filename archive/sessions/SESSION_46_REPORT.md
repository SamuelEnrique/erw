# Session 46 report: the gate stayed shut, so the fallback ran (battery game v1.1, problem set D)

**Daily run 13's failure, in five lines:**

1. **Failing step:** "Package tests" of daily-prices run 13 (workflow_dispatch, 5c00e9d), 1 of 296: `test_events_table_types_subset_and_provenance[policy_reads]`.
2. **The error:** the table's first header line was the restore's placeholder, "Restored from the Redivis draft ...", not an ERW provenance header, so it named no source and no run log.
3. **Cause:** on the runner, `policy_reads` comes back from the Redivis draft with that placeholder. `warehouse/policy/reads.py` rewrote the header only when it read something new, and on 2026-09-30 it read nothing. Runs 12 and 13 had also uploaded the placeholder as the table's header in `erw_headers`.
4. **Fix** (cf660b0):
   - `reads.py` rebuilds a placeholder header from the rows (latest `read_at`, `model_id`; no row changes).
   - `upload.py --restore` writes each table's header lines from `erw_headers` and never carries a placeholder forward.
   - `policy_reads` was the only table affected.
5. **The one approved workflow_dispatch:** run 14 (374f8fd, 23:04 UTC), not waited on. Session 45's fix held: run 13's package tests passed 290 and skipped 5 (CARB and the NYISO queue among the skips); run 12 had failed 11.

Energy Research Warehouse (ERW), session 46, run 2026-09-30 from 22:07 to about 23:15 UTC. **Wall time about 70 minutes.**

**API spend: USD 0.00, confirmed.** No model call; the policy reads fix was tested offline, on a copy. No data pull, no Supabase table, no force push. Part A and Part B did not run, so neither of their pulls was made: **0 rows** against the 150,000 (interchange) and 1.5 million (hub price) ceilings.

## Urgent: Supabase is at 447.9 MB, over the loader's 400 MB limit

Run 13's log, from the first daily load with session 45's plain vacuum:

- **Before the load:** 349.9 MB.
- **After the load and `VACUUM (ANALYZE)`:** 447.9 MB (469,650,579 bytes). The series table was 358.0 MB before and after the vacuum.
- **Why:** a plain vacuum marks the replaced rows' space for reuse but never shrinks the database. Until session 45, the load's `VACUUM FULL` (in the code, though the runbook said plain) had been returning that space after every load.
- **Effect:** `supabase_load` exited 1 at its `max_mb` check, after the data had loaded ("supabase_load: connector exit 1" in the day's commit). It will do so every day while the size stays over 400 MB.
  - The next loads should mostly reuse the freed space, so growth should slow, but that is not measured yet.
  - Supabase's free plan puts a database over 500 MB in read-only mode (reads work, loads do not).
- **I did not run `VACUUM FULL`.** The runbook makes it a person's command, it locks each table for minutes (the site's reads time out meanwhile), and this prompt does not approve it.
- **Samuel, one of:**
  - run `python warehouse/supabase/load.py --vacuum-full` once at a quiet hour, from a machine whose tables are current (it loads first; the GitHub runner's are, this laptop's are not);
  - or run `vacuum full analyze public.series;` (and the other shape tables) in the Supabase SQL editor;
  - and decide whether the daily load should vacuum FULL again, say weekly, or `max_mb` should rise.

## Part 0

1. **Prefetch off on `/severance/lease`** (095cc64).
   - **The change:** the page's own links are `prefetch={false}`. The shared links (header, nav, footer, citations) now go through `components/SiteLink.tsx`, which turns prefetch off on the pages in `NO_PREFETCH` (the lease page) and behaves as `next/link` elsewhere.
   - **Checked in Chrome:**
     - Before, on the live site, scrolling the lease page after loading the sample prefetched `/data` and `/terms`.
     - After, on a production build, no request beyond the page's own load (document, font, CSS, code chunks), after loading the sample, ticking, and scrolling past all 53 internal links.
     - `/severance` still prefetches `/data`.
   - `test-lease.mjs` checks the links (88 checks).
2. **Run 13:** still running at 22:07, checked every 10 minutes (22:17, 22:23, 22:33, 22:43, 22:48). Its package tests failed at 22:50 and the run showed "completed failure" at 22:58.
   - **Your instruction (22:20):** do the fallback while it runs.
   - **Routing:** failed, so I read the log, fixed it on main, and triggered one workflow_dispatch (above). The fallback was already done.
   - Run 14 cannot pass before this report, so Parts A and B did not run. `SESSION_42_PROMPT.md` stays at the root, and there is no `SESSION_42_REPORT.md`.

## The fallback (what shipped)

**1. Battery game v1.1** (`/play/battery`, c49a77d)

- **Leaderboard flag:** a score shown as 100 percent of perfect is flagged ("flagged: 100 percent of perfect"), with a note. The debrief prints the perfect plan, so such a score may replay it; the score stands, marked.
- **Fleet panel:** "The fleet: fictional and real".
  - **The game's 10,000 homes:** 50 MW and 135 MWh (from `lib/battery.ts`).
  - **Beside them, ERCOT's operating battery fleet from `storage_capacity`:** units, MW, and MWh where EIA gives the energy capacity, plus the ratio of the two fleets' power.
  - Every number is a checked value. New `check-values` keys: `storage|iso_n`, `storage|iso_n_mwh`, `battery|fleet_mw`, `battery|fleet_mwh`.
- **Share card:** drawn on a canvas in the page and saved from it as a PNG, or its text copied. Nothing is uploaded.
- **Famous days link to their event pages** in the picker and the debrief: Uri (2021-02-15) to `/events/uri-2021`, the 2023 heat day (2023-08-10) to `/events/ercot-heat-2023`. The calm, solar and negative-price days fall in no event window, so they have no link.
  - `test-battery.mjs` checks the event windows against `warehouse/derived/event_window.py`.

**2. Problem set D, "Storage and taxes"** (`/learn/problems/storage-and-taxes`, 0e367cd and 3fbdb1c)

Five questions, every answer computed on the server and checked; values as of the live check at 22:47:

| # | Question | Answer (live) | From |
|---|---|---|---|
| d1 | ERCOT batteries' energy out over energy in, 2026-09-22 to 28, against the game's assumed 90 percent | 189,034 out of 233,368 MWh: 81.00 percent | storage_daily_cycle, lib/battery.ts |
| d2 | The hours of peak charge and discharge, 2026-09-28 | hour 9 and hour 19, 10 hours apart | storage_daily_cycle |
| d3 | One full cycle of the game's battery at ERCOT's cheapest (09:00, 22.49) and dearest (20:00, 76.03 USD/MWh) average hour of 2026-09 | USD 0.65 a home; USD 6,536.74 for the fictional fleet | cost_of_power_hourly_profile, fullCycle |
| d4 | Oil tax on 1,000 barrels in 2026-08 at WTI's mean, 83.90 USD/bbl | TX 3,859.29, LA 10,487.20, NM 5,990.29 USD; LA is 2.72 times TX | eia_fuel_spot_prices, severance rules |
| d5 | A Texas gas well, 2,400 Mcf in 2026-08, at Henry Hub's mean, with the low-producing credit | the tax, then the certified USD 1.36 (2005 dollars) gives a 100 percent credit, so USD 0 | eia_fuel_spot_prices, severance rules |

- **New `check-values` keys:** `battery|round_trip_pct`, `bought_kwh`, `delivered_kwh`, `cycle`, `cycle_fleet`; `spotmean`; `sev`; `sevcert`; `sevcredit`.
- **Two text-comparison bugs, caught by check-values:**
  - **d1's seven-day sums:** they first showed 157,699 against Supabase's 189,034 MWh. Supabase writes `+00:00`, which sorts before `Z` as text, so the first day was dropped. Times are now compared parsed.
  - **Set A's generation sums:** the same test would have let in a row stamped exactly at the day's end. Fixed the same way.

**3. Checks**

- **Live:** routes 57 of 57, values 1,672 of 1,672, set D's 19 values among them.
- **Local:** values 1,693 of 1,698. The five misses were grid-page news counts, read by the build from Next's fetch cache before new stories loaded; live, all match.
- **Tests:** `tests/` 94 OK (with `test_session46.py`).
- **Builds and code:** `tsc` clean.
  - Eslint shows one pre-existing error in `Game.tsx` ("cannot access before declared", also at line 169 before this session).
  - One `<img>` warning, for the share card's data-URL preview, is suppressed with a reason.

## Supabase before and after

- **This session wrote nothing to Supabase.**
- **The database:** 349.9 MB before run 13's load and 447.9 MB after it (above).

## Decisions made without a human

1. **The routing:**
   - After your 22:20 instruction, the fallback ran while run 13 was checked.
   - When run 13 failed, I read the log, fixed it on main and dispatched once, then wrote this report, since the fallback was already done and deployed.
2. **Where the fix went:** the header is rebuilt from the rows, instead of downloading `erw_headers` into `reads.py`, because the draft's own copy of the header was already the placeholder.
   - The rebuilt Retrieved, Run log and Raw files lines say the run id is not in the rows, and name the latest `read_at`, rather than inventing one.
3. **The restore now writes the header lines it finds in `erw_headers`,** so any other table the connector does not rewrite on a quiet day keeps its provenance.
4. **`VACUUM FULL` was not run** (the urgent section above).
5. **Unfinished work: `warehouse/connectors/eia930_interchange.py`.** I drafted it while waiting on run 13, for session 42's A1: one entity per BA pair, `ba` the reporting BA, `x_to_ba`, a 150,000-row ceiling checked before paging, daily checkpoints.
   - It was never run and is **not committed** (untracked on this machine), so no EIA request was made.
   - The route's field names (`fromba`, `toba`) and the length-0 count request must be checked against the API when the gate opens.
6. **`test_session44.py` now counts four problem sets,** not three.

## Open questions

1. **Supabase at 447.9 MB:** which of the fixes in the urgent section above?
2. **Run 14** (374f8fd) was dispatched at 23:04. If it passes, the gate is open: Session 42, then the year of hub prices, next session.
3. **The leaderboard flag:** should a 100-percent score also be kept off the top ten, or only marked, as now?
4. **Set D's d3** uses the latest month of the hourly profile, which is the month in progress (2026-09). Should problem sets use only complete months?
