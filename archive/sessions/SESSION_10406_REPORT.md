# Session 10406 report: chain 720, part E: the pages read on production; the line "with the weather known"

Energy Research Warehouse (ERW). 26 November 2026, the portable laptop's first window (code role), unattended.

## The landing, and the pages read on production

- **Rows 54, 55 and 56 landed at 17:13 UTC** (window A's desk, landing 3, `693a4a3f5`): `/forecast`, `/equities`, the board's "Energy equities" group and the forecast's problem set. All are in review: the internal view shows them, a visitor sees the in-review page.
- **Read on production, 17:30 to 17:40 UTC:**
  - both pages and the board at 1280 and 390 px: drawn, no sideways scroll;
  - the site's value check: 1,950 of 1,950 figures of `/forecast`, `/equities` and the problem set equal to the files;
  - the 18 download addresses answer; a reader's address carries only the checked value; an unknown place answers 404;
  - the problem set: 6 questions, 1 worked example, 83 figures; not in the list of sets; its CSV address answers 404.
- **Against main's own files, on this laptop:** every drawn figure of `/forecast` (69,888, all 29 places) and of `/equities` (1,092): none differing. The problem set's 475 checks pass on the rebuilt file.
- **What changed against the files read before the landing** (window B rebuilt them at 14:05 UTC): Texas now uses the fourth method ("regression with the recent days"); the ERW forecast's error over the whole backtest is 5.47 percent in Texas (it was 5.86), against the operator's 2.39; it is the lower of the two in 6 of 29 places (it was 5: Southwest Power Pool joined); the forecast for 27 November was made at 14:00 UTC (it was 12:00). The problem set's answers moved with the file, as it is built to.
- **Not read on production:** the back button and the board's own check. The internal view allows 30 unlocks an hour for the whole laptop, and both windows' runs had used them by 17:42 UTC; this window's tries at 17:46 and 17:47 were refused and were not repeated. Both checks had passed in a build of the same code.

## The line "with the weather known" (row 59)

- **What it is:** the regression with the region's observed temperature of the day itself added. It reads the day's own weather, so **it is not a forecast**. Window B's files hold it for all 29 places since 14:05 UTC.
- **What the page does with it:** one table under "How it has done", headed "With the weather known (not a forecast)", beside the regression and the operator's forecast on the same hours, over the last two years and over every hour the weather is held. It is in no chart and no other table, and is never called the ERW forecast.
- **Texas, as the files stand:** over the last two years, with the weather known 3.90 percent, the regression 5.26, the operator 2.06. Knowing the weather removes about a quarter of the regression's error, and the operator's forecast is still the closest of the three.
- **California:** with the weather known 3.25 percent, the regression 4.18, the operator 7.60.
- **Tests:** 17 more checks in the Node test of the peak's branch (114 in all); `tests/test_session10406_forecast_weather.py`, 5 tests. Built (exit 0) and seen at 1280 and 390 px, one place and two; the value check 1,997 of 1,997; every drawn figure against the files, 73,696, none differing.

## The second window's rows

- Row 7 (the events page's link underlined), row 8 (two more links) and row 9 (the problem sets' list on a narrow phone): each seen in a build and marked requested. Row 9's build was put off twice for memory (under 2 GB free).

## Decisions made without you

- **The weather line is drawn.** The contract allows a page to show it if it is labelled; the chain's part E asks the page to be read against new files as they land. The other way was to leave it out until asked.
- **Its place is under the peak's table,** before the months. It has no chart.
- **Production's internal view was left alone** once it refused the browser, and later reads are gathered into fewer runs.

## For Samuel's ruling

- **Whether "with the weather known" belongs on the page at all.** Today (row 59): one table, labelled "not a forecast".
- **The internal view's allowance of 30 unlocks an hour** is shared by every window on one laptop. Two windows reading production in a browser reach it. Today: left as it is; this window keeps to few runs.

## Needs the key

- Nothing. No model was called.
