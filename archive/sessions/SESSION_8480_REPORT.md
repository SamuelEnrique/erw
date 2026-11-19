# Session 8480 report (chain 503, part E: `/demand`, "The whole country", on the real files)

Old laptop (samueloldlaptop, code machine), unattended, 19 November 2026, about 13:00 to 15:00 UTC (two runs: the first cut off at 13:30 UTC). Branch `wip/8450-demand-regions-done`, worktree `C:\Users\lossa\Documents\erw-8450`. Model spend USD 0 (`ERW_SPEND_CAP_USD=0`; nothing that calls a model was run).

## What was done

- **The page files on main.** The 108 untracked copies under `site/data/regions/` were checked against `origin/main` with `git hash-object` (108 of 108 identical, none kept aside), deleted, and origin/main merged (`f1af0f52e`). `site/data/demand_growth.json` and `demand_weather.json` did not move, so the pin needed no new base.
- **The unfinished edit of the first run** (about 100 lines, data request 328) was finished, tested and committed (`0f84ed5c2`): a day's demand counts as whole only on all the hours of its local day in the file's zone. On the real files row 328 holds for two days only: LGEE's 1 July 2018 and MISO's 16 November 2026, each written whole on 23 of 24 hours. "Least in a day" did not move for any place; MISO's newest day now reads blank with the day's hours and why; two counts of days held drop by one.
- **The five cases** of `docs/reviews/demand-regions-read-2026-11-19.md`, each taken start to finish on the view drawn with the site's own code: cases 1, 2, 3 and 5 answered; case 4 is not answerable from these files (the weather figures it asks for are not in them). Rows 12 to 24 of the document; rows 12 to 21 fixed at their cause with tests (`91e0d0abb`, `0f84ed5c2`, `027b4d116`, `e520f37df`).
- **The replication on the real files: 449,440 of 449,440 figures over 783 views of 71 places**, no difference, run after the last change. Files against themselves 2,563 of 2,565 (the two days above). The seven grids as authorities beside the as-metered file: 47 of 49 year averages equal (CAISO 2023 and 2025 differ by 0.1 and 0.4 MW). Written in the method note and the document.
- **The Stata do-file** `replication/demand/replicate_regions.do` (`c3e07fd19`): five headline figures with expected values at its top, from `eia930_ba_demand_hourly`. Stata is not installed here; it has not been run.
- **The cross-check** against published figures (read by a helper agent under the web rules; hosts table and figures table in the document): ERCOT's records and EIA's Today in Energy agree within 0.4 percent (0.03 to 0.09 on the same day). SRP's own records are 1.8 and 2.8 percent below the page in 2024 and 2025 (a narrower measure), but 12 percent below its 2023 figure, 9,283 MW at 14:00 on 22 July 2023. That hour looks faulty and gets past the screen (row 25, a data request). TVA, Duke Energy and APS refused the reader (robots files answering 403, terms out of reach, or terms forbidding automated reading). There was no published figure for Tennessee, the Carolinas, the Southeast or Florida. No figure was adjusted.
- **The decisions**: every choice inside the view says its default and whose choice it is on hover; the region's hour rule and the screen of hours did not and now do (row 21).
- **Tests**: `site/scripts/test-demand-regions.mjs` 114 of 114; `site/scripts/test-demand-pin.mjs` passes (no figure for the seven grids moved); Python 112 of 112 (`tests/test_session8420_demand_regions.py`, `8450`, `8440`, `8460`, `5171`, `152`, `239`, every file that imports or names a changed module).

## What to review

The branch is not landed; until it is, the addresses show main's version. After landing (landing row 52's new head):

- https://erw-flame.vercel.app/demand?view=country&a=se&b=fla&figure=summer&year=2025 : point at "not held" in the Southeast's rows of "With the weather taken out". Expect: "It holds 0 of the 5 years of this figure", the 95 percent rule and "80 to 99 percent of each region's hours". Point at the name "Southeast" at the top: "AEC is counted to 2021-09-01, when EIA gives it as retired". Point at "no growth since 2019" after Florida's sentence: "on 307 of the 365 days it holds".
- https://erw-flame.vercel.app/demand?view=country&a=ba-miso&b=ba-lgee : in "The days drawn", MISO reads 3,060 of 3,061 days with a whole day's demand and LGEE 3,054 of 3,061. In "The newest days", MISO's 16 November 2026 demand is "not held"; its hover says 23 of the day's 24 hours and why. (The newest day moves with each build of the files.)
- https://erw-flame.vercel.app/demand?view=country&a=ba-azps&b=ba-srp : point at "Day" in "The newest days": the line on EIA revising its values. Point at "not held" in the weather view: "choose Southwest as a place".
- https://erw-flame.vercel.app/demand?view=country&a=fla&b=none : in "Year by year", point at a blank cell of the "2026, to October" row: "for 2026, January to October" (no "ytd").
- https://erw-flame.vercel.app/demand?view=country : point at "What a region is" and "Which hours are used": each ends with "Default: ..." and whose rule it is.

## Needs the key

- Nothing in this session needed a model call.

## Decisions made without you

- The page refuses to count a day the file writes as whole on fewer hours than its local day (rather than showing the file as it stands): the contract gives a day's demand only for a day with all its hours used. Reversible: one function, `wholeDayMwh` in `site/lib/countrydemand.ts`.
- The do-file's fifth figure is the Southeast's average of 2025 and its growth, since the Southeast's summer peak with the weather taken out is not held in the file.
- The hovers of blank weather figures quote the data machine's method note (95 percent; 80 to 99 percent of hours) rather than a figure read per file, since the file does not carry the share.

## For Samuel's ruling

- Row 22: the weather view of the regions holds 53 of 256 figures (the Southeast none). Lower the 95 percent rule for the regions, or wait for the weather table's missing hours? Default taken: 95 percent, as for the seven grids, and a data request.
- Row 23: a region's hour needs every one of its authorities, so Florida has no whole 2019 (Seminole's 2019). Keep the rule? Default taken: as built.
- Row 24: count, in the "another file" hover, whether a grid's two files agree year by year (it needs the as-metered file inside this view)? Default taken: the hover as built.
- Row 25: a tighter screen of hours, which would leave out SRP's 14:00 hours of 22 and 23 July 2023? Default taken: as built (the as-metered view's 25 percent rule), and a data request.
- Rows 8 to 11 of the document stand as session 8450 left them (two charts of days, the words "the data machine" and zone names, the as-metered forms, the unsorted table).
