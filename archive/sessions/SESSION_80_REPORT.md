# Session 80 report: the shoulder on the worst days

**Half of this session could not be run on this machine, and one finding matters beyond it.**

1. **Texas's worst days were not measured.** They need EIA-930's hourly workbooks (`warehouse/raw/eia930_emissions`), and the old laptop holds no raw files; no pull was approved. The code that ranks them is written and tested on made-up days, and will run as it stands on a machine that holds the workbooks ("To finish", step 1). What this laptop could measure: the second shoulder measure for every month of both grids, from the average days the table already holds, and **California's worst days from CAISO's own data** (June 2025 to 2 October 2026).
2. **Flagged, and it reaches a live page: California's EIA-930 hours before 16 December 2025 look one hour late.** Set beside CAISO's own data, the EIA-based average day of July and of November 2025 has sunrise and sunset an hour late (solar's two profiles match at 0.9998 when EIA's is moved one hour earlier, 0.946 as it stands). Texas's profile is not late. After the December break the two sources agree to the hour. This makes session 75's California shoulder one hour short, and it means the seller tab's California solar before the break is paid on a shape that runs an hour into the evening. Details and evidence below; I changed nothing.
3. **On California's ten worst days of 2025 the fleet would need 5.25 hours at its rated power, against 3.99 on the average day,** to deliver all of the evening shoulder's energy above the mean (CAISO's own data, June to December). Its batteries ran 2.49 hours' worth on those days; the fleet holds 3.44.

Nothing live changed: `/shoulder` stays `review`, the table in `warehouse/output` and in Supabase is as it was, and the new table is a trial file under `runs/session80/build/`.

Energy Research Warehouse (ERW), session 80, fourth of the chain of 3 October, on the old laptop, 2026-10-03 from about 20:31 to 20:55 UTC, unattended. **Model spend: USD 0.00.** No pull, no model call, no force push. Branch `wip/080-shoulder-worst` (it holds 077 to 079). The data lock was never taken.

## To finish

```bash
# 1. On a machine that holds warehouse/raw/eia930_emissions (the personal laptop), after wip/077 has merged (this branch
#    holds its source_url fix). The builder then rebuilds all three entities, Texas's and EIA-California's worst days
#    included; on this laptop it could only keep their rows.
python warehouse/derived/shoulder_hours.py --out-dir runs/session80/trial; echo "exit=$?"     # a trial first: look at it
python warehouse/lock.py acquire --task "shoulder_hours_monthly: second measure and worst days" --minutes 30; echo "exit=$?"
python warehouse/derived/shoulder_hours.py; echo "exit=$?"
python warehouse/validate/erw_validate.py warehouse/output/shoulder_hours_monthly.csv; echo "exit=$?"
python warehouse/metadata/build_coverage.py > runs/coverage.out 2>&1; echo "exit=$?"
python warehouse/archive/archive.py write; echo "exit=$?"
python warehouse/redivis/upload.py --tables shoulder_hours_monthly; echo "exit=$?"
python warehouse/supabase/load.py --only '^shoulder_hours_monthly$'; echo "exit=$?"     # a review page's table
python warehouse/lock.py release

# 2. The page, against Supabase once the table is loaded (it is in check-values' pages), and the branch
cd site && npm run build && npx next start -p 3049 &
node scripts/check-values.mjs http://localhost:3049
git checkout wip/080-shoulder-worst && git fetch origin && git merge origin/main
git push origin wip/080-shoulder-worst:task/080-shoulder-worst      # /shoulder stays review; no live page changes with it

# 3. Before step 1, settle finding 2 (the hour): on that machine, compare EIA's CISO solar by hour with caiso_fuel_supply's
#    for a week before 2025-12-16 and a week after. If EIA's hours before the break are an hour late, shoulder_hours.py,
#    merchant_revenue.py, cost_of_power.py and the emissions extract all read them that way.
```

## In plain words

### What was built

- **A second shoulder measure** (`shoulder2_*`): the run of hours around the evening's highest net load in which net load is above the midpoint between its daily mean and that peak. Its hours, its start and end, its MWh above the midpoint, and the fleet's hours covered and needed against it.
- **The worst days** (`worst_rank`, `day_*`, freq P1D): for each grid and local year, the ten complete days with the most evening shoulder energy above the day's own mean. For each, the shoulder by both measures, the hours the month's fleet would need at its rated power, and what its batteries did in the shoulder where every hour of the day holds their output. Yearly rows (`year_worst10_*`) set the ten beside the average day.
- **California's two sources as two entities, never mixed:** `iso:caiso` is EIA-930 through November 2025, as before; `iso:caiso_own` is CAISO's own supply by fuel from June 2025. In the own series solar, wind and battery output are CAISO's and demand is the sum of its thirteen sources.
- **A builder that says what it could not do.** On a machine without an EIA grid's workbook it keeps that grid's rows as they stand, adds the second measure from the average day the table already holds (after checking that the first measure recomputed that way equals the held one: it did, in all 175 months), writes no worst day for it, and says so in the header and the log.
- **`/shoulder`**, still `review`: a second section, "A shoulder that ends inside the evening, and the worst days" (three headline numbers, the year's ten days, a second table by year), a third choice of grid ("CAISO, its own data"), and the summary sentence now gives the average day and the worst days together, for example: "In September 2025, by CAISO's own data, CAISO's evening shoulder lasted 6 hours, from 18:00 to 24:00 (midnight); its batteries could run 3.44 hours at full power, covering 3.44 of them. To deliver all of the shoulder's energy above the mean they would need 4.19 hours on the average day, and 5.25 on the ten worst days of 2025." Where a grid's worst days are not held, the sentence says so.

The trial table: **25,004 rows** (the 20,464 held, unchanged, and 4,540 new: 2,717 of California's own data, 968 of Texas's second measure, 855 of EIA-California's). Validator: PASS, 0 errors, 0 warnings.

### The second measure: does it end inside the evening?

In Texas, yes, every month. In California, mostly not.

| Texas (ERCOT), mean over the year's months | First measure, hours | Hours needed | Second measure, hours | Hours needed | Hours the fleet covers | Fleet's own hours |
|---|---|---|---|---|---|---|
| 2019 | 3.92 | 148.53 | 2.75 | 52.92 | 0.78 | 0.94 |
| 2021 | 4.08 | 49.93 | 3.00 | 18.40 | 1.23 | 1.29 |
| 2023 | 4.75 | 9.49 | 3.33 | 3.51 | 1.32 | 1.43 |
| 2024 | 5.17 | 6.15 | 3.42 | 2.16 | 1.45 | 1.43 |
| 2025 | 5.83 | 4.21 | 3.83 | 1.37 | 1.50 | 1.55 |
| 2026 (to September) | 5.78 | 3.17 | 4.00 | 1.01 | 1.58 | 1.65 |

- **Texas:** the second shoulder ends inside the evening in all 93 months (in 2026 it starts between 17:00 and 19:00 and ends at 22:00 or 23:00). Its energy above the midpoint would take the 2026 fleet **1.01 hours** at rated power, and the fleet holds 1.65. By the first measure it needs 3.17. So on the average day the answer turns on which energy one asks the batteries to cover: the top of the evening peak, which they already cover, or everything above the daily mean, which takes twice what they hold.
- **California, EIA-930:** the second measure is still above its midpoint at midnight in 42 of 82 months, and in every month of 2025. Second-measure hours needed: 72.46 in 2019, 11.28 in 2021, 2.67 in 2023, 1.48 in 2024, 1.16 in 2025 (first measure: 2.85).
- **California, CAISO's own data:** still above the midpoint at midnight in 14 of 16 months. **The second measure does not do in California what it was meant to do:** net load there stays high into the night, so any level between the mean and the peak is still exceeded at midnight, and the day's last hour cuts it. A window from noon to noon would be needed to see where California's evening ends. That is a definition for you to rule on, as the first one was.

### California's worst days, from CAISO's own data

| | Average day | The ten worst days |
|---|---|---|
| **2025 (June to December; 213 days ranked)** | | |
| Shoulder energy above the mean, MWh | 57,494 | 76,326 |
| Hours needed at the fleet's power | 3.99 | **5.25** (the worst day 5.88) |
| Hours needed, second measure | 1.56 | 1.98 |
| What the batteries ran, hours at rated power | | 2.49 |
| The fleet's own hours | 3.44 | |
| **2026 (January to 2 October; 272 days ranked)** | | |
| Shoulder energy above the mean, MWh | 59,434 | 82,008 |
| Hours needed at the fleet's power | 3.59 | not given: five of the ten are in September and October, whose fleet EIA has not published |
| The five August days among them | | 4.53 to 5.12 |
| What the batteries discharged in those shoulders, MWh | | 39,403 to 49,186 a day |

- The ten days of 2025: 1 September (84,551 MWh above its mean; 5.88 hours needed; the batteries ran 2.20), then 30 August, 5 October, 9 November, 31 August, 7 September, 3 August, 20 August, 6 October and 15 September. Six of the ten are in late August and early September.
- The ten of 2026: 2 October (90,220 MWh), 23 August, 8 September, 26 September, 19 August, 2 August, 23 September, 1 October, 9 August and 3 August.
- **What it says about longer storage:** on its worst evenings California's shoulder holds about a third more energy than on the average evening, and covering all of it above the mean would take a little over 5 hours at today's power, against the 3.4 the fleet holds. That is not 8 hours. And on those evenings the batteries delivered about 2.5 hours' worth, less than they hold: the rest of the shoulder was met by gas, hydro and imports. The worst days ranked here are high-demand evenings; a week of low sun, which is the other case for long storage, is not what this ranking finds.

### Finding: California's EIA-930 hours before the break look one hour late

The trial table holds California's average day from both sources for June to November 2025. Side by side, by local hour, July 2025, MW of solar:

| Local hour | 05 | 06 | 07 | 08 | 18 | 19 | 20 | 21 |
|---|---|---|---|---|---|---|---|---|
| EIA-930 (`iso:caiso`) | -35 | -21 | 2,429 | 10,189 | 14,460 | 9,189 | 1,977 | -5 |
| CAISO's own (`iso:caiso_own`) | -30 | 2,426 | 11,334 | 17,334 | 11,173 | 2,645 | 7 | -39 |

- **EIA's profile is CAISO's, one hour later.** The correlation of the two solar profiles is 0.946 as they stand and 0.9998 with EIA's moved one hour earlier; in November, 0.931 and 0.9997. It is the same hour in July (daylight time) and November (standard time), so it is not a clock-change error.
- **CAISO's is the one that fits the sun.** In early July the sun rises before 06:00 and sets about 20:15 in southern California: 2,426 MW between 06:00 and 07:00 fits; -21 MW in that hour and 1,977 MW after 20:00 do not.
- **Texas is not late.** ERCOT's held profile has solar from 07:00 in July and ending after 20:00, with sunrise near 06:40 and sunset near 20:35 there.
- **After the break the sources agree to the hour.** Session 78 measured it: from 16 December 2025 EIA's gas against CAISO's gas is 0.9999 at no shift, 0.99 at one hour either way.
- **Session 78's seller-tab comparison shows the same thing, from the money side.** Before the break the table's capture price for California solar is above CAISO-shape's every month (June 2025: USD 17.90 against 15.97 per MWh; October: 13.59 against 10.66); after it the two are equal to a cent or two (January 2026: 19.30 and 19.31; June: 2.60 and 2.59). A solar shape an hour late sells into the evening ramp.

**What I cannot settle here:** whether EIA's California record before 16 December 2025 is itself an hour late (and the break corrected that too), or whether the ERW's reading of that workbook is. Both builders that read it treat Texas and California alike, and Texas is right, which points at the data; the workbook is not on this laptop. "To finish", step 3.

**What it touches if it is real:** `iso:caiso` in this table (its shoulder starts and ends an hour late and is cut an hour early at midnight: 4 hours in July 2025 where CAISO's own data gives 5, and 40,769 MWh above the mean where it gives 60,633); `merchant_revenue_monthly`'s California solar and wind before the break, on the live seller tab; `cost_of_power`'s California load weights; California's hourly carbon intensity before the break.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session80.py` | 15 tests, OK: the second measure on a day by hand (four hours, 18:00 to 22:00, its MWh, the first measure cut at midnight beside it); what always holds between the two measures on 200 made-up days; no evening above the mean, no second shoulder; still above the midpoint at midnight is flagged; the fleet against it; one unit rule for every variable; ten days a year ranked by shoulder energy; hours needed is the day's energy over the month's fleet and is never guessed; the batteries' output only where every hour holds it; a clock-change day is not ranked. On the trial table: California's two sources are two entities and each stays in its window; the earlier rows are kept as they stand, all 20,464; the second measure is in every month and inside the first; ten ranked days a year where days are held |
| `tests/test_session75.py` | 7 tests OK, unchanged |
| `python -m unittest discover -s tests` | 443 tests, 1 failure, 12 skipped, exit 1: the failure is session 77's finding (`eia930_all_interchange` over its ceiling) |
| The trial build (`shoulder_hours.py --out-dir`) | exit 0: 4,540 rows written, 20,464 kept |
| Validator, the trial table | exit 0: PASS, 0 errors, 0 warnings, 25,004 rows |
| `check-shoulder.mjs` against the trial table (the stub serving it) | exit 0: **2,104 of 2,104 checks, 1,001 numbers equal the table's rows**, 9 page variants (three of them California's own data, each with its ten ranked days) |
| `npx tsc --noEmit`, `npm run build` (against the stub, then against the live set) | exit 0 each |
| `check-routes`, both passes, the live-set build | exit 0: 80 of 80 with the cookie; 14 live and 66 in review as a visitor |
| `snapshot-live.mjs`, production against this branch's build | the live pages differ only by sessions 77 and 78's two changes (`/about`, `/network`'s sentence) and by what moves by itself (latest prices, the network's refresh times) |

Against the live set, `/shoulder?grid=caiso-own` says "no data ... holds no month for CAISO, its own data", as it must until the table is loaded; `/shoulder` for Texas renders with "not held" where the new rows will go.

Not run: coverage, the archive, the uploader, the loader, `check-values` (the table was not written to the warehouse).

## Errors and decisions

- **Decision: the session went on without Texas's worst days,** by the chain's rule 8, and built everything that does not need the workbook.
- **Decision: nothing went to the Redivis draft,** though the table is ready as a trial file. It is not a brand-new table, a live-set page reads it, and session 77 found that uploads from unmerged branches break the daily run.
- **Decision: California's own data is a third entity,** `iso:caiso_own`, not more months of `iso:caiso`. The two overlap from June to November 2025 and disagree there, so the page never shows them as one series.
- **Decision: demand in the own series is the sum of CAISO's thirteen sources.** CAISO's demand series is not held. The sum counts imports and counts batteries net, so battery charging is not in it as load.
- **Decision: a year's worst-day hours needed is the mean over all ten days or is not written.** Half of 2026's ten have no published fleet; a mean over the five that do would be a mean of August.
- **Decision: the fleet for an unpublished month is not carried forward.** Session 74 used the newest month for an analysis and named it; in a table row I left it not held.
- **Decision: one unit rule.** Session 75's two rules gave `shoulder_mwh_above_mean` of a month the unit "count". Rows this laptop kept still carry it; a rebuild with the workbooks corrects them.
- **Decision: the "worst day" bullet under "What this cannot see" was replaced,** since the page now sees ten of them; the new bullet says what a ranking by one measure misses.
- **Error, mine:** a test first claimed the second shoulder is never longer than the first. On a made-up day whose evening dips to the mean and rises again it is longer, because the first measure stops at the dip. The test now states what does always hold; on the trial table's months and ranked days the second is never the longer.
- **Error, mine:** the commit message says "20 tests"; there are 15.

## For Samuel

1. **Settle the hour** (finding 2) before anything built on California's EIA hours before the break is shown to an investor: the seller tab's California solar is the live one.
2. **Run the builder where the workbooks are** ("To finish", step 1) to get Texas's worst days, which is the half of the question the investor asked about.
3. **Rule on California's evening:** the second measure still runs to midnight there. A noon-to-noon day would show where it ends.
4. **The answer so far, for the investor:** Texas's batteries (1.65 hours) already cover the top of the evening peak (1.01 hours needed by the second measure) and half of everything above the daily mean (3.17 by the first). California's worst evenings need a little over 5 hours against 3.4 held, and its batteries ran 2.5 hours' worth on them. Nothing measured points to 8 hours; a run of dark days was not measured.
