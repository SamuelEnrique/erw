# The Daily Digest: how a story is scored and how the issue is chosen (internal)

Energy Research Warehouse (ERW). Internal note: not published on the site (`site/scripts/build-content.mjs`, `INTERNAL_METHODS`). The readers' note for both periodicals is `docs/methods/periodicals.md`; this note is the working rule behind the Digest, with every number as the code holds it. Written by session 1995 of chain 228 (13 November 2026). The code: `warehouse/news/score.py` with `warehouse/news/rubric.md` (the scoring), `warehouse/news/brief.py` (the issue), `warehouse/analysis/findings/daily_chart.py` and `findings_scanner.py` (the chart). The faults that set the rules below: `docs/reviews/periodicals-faults-2026-11-05.md`.

## 1. The score of a story

- **Who scores.** A model, under the owner's key and the cost ledger (`warehouse/news/llm.py`), reads each ingested story once against the rubric and writes the scored fields to `news_stories`. A story is scored once; a rescore is the owner's.
- **Significance, 0 to 10**: how much the story changes what an informed energy professional believes about where the industry is going. 9 to 10 market-moving (an OPEC decision, a gigawatt deal, an LNG or nuclear final investment decision, a federal rule with industry-wide effect); 7 to 8 hundreds of MW or of millions of dollars, a major counterparty, a state rule, a notable price move; 4 to 6 incremental but real; 1 to 3 commentary and marketing; 0 not about energy (left out of every issue).
- **AI relevance** is a tag, never a credit: an AI or datacenter story is scored on the same energy consequences as any other.
- **The fields**: a sector, a region, a capacity in MW only when the text states MW, GW or kW (an energy unit such as GWh is refused), a price as written, the parties, a headline, and the why line: one sentence, the consequence, one fact the title lacks, no figure the title gives, no adjective of `docs/voice.md`'s list, no hollow verb.

## 2. The window and the ten

- **The window** opens at the previous issue's end, read from its first line's "for the N hours to <time> UTC" (`brief.STAMP_END`), and is capped at `WINDOW_CAP_HOURS` = 96; with no earlier issue it is `DEFAULT_HOURS` = 24. A story dated after the run waits for the next issue.
- **Clusters**: the stories of one event are one cluster; a cluster is ranked by its highest significance, then an event before commentary, then its number of outlets, then its time. AI relevance is no key.
- **One topic, one item**: a topic is the sector with the region; two price stories of one commodity are one topic; a sector holds at most `SECTOR_MAX` = 2 items of the ten; the rest of a topic folds under its item ("Also on this topic", "Also in <sector>").
- **Not again**: a cluster an earlier issue printed (by headline or link) is left out.

## 3. The opening number (`brief.opening_number`)

1. A move must pass its bar (`MATERIAL_PCT`): 3 percent for a benchmark's close (Henry Hub, WTI, Brent), 10 percent for a hub's day-ahead mean; yesterday's opening metric needs twice its bar; a move no story names needs `UNNAMED_FACTOR` = 1.5 times it.
2. Consequence first: a move a story of the day names (`brief.price_named`, by `PRICE_WORDS` and, since 13 November, an oil or crude headline that settles, rises, falls, jumps or slips: `brief.names_price`) scores 2, a benchmark 1 more. A story first reported more than `REASON_LAG_DAYS` = 3 days after the move's day neither names nor explains it (since 13 November, row 149).
3. Novelty second, source quality third, the size of the move last.
4. With no named move and no benchmark past its bar, the day's highest-ranked story stating a MW or a sum leads, said to be the outlet's figure; a single hub no story names is the last resort.
5. A benchmark's close no later than the one the last issue printed (`brief.previous_closes`, read from that issue's "- <label>: ... on <date>" lines) never leads: EIA publishes a close from one day to about a week after its day, so one close can be the newest on several issues running. When such a close passed its bar, the opening names it instead of saying no price moved ("Henry Hub natural gas's rise on 2026-11-03 (in the numbers below) was in the last issue"). Since 13 November (faults file row 146).

## 4. The numbers block (`brief.numbers_block`)

- **Market price**: the best candidate the opening did not take, a move of 0.0 percent after every move (since 13 November). A close the last issue printed says so in its status, in place of "the newest EIA had published": "the same close the last issue printed (no newer close is held)" (row 148).
- **Physical**: US48 demand's peak hour against the same weekday a year before, or a week before while the year is not held.
- **Project or capacity** and **policy, capital or reliability**: the highest-ranked stories of the whole issue stating a MW or a sum, the measure named by the sector, or "dispatched" when the headline says the power was dispatched (since 13 November); never a price story.
- **What moved most**: the moves of 0.05 percent or more, at most `MOVERS_N` = 5, the heading counting them; the unchanged prices on one line with no figure (since 13 November).

## 5. The chart of the day

The scanner's flags and the watch list, most related to the day's top stories first (`daily_chart.relevance`), then records and first negatives, then strength; a flag past `STRENGTH_CAP` = 50 robust standard deviations is a step from zero and never the chart. The line that ties the chart to a story is printed only when the shared words name the measure (a state, a grid, or a fuel and one more word: `daily_chart.names_measure`, since 13 November).

## 6. What changed on 13 November 2026 (chain 228, rows 79 to 92)

- The opening names the single hub's move it passed over, instead of "No price moved enough to lead" (row 79).
- The market row is never a price that did not move; an oil headline that settles names the crude benchmarks (row 80).
- EIA's closes: the row names the trading day; the lag is said to run from one day to about a week; "1 day" (row 81).
- "Storage dispatched", not "Storage capacity", for power dispatched (row 82).
- Outlets by name: "JPT", not "JPT Homepage"; "CA.gov" (row 83).
- No "parties:" line repeating the headline; "Also named:" for the rest; beside a figure the field stays, since the Roundup reads it (row 84).
- A policy action whose why line fails closes on its bracket (row 85); the publisher's sums in the money style (row 86).
- The scanner's "record until now" is the highest value before the new point, fresh points included, with the held record kept beside it (row 87; `docs/methods/automated_analysis_scanner.md`).
- The chart's tie to a story only when it names the measure (row 88).
- The subject: the top story's headline with no figure when a story's figure opens (row 89).
- The first line: "for the 96 hours to <end> UTC (the window opened <start> UTC): N scored stories", with "the first issue since <date>" after a gap of more than a weekday (row 90).
- A mover is never dropped for its reason's link; an unchanged price is no largest move (rows 91 and 92).

## 7. What changed later on 13 November 2026 (chains 232 to 244, rows 104 to 130)

- A story names a price's move only when its direction words do not contradict it (row 104: rise words beside a fall, or fall words beside a rise), and a story of another gas market (euros, the EU, TTF, Asia) names no move of Henry Hub's (row 115); a natural gas headline that rallies or falls names Henry Hub (row 110). A naming story's line or title that states a sum of its own is passed over (row 126).
- The block's key names the story each figure came from, not the cluster's id (row 107).
- The block's measure: "Deals in total" for a total of many deals (row 112), "Combined company value" only when the headline's sum stands before the company it describes (rows 123 and 124); the outlet once when no party is named (row 111).
- A party is named by its name, its initials ("DOE"), its singular ("Houthi"), its distinctive first word ("Saudi"); a description ("US regulator", "unnamed hyperscaler") is never printed as a name (rows 84, 113, 128). Beside a figure the field reads "Parties:" (row 130).
- The first line says when the window holds few stories or many unscored ones, counts only (row 114); thousands carry their separator (row 117).
- No en dash from a publisher's title (row 119); a refining or road-fuel title is oil's and a gas price title with a verb is gas's, whatever power tag the scorer gave (rows 120 and 125); sector codes print as "LNG", "PPA" (row 127).
- The emails drop a gated pointer link with its clause (row 105).
