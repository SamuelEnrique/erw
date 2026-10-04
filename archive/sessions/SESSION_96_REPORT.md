# Session 96 report: where power is cheap

**Built, on `wip/096-prices-compare`, nothing deployed.** A new tool, the review page `/prices/compare`, in the battery page's layout: every public hub and zone price the warehouse holds, on the average price, the share of hours below zero, the share above USD 200, the spread between the dearest and the cheapest four hours of the average day, and the carbon intensity of the hub's grid. Sortable by any of them, one chart, a summary sentence, and the statement that a hub is not a site. Behind it is one new derived table.

## To make it live

```bash
# Nothing below was run. No preview address: GitHub recorded no Vercel deployment for this branch's push.

# 1. THE TABLE into the warehouse's records. It exists only in warehouse/output on the old laptop today.
git fetch origin && git checkout wip/096-prices-compare && git merge origin/main
python warehouse/lock.py run --task "hub price comparison" --minutes 15 -- <the venv's python> warehouse/derived/price_compare.py --snapshot
python warehouse/validate/erw_validate.py warehouse/output/hub_price_comparison.csv        # exit 0
python warehouse/metadata/build_coverage.py                                 # read its exit code
python warehouse/archive/archive.py --tables "hub_price_comparison" write
python warehouse/redivis/upload.py --tables hub_price_comparison            # a draft; releasing is your click
#    and in warehouse/supabase/live_set.yaml, under catalogue_hold, while the page is in review:
#      - hub_price_comparison
#    then commit coverage.csv, sources.csv, docs/coverage.md, the live set and site/data/price_compare.json.

# 2. THE PAGE, in review at /prices/compare. A push to a task branch redeploys the site; no live page changes:
python -m unittest tests.test_session96                                     # read its exit code
cd site && node scripts/snapshot-live.mjs take before-096 && cd ..
git push origin wip/096-prices-compare:task/096-prices-compare
cd site && node scripts/snapshot-live.mjs take after-096 && node scripts/snapshot-live.mjs compare before-096 after-096

# 3. OPEN TO VISITORS, when you have used it: in site/lib/release.ts set "/prices/compare" (and
#    "/data/methods/hub_price_comparison") to "live", and add the page to the menu in site/lib/pages.ts.

# 4. TO KEEP IT CURRENT: the windows move with the last whole month, so the table wants a rebuild once a month:
#    one run_other line for price_compare.py --snapshot in warehouse/run_daily.sh on the first days of a month,
#    after the price connectors. It makes no request.
```

**Read these four first:**

1. **Only eleven hubs have twelve months, and no zone does.** You asked for every hub and zone over the last twelve months. The warehouse holds a year of history for eleven hubs (ERCOT's six, CAISO's SP15 and NP15, ISO-NE's Internal Hub, NYISO's New York City, SPP North); the zones of New England and New York and the other hubs have been pulled only since late August 2026. So the page has two periods: the twelve months to September 2026 for the eleven, and September 2026 for all thirty-one. Nothing was stretched to fill a year. A year for the zones is a pull to approve (the operators publish the history; perhaps 1.5 million rows for ISO-NE's and NYISO's zones, day-ahead and real-time, USD 0).
2. **MISO's eight hubs are held and not shown, and that is my decision, taken from your pause.** You asked for internal tables to be shown as "held, not shown: license needed". No hub or zone price table is marked internal today. But MISO's terms, as session 85 quoted them, forbid creating "derivative works" of its content, and its pulls are paused pending your review. A new derived table from MISO's prices is a derivative work, so I derived nothing from them: the eight hubs are named on the page with the reason and no number. The builder reads the pause list, so lifting the pause brings them into the next build with no code change. If you would rather they be shown while the older pages still show MISO's prices, it is one line (`hidden` in `price_compare.py`).
3. **PJM is "not held", not "held, not shown".** The warehouse has no PJM hub or zone energy price at all; the page says that, and does not claim a table it does not have.
4. **Two figures are not written, and the page says so.** ISO-NE's real-time price over the twelve months (8,112 of 8,760 hours held: under the 95 percent the table asks for), and SPP's carbon intensity over the twelve months (236 of 365 days held).

Energy Research Warehouse (ERW), session 96, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 09:51 to 10:12 UTC, unattended. **Model spend: USD 0.00.** No pull, no request to any publisher (MISO's among them), no model call, no force push, no deploy. The data lock was taken once (about a minute) and is free.

## The table

`hub_price_comparison`: 575 rows, 31 hubs and zones. It passes the validator (exit 0). Built by `warehouse/derived/price_compare.py`; method in `docs/methods/hub_price_comparison.md`. No new source: it reads price tables the warehouse already holds, all recorded as public (CAISO OASIS; ERCOT's settlement point price reports; ISO-NE's and NYISO's price reports; SPP's LMP by settlement location), and `carbon_intensity_daily`.

- **Two windows**, in each grid's own local time: the twelve months from 1 October 2025 to 30 September 2026, and September 2026.
- **Two markets**, day-ahead and real-time. An hour of real-time price is the mean of its four 15-minute prices, counted only when all four are held. ISO-NE's real-time price is held two ways (15-minute means, and ISO-NE's own hourly report); the one that holds more of the window is used, whole, never mixed.
- **Five measures:** the mean price; the share of hours below zero; the share above USD 200 per MWh; on the average day (the mean price of each local hour over the window), the four dearest hours less the four cheapest; and the mean of the grid's daily carbon intensity of generation.
- **A market of a hub is written for a window only when at least 95 percent of the window's hours are held**; the carbon intensity when at least 90 percent of its days are. Nothing is filled.

What it says, day-ahead, over the twelve months:

| Hub | Average, USD per MWh | Hours below zero, percent | Hours above USD 200, percent | Spread, USD per MWh | Grid carbon, kg CO2 per MWh |
|---|---|---|---|---|---|
| CAISO, SP15 | 28.92 | 12.82 | 0.01 | 29.78 | 120.06 |
| ERCOT, West | 33.00 | 7.42 | 0.78 | 37.92 | 302.25 |
| CAISO, NP15 | 33.41 | 4.42 | 0.01 | 22.75 | 120.06 |
| SPP, North | 33.51 | 6.68 | 1.26 | 35.34 | not held |
| ERCOT, Hub Average | 34.30 | 0.63 | 0.75 | 33.80 | 302.25 |
| ERCOT, Bus Average | 34.40 | 0.49 | 0.74 | 33.96 | 302.25 |
| ERCOT, North | 34.43 | 0.72 | 0.75 | 34.86 | 302.25 |
| ERCOT, South | 34.55 | 0.56 | 0.71 | 31.85 | 302.25 |
| ERCOT, Houston | 35.22 | 0.02 | 0.71 | 30.57 | 302.25 |
| NYISO, New York City | 73.10 | 0.00 | 4.43 | 42.35 | 248.74 |
| ISO-NE, Internal Hub | 74.19 | 0.00 | 5.16 | 32.48 | 229.96 |

In September 2026, across all thirty-one, day-ahead averages run from USD 36.21 (SPP North) to USD 45.58 (NYISO's Long Island): a mild month compresses them, which is itself a reason not to read one month as a ranking. The page says a year holds one winter and one summer.

## The page, `/prices/compare`

A sentence about a hub not being a site sits above everything, in a bordered block: a hub or zone price is an average over many points; the price at one substation differs by congestion and losses; a buyer also pays delivery, capacity and other charges; the page compares markets and does not price a location. Then the panel (period, market, sort by, and a link that turns the order round), the summary sentence, three headline numbers (lowest average price, most hours below zero, widest daily spread), one chart (a bar per hub or zone for the measure sorted by, in the table's order), and the table, whose headings are links that sort by their column. A hub that lacks the measure sorts last whatever the direction. Under the table: "Held, not shown" (MISO's eight hubs and PJM, each with its reason), how it is computed, and what the page does not tell you (the price at a site; a delivered price; next year; the carbon of the power a site would take; whether power can be had there at all).

**Decision: sorting is in the address,** not in the browser: the page is drawn on the server like the battery page, a sorted view can be sent as a link, and there is nothing to break without scripts.

**Decision: the page reads the site's own copy** (`site/data/price_compare.json`, 12 kB), as the other review tools of tonight do.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session96.py` | 11 tests pass. The measures on prices made for the test: the mean, the two shares and the spread of a known day; an hour of real time only from four quarter hours; the hours of a window across both clock changes; a window with too few hours not written; a paused publisher's hub named and given no row; the basis that holds more used whole. The table as built: New York City's twelve months and SP15's September computed again from the price tables by hand; no MISO and no PJM row; every window at 95 percent or more; 11 hubs and 31; no carbon for SPP's year; no real-time year for ISO-NE's hub. The site's copy equal to the table, row for row. In Node: the choices, the ordering, the names. The page is in review, says a hub is not a site, and reads its own copy |
| `site/scripts/check-prices-compare.mjs`, the built site | 54 checks pass: on five views every number the page marks equals the copy (63 to 200 a view); the bars and the table's rows in the order asked for; five headings that sort and the one sorted by turning the order round; a hub that lacks the market named with no number; "a hub is not a site"; MISO's eight hubs "held, not shown" and no number of theirs anywhere; PJM "not held"; an address it does not understand opens the default; a visitor gets the in-review page with no number on it; `/prices/<hub>` is still the hub's own page |
| Site: types, build (twice), route check | exit 0 each; no statement cancelled in either build. Route check: 103 of 103 pages, and 16 live with 87 in review as a visitor |
| `check-values.mjs` | exit 0 on the second run: 7,454 of 7,485 values match and 31 are latest prices a newer interval replaced during the run. The first run stopped on a Supabase read cancelled at its timeout, the checker's own read, not a wrong value |
| The validator on the table | exit 0 |
| Two screenshots | looked at. The first showed a fault of mine: the table's sorting headings were drawn in the accent color on the accent header row and could not be read. Fixed (white, underlined, with an arrow on the column sorted by), rebuilt, checked again, and looked at again |

After the last build I widened the chart's label column by 42 units so that the two longest zone names are not clipped at the left. The type check passes; the page was not rebuilt for that one constant.

## Errors and decisions

- **Error, mine: the unreadable headings** (above). The page check passed while a person could not have used the sort; only the screenshot showed it.
- **Error, mine, in the check, not the page:** it looked for a heading's attributes in an order the page does not write them in.
- **Decision: the spread's four hours need not be next to each other.** It is the four dearest and the four cheapest hours of the average day. A battery's own spread, with charging before discharging and efficiency, is the battery page's subject, and this page links to it.
- **Decision: the carbon intensity is the grid's, stated as such,** and every hub of a grid carries the same figure. A hub has no carbon intensity of its own.
- **Decision: the mean of the daily intensities, not of the monthly ones.** The monthly table is written only for months whose every day is complete, and California holds three such months of the twelve; the daily table holds 347 of 365 days.

## For Samuel

1. **MISO's hubs on this page** (the second point above): shown, or not until the review.
2. **A year of zone prices:** a pull to approve, if the page is to compare zones over twelve months.
3. **Not in any cloud:** the table is only in `warehouse/output` on this machine until step 1 is run. The builder and the site's copy are in git.
