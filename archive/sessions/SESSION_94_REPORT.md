# Session 94 report: the energy mix, version 2

**Built, on `wip/094-mix-v2`, nothing deployed.** Version 2 of the energy mix is the review page `/mix/v2`, in the battery page's layout: any of the seven grids, any month or year since 2019; generation by fuel by hour as a stack; a second grid beside it; one calendar month across the years, where the duck curve can be watched growing; and the records of an hour with their dates. Behind it are two new derived tables. The page `/mix` is as it was.

## To make it live

```bash
# Nothing below was run. No preview address: GitHub recorded no Vercel deployment for this branch's push.

# 1. THE TWO TABLES into the warehouse's records. They exist only in warehouse/output on the old laptop today.
git fetch origin && git checkout wip/094-mix-v2 && git merge origin/main
python warehouse/lock.py run --task "the energy mix by hour" --minutes 20 -- <the venv's python> warehouse/derived/mix_profile.py --snapshot
python warehouse/validate/erw_validate.py warehouse/output/generation_mix_hourly_profile.csv warehouse/output/generation_mix_records.csv   # exit 0
python warehouse/metadata/build_coverage.py                                 # read its exit code
python warehouse/archive/archive.py --tables "generation_mix_(hourly_profile|records)" write
python warehouse/redivis/upload.py --tables generation_mix_hourly_profile generation_mix_records      # a draft; releasing is your click
#    and in warehouse/supabase/live_set.yaml, under catalogue_hold, while the page is in review:
#      - generation_mix_hourly_profile
#      - generation_mix_records
#    then commit coverage.csv, sources.csv, docs/coverage.md, the live set and site/data/mix/*.json.

# 2. THE PAGE, in review at /mix/v2. A push to a task branch redeploys the site; no live page changes:
python -m unittest tests.test_session94                                     # read its exit code
cd site && node scripts/snapshot-live.mjs take before-094 && cd ..
git push origin wip/094-mix-v2:task/094-mix-v2
cd site && node scripts/snapshot-live.mjs take after-094 && node scripts/snapshot-live.mjs compare before-094 after-094

# 3. AS THE ENERGY MIX PAGE, when you have used it: move site/app/mix/v2/ over site/app/mix/ (the old page's "today so
#    far" strip and its state view are not in version 2: decide whether they stay as a second page), take the line
#    "/mix/v2" out of site/lib/release.ts, and set "/mix" to "live" there only when you open it to visitors.

# 4. THE TABLES ARE BUILT BY HAND, not by the daily run. To keep the newest month current: one run_other line for
#    mix_profile.py --snapshot after the emissions connector in warehouse/run_daily.sh (it reads the workbooks that
#    connector saves; it makes no request).
```

**Read these three first:**

1. **EIA's file holds no hydro for California from October 2019 to mid August 2020, and I found it only because the records looked wrong.** In those ten months hydro is blank in 97 to 100 percent of the hours, and EIA's own total leaves it out too, so the sources still add up. What gives it away is EIA's balance: demand against net generation less interchange is off by 9 to 15 percent of demand in those months against 2 to 4 around them. The new tables do not write those months. **Other tables of the warehouse are built on the same hours and I did not touch them:** California's generation mix, and its carbon intensity of generation, for October 2019 to August 2020 are computed without hydro and so read dirtier than they were. That is worth a session of its own; it is the first item under "For Samuel".
2. **PJM is held at a looser test than the other six, and that is a choice of mine.** An hour is used when its sources add up to EIA's total within 5 percent. PJM itemizes no storage, and in 2,689 of its hours (most at 05:00 and 06:00, 2020 to 2024) its sources and its total part by 5 to 15 percent, above about as often as below, with no source blank. At 5 percent only 36 of PJM's 93 months could be written; at 10 percent, 74; at 15 percent, 91. I set PJM at 15 percent, kept the other six at 5, and the page says so. The shares are of the sum of the sources, so they are not bent by the gap; but if you would rather PJM show four empty years than hours whose total and parts disagree, it is one constant (`LOOSE` in `mix_profile.py`).
3. **Texas's December 2025 is not written, and the 5 percent test is why.** From 6 to 14 December 2025 EIA's "other" for ERCOT repeats the batteries' output (other at 3,281 MW in an hour with storage at 3,172) and the sources stand 5 to 8 percent above the total. A looser test would have written the month with the batteries counted twice.

Energy Research Warehouse (ERW), session 94, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 08:36 to 09:38 UTC, unattended. **Model spend: USD 0.00.** No pull, no request to any publisher, no model call, no force push, no deploy. The data lock was taken three times for the builder (under two minutes each) and is free.

## The two tables

Built by `warehouse/derived/mix_profile.py` from files the warehouse already holds: EIA-930's hourly net generation by energy source (the per-balancing-authority workbooks the emissions connector saves), CAISO's own supply by fuel from the join, and `carbon_intensity_hourly`. Both pass the validator (exit 0). Both are public: EIA-930 is in the public domain, and CAISO's Today's Outlook data is already held as a public table. Method: `docs/methods/generation_mix_hourly.md`.

| Table | Rows | What a row is |
|---|---|---|
| `generation_mix_hourly_profile` | 162,911 | one figure of a grid's month: a source's average MW in one local hour over the month's complete days, a source's MWh or share, the days counted |
| `generation_mix_records` | 306 | one record of a grid, for the whole history or for one local year, dated the hour that holds it |

**Which hours are used.** Net generation held and positive; the sources within 5 percent of it (PJM 15); no main source blank (a main source supplies at least 5 percent of the grid's generation over its history). A day is complete when every hour of the local day is used; a month is written when at least 90 percent of its days are complete. Nothing is filled. Both tables are rebuilt whole each run, so a month that stops passing does not stay from an earlier run (my first rebuild kept 3,367 rows of the months I had just ruled out; the merge keeps old keys, and the builder now removes the file first, as five other derived builders do).

| Grid | Months held of 93 | Hours not used, of about 67,990 | Not written |
|---|---|---|---|
| CAISO | 79 | 7,942 (7,904 with a main source blank) | September 2019 to August 2020, October 2020, December 2025 (the join month) |
| ERCOT | 92 | 97 | December 2025 |
| ISO-NE | 93 | 44 | none |
| MISO | 93 | 24 | none |
| NYISO | 93 | 67 | none |
| PJM | 91 | 833 | January 2020, June 2022 |
| SPP | 88 | 221 | April and June 2019, August 2020, February and May 2026 |

**California's join.** EIA-930 to 2025-12-16T08:00:00Z, CAISO's own supply by fuel from it, never blended; December 2025, the month that holds the join, is not written on either source; demand is EIA's throughout. Each row's `source` says which side it rests on, and the page says it for the period shown.

**The records as built** (the whole history; each also by year):

| Grid | Highest solar share of an hour | Highest wind share | Cleanest hour, kg CO2 per MWh | Dirtiest hour |
|---|---|---|---|---|
| CAISO | 79.80 percent, 29 April 2026 | 50.57, 17 May 2026 | 11.36, 16 May 2026 | 388.25, 20 October 2022 |
| ERCOT | 64.93, 2 May 2026 | 68.74, 10 April 2022 | 84.64, 14 March 2026 | 542.68, 3 March 2019 |
| ISO-NE | 14.49, 26 April 2026 | 20.48, 4 April 2026 | 56.45, 16 May 2026 | 501.17, 25 January 2026 |
| MISO | 26.99, 28 March 2026 | 39.59, 19 March 2025 | 221.94, 28 March 2026 | 672.71, 16 January 2019 |
| NYISO | none: EIA reports no solar for it | 20.52, 16 March 2025 | 66.42, 7 May 2019 | 391.63, 22 May 2024 |
| PJM | 17.55, 3 May 2026 | 12.39, 5 November 2022 | 198.70, 3 September 2020 | 508.53, 1 July 2021 |
| SPP | 6.91, 27 September 2026 | 78.51, 8 May 2021 | 129.54, 26 April 2021 | 766.49, 2 October 2021 |

Dates are local. Three rules keep a faulty hour from being a record, each counted in the run log: a share is of what the hour's sources put out (against net generation, a grid whose batteries charge at midday shows solar above 100 percent); an hour of EIA's is not ranked when EIA's own balance for it is off by more than 20 percent of demand or cannot be checked (California has hours in which only its wind was reported); and an hour is not ranked for carbon intensity when its intensity is less than half of what its own gas generation implies. Before the main-source rule, California's dirtiest hour was an evening of December 2019 with no hydro in it.

## The page, `/mix/v2`

In the battery page's layout: a panel on the left (grid; a second grid beside it; a year or one of its months), a sentence, three headline numbers, then:

- **Generation by fuel, by hour.** The average day of the period as a stack of sources with demand as a line. What is above zero is stacked up from zero; batteries charging are drawn below it, so California's midday charging shows as its own band. With a second grid, the two stacks stand side by side, each on its own scale, with a table of both grids' shares and MWh beneath.
- **One calendar month, year after year.** Net load (demand less wind and solar) by hour, a line per year, and solar by hour; a table of each year's solar peak, net load's midday low, its evening high and the ramp between them. For California's April: a midday low of 10,781 MW and a ramp of 12,209 MW in 2019; 4,636 MW and 16,749 MW in 2026.
- **The records of an hour**, for the whole history and for the year of the period shown, each with its local date and hour, and for California the side it rests on.
- **A year** is its months weighted by their complete days, computed once in the builder and written into the site's copy; it is given only when at most one of its months is missing (so California has no 2019 or 2020, and SPP no 2019 or 2026).

**Decision: the page reads the site's own copy** (`site/data/mix/<grid>.json`, 1.4 MB for the seven), not the database, as the other review tools of tonight do: the tables are not in the live set, and the freeze forbids loading. A test holds every figure of the copy equal to the table.

**Decision: a month or a year, not any range of dates.** "Any period" is every month and every year since 2019. An arbitrary range would need the hourly table on the page; the monthly average days are what the table holds.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session94.py` | 19 tests pass. The held-hour tests on hours made for the test (a blank main source, a blank small source, sources 8 percent off, PJM's allowance); a month with too few complete days is not written; the day the clocks change; the join month; a share is of what the sources put out and a partial report is not a record. The tables as built: what each grid holds and does not, the shares, California's side. The site's copy equal to the tables, figure for figure, and holding nothing more; a year equal to its months weighted by days. In Node: the page's choices, its stack, net load, the months across years. The page is in review, `/mix` unchanged against main |
| `site/scripts/check-mix-v2.mjs`, the built site | 56 checks pass: on six views (a month, a year, two grids, a grid with no solar) every number the page marks equals the copy (56 to 90 numbers a view); a band per source held and a demand line; two stacks side by side when a second grid is named; a line per year; the records named and dated; the join stated for California and not elsewhere; a period the second grid lacks says so and draws nothing; an address it does not understand opens the default; a visitor gets the in-review page with no number on it |
| Site: types, build, route check | exit 0 each. The first build failed on the home page (a Supabase read cancelled at its timeout; `required()` stops a render with a failed read from being cached, as session 90 meant); the second passed with no statement cancelled. Route check: 96 of 96 pages, and 16 live with 80 in review as a visitor |
| `check-values.mjs` | exit 0: 7,485 of 7,485 values match |
| The validator on both tables | exit 0 |
| The whole suite, here | 677 tests; one failure, old and known (`test_session49`). A second, mine, was fixed: I had written the join's date into the builder's text, and session 78's test holds it to one constant |
| A screenshot of California beside Texas | looked at: the two stacks, the tables, the years' lines and the records as described |

After the last build I changed two sentences of the page to take "December 2025" from the join's constant instead of writing it out. The words on the page are the same; the type check passes; the page was not rebuilt for it.

## Errors and decisions

- **Error, mine: the first tables held California's months without hydro.** I had written "a source EIA left blank counts as zero" and built on it. The balance rule for records showed hours that could not be records, and following those led to the blank months. The rule is now that a main source is never zero.
- **Error, mine: a rebuild that kept stale rows** (above).
- **Decision: PJM at 15 percent** (above, "Read first", 2).
- **Decision: a record of zero is not written.** New York has no solar record; the page says in words that EIA reports none.
- **Decision: storage is shown as EIA itemizes it.** It is a source only from when EIA lists it (Texas and New England from late 2024, MISO from 2025, SPP from 2026); before, it is inside "other" or absent, and nothing is moved between sources.

## For Samuel

1. **California without hydro, October 2019 to August 2020, in the tables that were there before tonight.** `eia930_all_generation`, the carbon intensity tables and anything derived from them carry those months as EIA published them. No live page shows California's 2019 or 2020 mix by month, but the carbon history does reach back. A session to measure it and decide (leave out, or mark) would settle it; nothing was changed tonight.
2. **PJM's tolerance** (above).
3. **Whether version 2 replaces `/mix` or stands beside it.** The old page has two things version 2 does not: today so far, and the mix by state since 2001.
4. **Not in any cloud:** the two tables are only in `warehouse/output` on this machine until step 1 of "To make it live" is run. The builder and the site's copy are in git, so they can be rebuilt from the workbooks.
