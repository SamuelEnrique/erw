# Session 78 report: the California correction, prepared and held

**Nothing live changed.** No push to `main` or to a `task/` branch, no table in `warehouse/output` rewritten, nothing loaded or uploaded. Everything is on `wip/078-california` (which holds `wip/077-housekeeping`), and the corrected tables are scratch files under `runs/session78/`.

**What the ruling changes, in one line:** from 16 December 2025 California's carbon intensity of generation falls by 7 to 11 percent (110.80 to 100.91 kgCO2/MWh over the 6,657 hours held since), because it is now divided by CAISO's own generation, which is larger than EIA's. The consumed intensity does not change at all.

**Three things to know before making it live:**

1. **It cannot go live as a one-off.** From the join California's figure exists only where `caiso_fuel_supply` holds the hour, and that table is not in the daily run: it ends at 2026-10-03T06:00Z. Switched on today, California's carbon number on `/network` would stop at the last hour pulled. The supply has to be scheduled first ("To finish", step 2), and a scheduled pull needs your approval.
2. **Three months of 2026 lose their monthly figure.** A month needs every day and a day its 24 hours, and CAISO's supply is short on three Pacific days (2026-03-08, a clock change the connector could not place; 2026-08-21, CAISO's file empty; 2026-09-22, 287 of 288 intervals). So March, August and September 2026 have no monthly California figure after the join, and neither has December 2025, which holds the join. Nothing was filled.
3. **The mix pages are not switched.** `/mix`, `/grid` and the California grid page still read EIA-930's generation by fuel for California. Their sentence now says so plainly. The ruling covers the mix too; that switch is listed, not built.

Energy Research Warehouse (ERW), session 78, second of the chain of 3 October, on the old laptop, 2026-10-03 from about 19:55 to 20:25 UTC, unattended. **Model spend: USD 0.00.** No pull, no model call, no force push. The data lock was never taken.

## To finish

After the freeze (6 October), in this order. Steps 1 to 3 are code still to write or lines to add; I did not add them to the daily run blind, since this laptop has no raw extracts to run those builders on.

```bash
# 0. wip/077-housekeeping first (its "To finish", step 2); this branch holds it.

# 1. A daily mode for the supply connector (not built). warehouse/connectors/caiso_fuel_supply.py takes --start and
#    --end and rewrites its window; it needs to merge the last days into the held table, as caiso_as_prices does.
#    Then in warehouse/run_daily.sh, before carbon_intensity:
#      run_other caiso_fuel_supply "$PYTHON" warehouse/connectors/caiso_fuel_supply.py --days 3
#    and in warehouse/redivis/config.yaml, restore_before_run:
#      - '^caiso_fuel_supply$'
#    This is a scheduled source pull (about 312 rows a day): yours to approve.

# 2. Two lines in warehouse/derived/carbon_intensity.py, so EIA's generation is never written for California from the
#    join (a day the next step fails then leaves those rows absent, not EIA's):
#      sys.path.insert(0, HERE); import caiso_join as cj                      # with the other imports
#      if code == "ciso" and var == cj.VARIABLE: j = cj.before_join(j)       # after: j = j[j["mwh"] > 0].rename(...)
#    and in warehouse/run_daily.sh, directly after carbon_intensity:
#      run_other caiso_join "$PYTHON" warehouse/derived/caiso_join.py --apply

# 3. cost_of_power_carbon's California intensity_generation: the same join inside warehouse/derived/cost_of_power.py
#    (its denominator is the workbook's net generation; from cj.JOIN it should be cj.caiso_hours()["net_generation_mwh"]).
#    Not built. runs/session78/before_after_cost_carbon.csv holds what it will give.

# 4. The switch, on a machine with warehouse/raw (the personal laptop), with a snapshot before and after: /network is
#    live and reads carbon_intensity_hourly, so its California number moves (83.12 to 75.86 at the hour held today).
node site/scripts/snapshot-live.mjs take before_078
python warehouse/lock.py acquire --task "California from the join" --minutes 60; echo "exit=$?"
python warehouse/derived/carbon_intensity.py; echo "exit=$?"
python warehouse/derived/caiso_join.py --apply; echo "exit=$?"
python warehouse/validate/erw_validate.py warehouse/output/carbon_intensity_hourly.csv warehouse/output/carbon_intensity_daily.csv warehouse/output/carbon_intensity_monthly.csv; echo "exit=$?"
python warehouse/derived/grid_network.py; echo "exit=$?"
python warehouse/metadata/build_coverage.py > runs/coverage.out 2>&1; echo "exit=$?"
python warehouse/archive/archive.py write; echo "exit=$?"
python warehouse/redivis/upload.py --changed; echo "exit=$?"
python warehouse/supabase/load.py; echo "exit=$?"
python warehouse/lock.py release

# 5. The pages: the branch through a task/ branch. On live pages only /network differs (one sentence), plus /about
#    from session 77.
git checkout wip/078-california && git fetch origin && git merge origin/main
git push origin wip/078-california:task/078-california
node site/scripts/snapshot-live.mjs take after_078 && node site/scripts/snapshot-live.mjs compare before_078 after_078

# 6. If /network's sentence should link for visitors: in site/lib/release.ts, "/data/methods/eia930_caiso_break": "live".
#    Today the method note is in review, so a visitor sees "the method note" greyed.

# 7. The mix pages (not built): caiso_fuel_supply into the live set (warehouse/supabase/live_set.yaml), and /mix, /grid
#    and /grid/caiso reading it for California from cj.JOIN.

# 8. The three short days, if CAISO has them: a pull of 2026-03-08, 2026-08-21 and 2026-09-22 (the first needs the
#    connector to place a 23-hour day). Yours to approve.
```

## In plain words

### How the join is built

- **One constant.** `JOIN = "2025-12-16T08:00:00Z"` in `warehouse/derived/caiso_join.py`, the first hour that is CAISO's own (midnight Pacific). The site holds one copy (`site/lib/caisoJoin.ts`), and a test fails if the two differ or if any other code that builds tables or pages names the date.
- **What changes:** California's `intensity_generation`. Before the join the held rows stand, unchanged. From the join it is EIA's CO2 generated over CAISO's own net generation: every source of CAISO's supply but imports, batteries net.
- **Why the CO2 stays EIA's.** CAISO's supply carries no emissions, so CO2 can only come from factors, and EIA's are the ones held. I first rebuilt it from CAISO's gas and coal times EIA's factors; that dropped what EIA counts under oil and other, 2.4 to 12.8 percent of California's CO2 depending on the month, and lost hours wherever EIA's by-fuel CO2 has gaps. And it is not needed: from the join EIA's gas series is CAISO's own. EIA's gas CO2 over CAISO's gas MWh is **0.4049 tCO2/MWh over 6,609 hours**, against EIA's own factor of 0.4051. What the break left wrong is the denominator. The build repeats this check on every run and stops if the ratio leaves the factor by more than 2 percent.
- **What does not change: the consumed intensity.** Its numerator (EIA's CO2 generated plus imported less exported) and its denominator (EIA's demand) are not generation series, so its rows are EIA's on both sides. Its fall across the date is still partly EIA's reporting change; no data held can correct it.
- **Never mixed.** A period is written from one source or not at all. An hour from the join rests on CAISO's generation or is absent. The day and the month that hold the join are not written. Each row says its side in its own `source` column: `erw:carbon_intensity` before, `erw:carbon_intensity_caiso` from the join.

### The corrected tables (scratch, `runs/session78/`)

Each carries the join date, the rule and the method's address in its header. All three pass the validator (0 errors, 0 warnings). Every row that is not California's `intensity_generation` from the join equals the held table's, checked row for row.

| Table | Rows | Copied as they stand | EIA rows of California from the join, dropped | Written on CAISO's generation |
|---|---|---|---|---|
| `carbon_intensity_hourly` | 1,120,341 | 1,113,684 | 6,712 | 6,657 |
| `carbon_intensity_daily` | 46,666 | 46,392 | 280 | 274 |
| `carbon_intensity_monthly` | 1,275 | 1,272 | 6 | 3 |

The six days lost: 2025-12-16 (it holds the join) and 2026-03-09, 08-21, 08-22, 09-22, 09-23 (CAISO's short days, in UTC). The monthly table under EIA held December 2025 and May to September 2026; joined, it holds May, June and July 2026.

### Before and after: California's carbon intensity of generation, by month

The same hours both ways (`runs/session78/before_after_carbon_monthly.csv`); kgCO2/MWh.

| UTC month | Hours both hold | EIA's generation, GWh a day | CAISO's own | On EIA's generation | Joined | Change | Monthly table, EIA | Monthly table, joined |
|---|---|---|---|---|---|---|---|---|
| 2025-12 (from the join) | 376 | 337.5 | 374.8 | 135.27 | 121.79 | -10.0 percent | 183.00 (whole month) | not written |
| 2026-01 | 696 | 348.4 | 385.7 | 126.56 | 114.31 | -9.7 | not held | not written |
| 2026-02 | 600 | 361.5 | 403.6 | 119.47 | 107.01 | -10.4 | not held | not written |
| 2026-03 | 665 | 403.4 | 449.3 | 90.01 | 80.80 | -10.2 | not held | not written |
| 2026-04 | 696 | 389.0 | 436.6 | 62.80 | 55.96 | -10.9 | not held | not written |
| 2026-05 | 744 | 429.1 | 476.2 | 49.07 | 44.21 | -9.9 | 49.07 | 44.21 |
| 2026-06 | 720 | 478.2 | 530.7 | 53.58 | 48.28 | -9.9 | 53.58 | 48.28 |
| 2026-07 | 744 | 596.5 | 640.6 | 136.72 | 127.31 | -6.9 | 136.72 | 127.31 |
| 2026-08 | 720 | 655.8 | 706.1 | 171.92 | 159.68 | -7.1 | 172.56 | not written |
| 2026-09 | 696 | 514.6 | 556.4 | 135.38 | 125.19 | -7.5 | 134.55 | not written |

January to April 2026 have no monthly figure either way: EIA's own CO2 is short of days in those months.

### Before and after: the mix

On the 888 hours both tables hold from the join (2026-08-26 to 2026-10-02; EIA's by-fuel history before that is in the raw workbooks, which this laptop does not hold). Mean MW (`runs/session78/before_after_mix.csv`):

| Fuel | EIA-930 | CAISO's own | Difference |
|---|---|---|---|
| Natural gas | 8,127.9 | 8,128.3 | 0.4 |
| Geothermal | 779.0 | 779.0 | 0.0 |
| Hydro (CAISO: large and small) | 2,048.7 | 2,048.8 | 0.1 |
| Nuclear | 2,177.3 | 2,177.3 | 0.0 |
| Coal | 1.6 | 1.6 | 0.0 |
| **Solar** | 7,029.3 | 7,973.0 | **943.7 (13.4 percent)** |
| **Wind** | 2,719.0 | 3,192.0 | **473.0 (17.4 percent)** |
| Oil (CAISO: no such source) | 16.3 | none | |
| Other (EIA) against biogas, biomass, other and batteries (CAISO) | -281.2 | 58.1 | 339.3 |
| **All generation** | 22,617.7 | 24,358.0 | **1,740.3 (7.7 percent)** |

So after the break five fuels are the same series, and the gap is solar, wind and "other". CAISO's own mix by month from the join is in `runs/session78/caiso_mix_monthly.csv` (solar from 3,056 MW in December to 9,619 in June; gas from 1,889 MW in May to 11,459 in August).

### Before and after: the other figures

| Figure | Before | After | Note |
|---|---|---|---|
| The network's California number (`grid_network_nodes`, the hour held, 2026-09-29T23:00Z) | 83.12 kgCO2/MWh | 75.86 | the live page's sphere colour and panel |
| The same, the newest hour both hold (2026-09-30T23:00Z) | 106.06 | 96.69 | |
| `ai_power_regions`: California's carbon (consumed, the year's daily mean) | 142.80 | 142.80 | unchanged: consumed intensity is EIA's |
| `ai_power_regions`: California's import share by EIA's balance, the year to September 2026 | 26.91 percent | 21.89 | on the 8,441 hours the join holds; the held table says 27.02 on the workbook's hours |
| The same, from the join only (5,961 hours) | 29.53 percent | 22.48 | by its ties, session 68 measured about 16.5 |
| `cost_of_power_carbon`: California, January 2026 | 125.87 | 113.64 | the builder's rule, replicated |
| February 2026 | 118.91 | 106.56 | |
| April 2026 | 61.13 | 54.47 | |
| May 2026 | 48.86 | 44.02 | |
| June 2026 | 53.63 | 48.32 | |
| July 2026 | 138.12 | 128.68 | |
| December 2025, March, August and September 2026 | 182.77, 90.88, 172.17, 134.55 | not written | the join's month, and CAISO's short days |

The import share still reads above the ties' figure after the correction: EIA's demand counts energy that is in no one's generation (session 73, not settled).

### The pages

One sentence, with the method link, in place of "under review" (`site/components/CaisoBreakNote.tsx`), and it differs by what the page shows:

- **`/network` (live), `/emissions`, `/cost-of-power`:** "California's carbon intensity of generation is EIA's CO2 over EIA's generation before 16 December 2025 and over CAISO's own generation from that date, joined there and not blended: the method note." `/network` had no label; it has this one now, above its source line.
- **`/mix`, `/grid`:** "California's generation by fuel here is EIA-930's, whose solar and wind have read below CAISO's own supply since 16 December 2025: the method note."
- **The California grid page:** the first sentence, ending "; its generation by fuel here is still EIA-930's".
- **The AI gigawatts draft:** its carbon figure is consumed intensity and its import share is EIA's balance, so its sentence says the import share reads high from that date and the carbon figure is EIA's on both sides.

The first sentence is true only once the joined tables are live; the sentence and the tables go live together. The method note (`docs/methods/eia930_caiso_break.md`) now states the ruling, the join, what changes and what does not.

### The seller tab's California solar (analysis only)

`merchant_revenue_monthly` pays a solar plant on EIA's solar per MW installed. The same arithmetic on CAISO's own solar (`warehouse/analysis/caiso_solar_seller.py`; it reproduces the table's September 2026 row exactly on EIA's solar, 183.9650 MWh and USD 4,409.6639 per MW). Over the **13 months both rest on the same hours** (June 2025 to July 2026 without March):

- **Energy: 14.4 percent more** (2,359.7 against 2,700.2 MWh per MW).
- **Revenue: 7.9 percent more** (USD 38,087 against 41,077 per MW). Less than the energy, because the extra output is at midday, when prices are lowest.
- **Not every month gains.** October 2025 falls 10.4 percent (USD 2,296 to 2,057). April and May 2026 are negative and become more so (USD -1,330 to -1,525; -1,176 to -1,356): more output sold at negative prices.
- The largest gains: July 2026, USD 915 per MW (13.8 percent); August and July 2025, USD 647 and 642.

Month by month: `runs/session78/seller_solar_caiso_shape.csv`. March, August and September 2026 are left out of the comparison (the two rest on different hours).

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session78.py` | 18 tests, OK: the constant and its one copy; no other code names the date; the sides of an hour, a day, a month; before the join every hour is EIA's and from it every hour is CAISO's, on toy frames; an hour CAISO lacks is absent, never EIA's; values by hand; the join's day and month left out; a short day and its month left out; the splice changes nothing else and keeps the file's order; the check names a row on the wrong side; the scratch build refuses `warehouse/output`; on the built tables, no series mixes the two sources on one side, the values equal EIA's CO2 over CAISO's generation, and EIA's gas is still CAISO's gas; the sentence |
| `python -m unittest discover -s tests` | 414 tests, 1 failure, 12 skipped, exit 1: the failure is session 77's finding (`eia930_all_interchange` over its ceiling), nothing of this session |
| `caiso_join.py` (scratch build and its own check) | exit 0 |
| Validator, the three scratch tables | exit 0: PASS, 0 errors, 0 warnings each |
| `npx tsc --noEmit`, `npm run build` | exit 0 each |
| `check-routes`, both passes, local build | exit 0: 80 of 80 with the cookie; 14 live and 66 in review as a visitor |
| The note on each page, local build | once on `/network`, `/emissions`, `/cost-of-power`, `/mix`, `/grid`, `/grid/caiso`; not on `/grid/ercot` |
| `snapshot-live.mjs`: production against this branch's local build | 5 lines of difference: `/about`'s four (session 77) and `/network`'s new sentence; 0 of 3,797 checked number keys |

Not run: `check-values` (no number on a page changed), the coverage builder, the archive, the uploader, the loader (nothing was written to the warehouse).

## Errors and decisions

- **Decision: CO2 generated stays EIA's from the join,** for the reasons above. The ruling's words could also mean CO2 rebuilt from CAISO's fuels; the two differ by 0.05 percent on gas, and the rebuilt one loses the CO2 EIA counts under oil and other. If you want it rebuilt, say so.
- **Decision: the consumed intensity is left as EIA's.** "The generation side of its carbon figures" is the intensity of generation. This means `ai_power_regions`' carbon figure does not move.
- **Decision: the join is a splice of the built tables, not a change inside the builders.** `carbon_intensity.py` needs the raw extracts, which this laptop does not hold, so I could not run it. The join reads the held tables and replaces only California's rows from the join; the same code is the scratch build and, with `--apply`, the live step. `--apply` was written and is covered by the same check, but was not run.
- **Decision: EIA's hourly demand and generation are recovered from the held tables** (CO2 times 1000 over the held intensity) for the comparisons. Against the hours `eia930_all_demand` and `eia930_all_generation` hold, the largest difference is 0.04 MWh.
- **Decision: the daily run is not wired.** Adding two steps to `run_daily.sh` without being able to run them here risks the run that keeps the live site fed. The lines are in "To finish".
- **Decision: session 75's page note keeps its own mention of the date** (`site/lib/shoulder.ts` runs in Node without imports); the one-constant test allows it by name, with session 73's two analysis scripts.
- **Found: `cost_of_power_carbon`'s held rows are not all rebuilt from today's hours.** My replication of its EIA figure equals the held row to four decimals in 10 of 16 months; in six (October 2025, January to April and September 2026) the held row differs by up to 2.26 kgCO2/MWh. Those rows were written when fewer of the month's hours were held, and the builder carries them. Not this session's subject; flagged.
- **Error, mine:** my first build rebuilt the CO2 from CAISO's gas and coal and dropped EIA's oil and other CO2; May's consumed intensity fell 7 percent for no reason in the data. Caught on the first monthly comparison, before anything was committed.
- **Error, mine:** the first test run failed on my own files naming the date in comments; reworded.

## For Samuel

1. **Approve the daily pull of CAISO's supply by fuel** (about 312 rows a day), or the correction has nothing to stand on after today.
2. **Rule on the three months without a monthly figure** (and December 2025): accept the gaps, or approve a pull of the three short days.
3. **The mix pages:** build the switch, or leave them on EIA-930 with the sentence they now carry.
4. **The seller tab:** on CAISO's own solar a California solar plant earns about 8 percent more over the 13 months compared, on 14 percent more energy. Say whether the tab should switch.
5. **The method note's status for visitors:** `/network` is live and now points to a note that is in review.
6. **The import share stays above the ties' figure** (22.5 percent by EIA's balance from the join, about 16.5 by its ties): EIA's demand, not its generation, is the open question there.
