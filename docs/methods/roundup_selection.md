# The Weekly Roundup: how the week is selected (internal)

Energy Research Warehouse (ERW). Internal note: not published on the site (`site/scripts/build-content.mjs`, `INTERNAL_METHODS`). The readers' note is `docs/methods/periodicals.md`; this note is the working rule behind the Roundup, with every number as the code holds it. Written by session 1996 of chain 228 (13 November 2026). The code: `warehouse/news/roundup.py`, with the Digest's scoring and clustering from `warehouse/news/brief.py` (`docs/methods/digest_scoring.md`). The faults that set the rules below: `docs/reviews/periodicals-faults-2026-11-05.md`.

## 1. The week

- An ISO week, Monday to Sunday UTC, written on Sunday at 23:00 UTC (`.github/workflows/roundup.yml`). The masthead says how far the stories and the tables reach when they stop short of the week's end (row 59), and the weekend line says when no story of Saturday or Sunday is held (row 60).
- The stories are the week's scored stories, clustered and ranked as the Digest ranks them.

## 2. The opening number (`roundup.opening_number`)

In order, the first that holds: a benchmark's close a week apart that moved `WEEK_FUEL_PCT` = 3 percent or more and that a story of the week names; the deal of the week at `DEAL_USD_MIN` = USD 1 billion or more; the largest datacenter load first reported in the week at `DC_MW_MIN` = 500 MW or more; the top story's structural figure; an unnamed benchmark at 4.5 percent (`UNNAMED_FACTOR` = 1.5); a hub's weekly mean at 10 percent; the US48 peak. Its status is said: observed, calculated, or reported. A benchmark's newest close dated before the week began is no move of the week: the fuel table prints it, marked "EIA's newest close is from before this week, so this is no move of the week", and the opening, the subject and the five numbers do not use it (since 13 November, faults file row 147).

## 3. The week in five numbers (`roundup.five_numbers`)

- The price move of the week (the largest of the main hubs' complete weekly means and EIA's closes a week apart; a grid held for license or paused is never one); the US48 peak with its hour and the hours held; the deal of the week by US dollars, by MW when none states dollars; the largest datacenter load first reported in the week; the chart of the week's figure.
- The deal and the datacenter rows read `energy_deals` and `datacenter_projects` at the tables' own floor, `ROW_CONFIDENCE` = 0.7 (row 52). The deal row names the outlet its sum was read from (row 96).
- A category with nothing stands in, in order: a capacity the week's stories name and EIA-860M lists (row 68), a policy action, then the next price move not yet among the five that passes the opening's bar, 3 percent for a benchmark and 10 percent for a hub; with none, the row says no other price moved that much (row 97).

## 4. What mattered

- `WHAT_MATTERED_N` = 3 developments, first reports before a step in a deal an earlier issue or `energy_deals` already holds (row 63).
- Each with its why line when it passes the Digest's check, and what the evidence does not establish, from the record alone: the outlet's figure, or what a warehouse table holds instead (EIA-860M's plant, row 64; the benchmark's close in the week's fuel table, row 98); no party named (not asked of a market move); no capacity or sum stated; one outlet so far; an analysis piece. Nothing when every field is stated.

## 5. More

The weekend's stories, the five stories of the week, the deals and datacenter tables (confidence 0.7 or more and an operator, a site or MW, US first, at most 15), the policy of the week, and the numbers in full. A grid held for license prints "licensed source needed" in the weekly table, and its real-time table is not read for the week's highest price (row 93); a paused grid says its pause.

## 6. The subject

"ERW Weekly | <move> on the week; <headline clause>" when the opening is the week's move; else the headline's clause. The clause never carries a figure (a figure only when it is a warehouse table's), is cut at a word to 70 characters with no "...", and a cut does not split a name (rows 62 and 95).

## 7. What changed on 13 November 2026 (chain 228, rows 93 to 99)

- The weekly table and the real-time maximum hold a grid held for license (row 93); the page holds the held cells of the stored W44 and W45, which printed NYISO's and ISO-NE's weekly means (row 94: `holdRoundupGrids` in `site/lib/digest.ts`).
- The subject carries no outlet figure in any case (row 95).
- The deal row names the outlet of its sum (row 96).
- A stand-in move passes the opening's bar and is the next unused one (row 97).
- A story naming a benchmark is given the warehouse's close (row 98).
- One colon in the deal opening's status (row 99).

## 8. What changed later on 13 November 2026 (chains 232 to 244, rows 100 to 130)

- The opening asks the week's stories, not only the printed ones, whether one names a benchmark's move (row 110): W46 opens on Henry Hub's 14.1% rise with its reason where it opened on a deal. The move carries the naming story's line ("Reason, from the week's stories: ..."), else its title ("Named in the week's stories: ..."), only when the story's direction agrees and it states no sum of its own (rows 101, 104, 126).
- The masthead names the real-time tables' reach (row 100). The deal's financing words: "an investment in", "a loan for" (rows 103 and 121).
- The datacenter load row says how many larger loads of the week it leaves out for naming no operator or site (row 118).
- Each list of More is numbered from 1 (row 122); the subject's cut goes back to a comma (row 116).
- The page holds a held grid's real-time line and summary sentence in stored issues (W39 to W44), as well as its table cells (row 108).
- The fun fact repeats the week's newest Digest fact by design; a fact of the Roundup's own is the owner's to rule on (row 109).

## 9. What changed on the evening of 13 November 2026 (chains 252 and 254, rows 152, 157, 161, 162, 165 and 172 to 174)

- The real-time line's helpers (`rt_when`, `interval_words`, `ZONE_WORDS`) live in `brief.py`, which the Digest's line uses too (row 152); the Roundup's words are unchanged.
- The subject's cut goes back to before a phrase it would cut inside (row 157, `phrase_back`).
- The five's deal of the week is always in the Deals table, in place of the last row otherwise shown (row 161).
- The five's datacenter load counts a developer as naming the facility, as the table does since row 150 ("1,400 MW, CDC (developer), Kemps Creek, Australia"), names a country other than the United States, and "1 larger load ... names" (row 162).
- The subject's figure goes with its quantity words and a capacity with its "of"; a percent is a figure (row 165).
- A subscriber's topics read the v2 Roundup's What mattered and its five stories (row 172).
- Next week's empty line speaks of the week ahead, not this week (row 173).
- A story that names a benchmark is given the close of its own trading day against the close before it, when the week's closes hold it; else the week's pair (row 174).
