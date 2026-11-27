# Session 10409 report: chain 720, part E: `/forecast` gives a view to each output the forecast gained on 27 November

Energy Research Warehouse (ERW). 27 November 2026, 09:27 to 10:17 UTC, the portable laptop's first window (code role), unattended. The only window on this laptop tonight.

## Why

- You asked for a view on `/forecast` for each new output of the desktop's second window. Its dated lines of 27 November name six: the operator's filing checked by month, a separate line with the weather forecast, net demand, the band's record, the wind and solar file, and the real-time price file. One line of 26 November was also not drawn yet: a forecast kept as first made.
- All are on main in `site/data/predict/` since 06:40 UTC. The page as landed drew none of them (read on production at 09:55 UTC, where it stands at both widths on the new files).

## What a reader now sees (`wip/c720-forecast-lines`, part of row 63)

- **Under "Tomorrow": wind, solar and net demand.** Four figures (lowest and highest net demand, highest wind hour, highest solar hour), one chart of four lines (demand, net demand, wind, solar), how each has scored, and the hours behind a fold. In the 14 places whose file holds net demand.
- **Under "How it has done": wind and solar on a past day,** the forecast as a line and what happened as a dashed line of the same color.
- **The operator's filed forecast, checked by month.** Where months are flagged the page says what the contract asks: in those months the filed forecast is not the operator's own. Beside it, the scores on every month and on the months that pass. Every month is behind a fold. Sixteen of the 29 places have a flagged month; Duke Energy Florida has all 89, and its row says no month passes.
- **The line "with the weather forecast".** Named a separate line, not the ERW forecast; in no chart. All 14 places that have it say "too few days to judge" (13 to 20 of the 30 days needed).
- **The band's record.** How often what happened fell inside the band, below it and above it; by hour of the day as a chart; by month behind a fold. For demand, price, wind, solar and the real-time price.
- **With "Price": a section "Real-time price"** for the six places whose hub the file holds (three hubs). The day forecast now beside the hub's day-ahead price, a past day, and the report card by month and hour. The day-ahead price is named the comparator, never an ERW method. For today the file holds no forecast, and the page says so in the file's own words: "no forecast yet".
- **Two more rows in the table of the other cuts:** the months whose operator filing passes its check, over the backtest and over the last two years.
- **The place's hover** says when a forecast is the one first made for the day and kept.
- **A loss is drawn as a win is.** Texas: net demand over the hours the operator also forecast, the ERW forecast 17.06 percent of the mean, the operator 5.46. The real-time price over the last two years: the ERW forecast missed by 12.33 USD/MWh, the day-ahead price by 11.83. Same table, same weight.

## What is real and what is not

- **Real, from window B's files:** every figure, each with its key into its file. Against main's files: 120 pages (all 29 places, both series, both scores), 104,167 figures, none differing.
- **Blank, and why:** net demand for today in four regions (the file is empty and gives no reason: asked); the real-time price for today at all three hubs (the file's reason); wind and solar forecasts for today in the Midwest and the Northwest.
- **Not drawn:** CAISO's own wind and solar lines. No place's file names them (asked).

## Checks

- **New test:** 112 checks on a fixture in the files' shapes; 87 Python tests of the forecast and the site's lists pass.
- **Type check and lint:** clean.
- **The value check** knows the new megawatt figures are written whole (one rule on a line of its own).
- **The 230 test files that walk the site or name the page's files:** 3,038 passed, 97 skipped, 6 failed. The six are the ones that fail on main's own tree on this laptop (run there at 09:27 UTC); none names the forecast page.
- **Built and seen twice.** The first commit, with 3,183 MB free: seven addresses a width at 1280 and 390 px, no sideways scroll, the charts under a mouse and a finger, the folds by the keyboard. Its pictures showed two faults of mine, mended: with two places the score tables were squeezed into half-width columns, and on a phone the long line names took half of each chart. The mended head was seen in session 10410's build.

## Mistakes of mine, found on the way

- **A command with a stray `python -` and a heredoc,** which this chain forbids and which hangs the interpreter here. It changed nothing; I stopped it.
- **A commit made with two failing tests** (I chained the commit after the test command without reading its exit code). Not pushed; mended in the next commit. One was my own pin; the other an older test of mine that counts the page's four sections, so the new section is now a component of its own and the four stand as they were.
- **A test list by the word "predict"** pulled in the desktop window's model tests, which ran eight minutes without finishing. Stopped and run again on the tests that walk the site or name the page's files.
- **A test run that never started:** 291 file names were too long for one command line. My runner now passes them as a list.

## Decisions made without you

- **One landing row for all the views,** not one a view: they share two new files and the page's one file.
- **With two places, the new tables stand one place under the other** at the page's full width; six and seven columns do not fit half of it.
- **The lines' names in the new charts are short** ("Demand", "Net demand", "Wind", "Solar"); the words "ERW forecast" are in each chart's title.
- **The wind and solar a place shows are the entry its net demand names.** A place with no net demand shows none.
- **The real-time price is joined to a place by the hub of its day-ahead price forecast.**
- **A method's id in a sentence of a file is put in the page's words** ("regression_recent" reads "regression with the recent days").
- **The cut "top10" of the real-time price is named with the score file's words** ("the ten highest-demand days") until window B says otherwise (asked, its request 12).
- **The row was not requested while under 2 GB of memory was free** for a build of the mended head (1,620 to 1,901 MB between 09:58 and 10:17 UTC). I went on to the next unit on a stacked branch instead of waiting.

## For Samuel's ruling

- **Where the new blocks sit.** Today: after what the page had, in the order above.
- **Whether a place with no flagged month should say so in a sentence.** Today: no sentence; its fold says "none flagged".

## Needs the key

- Nothing. No model was called.
