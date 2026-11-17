# Session 7544 report: `/curtailment` read as a solar or battery developer (chain 304, part C, samueloldlaptop, 16 November 2026)

Energy Research Warehouse (ERW). Branch `wip/7544-curtailment-read`, worktree `C:\Users\lossa\Documents\erw-7544`, stacked on origin/main `5c997c9de`. The read: `docs/reviews/curtailment-read-2026-11-16.md` (19 rows).

## What was done

- The reader: a solar or battery developer in CAISO or ERCOT sizing how much is curtailed, when, at what price, and what storing it would be worth. Five cases: CAISO April 2026; SP15 and NP15, January to October 2026 and October 2026; a 4-hour against an 8-hour battery, April and October 2026; ERCOT October 2026 at HB WEST; the figures shared with `/shoulder`, `/storage` and `/cost-of-power/battery`.
- The whole page drawn to HTML for twelve addresses by its own function, without a build (`site/scripts/curtailment-page.mjs`, new; registered with `scripts/battery-awards-page-register.mjs` for the font stand-in).
- 8 site faults fixed in `site/app/curtailment/page.tsx` and `site/app/curtailment/Sections.tsx`, held by `site/scripts/test-curtailment-read.mjs` (24 of 24).
- The other machine's stack touched: `site/app/curtailment/page.tsx` and `Sections.tsx` only (the lab desktop's chain 301 tool). Not touched: `replication/curtailment/`, `docs/methods/curtailment.md`, the faults file, `site/lib/decisions.ts`, any builder or table, `site/lib/license.ts`, `site/components/Num.tsx`.
- Tests run: the new test (24 of 24); pytest `test_session114_part2, 144_page, 149_map, 153, 215, 238, 241a, 281, 317, 321, 331, 412, 7018_curtailment_done, 98`: 205 passed, 10 skipped by their rules; node `test-freeenergy` (all passed), `test-seller-read` (14 of 14), `test-ask-tables` (16 of 16). Not run: a build, `tsc`, `check-curtailment`, `check-values`, `check-routes` (memory).

## What to review

- `https://erw-flame.vercel.app/curtailment`: the summary's last sentence reads "In October 2026, 91.54 percent of that month's curtailment fell ..."; under "Against battery charging", the note of "Taken in by the batteries" names the storage page; open the fold "Every month's share, CAISO" and hover October 2026's "Curtailed, MWh" (145,902, underlined): it names the 30 of 31 days and gives 182,465 MWh over 31 days.
- `https://erw-flame.vercel.app/curtailment?period=2026-10&dur=8`: "What it is worth": the first figure's note ends "Of the 182,465 MWh curtailed in October 2026, 36,563 fell in hours with no real-time price held and are left out."; hover "SP15, real time" in the hub table: "604 of the 720 hours with a price had any curtailment"; the battery part reads "An 8-hour battery" and "What an 8-hour fleet".
- `https://erw-flame.vercel.app/curtailment?grid=ercot`: the head's third figure reads "A whole month, October 2026: 6.05 percent"; no "ERCOT, a whole month: not held yet" line under "By month"; in "What it is worth", hover "HB HUBAVG" (the head's note and the hub table): ERCOT's hub average in words.

## Needs the key

- Nothing. (The live set's rows were not read: no key in the worktree; this machine's two daily tables stop at 4 November 2026.)

## Decisions made without you

- The battery's charging and the storage page's: said in words with a link, no figure of the other page drawn here (row 2).
- The share's fewer days: said on hover in the fold's cell; the share itself is unchanged by its rule (row 3).
- The hub average's words are ERCOT's definition as the Protocols give it (the simple average of the four hubs); no figure depends on it.

## For Samuel's ruling

- Row 14: what stored curtailed energy would earn. Default: no revenue on this page (it has no dispatch rule); the header links the battery page. Other choice: one line with the battery page's figure for the same hub and duration.
- Row 15: SP15's and NP15's rows value the system's one curtailment figure at two hubs. Default: words unchanged (the method note says it). Other choice: a hover on the hub table saying the MWh are the whole system's.
- Row 16: Texas shows three shares of the limit for three spans (6.23, 5.91, 6.05 percent). Default: unchanged, each labeled. Other choice: the head's span only.

## Rows for the coordinator

### (a) Landing request, row 42

| 42 | `wip/7544-curtailment-read` | `f866fe8ec` (the report commit follows) | `7544-curtailment-read` | 7544 | 2026-11-16 | `site/scripts/test-curtailment-read.mjs` (24 of 24, the whole page drawn to HTML by its own function without a build, on the site's files); pytest `test_session114_part2, 144_page, 149_map, 153, 215, 238, 241a, 281, 317, 321, 331, 412, 7018_curtailment_done, 98`: 205 passed, 10 skipped by their rules; node `test-freeenergy`, `test-seller-read`, `test-ask-tables` pass; `tsc` not run; not built here (memory); `check-curtailment`, `check-values` and `check-routes` not run | requested |

## Row 42: what it holds (chain 304, part C, session 7544, `/curtailment` read as a solar or battery developer)

- **Stacked on** origin/main `5c997c9de`. Report: `archive/sessions/SESSION_7544_REPORT.md` on the branch.
- **What changes:** `site/app/curtailment/page.tsx` (the summary's battery sentence names the month; the note of "Taken in by the batteries" with a link to `/storage`; Texas's head gives the newest whole month and the "a whole month: not held yet" line is drawn only with none; the fold's share cells over fewer days than the month carry a hover with the whole month), `site/app/curtailment/Sections.tsx` (the worth note names MWh with no real-time price; the hub table's hover counts; "an 8-hour"; ERCOT's hub average and bus average in words on hover; new exports `an`, `An`, `HUB_WORDS`, `curtailedOf`, `ercotWholeMonths`). New: `site/scripts/curtailment-page.mjs`, `site/scripts/test-curtailment-read.mjs`, `docs/reviews/curtailment-read-2026-11-16.md`, this report.
- **What does not change:** any table, builder or site data file (`site/data/curtailment/`, `curtailment_profile.json`), `replication/curtailment/`, `docs/methods/curtailment.md`, the faults file, `site/lib/decisions.ts`, `site/lib/curtailment.ts`, `site/lib/freeenergy.ts`, `site/lib/license.ts`, `site/components/Num.tsx`, `site/lib/release.ts`, `check-values.mjs`. No figure or check key changes; new `data-n` keys: `worth|mwh_all`, `worth|unpriced`, `head|month`, `head|month_wind`, `head|month_solar` (Texas's head).
- **Before landing:** a site build on the landing machine (`tsc` was not run here); `node --import ./scripts/battery-awards-page-register.mjs scripts/test-curtailment-read.mjs`; `node scripts/check-curtailment.mjs` against the built page (the new `data-n` keys above must be known to it or ignored); `check-values` on `/curtailment`.
- **Snapshot differences to expect:** none on the 25 addresses (`/curtailment` is in review; a visitor is shown the in-review page). **Tables:** none.
- **After the landing:** browser reads 206 to 208; data requests 179 to 183 are the data machine's and do not hold this row.

### (b) Browser reads

| 206 | 2026-11-16 | 7544 | `wip/7544-curtailment-read` (row 42) | `https://erw-flame.vercel.app/curtailment?period=2026-10&dur=8` | "What it is worth": the first figure's note; hover "SP15, real time" in the hub table; the battery part's labels | The note ends "Of the 182,465 MWh curtailed in October 2026, 36,563 fell in hours with no real-time price held and are left out." (or the figures of the live file); the hover reads "604 of the 720 hours with a price had any curtailment"; "An 8-hour battery could have taken in" and "What an 8-hour fleet could have absorbed" | wanted |
| 207 | 2026-11-16 | 7544 | `wip/7544-curtailment-read` (row 42) | `https://erw-flame.vercel.app/curtailment?grid=ercot` | The head's third figure; "By month"; hover "HB HUBAVG" in "What it is worth" (the head's note, dotted underline, and the hub table) | "A whole month, October 2026" 6.05 percent with wind's and solar's MWh below the limit; no "ERCOT, a whole month: not held yet" line; the hover says ERCOT's hub average is the simple average of its four trading hubs' prices | wanted |
| 208 | 2026-11-16 | 7544 | `wip/7544-curtailment-read` (row 42) | `https://erw-flame.vercel.app/curtailment`, at 1280 and at 390 px | The fold "Every month's share, CAISO": hover the underlined "Curtailed, MWh" of October, September and August 2026; the battery section's note | Each hover names its days ("Over the 30 of 31 days ...") and the month's MWh over every day held; the note's "storage page" link opens `/storage`; the fold's table scrolls in its frame and the page does not scroll sideways at 390 px | wanted |

### (c) Data requests

| 179 | 2026-11-16 | 7544 (chain 304, samueloldlaptop; branch `wip/7544-curtailment-read`) | `iso_curtailment_monthly` | The table stops at September 2026: `run_status.csv` shows 3,256 rows on the GitHub runner's runs of 5, 12 and 15 November, while the daily tables hold every day of October 2026 for CAISO (and ERCOT's October is whole in the hourly table). `/curtailment`'s "last 13 complete months" and its monthly chart end at September. Build it from the full daily tables (as faults row 1 moved the profile to the data machine) and load it | the read's row 9 | requested |
| 180 | 2026-11-16 | 7544 (chain 304, samueloldlaptop; branch `wip/7544-curtailment-read`) | CAISO real-time hub prices (`iso_rtm_hub_prices`, SP15 and NP15) and `caiso_fuel_supply` | 15 October 2026: no real-time hour at SP15 or NP15 (720 of October's 744 held) and 7 of 24 hours of Today's Outlook supply (16 October: 17 of 24); 21 August and 22 September 2026 lack output too. 15 October was October's largest curtailment day (36,563 MWh, 20 percent of the month): it is out of October's share and its real-time worth. Fill the hours from CAISO's open files if they are there, then rebuild `shares.json` and `worth.json`; nothing filled by estimate | CAISO OASIS and Today's Outlook; the read's rows 3, 4 and 10 | requested |
| 181 | 2026-11-16 | 7544 (chain 304, samueloldlaptop; branch `wip/7544-curtailment-read`) | `site/data/curtailment/worth.json` (`warehouse/derived/curtailment_worth.py`), ERCOT | `months_missing` says "no whole month is held ... before 19 September 2026", while `ercot.json` holds October 2026 whole (744 of 744 hours) and its first hour is 28 September 2026. Write October 2026's worth by the file's own month rule, and take the date in the words from the file's first hour | the read's row 11 | requested |
| 182 | 2026-11-16 | 7544 (chain 304, samueloldlaptop; branch `wip/7544-curtailment-read`) | `site/data/curtailment/ercot.json` and `worth.json` | One view, two spans: `ercot.json` built 15 November 15:18 UTC (to 15 November 13:00, 1,159 hours, 47 whole days, 1,426,875 MWh below the limit), `worth.json` built 16 November 19:05 UTC (to 16 November 12:00, 1,182 hours, 48 whole days, 1,466,136 MWh). Build both in the same run of the data machine | the read's row 12 | requested |
| 183 | 2026-11-16 | 7544 (chain 304, samueloldlaptop; branch `wip/7544-curtailment-read`) | `site/data/curtailment/worth.json`, the battery rule | The 2, 4 and 8-hour battery's MWh per MW have no price. Add, for each period and duration, the hub's real-time and day-ahead price weighted by the MWh the rule takes in each interval (USD per MWh charged), by the note's rule; the page can then say what the battery paid for what it took in | docs/methods/curtailment.md, "A battery of 2, 4 or 8 hours"; the read's row 13 | requested |

### (d) Progress, part C

| `/curtailment` | lab-desktop | done `<head>` on `wip/7544-curtailment-read` (landing row 42): the reader a solar or battery developer in CAISO or ERCOT sizing curtailed energy, its hours, its price and what storing it is worth; five cases (CAISO April 2026: 1,348,695 MWh of solar, 15.81 percent, most at 15:00; SP15 and NP15 in 2026: USD -5.48 and 4.99 per MWh, October's 36,563 MWh of 15 October with no real-time price; a 4-hour against an 8-hour battery, 120 and 240 MWh per MW in April 2026, unpriced; ERCOT October 2026 6.05 percent of the limit, at HB WEST 20.54 per MWh over the hours held; `/shoulder` 97 of 97 month figures equal, `/storage`'s charging nets each hour); rows: 19 (8 site fixed, 5 data machine, 3 browser, 3 rulings) | 7544 |
