# Session 97 report: the demand growth explorer

**Built, on `wip/097-demand`, nothing deployed.** A new tool, the review page `/demand`, in the battery page's layout: annual and peak demand and their growth since 2019; where the growth concentrates by month and by hour of the day; a ranking; a summary sentence; weather not removed, said above everything else; and California checked across the break of December 2025. Behind it is one new derived table.

## To make it live

```bash
# Nothing below was run. No preview address: GitHub recorded no Vercel deployment for this branch's push.

# 1. THE TABLE into the warehouse's records. It exists only in warehouse/output on the old laptop today.
git fetch origin && git checkout wip/097-demand && git merge origin/main
python warehouse/lock.py run --task "demand growth" --minutes 15 -- <the venv's python> warehouse/derived/demand_growth.py --snapshot
python warehouse/validate/erw_validate.py warehouse/output/eia930_demand_growth.csv        # exit 0
python warehouse/metadata/build_coverage.py                                 # read its exit code
python warehouse/archive/archive.py --tables "eia930_demand_growth" write
python warehouse/redivis/upload.py --tables eia930_demand_growth            # a draft; releasing is your click
#    and in warehouse/supabase/live_set.yaml, under catalogue_hold, while the page is in review:
#      - eia930_demand_growth
#    then commit coverage.csv, sources.csv, docs/coverage.md, the live set and site/data/demand_growth.json.

# 2. THE PAGE, in review at /demand. A push to a task branch redeploys the site; no live page changes:
python -m unittest tests.test_session97                                     # read its exit code
cd site && node scripts/snapshot-live.mjs take before-097 && cd ..
git push origin wip/097-demand:task/097-demand
cd site && node scripts/snapshot-live.mjs take after-097 && node scripts/snapshot-live.mjs compare before-097 after-097

# 3. OPEN TO VISITORS, when you have used it: in site/lib/release.ts set "/demand" (and "/data/methods/demand_growth")
#    to "live", and add the page to the menu in site/lib/pages.ts.

# 4. TO KEEP IT CURRENT: the year to date moves with the last whole month. One run_other line for
#    demand_growth.py --snapshot after the emissions connector in warehouse/run_daily.sh, early in each month
#    (it reads the workbooks that connector saves; it makes no request).
```

**Read these four first:**

1. **"The larger balancing authorities" are not on the page, because the warehouse does not hold them.** You asked for the seven ISOs and the larger balancing authorities. The hourly demand since 2019 is on this machine for the seven ISO balancing authorities and the Lower 48 only (the workbooks the emissions connector saves). Tennessee Valley, Southern, Bonneville, Duke, Florida Power and Light and the rest would be a pull, and tonight's two approved pulls are the curtailment and the reserve quantities. The page says they are not held and that they can be added. The pull: EIA's per-authority workbooks, one file each, public domain, USD 0; about 68,000 hours an authority. The builder takes a new authority as one line.
2. **EIA's file holds faulty hours, and one of them would have been a year's peak.** PJM's file has 224,345 MW at 18:00 on 13 July 2020 between hours near 140,000, and 155,276 MW on the afternoon of 12 December 2019, which would have been 2019's peak. So an hour is used only when it is above zero and within 25 percent of the median of the four hours around it. That leaves out 7 hours of PJM, 38 of California (a run of hours near 13,000 MW in early 2019, and the good hours caught between them), 12 hours of zero in New York, 2 of SPP. The steepest real ramps of these grids move about a tenth in an hour, so no real hour is lost to it.
3. **The Lower 48 has an average and no peak.** Its demand is EIA's sum over every balancing authority, faulty hours included: PJM's bad hour is inside the Lower 48's 776,575 MW of the same hour, which stands only 12 percent above its neighbours and passes the screen. An average over 8,760 hours does not move for it; a peak would be that hour. The page says why there is none.
4. **California's demand does not step at the break.** EIA's generation series for California changed on 16 December 2025; demand is a different series. The check: the mean of the 28 days before that date and of the 28 days from it, in 2025 and on the same dates of each earlier year. 2025's ratio is 0.9770; the six earlier years run from 0.9699 to 1.0247. Month on the year before, California was 1.5 percent up in December 2025 and 2.2 percent up in January 2026. The table is on California's page.

Energy Research Warehouse (ERW), session 97, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 10:09 to 10:36 UTC, unattended. **Model spend: USD 0.00.** No pull, no request to any publisher, no model call, no force push, no deploy. The data lock was taken twice (about a minute each) and is free.

## The table

`eia930_demand_growth`: 24,108 rows, eight areas. It passes the validator (exit 0). Built by `warehouse/derived/demand_growth.py`; method in `docs/methods/demand_growth.md`. Source: EIA Form EIA-930, hourly demand, public domain; no new source.

- **Whole years 2019 to 2025:** the mean of the used hours, the highest used hour and when, their change since 2019 and on the year before. A year is written when at least 95 percent of its hours are used.
- **The year to date:** the same over January to September of every year, so that 2026 is compared with the same nine months of 2019 and not with a whole year.
- **By month, by hour of the day, and by month and hour** (288 cells a year), and on 2025's row the change of each from 2019.

What it says (weather not removed):

| Grid | Average demand, 2019 | 2025 | Change, percent | Peak, 2019 | 2025 | Change, percent | January to September 2026 against 2019, percent |
|---|---|---|---|---|---|---|---|
| ERCOT | 43,798 MW | 55,717 | +27.22 | 74,533 MW | 83,597 | +12.16 | +33.10 |
| SPP | 30,764 | 34,191 | +11.14 | 50,511 | 54,411 | +7.72 | +16.08 |
| PJM | 91,354 | 96,257 | +5.37 | 152,315 | 160,560 | +5.41 | +8.25 |
| CAISO | 24,476 | 25,565 | +4.45 | 43,849 | 43,860 | +0.03 | +10.18 |
| MISO | 74,147 | 75,780 | +2.20 | 116,600 | 120,343 | +3.21 | +4.80 |
| ISO-NE | 13,503 | 13,160 | -2.54 | 23,973 | 25,898 | +8.03 | -0.87 |
| NYISO | 17,789 | 17,304 | -2.73 | 30,397 | 31,857 | +4.80 | -3.37 |
| Lower 48 | 458,599 | 490,819 | +7.03 | not given | not given | not given | +10.25 |

Where it concentrates, for ERCOT: every one of the 288 cells grew; the most in January at 02:00 (+42.55 percent, 15,250 MW) and the least in September at 14:00 (+14.29 percent). Growth that is larger at night and in the cool months than on summer afternoons is the shape of a load that runs around the clock, and of a 2025 summer milder than 2019's; the page shows the cells and does not say which.

Texas's 2025 holds 8,736 of 8,760 hours: EIA's file is blank for parts of 5 to 14 December 2025.

## The page, `/demand`

"Weather is not removed" sits in a bordered block above the tool. Then the panel (eight areas; rank by average, peak or the year so far), the summary sentence, three headline numbers, a chart of each year's average with the peak as a mark above it, a table by year with each peak's local date and hour and the hours used, the heat map of month by hour with the largest and smallest cell named, the change by month and by hour as bars, and the ranking, whose headings sort it. For California, the check across December 2025 with its seven rows. Two folds: how it is computed (with the hours the screen left out for the area shown), and what is not here (a weather adjustment; the larger balancing authorities; who is using the power; demand behind the meter; the instant peak; a forecast).

**Decision: the page reads the site's own copy** (`site/data/demand_growth.json`, 330 kB), as the other review tools of tonight do.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session97.py` | 12 tests pass. The screen on hours made for the test: a spike, a zero and a blank not used, a real ramp kept whole; a faulty hour never a peak. The years: growth against 2019 and on the year before, the year to date over the same months of every year, the partial year with no annual figure, a year with too few hours not written, the 288 cells and their change, the Lower 48 with no peak, the break check on the same dates of each year. The table as built: SPP's 2024 computed again from the workbook by hand; PJM's 2020 peak under 160,000 and its 2019 peak in July; no annual row for 2026. The site's copy equal to the table, row for row, and 2025's break ratio inside the earlier years' range. In Node: the choices, the ranking, the cells |
| `site/scripts/check-demand.mjs`, the built site | 83 checks pass: for each of the eight areas, and two more rankings, every number the page marks equals the copy (86 to 100 a view); a bar per year, a cell per month and hour held, the change by month and by hour; the ranking in the order asked for with the Lower 48 last where it has no figure; "weather is not removed" above the tool; each peak dated in local time; the break check on California's page only, with its rows; an address it does not understand opens the default; a visitor gets the in-review page with no number on it |
| Site: types, build (twice), route check | exit 0 each; no statement cancelled. Route check: 107 of 107 pages, and 16 live with 91 in review as a visitor |
| `check-values.mjs` | exit 0: 7,494 of 7,494 values match |
| The validator on the table | exit 0 |
| Two screenshots | looked at. The base year's row said "not held" for its growth since 2019; it now says "the base year" (rebuilt and checked again) |

## Errors and decisions

- **Error, mine, caught by a test:** the rows of percent change by month and hour carried the unit MW. The test of units failed; the builder was fixed and the table rebuilt.
- **Error, mine, caught by the validator:** the table's first name, `demand_growth`, is not the standard's three parts.
- **Decision: the average is the mean of the used hours, not a sum.** A sum over a year with 24 blank hours would be short by them; a mean is not, and nothing is scaled up or filled.
- **Decision: the screen's 25 percent.** Wide enough that no real ramp is touched, narrow enough for every faulty hour I found. A fault that lasts several hours at a believable level would pass; none showed in the top hours of any year, which I read.
- **Decision: 2026 is the year so far, never a year.** It has no annual average and no annual peak.

## For Samuel

1. **The larger balancing authorities:** a pull to approve (the first point above).
2. **The faulty hours are in the warehouse's other tables too.** `eia930_all_emissions` and anything that reads EIA's hourly demand carry PJM's 224,345 MW and New York's zeros as published. A peak read from them is wrong for 2019 and 2020 in PJM. Not changed tonight.
3. **Not in any cloud:** the table is only in `warehouse/output` on this machine until step 1 is run. The builder and the site's copy are in git.
