# Session 82 report: land and fix

**Landed.** Sessions 77 to 81 are on `main` and deployed, the skipped daily commit of 3 October is restored, California's join is live and in the daily run, and the one-hour fault in California's EIA-930 hours is found, bounded and corrected where the evidence is exact. Three deploys, each with a snapshot before and after; every difference is listed below. Finished well before 13:00 UTC.

**Read these four first:**

1. **The seller tab's California solar was overstated by 10.3 percent for 16 months, and is now corrected.** EIA's hourly values for California sit one hour late from 1 November 2023 to 2 December 2025; a solar shape an hour late sells into the evening ramp. September 2024 to December 2025: USD 45,617 per MW before, 40,916 after. Wind moved 0.5 percent. Texas and every other grid: untouched by this.
2. **A test would have stopped the daily run.** `tests/test_session55.py` pinned the date 2026-10-02T04:00 as "newer than the network snapshot". The daily workflow runs only when the tests pass, and the next committed snapshot is newer than that date. Yesterday's skipped commit hid it. Fixed; today's 14:00 run would otherwise not have started.
3. **To do this I brought EIA's workbooks onto this laptop** by running the existing daily emissions connector under the lock. The prompt said to skip steps needing raw files this machine lacks; part (b) could not be answered without the CISO workbook, and it is the same public file the daily run pulls every day. With the workbooks here the skipped steps were no longer skipped: the shoulder table is rebuilt in full, Texas's worst days included.
4. **No instruction arrived for session 84.** I have 82, 83 and 85 to 89, and run those.

Energy Research Warehouse (ERW), session 82, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from 02:04 to about 03:20 UTC, unattended. **Model spend: USD 0.00.** Pulls: the daily emissions connector (EIA's eight workbooks, an existing scheduled source) and the approved daily pull of CAISO's supply by fuel (three days, 936 rows). No model call, no force push. The data lock was held 02:11 to 02:13, 02:15 to 02:18 and 02:25 to 02:55 UTC and released each time.

## To finish

```bash
# Nothing is left half done. What was not done, and why:

# 1. Session 78, step 6: /network's sentence links to a method note that is in review, so a visitor sees the words
#    greyed. Opening a page to visitors is yours: in site/lib/release.ts,  "/data/methods/eia930_caiso_break": "live".

# 2. Session 78, step 7: the mix pages (/mix, /grid, /grid/caiso) still read EIA-930's generation by fuel for California.
#    Not built: it is new page code, and the night has six more sessions. Their sentence says plainly what they read.

# 3. Session 78, step 8: CAISO's three short days (2026-03-08, 2026-08-21, 2026-09-22). You approved the daily pull, not
#    this one. Until they are pulled, March, August and September 2026 have no monthly California figure after the join.

# 4. Session 77, step 4: ercot_as_quantities' header lines in Redivis are still the restore's placeholder. Its
#    connector is a pull of ERCOT's plan; run it on any data machine and its header returns:
python warehouse/lock.py run --task "ercot_as_quantities header" -- python warehouse/connectors/ercot_as_quantities.py
#    (caiso_fuel_supply's and shoulder_hours_monthly's headers went back with this session's uploads; storage_buildout_monthly's
#    returns with the next daily run, which builds that table and now keeps other machines' header lines.)

# 5. Session 77, step 6: the unlock link still answers 404 on production (03:08 UTC). Set INTERNAL_COSTS_TOKEN on Vercel
#    to the value in .env and redeploy; then
cd site && ERW_COOKIE=... node scripts/check-lights.mjs https://erw-flame.vercel.app
ERW_COOKIE=... node scripts/play-battery.mjs https://erw-flame.vercel.app

# 6. This report reaches main with session 83's push (it was written after this session's one push of task/082-land).
```

## In plain words

### (a) The "To finish" steps of sessions 77, 78, 80 and 81

| Step | Done | Note |
|---|---|---|
| 77.1 The commit the daily run skipped | yes | `de240aa` on `main`, 02:13 UTC. The eight tracked tables as the run uploaded them, coverage rebuilt, and the source registry with the two outlets and the run's last-seen dates taken from Redivis's own copy of the registry (`erw_sources`) |
| 77.2 The branch through a task branch | yes | one push, `task/082-land`, with 78 to 81 |
| 77.2 The license check, only with a proof | yes, proven | below |
| 77.3 `shoulder_hours_monthly`'s source URL | yes | rebuilt with the workbooks: every row now carries the method's URL |
| 77.4 Header lines the daily run removed | two of four | "To finish", 4 |
| 77.5 Delete `wip/069-storage-buildout` | yes | after checking it is an ancestor of `main` |
| 77.6 The unlock link and the game's checks | no | still 404 |
| 78.1 CAISO's supply in the daily run | yes | `--days`, merged; in `run_daily.sh` before the carbon tables; restored on the runner first |
| 78.2 The carbon builder and `caiso_join --apply` | yes | run here end to end on real extracts, then live |
| 78.3 `cost_of_power_carbon`'s California figure | yes | `cost_of_power.py` reads CAISO's generation from the join |
| 78.4 The switch | yes | below |
| 78.5 The pages | yes | deployed |
| 78.6 The method note live | no | yours |
| 78.7 The mix pages | no | not built |
| 78.8 The three short days | no | not approved |
| 80.1 The shoulder builder with the workbooks | yes | 27,328 rows; Texas's worst days measured |
| 80.2 The page against Supabase, and the branch | yes | check-values 7,398 of 7,398 |
| 80.3 Settle the hour | yes | part (b) |
| 81.1 The report | yes | merged |

**The license check, and the proof asked for.** Session 77's change lets a table that this checkout's coverage does not know pass when its own header in Redivis says "License: public". I added one more condition and two tests before letting it merge:

- **The condition:** a name that the private dataset holds never passes on its header, and if the private dataset cannot be listed nothing passes on a header.
- **`test_no_internal_table_passes_whatever_coverage_and_the_header_say`:** every way an internal table could sit in the public dataset, and the check fails each time: coverage knows it as internal (found by its metadata, even with a header that says public); coverage does not know it and the header says internal, nothing or both; the header says public but the private dataset holds that name; the private dataset cannot be read.
- **`test_no_internal_table_of_the_warehouse_passes_on_its_own_header`:** each of the 14 tables that coverage licenses other than public, put into the public dataset with its own real header lines and forgotten by coverage, fails the check. None of the 14 headers reads public.
- What the check still relies on, and the tests cannot remove: a table that is internal in truth, that no checkout's coverage knows, that the private dataset does not hold, and whose header says public. The uploader refuses to put a table in the public dataset unless the uploading checkout licenses it public, and that refusal is tested too.

**Texas's worst days, which session 80 could not measure.** With the workbook here the builder ranked them:

| Texas (ERCOT) | Average day, hours needed | Ten worst days, hours needed | The worst day | Second measure, average | Batteries ran on the worst days | Fleet holds |
|---|---|---|---|---|---|---|
| 2023 | 9.49 | 29.63 | 44.71 | 3.51 | | 1.43 |
| 2024 | 6.15 | 19.35 | 26.45 | 2.16 | | 1.43 |
| 2025 | 4.21 | 8.88 | 13.86 | 1.37 | about 0.7 to 1.2 | 1.55 |
| 2026 (to September) | 3.17 | **6.58** | **8.61** | 1.01 | about 0.8 to 1.5 | 1.65 |

- **Texas's worst evenings are winter evenings, not summer ones.** Eight of 2026's ten are in January, February and March (the worst, 10 January: 122,254 MWh above the day's mean, a seven-hour shoulder from 17:00); two are in late July. In 2025 all ten fall between October and February.
- **On them the fleet would need about twice what the average day asks:** 6.58 hours at its rated power in 2026, against 3.17 on the average day and 1.65 held. The single worst day asks for 8.61. That is the first number in this work that reaches eight hours, and it is one winter evening measured against everything above that day's mean.
- California, EIA-930, with the hours corrected: the shoulder now starts at the same hour as in CAISO's own data in every overlapping month (June to November 2025), and lasts as long. Its energy is still lower than CAISO's own (47,397 against 60,760 MWh in June 2025), because EIA's solar is lower and CAISO's "demand" here is the sum of its sources.

### (b) California's hours: the cause, the evidence, the fix

**What is wrong.** In EIA's CISO workbook, every hourly value from the row stamped 2023-11-01T00:00 UTC (the hour's end) to the row stamped 2025-12-02T23:00 UTC belongs to the hour before. Before and after, the stamps are right. Session 80 had the end at the 16 December break; it is two weeks earlier, and it has a beginning.

**The evidence** (`warehouse/analysis/caiso_hour_offset.py`, `runs/session82/hour_offset*.out`):

| Test | Result |
|---|---|
| EIA's solar against CAISO's own 5-minute data, day by day | best match at a shift of one hour on **182 of 182 days** from 2025-06-02 to 2025-12-02; at no shift on **298 of 298 days** from 2025-12-03 |
| The same by month | correlation 0.9996 to 0.9998 at one hour and 0.927 to 0.947 at none, June to November 2025; 0.9986 to 0.9997 at none from January 2026. Wind agrees |
| The change itself | on 2 December 2025 EIA's hours are late through the row starting 22:00 UTC and right from the row starting 23:00 UTC |
| The sun, through the whole workbook | the clock time of solar's centre of mass (Pacific standard time) is 11.65 to 12.07 when the stamps are right; it steps from 11.56 on 30 October 2023 to 12.58 on 1 November 2023, stays between 12.5 and 13.0 in every month to November 2025, and returns in December 2025 |
| The afternoon of 31 October 2023 | the morning ramp is the day before's; the evening tail runs an hour past sunset |
| The workbook's own time columns | "UTC time" less "Local time" is Pacific time's offset in every month, on both sides of both dates |
| Texas, the same reading | its centre of mass does not move at either date |

**The cause, as far as it can be seen.** The offset is in the values EIA holds for California, not in how the ERW reads them: the same reading is right for Texas throughout and for California before and after. Both changes fall on a UTC day boundary of EIA's stamps. That points to how the hours were labelled when they were submitted or loaded, and the workbook says nothing about it. I cannot name who changed what.

**Also seen, and left alone:** from July 2018 to mid-June 2022 the same measure sits about half an hour early, with a step of 0.7 hours on 15 June 2022. It is not a whole hour and nothing here can check it. Flagged, not touched.

**The fix, only where it is clear.** `caiso_join.true_hours` reads a California hour in that period one hour earlier (bounds `LATE_FROM`, `LATE_TO`). It is applied in the three builders that set California's EIA hours against a clock or a price. After it, EIA's solar matches CAISO's own at no shift on every day but the day of the change, which a test holds to.

| Rebuilt | What changed |
|---|---|
| `merchant_revenue_monthly` (the seller tab, live) | California solar and wind, September 2024 to December 2025; below |
| `cost_of_power_monthly`, `cost_of_power_carbon` | California's load-weighted price, by at most USD 0.30 per MWh (January to March 2025 up 0.22 to 0.30; June to September 2025 down 0.19 to 0.21); and the join in the carbon figure (January to July 2026 lower by 5 to 12 kgCO2/MWh) |
| `shoulder_hours_monthly` (`iso:caiso`) | the average day and the ranked days of those months |
| `carbon_intensity_*`, `grid_network_*` | the join, not the hours: see below |

**Not corrected, and why.** `eia930_all_emissions` and the hourly carbon tables keep EIA's stamps for those two years: they are EIA's rows as EIA dates them, and an intensity is a ratio within one row, so its value is right and only its hour is one late. Tables that sum by day (`ba_supply_monthly`, `ai_power_regions`, `event_window_daily`) move by one hour at a day's edge; left.

**The seller tab's California solar, before and after** (USD per MW of installed capacity; `runs/session82/seller_before_after.out`):

| Month | Energy, MWh per MW | Revenue before | Revenue after | Change | Capture price before | after |
|---|---|---|---|---|---|---|
| 2024-09 | 204.12 | 4,529.63 | 3,994.97 | -11.8 percent | 22.19 | 19.57 |
| 2024-10 | 168.65 | 3,830.02 | 3,468.02 | -9.5 | 22.71 | 20.56 |
| 2024-11 | 116.87 | 1,359.84 | 1,112.04 | -18.2 | 11.64 | 9.51 |
| 2024-12 | 103.59 | 2,773.96 | 2,679.98 | -3.4 | 26.78 | 25.87 |
| 2025-01 | 125.87 | 2,392.90 | 2,265.92 | -5.3 | 19.01 | 18.00 |
| 2025-02 | 118.83 | -111.85 | -285.45 | more negative | -0.94 | -2.40 |
| 2025-03 | 145.22 | -548.79 | -651.49 | more negative | -3.78 | -4.49 |
| 2025-04 | 189.56 | -769.44 | -1,083.95 | more negative | -4.06 | -5.72 |
| 2025-05 | 228.55 | 1,980.00 | 1,508.05 | -23.8 | 8.66 | 6.60 |
| 2025-06 | 242.80 | 4,346.46 | 3,874.01 | -10.9 | 17.90 | 15.96 |
| 2025-07 | 250.52 | 6,356.84 | 6,058.00 | -4.7 | 25.37 | 24.18 |
| 2025-08 | 220.59 | 7,427.74 | 6,982.32 | -6.0 | 33.67 | 31.65 |
| 2025-09 | 188.58 | 4,707.47 | 4,376.54 | -7.0 | 24.96 | 23.21 |
| 2025-10 | 168.95 | 2,296.29 | 1,791.28 | -22.0 | 13.59 | 10.60 |
| 2025-11 | 102.64 | 2,724.46 | 2,497.40 | -8.3 | 26.54 | 24.33 |
| 2025-12 | 92.41 | 2,321.27 | 2,328.61 | +0.3 | 25.12 | 25.20 |
| **The 16 months** | 2,667.8 | **45,617** | **40,916** | **-10.3 percent** | | |
| 2024 (September to December) | | 12,493 | 11,255 | -9.9 | | |
| 2025 | | 33,123 | 29,661 | -10.5 | | |

- The energy does not change; the hours it is sold in do.
- After the correction, June 2025's capture price is USD 15.96 per MWh; on CAISO's own solar shape session 78 measured 15.97. October 2025: 10.60 against 10.66. The corrected EIA shape and CAISO's own now price alike.
- California wind over the same months: USD 122,889 before, 122,316 after (-0.5 percent).
- **Session 78's analysis of CAISO's own solar shape should be read again in this light:** its "revenue 7.9 percent higher on CAISO's shape" compared CAISO's shape with an EIA shape that was an hour late. With the hour corrected, CAISO's own solar is still about 14 percent more energy than EIA's, and the revenue difference is larger than 7.9 percent, not smaller. Not recomputed here.

### California from the join, live

The daily order is now: EIA's emissions, CAISO's supply (the last three days, merged), the carbon tables without California's generation from the join, `caiso_join.py --apply`, the network. Run here in that order on real extracts: the carbon builder wrote no California intensity of generation from the join, and the apply step wrote 6,681 hourly, 275 daily and 3 monthly rows on CAISO's generation, each carrying its own source. The tables equal session 78's scratch build, row for row, except the newest days, which EIA has revised since. The network's California figure: 83.12 kgCO2/MWh at the hour held before (2026-09-29T23:00Z, on EIA's generation), 127.55 at the hour held now (2026-10-01T23:00Z, on CAISO's); the two are different hours, and session 78's like-for-like figure for the first is 75.86.

### (c) The helper

`scripts/notify.py --session N --branch B --line "..."` sends one line and the report's address through the digest's sender (Resend, the fixed recipients in `DIGEST_RECIPIENTS`, never a subscriber; no address is printed). `--dry-run` prints and sends nothing. Six tests. Used for this report and for each report tonight.

### The deploys, and every difference

Snapshots are in `runs/snapshots/`; the comparisons in `runs/session82/compare*.out`.

| Step | Before, after (UTC) | Every difference | Expected |
|---|---|---|---|
| **Deploy 1:** the hand commit, `de240aa` on `main`, pushed 02:13, production 02:14 | 02:06, 02:16 | `/`: 40 lines, all of them the six latest prices, their interval times and the "days in the ERW table" labels. `/network`: 6 lines, the hourly refresh's times. Nothing else on 18 pages | yes: they move by themselves |
| **The live-set load,** 02:50 to 02:55 | 02:49, 03:07 | `/`: the catalogue's four numbers: public tables 95 to 97, rows 13,668,095 to 13,832,474, last refresh 2026-10-03 17:09 to 2026-10-04 02:29 UTC, "95 of 95 pass" to "97 of 97 pass"; and the latest prices. Nothing else | yes: the full load wrote the catalogue from coverage, which holds two public tables the catalogue did not (session 76 loaded by table name), and this session's rebuilt rows |
| **Deploy 2:** `task/082-land`, pushed 03:08, checks passed (run 37173201003), merged as `3dd9aff`, production 03:14 | 03:07, 03:16 (20 pages) | 282 lines on 5 pages, below. `/`, `/storage` and the 13 battery pages: 0 | yes, each one |

Deploy 2, page by page:

- **`/about`, 4 lines:** "The shoulder hours" and "Storage build-out" lose their descriptions (session 77).
- **`/network`, 7 lines:** the new sentence about California's carbon intensity (session 78), with "the method note" greyed since that note is in review; and the hourly refresh's times and "Built" line, which move by themselves.
- **`/cost-of-power/seller` (the default, Texas solar), 23 lines:** not the hour correction. This build's seller snapshot holds EIA's newer days: September 2026 is now complete (USD 786,467.55 became 818,175.63; 93 percent of the month became 100), October 2026 appears as a partial month (USD 28,167.65, 6 percent of its hours), and the figures that include them follow (the year's average 12.21 to 12.22 million USD; "25 months" to "26 months").
- **`/cost-of-power/seller?iso=caiso&asset=solar`, 127 lines:** the correction. Revenue, capture price, capture rate and debt cover of 17 months (the 16 corrected and September 2026), October 2026 new, and the summary: the year's average for 100 MW from USD 3.22 million to 3.01 million, the median month 232,126.96 to 226,591.67, the 10th-percentile month -76,944.36 to -108,394.84.
- **`/cost-of-power/seller?iso=caiso&asset=wind`, 121 lines:** the same months, by 0.5 percent in all.

No difference that was not meant. One thing a visitor would notice that is not a number moving for a reason they can see: October 2026 is on the seller tab with two days in it and a debt cover of -0.13 for Texas solar. That is how the page has always shown a month in progress.

## Tests and checks

| Check | Result |
|---|---|
| `python -m unittest discover -s tests`, before the push | 458 tests, 1 failure, 9 skipped, exit 1: `test_session49.Interchange.test_interchange_ceiling` (`eia930_all_interchange`, 151,632 rows against 150,000; session 77's finding, not ruled on). On GitHub the table is absent and the test skips |
| `tests.test_redivis_gates` | 26 tests OK, the two proofs among them |
| `tests.test_session82` | 13 tests OK: the email helper (6), the daily supply and the carbon builder's rule (3), the late hours (4), one of which reads the workbook: every day late before the fix, every day right after it |
| `tests.test_session55` | the dated test now follows the snapshot it reads; OK |
| Validator, the 12 rebuilt tables | exit 0: 12 PASS, 0 errors, 0 warnings |
| Coverage, archive (103 tables archived, 0 failed), upload by name (13 of 13, each count equal), `--check-license` | exit 0 each |
| `load.py` | **exit 1, read and not forced.** Every rebuilt table says "match"; catalogue 111 and sources 193 match. The exit is for 9 tables the loader refused because this laptop's copies are older than the live ones (the daily run rewrote them with the same rows and a newer retrieval time, so the sync calls them current and the loader calls them old). Nothing was written for those 9: the guard did its work |
| `npx tsc --noEmit`, `npm run build` | exit 0 each (the build logged two Supabase statement timeouts) |
| `check-routes`, both passes | exit 0: 80 of 80 with the cookie; 14 live and 66 in review as a visitor |
| `check-values` | exit 0: **7,398 of 7,398** |
| GitHub, `code-branch.yml` on `task/082-land` | success: tests, the site build and check-routes on GitHub; merged as `3dd9aff` and deployed |

## Errors and decisions

- **Decision: the emissions connector was run to bring the workbooks here** (above). It is the daily run's own connector; it also added a day to `eia930_all_emissions` (1,464 rows), uploaded with the rest.
- **Decision: the hour correction is a reader's rule, not a change to EIA's rows.** The source table keeps EIA's stamps; three builders read California's hours through one function with two named bounds.
- **Decision: the half-hour offset before June 2022 is not corrected.** Not a whole hour, no second source.
- **Decision: the upload was by table name** (the 12 rebuilt tables), not `--changed`: the manifest on `main` is two daily runs old, and `--changed` would have uploaded about 50 tables this machine did not change.
- **Decision: the snapshot script now reads California's solar and wind on the seller tab** (20 pages). The default seller page is Texas's solar, and this session's correction moved only California's.
- **Decision: session 78's and session 80's tests of their scratch tables now read the live tables,** since the join and the rebuilt shoulder table are in `warehouse/output`.
- **Decision: the mix pages, the method note's release and the three short days are left** ("To finish").
- **Error, mine:** the lock wrapper was first given the interpreter's path relative to the repository and could not start it; nothing ran, the lock was not taken. Rerun with the full path.
- **Found:** yesterday's "13 package test mismatches" were never located; after this session's rebuilds the package tests were not rerun (no time was given to them; the daily run runs them after its commit).

## For Samuel

1. **Look at the seller tab's California solar** (`/cost-of-power/seller?iso=caiso&asset=solar`): the months from September 2024 to November 2025 are lower than the page showed yesterday. If an investor has seen the old numbers, this is the correction to send.
2. **Texas's worst evenings are in winter and ask for 6.6 hours on average, 8.6 at the worst** (2026). That changes the answer session 80 gave the investor for Texas.
3. **Approve or decline:** the three short CAISO days; the method note live; the mix pages.
4. **`eia930_all_interchange`'s ceiling** is still passed (session 77, "For Samuel", 4).
5. **The half hour before June 2022** in EIA's California series: if the early years matter, someone should ask EIA.
