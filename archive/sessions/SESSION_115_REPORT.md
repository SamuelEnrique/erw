# Session 115 report: what Texas's storage resources were awarded day-ahead

**Done, with one thing short of the prompt: no duration class (read first, 4).** The Energy Storage Resource file of ERCOT's 60-Day DAM Disclosure is in the warehouse for every day it exists: 243 operating days, 6 December 2025 to 5 August 2026, 1,833,357 rows, none missing. From it, `ercot_storage_dam_awards_monthly` holds the fleet's day-ahead awards by month, and the review page `/cost-of-power/battery/awards` shows them. One deploy (run 37261258743, merged as `5a780a8`), with the snapshot of the live pages before and after: 40 differences, every one the home page's latest prices or `/network`'s hourly refresh. The 13 battery pages show none.

## Read these first

1. **Over the seven whole months of 2026 held (January to July), the fleet's day-ahead awards come to USD 6.53 per kW: 3.75 energy net of charging, 2.78 ancillary services.** The battery page's model, for a 2-hour battery on the day-ahead schedule over the same months, gives USD 30.14 per kW (14.48 and 15.66). The awards are 22 percent of the model's figure.
2. **That is not what the batteries earned, and the page says so before it shows a number.** These are day-ahead awards at day-ahead prices: no real-time settlement, no deployment energy, no contracts. A floor on market revenue. A storage resource held a day-ahead energy award in 7.0 percent of its hours (127,958 of 1,833,357).
3. **The gap is mostly volume, not price, as far as the rows show.** Per MW of the fleet, 0.39 MWh a day was sold day-ahead, against the 1.81 MWh a day the model's battery discharges: about a fifth of the model's cycle. On each MWh it did sell, the fleet netted more than the model does (USD 44.50 against 37.67). In ancillary services the model takes 61 percent of its money from Regulation; the fleet's Regulation awards came to 4 percent of what the model assumes per kW. Detail under "How far the awards sit from the model".
4. **No duration class was written.** The prompt asked for it "where the resource's energy and power are both stated". ERCOT's file states power (HSL, LSL) and never energy, for any resource. Energy is in EIA-860M, and matching ERCOT's resource names to EIA's plants is a list a person has to check; I did not guess one. The table holds the fleet only.
5. **The pull stayed under both ceilings:** 1,833,357 rows of 9,000,000, and 1.95 GB of 3 GB. **I made one mistake in it** (decision 1): I started the pull from 5 December 2025 believing the file began there, then stopped it for a minute on a false alarm. Nothing was requested twice. Three of the zips downloaded hold no ESR file (22 MB of the 1.95 GB): two were probes to find the file's first day, and one was the mistake.
6. **The file's first day is 6 December 2025, not the 5th.** The zip of 5 December, the day of ERCOT's market change, has 13 files and no ESR file; from the 6th there are 17. This settles the "if" of session 108's note.
7. **ERCOT's terms do not forbid republishing, so both tables are public.** Quoted under "License".
8. **The row-level table is kept out of the site's database,** as asked. It is validated, in coverage, archived (1,833,357 rows) and in the Redivis draft (1,833,357 rows counted there). The monthly table is in all of those and in the site's database, held under review: no count a visitor sees includes it.

## The pull against its ceilings

`warehouse/connectors/ercot_dam_esr.py`. ERCOT's servers were asked between 03:13 and 03:29 UTC on 5 October 2026, one zip at a time, two seconds between requests.

| | Used | Ceiling |
|---|---|---|
| Rows (a resource and hour, as in ERCOT's file) | 1,833,357 | 9,000,000 |
| Downloaded | 1,949,656,746 bytes (1.95 GB), 215 zips | 3,000,000,000 bytes (3 GB) |
| Cost | USD 0 | USD 0 |

- **215 zips requested:** the 212 operating days from 6 December 2025 to 5 August 2026 that were not on the machine, and three that turned out to hold no ESR file (5 December 2025, 4 December 2025, and 24 January 2024, the oldest on ERCOT's list).
- **31 zips not requested:** July 2026, saved by session 108 (339 MB), read from the disk. No zip was asked for twice: each is in `warehouse/raw/ercot_60d_dam/zips/manifest.csv` with its bytes, SHA-256 and time.
- **Other requests:** ERCOT's file list five times (an index, 425 kB), its terms page once, and one request to learn whether part of a zip can be had without the whole (it cannot: ERCOT answered with the whole file and I closed the connection without reading it). A file cannot be had without its zip, so the ESR file's 507 MB cost 1.95 GB.
- **A month at a time:** each month was read, checked and written before the next began; the table was then written from the months, a line at a time.
- **Before any request** the connector adds up what it would download and stops if that passes the ceiling. The plan read 1,816,750,044 bytes to come on top of 132,906,702 already requested.
- **The raw zips are kept** in `warehouse/raw/ercot_60d_dam/zips/`, a folder the 14-day pruning leaves alone: 246 zips, 2.2 GB. July's 31 were copied there from session 108's run folder, which the pruning would have removed.

## What is held

| | |
|---|---|
| First and last operating day | 6 December 2025 and 5 August 2026 (the newest ERCOT has posted: 60 days behind) |
| Days | 243 of 243; none missing, none failed a check |
| Resources | 336 ever; 301 in December 2025, 332 in July 2026 |
| Fleet MW (each resource's highest limit in the month) | 16,392 in December 2025; 21,365 in July 2026 |
| Day-ahead awards, all 243 days | USD 133.59 million: 76.97 energy net of charging, 56.62 ancillary services |

July 2026 matches session 108's sample to the dollar: 244,968 rows, 332 resources, 21,365.1 MW, USD 14,560,994.

**Implausible, kept as printed:** 48 rows have a negative High Sustained Limit (`BUDA_ESR1` at -9.9 MW for the 24 hours of 4 June 2026, status ONTEST, and `ALAMO_ST_ESR1` at -0.3 for 24 hours). A resource's MW is its highest limit of the month, so neither moves a sum.

## The table by year, and by month

USD per kW of the fleet's MW. A year is the sum of its months, each over its own MW. **No partial month is scaled.**

| Year | Days held | Energy | Ancillary services | Total | Months held whole | Awards over them | The model's, same months | Awards as a share |
|---|---|---|---|---|---|---|---|---|
| 2025 | 26 (6 to 31 December) | 0.20 | 0.28 | 0.48 | none | | not set beside it | |
| 2026 | 217 (January to July, and 1 to 5 August) | 3.84 | 2.81 | 6.65 | January to July | 6.53 (3.75 and 2.78) | 30.14 (14.48 and 15.66) | 22% |

The model's column is `battery_stack_monthly`: a 2-hour battery, the day-ahead schedule, at the hub average. For scale only, its whole December 2025 is 4.33 and its whole August 2026 is 3.57; the awards hold 26 and 5 days of those months, so I do not set them side by side.

| Month | Days | Resources (with any award) | MW | Energy | Ancillary | Total | Model: energy | Model: ancillary | Model: total | Awards as a share |
|---|---|---|---|---|---|---|---|---|---|---|
| Dec 2025 | 26 of 31 | 301 (196) | 16,392 | 0.20 | 0.28 | 0.48 | 1.28 | 3.05 | 4.33 | partial |
| Jan 2026 | 31 | 306 (216) | 17,180 | 1.00 | 1.36 | 2.36 | 4.33 | 7.00 | 11.33 | 21% |
| Feb 2026 | 28 | 313 (231) | 17,722 | 0.28 | 0.16 | 0.45 | 1.14 | 1.06 | 2.20 | 20% |
| Mar 2026 | 31 | 316 (231) | 18,970 | 0.53 | 0.18 | 0.70 | 1.89 | 0.91 | 2.80 | 25% |
| Apr 2026 | 30 | 321 (228) | 19,955 | 0.72 | 0.42 | 1.13 | 2.69 | 2.43 | 5.12 | 22% |
| May 2026 | 31 | 321 (230) | 19,709 | 0.40 | 0.33 | 0.72 | 1.45 | 2.08 | 3.53 | 21% |
| Jun 2026 | 30 | 325 (241) | 20,557 | 0.30 | 0.18 | 0.48 | 0.97 | 1.32 | 2.29 | 21% |
| Jul 2026 | 31 | 332 (252) | 21,365 | 0.53 | 0.15 | 0.68 | 2.02 | 0.86 | 2.87 | 24% |
| Aug 2026 | 5 of 31 | 332 (246) | 21,207 | 0.09 | 0.03 | 0.12 | 2.45 | 1.12 | 3.57 | partial |

The share is steady, 20 to 25 percent in every whole month, through a January whose total is five times February's.

## How far the awards sit from the model, and what explains it

Over January to July 2026 the awards are USD 23.61 per kW below the model: 10.73 in energy, 12.88 in ancillary services. What the rows show (`runs/session115/analysis.py`, from the two tables):

**Energy: 26 percent of the model's (3.75 against 14.48).**

| | The fleet, day-ahead | The model's 2-hour battery |
|---|---|---|
| Energy sold, MWh per MW per day | 0.39 | 1.81 discharged |
| Net per MWh sold | USD 44.50 | USD 37.67 |
| Hours with an energy award | 7.0% of resource-hours | most days, a full cycle |

- The fleet sold about a fifth of the model's volume and netted more on each MWh. The gap is how much was put through the day-ahead market, not the price it got there.
- The fleet bought day-ahead only 71 percent of the energy it sold day-ahead (1.15 against 1.61 million MWh). A battery has to buy more than it sells, so part of the charging behind these sales was not bought day-ahead. That charging cost is not in this table, which is one more reason the figure is not earnings.

**Ancillary services: 18 percent of the model's (2.78 against 15.66).**

| USD per kW, January to July 2026 | The fleet's awards | The model | Awards as a share |
|---|---|---|---|
| Regulation Up | 0.25 | 4.27 | 6% |
| Regulation Down | 0.13 | 5.36 | 2% |
| Responsive Reserve | 0.85 | 3.39 | 25% |
| ECRS | 0.54 | 1.10 | 49% |
| Non-Spin | 1.00 | 1.54 | 65% |
| All five | 2.78 | 15.66 | 18% |

- The model takes 61 percent of its ancillary money from Regulation (9.63 of 15.66). It is one MW taking the clearing price on all of its power. The fleet's Regulation awards came to 0.38, 4 percent of that. Regulation is 72 percent of the ancillary gap (9.25 of 12.88).
- In all, a day-ahead ancillary award was held on 20 to 26 percent of the fleet's limit-hours in each whole month (award MW over HSL, hour by hour). The model's battery commits nearly all of its power every hour.

**Capacity that took nothing day-ahead is in the denominator.**

- Each whole month, resources with no day-ahead award of any kind were 23 to 33 percent of the fleet's MW (80 to 93 resources).
- Resources never in status ON during the month were 7 to 18 percent of the MW. Status was OUT in 10 to 15 percent of resource-hours and ONTEST in 5 to 7 percent.

**What the rows do not show:**

- Whether unawarded capacity offered and lost, or never offered. The offer curve is in ERCOT's file and in the saved zips; the table leaves it out. Reading it needs no new pull.
- Anything in real time: the energy sold or bought there, reserves awarded there, and deployment.
- Differences of place and duration: the model is at the hub average for two hours; the fleet is at 293 settlement points and of every duration.

So the 22 percent is not the model's error. It is the share of a perfect day-ahead schedule that the fleet actually took day-ahead.

## What the real-time side would take

1. **The 60-Day SCED Disclosure Reports** (type 13052), the file `60d_ESR_Data_in_SCED`: a row per resource and SCED run, with base point, telemetered output, state of charge and real-time ancillary awards. Session 108 read about 12 MB a day from ERCOT's list, so about 2.9 GB for these 243 days, and many times the rows (a run every five minutes or so). Pull one month first to learn its shape and size.
2. **Real-time settlement point prices at each resource's node** (293 of them). The warehouse holds hubs only. Not sized.
3. **ERCOT's protocols on settlement under Real-Time Co-optimization:** how real-time energy settles against the day-ahead award, and how real-time ancillary awards settle against day-ahead ones. No session has read them. They have to be read before the arithmetic is written.
4. **Still undisclosed after all that:** contracts and tolls, the charges of the private settlement statement, station power. It would be market revenue at posted prices, not cash.

## The tables

| | `ercot_dam_esr_awards` | `ercot_storage_dam_awards_monthly` |
|---|---|---|
| What | a row per resource and hour, as ERCOT prints it | the fleet by month, 28 variables |
| Rows | 1,833,357 | 252 (9 months) |
| Tier, license | source, public | derived, public |
| Validator | exit 0, 0 warnings | exit 0, 0 warnings |
| Coverage, source registry | yes (two rows added to main's file; no other row moved) | yes |
| Archive | 1,833,357 rows, to `warehouse/archive` and the bucket | 252 rows, to `warehouse/archive` and the bucket |
| Redivis draft | 1,833,357 rows counted there; nothing released | 252 rows counted there; nothing released |
| Site's database | **not loaded** (`catalogue_hold`) | 252 rows; the catalogue row says "review"; no count a visitor sees includes it |

- **Shape of the row-level table (the data standard's Decision 40):** the row's value is the resource's limit (HSL), which every row has; the awards and prices are `x_` columns, because a blank award is no award and a series value may not be empty. One value a row would have been up to about 27 million rows.
- **Per kW is stored as USD/MW,** as `battery_stack_monthly` stores it, so the two tables join; the page divides by 1,000.
- **`days_missing`** counts days without rows between the table's first and last day. The days of December before the file began and of August not yet posted are not missing; they show as `days_held` below `days_in_month`.
- **Neither table is in the daily run.** A new day means a new request to ERCOT, and the approval was for this pull. To add a day: `ercot_dam_esr.py --pull --from 2025-12-06`, then `--write`, then the builder (it asks only for zips the machine lacks).

### License

ERCOT's terms (`https://www.ercot.com/help/terms`), quoted: "The publicly available contents of this website may be used, reproduced, and redistributed, provided that the contents are not modified and that you maintain all copyright and other notices contained in the contents, including this Agreement. Notwithstanding the foregoing, raw data provided in public portions of this website may be used, reproduced, and redistributed in compilations, charts, and analyses without maintaining such notices."

Nothing there forbids republishing, so neither table is marked internal. I read the page again at the end of this session (5 October 2026, one request): the passage is there word for word. The same page says, at its point 6: "Use of this website in a manner that negatively affects the performance of this website or other ERCOT systems is prohibited." The pull was one zip at a time with two seconds between requests, 215 zips in fifteen minutes. The page has no clause on automated access. The files name each resource and its scheduling entity; that is ERCOT's own disclosure under PUCT rule 25.506.

## The page

`/cost-of-power/battery/awards`, in review (its own line in `site/lib/release.ts`; without it the page would have taken the live battery page's status). In the battery page's layout. In order:

1. **What this is not, first:** "These are day-ahead awards only: no real-time settlement, no deployment energy, no contracts. So this is a floor on market revenue and not what any battery earned."
2. One summary sentence, from the newest whole month.
3. The awards per kW by month, energy and ancillary services stacked; a partial month is hatched and labeled with its days. Then the table by month.
4. By year, with the model's figure beside the awards over the whole months only, in a column headed "The model's".
5. "Why the two differ": the share of hours with an energy award, and that the distance is not the model's error.

On production after the deploy (`site/scripts/check-review-pages.mjs`, 04:02 UTC): in the internal view the page answers 200 with 177 figures in its text and says nowhere that a table could not be read; a visitor gets the in-review page. The method page, `/data/methods/ercot_storage_dam_awards`, the same.

The live battery page is not changed: its three files are as on main, nothing live links to the new page, and the page is not in the menu or on About (both would change a live page's HTML).

## Deploy and snapshots

One push, to `task/115-storage-awards` at 03:54 UTC. Run 37261258743 passed (tests, site build, route check, the no-request check) at 03:59 and merged as `5a780a8` at 04:00; production served the new page by 04:02. Three snapshots of the 25 live pages: `before-115` (03:22 UTC, before any table was written or loaded), `after-115-load` (03:47, after the load, before the push), `after-115` (04:02, after the deploy).

`before-115` against `after-115`: **40 differences.**

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 34 | the latest real-time prices of five hubs (ERCOT, CAISO, NYISO, SPP, ISO-NE): 10 numbers (5 keys gone, 5 new) and 24 lines of text: the prices, their interval lines, and four lines that count down with the clock ("6.1 days in the ERW table" to "6.0", "6.2" to "6.1", "5.1" to "5.0") | yes: the 15-minute refresh. Not this session's |
| `/network` | 6 | "refreshed 02:05 UTC" became "03:05 UTC"; demand's newest hour 00:00 became 01:00 (two lines); "Built 02:05 UTC, onto the daily build of 01:05" became "03:05, onto 02:05" | yes: the hourly refresh. Not this session's |
| `/cost-of-power/battery` and its 12 variants (both grids, 2, 4 and 8 hours, both strategies) | 0 | | |
| `/about`, `/storage`, the three seller pages, `/terms`, the four methods pages | 0 | | |

`before-115` against `after-115-load` (the load alone): 30 differences, all on `/`, all latest prices. `after-115-load` against `after-115` (the deploy alone): 36, 30 on `/` and the 6 of `/network`. **"Rows", "Last refresh", the count of tables, and the count of sources on `/terms` did not move:** the monthly table is under `review_hold`, the row-level one under `catalogue_hold`, and both new sources under `sources_hold`. No difference was unexpected.

## Tests and checks

- `tests/test_session115.py`, 17 tests, on a saved real sample (the rows of 6 and 8 December 2025, every resource, 12,672 rows; and the first 400 rows of ERCOT's own file for the 6th):
  - **the monthly sums equal the sum of the rows,** computed again in exact decimals without the builder's code, for energy sold and bought and each of the five services;
  - **a resource with no award contributes nothing and is still counted in the MW:** with it taken out, no sum moves, the MW falls by its highest limit and the per kW rises;
  - **nothing is filled for a missing day:** the 7th is left out of the sample; the month reads 2 days held, 1 missing, and its sums are the two days' sums;
  - an award without its price stops the build; a blank award stays blank; a file of another day, a zip without the file, and a repeated hour are each a missing day; the pull stops before either ceiling and never asks for a zip twice (against a stand-in for ERCOT's server; no request);
  - the row-level table is under no live-set rule; the hold lists; the method's words.
- `tests/test_session115_page.py`, 13 tests: the page is in review; "what this is not" comes before any number; "earned" appears only in "not what any battery earned"; the model's column is labeled as the model's; the year sums and the whole-month rule; the live battery page's files are as on main.
- Every session's tests on this machine before the push: 952 ran, 17 skipped, **one failed**: session 108's test, which pinned that no table named like `esr_awards` is in coverage. That was true of its sample and is not true of the table approved today; I changed the test to tell the two apart (decision 9), and its file then passed, 5 of 5. I did not run all 952 again on this machine after that change; GitHub's run 37261258743 ran them all in a clean checkout and passed.
- In a clean checkout without the tables, this session's tests with those of sessions 102 and 114: 57 ran, none failed, 4 skipped.
- This machine's build of the site: exit 0. The route check: exit 1 the first time (`/shoulder`, a page in review that is not this session's, showed one "no data" block that production did not), exit 0 the second time with nothing changed between: 113 of 113 pages, then 16 live pages and 97 in review as a visitor, 0 failed. A read that failed once.
- The validator on the two tables: exit 0, 0 warnings.

## Errors and decisions

1. **I began the pull a day early and then stopped it needlessly.** The zips shrink on 5 December 2025 and I took that for the file's first day without opening one. Fifteen zips in, I opened the first, found no ESR file, and stopped the run, thinking the file began later. The second zip had it. I restarted from the 6th; nothing was requested twice. Cost: the zip of 5 December (7 MB) and about a minute.
2. **Two probes before the pull,** 4 December 2025 and 24 January 2024: neither has an ESR file. With the 5th, three zips say the file begins on the 6th. I did not open the 678 days between; the claim rests on those three and on the market change of 5 December.
3. **The prompt arrived as a paste with no word outside it,** and it named a deploy inside the freeze of 3 to 6 October. I asked once before starting. Samuel answered "yes, run session 115". The prompt is kept verbatim in `archive/sessions/SESSION_115_PROMPT.md`.
4. **No duration class** (read first, 4).
5. **Coverage was patched, not rebuilt,** as sessions 113 and 114 did: main's file with this session's two rows added.
6. **The page was written by a second copy of me** while I built the tables, as in session 114. I read its code and changed one sentence that said more than the data shows ("what it did in the other hours was decided in real time").
7. **`run_status.csv`: two rows added by hand,** this session's two runs.
8. **No model call. Model spend USD 0.00.** No other pull. MISO was not requested. No force push.
9. **I changed a test of session 108.** It asserted that no table whose name holds `esr_awards` is in coverage. It now asserts that the sample (`ercot_60d_dam_esr_awards_<month>`) is not, and says why. Without the change the branch could not merge.
10. **Per kW is stored as USD/MW** (the tables section). The prompt said "each per kW"; the page shows per kW.
11. **`days_missing` is not `days_in_month` less `days_held`** (the tables section): December's first five days and August's last 26 are not missing days.
12. **The model's figure stands beside the awards only over whole months,** so 2025 has none (For Samuel, 1).
13. **A first full run of the tests failed a test of session 102** because it ran before the builder had written the new source into the registry. It passed afterwards with nothing changed in it.
14. **I stopped the local site server by its process** (a `node` process on port 3049 that this session started): the ordinary stop left it running.
15. **`wip/114-ask-history`:** deleted on the remote. It had 0 commits not on main, checked twice (its report reached main with this deploy). The task branch was deleted by the workflow when it merged.

## To finish

Nothing is owed for this session's tables or page. This report is on `wip/115-storage-awards`; it reaches main with the next deploy.

Still owed from session 114, and not touched here (this session spent nothing on a model): the cost ledger's rows of session 114, by the commands in that report.

For the record, the commands that ran, each with its exit code read:

```bash
PY="<the repository>/.venv/Scripts/python.exe"
python warehouse/connectors/ercot_dam_esr.py --pull --days 2025-12-04,2024-01-24                                      # exit 0 (the two probes)
python warehouse/connectors/ercot_dam_esr.py --pull --from 2025-12-06                                                 # exit 0 (no lock: it writes raw files only)
python warehouse/lock.py run --task "ercot_dam_esr_awards" --minutes 15 --wait 15 -- "$PY" warehouse/connectors/ercot_dam_esr.py --write          # exit 0
python warehouse/lock.py run --task "ercot_storage_dam_awards_monthly" --minutes 15 --wait 15 -- "$PY" warehouse/derived/ercot_storage_dam_awards.py   # exit 0
python warehouse/validate/erw_validate.py warehouse/output/ercot_storage_dam_awards_monthly.csv                       # exit 0
python warehouse/validate/erw_validate.py warehouse/output/ercot_dam_esr_awards.csv                                   # exit 0
python warehouse/metadata/build_coverage.py                                                                           # exit 0, then runs/session115/patch_coverage.py
python warehouse/lock.py run --task "archive" -- "$PY" warehouse/archive/archive.py --tables "^ercot_storage_dam_awards_monthly$" write          # exit 0
python warehouse/lock.py run --task "Redivis draft" -- "$PY" warehouse/redivis/upload.py --tables ercot_storage_dam_awards_monthly               # exit 0
python warehouse/lock.py run --task "live set" -- "$PY" warehouse/supabase/load.py --only '^ercot_storage_dam_awards_monthly$'                   # exit 0 (955.1 MB before, 955.2 after)
python warehouse/lock.py run --task "archive" -- "$PY" warehouse/archive/archive.py --tables "^ercot_dam_esr_awards$" write                      # exit 0
python warehouse/lock.py run --task "Redivis draft" -- "$PY" warehouse/redivis/upload.py --tables ercot_dam_esr_awards                           # exit 0
```

The data lock was taken for each write step and released after it; it is free now.

## For Samuel

1. **Whether the page's comparison is the one you want.** I set the model beside the awards only over whole months, so 2025 has no model figure. If you would rather see December's 26 days against a 26-day model figure, the model's table is monthly and would need a daily one.
2. **Duration classes need a checked match** of ERCOT's 336 resource names to EIA-860M's plants. With it, the same table splits by duration and the per kW could be over nameplate.
3. **The offer curves are already on the disk** (in the 246 zips). They would say how much of the unawarded capacity was offered day-ahead and at what price: the cheapest next step, and no pull.
4. **The real-time side** is the three things above, in that order of cost: one month of the SCED file, node prices, the protocols.
5. **Whether to keep this current.** ERCOT posts a day every day. A daily request of one 11 MB zip would keep the table 60 days behind; it needs your approval as a standing pull.

Energy Research Warehouse (ERW), session 115, on the old laptop (`samueloldlaptop`, data role), 2026-10-05 from about 03:05 UTC to about 04:10 UTC, unattended.
