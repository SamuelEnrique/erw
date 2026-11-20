# Session 8450 report: the done line of `/demand` for the whole country, as far as it goes without the files (chain 503, part E)

19 November 2026, samueloldlaptop (code role), unattended. Branch `wip/8450-demand-regions-done`, made from `wip/8420-demand-regions` at `fc0d257f5` (part C, which holds part B at `dffb83952`). Model spend USD 0: no model call. Nothing landed, no table written, no web read, `site/lib/release.ts` not touched: the page stays in review.

## What was done

- **The replication of the view** (`/demand?view=country`): `replication/demand/replicate_regions.py`, standard library only, written from the method note's section and the contract (`docs/state/page_files_regions.md`, sections 2 and 3). It recomputes every figure the view prints from the page files and sets it beside the figure the site's own code draws. A figure passes within half the last digit shown; a figure the rule gives that the page does not show fails, and so does one the page shows that the rule does not give. Exit 0 also when no file is on the site (it says so).
- **The figures script** `site/scripts/demand-regions-figures.mjs`: the site's own component draws each place alone, each year of days, each figure and each year of the weather view, the view as it opens, and each region beside its grid as two places; every checked number, every figure a chart carries as a hover (the years, the cells by month and hour, the bars by month and by hour, the weather chart) and the two points a day of the chart of days go to one JSON file. `--fixture <dir>` writes the test's fixture as a folder; `--draw <out.html> --address ...` writes the view at one address as HTML.
- **On the fixture: 19,191 of 19,191 figures over 166 views of 20 places.** The fixture's values are made by a rule and are not data.
- **Each file read against itself and the contract**, after the count: a growth against the two averages it is formed from, a region's difference from its grid, the days in order and each array as long as the days, a whole day against the hours of its local day, a year's hours and highest hour against its days', the time zone's name. What does not agree is a note for the data machine and fails nothing unless `--strict` is given. On the fixture 501 of 501. Last, each of the seven grids drawn as a balancing authority is set beside the as-metered view's own file, year by year (notes only: both stand).
- **The reader's read** `docs/reviews/demand-regions-read-2026-11-19.md`: the reader (a load forecaster at a utility in the Southeast), five real cases with their addresses, the state table of what is done and what waits for the files, and eleven numbered rows found before any file.
- **Five faults fixed in the view** (`site/components/demand/Country.tsx`, each with a test in `tests/test_session8450_demand_regions_replication.py`):
  1. the two lists of places are held to the width of the form: EIA's longest names of balancing authorities are wider than a 390 px window, which the fixture's short names hid;
  2. each head of the check on the fit's years, and "Give or take", says what it is and its unit on hover (the words of the heads did not move);
  3. a balancing authority that is one of the seven grids carries a link to that grid's own view and a hover naming the two files it is drawn from, both standing;
  4. a summary with no growth (a place whose first whole year is not 2019) says why, in the words "no growth since 2019" with a hover;
  5. the hover of "Which hours are used" says since when the hours left out are counted.
- **The method note** `docs/methods/demand_growth.md`, "The whole country": three bullets added. The section did not say enough to recompute each figure, which is a fault of the note: "Every figure, in the view's order" now gives the conditions of the summary, the rule of the newest days, the last whole year of the weather view, how two equal cells are ordered, and the count under a region and its grid. The rules that the as-metered note and the weather note already state were taken from them; the rest were set from the view as drawn on the fixture, and the replication was then written from the note.

## The files it waits for

- `site/data/regions/index.json`, `demand/<region>.json` and `demand/ba/<code>.json` were not on origin/main at the start or before the push (`git ls-tree -r origin/main --name-only site/data/regions`: nothing, then `ba_boundaries.json` alone, the map's file). The data machine's branch `origin/wip/c501-pages` (at `5943bdad3`) holds the builder and no demand file. Nothing was waited on.
- What waits, said in the read's state table: the five cases read start to finish on real files; the replication's count on real files; the Stata do-file's five headline figures (no do-file is written: its expected values are real figures); the cross-check against published figures (EIA's regional demand on its Hourly Electric Grid Monitor, the Electric Power Monthly's retail sales, the operators' own records), with each host's robots file and terms read first.
- First steps when the files land: merge `origin/main` into the branch; from `site/`, `node --import ./scripts/battery-awards-page-register.mjs scripts/demand-regions-figures.mjs <figures.json>` (about 900 views by a count of thirteen regions and some 65 authorities over nine years of days; not timed on real files: the fixture's 166 views take 10 seconds, `--places ten,car` draws two places only), then `python replication/demand/replicate_regions.py --figures <figures.json>`; read its notes first (data request 328 below is the one to expect); then the five cases.

## Add, never change: how it is held

- Session 8420's pin, `site/scripts/test-demand-pin.mjs`: 101 of 101 after the five fixes. Its view test, `site/scripts/test-demand-regions.mjs`: 93 of 93, not edited. `site/scripts/test-demand-read.mjs`: 24 of 24.
- `tests/test_session8450_demand_regions_replication.py`: 20 passed (the count on the fixture; a figure moved by one in its last digit caught four ways; a dropped figure and one the rule does not give; a held file; a day counted whole on two hours noted, and failed only with `--strict`; a grid beside the as-metered file; the site as it stands; bad input; the five fixes; the source rules).
- The older tests that name a changed file (`test_session8420_demand_regions, 8410_events_regions, 152, 239, 97, 331, 404, 2204, 281, 2877, 472, 538, 7018_demand_done, 7508_demand_growth, 7517_demand_growth_read`): 158 passed, 5 skipped by their own rules, none failed.
- `tsc` on `components/demand/Country.tsx` (a scratch tsconfig, deleted), exit 0; `eslint` on the two changed site files, exit 0.
- Not done here: no site build, no browser, no `check-values`, no `check-routes`, no full suite. No screenshot is claimed.

## What to review

The page needs the review cookie. Until the data machine's files land, each place reads "not built yet", so these are read once they have.

- `https://erw-flame.vercel.app/demand?view=country` at 390 px: open "Place A" and "Place B". The lists stay inside the grey form and the page does not scroll sideways.
- `https://erw-flame.vercel.app/demand?view=country&a=tex&b=ba-erco`: beside "Electric Reliability Council of Texas, Inc." a link "ERCOT as metered" and the words "another file"; rest the mouse on them: both files named, "Both stand; neither is corrected to the other."
- `https://erw-flame.vercel.app/demand?view=country&a=se&b=fla#weather`: open "The check: years the fit had not seen"; rest the mouse on each head: what it is and its unit.
- `https://erw-flame.vercel.app/demand?view=country#years`: rest the mouse on "Which hours are used": the last sentence says since when the hours left out are counted.
- A balancing authority whose record begins after 2019 (the fold "The balancing authorities" gives each one's "Held from"): after its sentence, "no growth since 2019" with why on hover.

Browser reads wanted: rows 410 to 414 (in the hand-back). Data requests: rows 328 and 329.

## Needs the key

- Nothing.

## Decisions made without you

- **A figure is more than a checked number.** The replication also holds the figures the charts carry as hovers and the points of the chart of days. The points are not words in the first HTML, so the script takes them from the function the view hands the chart and writes them as the chart's card writes a value (a copy of one line of `components/TimeChart.tsx`, held to the source by a test).
- **Not held by the replication:** the figures inside the hovers of the table cells (a day's MWh, the hours the weather fit holds) and the "of 8,760" beside the hours used, which carry no mark. The dates and hours ("On", "When, local time") are words, not figures, and are not compared.
- **A file's fault is a note, not a failure.** The replication's exit says whether the page shows what the files give. What a file gets wrong against the contract is printed for the data machine and fails only with `--strict`.
- **The builder was read on its branch, not run.** Two requests came from that reading (below). The first is a fault that would show on the page: the first and the last local day of a record are written as whole days on the hours the record holds (2 hours of 30 June 2018 in Pacific time, 1 hour of the newest day in Eastern time), so "Least in a day" and the newest day of several regions would be wrong.
- **The weather check's years are the first region's.** The view takes the fit's years of the first region drawn for both; the builder writes one list for every region, so the note says so and nothing was changed.
- **A test mode in the figures script, not a new test script**, so the session's new files are the four the prompt names and this report.
- **No web read was made**, so there is no table of robots files and terms yet; the read names what the cross-check will be set against.

## For Samuel's ruling

- **Two charts of days with two scales, or one axis for both places** (row 8 of the read). Default taken: two charts, as built. Other choice: a third chart with each place's highest hour on one axis.
- **Words: "the data machine" in several hovers, and time zones by their computer names ("America/Chicago")** (row 9). Default taken: as built, on the three pages alike.
- **Two forms kept from the as-metered view** (row 10): "the base year" in the base year's cell of "On the year before", and no "+" on the MW of the largest and smallest cell. Default taken: as the as-metered view writes them, for both views.
- **Tables that cannot be sorted** (row 11): a question for every page, since the shared table sorts nowhere. Default taken: not changed.
- The rulings session 8420 asked (the places drawn first, every day drawn, the tab's name, New England, New York and the Midwest drawn, generation-only authorities listed) stand as it left them.
