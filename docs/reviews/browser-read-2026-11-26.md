# The browser read of 26 November 2026: everything landed since 20 November, and what lands tonight

Energy Research Warehouse (ERW). Chain 750 (`queue/done/750-night-26-november-portable-window2-browser-read.md`), the portable laptop's second window, sessions 11000 on. Every page is read on production (`https://erw-flame.vercel.app`) in the internal view, in the laptop's own Chrome driven by `site/scripts/browser.mjs`, at 1280 px with a mouse and at 390 px with a finger (touch events). No build is made here and no model is called. The scripts are in `runs/c750/` on the laptop (not in git); the pictures are in `docs/reviews/browser-read-2026-11-26/`.

How a row reads: what was done, what was seen, what should be seen, and whose it is. A site fault on a page no window owns tonight is fixed on a branch `wip/c750-<page>` with a test and is a row of `docs/state/landing_request_portable_w2.md`. A fault on a page another window owns tonight is a row here that names the window, and its code is not edited. A data fault is a row of `docs/state/data_requests_done_line.md`. A thing that is a choice is one line under "For Samuel's ruling" at the foot, with the page left as it is.

## Part A: the rows that waited for a browser

Rows 418 to 422 of `docs/state/browser_reads_wanted.md` were the only rows in state `wanted`. On 20 November their commits (the old laptop's sessions 8470, 8480 and 8490) were not in main. All three branch heads are in main now (`c7a96eea1`, `34c53f280`, `1e3a9e95b`), so each was read on production at 1280 and 390 px on 26 November about 11:20 UTC. All five are marked `seen` there, with the words read.

| Row | Address | What was seen | State |
|---:|---|---|---|
| 418 | `/events/uri-2021?region=tex&b=cent#whole-country`, and `/events/caiso-heat-2020?region=nw&b=cal#whole-country` | The Midwest's net imports hover gives both figures (pairs +9,619 MW against net imports +5,427 MW over 435 hours) and why they need not agree. Over Uri the Northwest's sources now rest on 434 hours both sides hold, so the line the row asked for was read where the case still arises, the Northwest over the August 2020 heat: "Northwest's sources are held for no hour of the window and 123 of the baseline, never the same hour, so none is set against it". No sideways scroll | seen |
| 419 | `/demand?view=country&a=se&b=fla&figure=summer&year=2025` | Each of the nine blank weather cells says why it is blank, with the 95 percent rule and the regions' 80 to 99 percent of hours; "no growth since 2019" has its hover; the long names fit; no sideways scroll | seen |
| 420 | `/demand?view=country&a=ba-miso&b=ba-lgee` | MISO's newest day (now 19 November 2026) is blank with the hover "23 of the day's 24 hours are used, so no demand of the whole day is given"; twelve charts drawn | seen |
| 421 | `/supply?region=mida&b=midw&year=2022#whole-country` and `year=2021` | 2025 now holds every month, so the row was read on the Mid-Atlantic's June 2022 and the Midwest's March 2021: each is a row reading "not held yet" with the builder's 90 percent rule on hover; no sideways scroll of the page | seen |
| 422 | `/supply?region=ten&b=car&year=2025#whole-country` | The mean's hover says it runs over the 8,734 hours both reported and need not lie between the two reports; the percent's hover says the two sides filed different hours (8,759 and 8,735) | seen |

Pictures: `docs/reviews/browser-read-2026-11-26/part-a/row418-caiso-heat-2020-northwest-line-1280.png` (the line under the sources table naming the Northwest, with its row of blanks above); `docs/reviews/browser-read-2026-11-26/part-a/row421-supply-midatlantic-june-2022-390.png` (the mix table at 390 px with June 2022 as a row of "not held yet").

Two things these reads showed beside what the rows asked, carried into part B's sections:

1. **A reason given on hover cannot be opened by a finger.** Every reason read above (why a cell is blank, why two figures differ) is the browser's own tooltip (a `title`). At 390 px with touch a tap opens none of them. The "i" marks and the chart cards do open on a tap; a blank cell's reason does not. Not new (chain 620 noted it for three charts as row S2), and it is site-wide, so it is one line under "For Samuel's ruling" and not a fix here.
2. **The mix table grows by half when a month is left out** (`/supply`, whole country): the words "not held yet" do not wrap, so the table is 1,325 px wide inside its 358 px frame at 390 px (900 px for a year with every month), and two columns show at a time. The page itself stays 390 px wide. Row S1 of the `/supply` section below.
