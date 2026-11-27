# Session 10411 report: chain 720, part E: `/forecast` reads the second window's lines of 27 November, 10:45 UTC (more hubs, the backtest by year, 35 more places)

Energy Research Warehouse (ERW). 27 November 2026, 10:52 to 11:36 UTC, the portable laptop's first window (code role), unattended.

## What a reader now gets (`wip/c720-forecast-hubs`, row 64, stacked on row 63)

The second window's note of 10:45 UTC named what its branch `wip/c730-predict-v4` (its landing row 9) adds. Its files are not on main yet. The page reads each addition the day the files land, and draws main's files of today exactly as before.

- **More hubs.** With price, a new section "More hubs": the other hubs of the place's grid, one row a hub (the highest and the lowest hour of its day-ahead forecast, and how each market's forecast has scored). A hub's name draws it whole under the table: its day-ahead price (from the new file `price_hubs.json`) and then its real-time price, each with the day forecast now, a past day, the report card and the band. "Close" puts it away. The hub is in the address (`hub=`), so the view can be linked and the back button works.
- **The real-time backtest from 2016, year by year,** for every hub that carries it: the whole span, each year, and the share of hours inside the band.
- **35 more balancing authorities** in the list of places (64 in all). Each draws as a place does: demand only, the price a blank that says why.
- **CAISO's wind and solar under its own authority** (my request 11, met by the second window's `shown_for`). A place with wind and solar but no net demand of its own shows the two lines without one.
- **Why a day is not forecast,** in the file's own words, on the blank (the second window's `tomorrow_held`).
- **A price's ten days are named by the price** ("The ten days with the highest price hour"), with each file's own words for a cut on hover (my request 12, met by `cuts` and `cuts_price`). The score file's words for demand are no longer quoted for a price.
- **One more download:** a hub's day-ahead price forecast (`/forecast/hub-price?hub=`), a CSV with a Python and a Stata reader, as the other views have.

## Seen

- **On the second window's files** (a copy of its branch's `site/data/predict` on this laptop, served to a local build; never deployed, never committed): ten addresses a width at 1280 and 390 px. 64 places in the list. Texas with price lists three hubs (Houston, South, West); California lists one (NP15). A hub pressed is drawn, the address carries it, and the back button puts it away. A hub of another grid in the address draws nothing. The year-by-year table shows 2016 to 2026. No page is wider than the screen; 118 keyboard stops on the price page, each with a ring.
- **One fault seen at 390 px and mended:** the links under a hub drawn were 18 px tall. They are 28 px in a second build, of the head, and pinned in the test. The "Chart" and "Table" switches of the site's shared chart are 22 px tall there, as on every page that has a chart; not this page's to change.
- **In the files, as they are:** at ercot:HB_WEST the ERW real-time forecast missed by 127.29 USD/MWh over 2021 and the day-ahead price by 47.35. The page draws both, and a year the day-ahead price was closer is drawn as any other.

## Checks

- **The Node test:** 211 checks (it was 147), the hubs from a fixture of the contract's words, the new route asked as a browser asks it.
- **Python:** 115 passed (the new test, the forecast's, the site's lists).
- **Type check and lint:** clean.
- **Every drawn figure against the files:** on the second window's files 268 pages, 259,718 figures, none differing, four hubs drawn whole; on main's files 120 pages, 122,962 figures, none differing.
- **The value check on the build** (main's files): 4,102 of 4,102.
- **Built twice:** at 11:22 UTC with 2,449 MB free (exit 0, 114 s), and the head at 11:35 UTC with 2,957 MB free (exit 0, 60 s).
- **The 231 test files that walk the site or name the page's files,** on the head: 3,050 passed, 97 skipped, 6 failed. The six are the ones that fail on main's own tree on this laptop; none names the forecast page. The new test file ran beside them: 51 passed with the three it shares pins with.

## Decisions made without you

- **Which place shows a hub.** Neither hubs file says. The page offers a hub under every place whose own price hub is on the same grid, read from the hub's id before its colon: the three ERCOT hubs under Texas and ERCOT, NP15 under California and CAISO. Asked of the second window as its request 15.
- **One hub drawn at a time,** chosen in the table. A hub drawn whole adds 0.37 MB of markup to a price page of 0.58 MB (measured on the second window's files); the list alone adds 9 KB.
- **A stacked row.** Row 64 is cut from row 63's head, so the desk lands 63 first or lands 64 alone, which holds both.
- **No ruling taken on the year-by-year table's words.** It says what each number is and names no winner.

## For Samuel's ruling

- **Whether "More hubs" belongs on `/forecast` or on a page of its own.** Today: a section of the price view, closed until a hub is chosen.

## Needs the key

- Nothing. No model was called.

## Waits on others

- **The second window's row 9** (its files). Until it lands, production shows none of this: the section "More hubs" does not appear, and the list holds 29 places.
- **Seen on its branch at 11:27 UTC, not asked:** `scores.json` has no `cuts_price` yet and the place files no `tomorrow_held` for net demand (its rebuild was running). The page draws each when the file holds it.

## Next

- Session 10412: the equities problem set on what companies filed, held out of the dated edition.
