# Session 10413 report: chain 720, part E: the new views at a phone's width, by a finger

Energy Research Warehouse (ERW). 27 November 2026, 11:57 to 12:17 UTC, the portable laptop's first window (code role), unattended.

## What was read

Each view added since you took the laptop, taken through its page's cases (the five written before each page, `docs/reviews/pages-ground-2026-11-26.md`) at 390 px with touch events only. A mouse was never used: it shows hover cards a phone never shows.

- **`/forecast`, the views of sessions 10409 to 10411,** on a local build served with a copy of the second window's branch files: net demand, wind and solar; a past day's wind and solar; the operator's filing by month; the band; the real-time price; "More hubs" with a hub drawn; the downloads.
- **`/equities`, the filed figures of session 10408,** on production, where row 62 has landed: two utilities side by side, a company found by its name, one company from chart to download. Two of the page's five cases read share prices, which are held, and were not taken.

## What a finger gets

- **No page is wider than the screen,** with every fold open and with a hub drawn. Every wide table scrolls inside its own frame.
- **Every chart answers a tap** with a card that stays on the screen: the four lines of net demand at an hour, the band's shares, a hub's forecast with its band, a company's revenue for a quarter.
- **Every fold opens by a tap.** A hub's name draws the hub, the address carries it, and "Close" puts it away.
- **A form works by a finger:** a past day and "Show"; a filed figure and its periods and "Show"; part of a name and "Filter" (one company found of 307), then the company.
- **The downloads answer:** each new CSV and reader 200, a hub the file does not list 404.

## Three gaps found, each mended (`wip/c720-phone-gaps`, row 66)

A finger's target should be 24 px in each direction. Three kinds of link were under that and are not links inside a sentence:

- **A company's name in the table of every company** on `/equities`: 18 px tall. Now 48 px on a phone (the name wraps), measured in a build.
- **A filing's link under a filed figure** on `/equities`: 15 px tall. Now 30 px.
- **A place's name in the table of every place** on `/forecast`: 18 px tall. No longer among the small targets in the build.
- **How:** padding, with a negative margin of the same size. The row or the line keeps its height (307 rows of companies would otherwise each grow) and only the place a finger lands grows.

## Left as they are, and why

- **The Chart and Table switch of the site's shared charts:** 22 px tall, on every page with a chart. Already with you for a ruling (session 10401).
- **The links of the shared source line** at a page's foot (15 px tall: CSV, Python, Stata, "on Redivis", the method notes). A shared part of the site, on many pages, and each is a link in a line of text.
- **On a problem set's page:** "Show answer" is 20 px tall. The page is the problem sets' builder's, not this window's.
- **Not a gap:** the "i" mark is drawn 16 px wide, and my probe listed it. Its own code gives it a 24 px place to tap (a part 4 px past its edges that draws nothing, since session 2203).

## Checks

- **The two pages' Node tests:** 128, 211, 131, 78 and 104 checks. **Python:** 131 passed.
- **The 242 test files that walk the site or name the two pages, the problem sets or the value check:** 3,094 passed, 97 skipped, 7 failed, the same seven as on main's own tree on this laptop. None names either page.
- **Built** at 12:02 UTC with 3,751 MB free (exit 0, 107 s): a branch that holds main, rows 63 and 64, and the fixes. Both pages at 390 px, every target measured; five addresses at 1280 px with no fault; the value check on `/equities`, 174 of 174.

## Decisions made without you

- **One branch for both pages' fixes, stacked on row 64 with main merged in.** The desk can land this one head and rows 63 and 64 land with it, or land them first. It also shows that rows 63 and 64 merge with main as it stands (no conflict) and build.
- **Padding with a negative margin, not taller rows.** Above.
- **The equities cases E1 and E4 were not taken:** both read a share price, which is held.

## For Samuel's ruling

- **The shared parts under 24 px** (the chart's switch, the source line's links, "Show answer"): whether to raise each across the site. Default taken: left as they are.

## Needs the key

- Nothing. No model was called.

## Next

- `/forecast` and `/equities` read on production after rows 63 to 66 land, and after the second window's row 9.
