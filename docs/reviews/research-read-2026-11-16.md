# Automated Analysis (`/research`) read as its reader, 16 November 2026

Energy Research Warehouse (ERW). Session 7605, chain 305 (part C), the portable laptop, 17 November 2026. The page as built from origin/main of that morning, served here and read in a browser at 1280 and 390 px in the internal view. The tool's notes are `docs/methods/automated_analysis.md` and its two siblings; its signature pack `docs/reviews/five-tools-signature-pack-2026-11-14.md`. No model was called: the ask form was read, not sent.

## The reader and the five cases

The reader: **a fund analyst reading the week's findings on a Monday**, who will quote one figure to a committee and wants to know where it comes from and whether another page says otherwise.

1. **This week's chart, 2026-W45:** what moved, by how much, and from which table.
2. **Today's chart, 12 November 2026:** "Net generation from natural gas in Wyoming: 1,060,504 MWh in August 2026, the highest monthly value held since January 2001", 39 percent above the record before (765,381 MWh, July 2024): can the reader read the record's figures, and is the jump real?
3. **The card "Batteries ate their own lunch? Five grids":** ERCOT's coefficient, its caveat, and its data, Python and Stata files.
4. **The library filtered to ERCOT:** the cards that read ERCOT's tables, with an address to send.
5. **An analysis asked of the deal tracker's table** (`energy_deals`), for the AI-power deals by quarter.

## What the reader got

| Case | Answer on the page | Without leaving it? | Agrees with the other pages? |
|---:|---|---|---|
| 1 | "Lower 48 battery discharge, daily mean of the week: 47,682.14 MWh a day in the week of 2026-10-26 to 2026-11-01, down 6,317.57 from 53,999.71 the week before. Of the 102 week-to-week moves before it, 8 were as large."; the five next moves by the same rule; the source line reads "Energy Research Warehouse (ERW), derived, Energy Research Warehouse (ERW), derived from California ISO via the Energy Research Warehouse (ERW), table storage_daily_cycle" (row 3) | yes, but the source line is not right | the "Also moved" line's ERCOT fleet, 19,194.6 MW in September 2026 up from 18,204.5, is `/storage`'s and the battery game's 19,194.60 MW |
| 2 | The fact and its source table; the record's figures printed under the scanner's own names: "sigma 26,822; ... stood points 25; history years 25.41; margin sigmas 11.00; history points 306" (row 2, fixed) | in part | the jump is not checked anywhere on the site (row 4) |
| 3 | "ERCOT: with load, Henry Hub and the month of the year held fixed, each added GW of batteries goes with a worst-interval multiple 10.81 lower (standard error 2.33, p < 0.001)", with its caveat; the three files are served (the CSV answers 200, text/csv) | yes | the card's own replication is the done line's |
| 4 | "By grid ... ERCOT 9": a click makes the address `/research?grid=ercot` and the index "Card index, 9 of 12" | yes | |
| 5 | The list "The tables to read ...: the public tables of the live set" offered `energy_deals`, `datacenter_facilities`, `news_index` and the other tables held whole (row 5, fixed). Sending it needs the key | no (key) | the deal tracker holds the same table whole |

## The rows

| # | Case | The cell or click | What the reader meets | Kind | State |
|---:|---|---|---|---|---|
| 1 | 3 | At 390 px, a card's fold "Method, the table of estimates" opened | The page grew to 712 px and scrolled sideways: the library's grid on a narrow screen took the widest card's least width, though the table itself is in a frame that scrolls | site | fixed (`site/app/tokens.css`: `.with-index > .index-main { min-width: 0; }`; `tests/test_session7603_research_read.py`); read again: 390 px |
| 2 | 2 | Today's chart, "The record's figures" | The scanner's names: "sigma", "margin", "strength", "threshold", "stood points", "history years", "margin sigmas", "history points": words a fund analyst does not know, and two of them (threshold, old record) the same figure | site | fixed (`site/lib/researchrules.ts`, `FIGURE_WORDS`): "the series' usual move (one standard deviation) 26,822; the new value 1,060,504; above the record by 295,122; ...; periods the record before had stood 25" |
| 3 | 1 | This week's chart, its source line | "Energy Research Warehouse (ERW), derived" twice, and "derived from California ISO" for a figure of the Lower 48 (EIA-930's battery net generation, with CAISO's own outlook for California) | data machine | request row 262 of `docs/state/data_requests_done_line.md`: the weekly job's source line for `storage_daily_cycle` |
| 4 | 2 | Today's chart, Wyoming's record | 1,060,504 MWh against a record of 765,381: 39 percent above it and 11 of the series' usual moves; a revision or a unit slip would look the same. Not checked on this machine (the live set's series did not answer a read by name here) | data machine | request row 263: the August 2026 value set beside EIA's own electricity data browser for Wyoming |
| 5 | 5 | The ask form's list of tables | Called "the public tables of the live set", it offered the tables held whole | site | fixed (`site/app/research/page.tsx`): a table held whole is not offered; one held by grid or by row keeps its public rows and stays |
| 6 | 5 | "Ask the warehouse" | Not sent: a request is answered by a model | key | under "Needs the key" |
| 7 | 1 | The weekly note, "Note: model claude-sonnet-5-5, literal-number check passed (attempt 1), USD 0.0090." | A line about how the note was written, in the reader's way between the chart and its five next moves | ruling | default: left (it says how the words were checked) |

## Two pages that share a figure

- ERCOT's operating battery storage, 19,194.6 MW in September 2026: the weekly chart's "Also moved", `/storage` and the battery game, the same.
- `energy_deals`: held whole on `/deals`; it was offered on the ask form as public (row 5).

## Needs the key

- **Ask the warehouse** (case 5): not run. One request is one model call over the question and the chosen tables' catalogue rows; by the weekly note's own cost (USD 0.0090 for a note of a few hundred words) an answer is estimated at about USD 0.05. Not measured.
