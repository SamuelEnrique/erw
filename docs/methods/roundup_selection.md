# The Weekly Roundup: how the week is selected (internal)

Energy Research Warehouse (ERW). Internal note: not published on the site (`site/scripts/build-content.mjs`, `INTERNAL_METHODS`). The readers' note is `docs/methods/periodicals.md`; this note is the working rule behind the Roundup, with every number as the code holds it. Written by session 1996 of chain 228 (13 November 2026). The code: `warehouse/news/roundup.py`, with the Digest's scoring and clustering from `warehouse/news/brief.py` (`docs/methods/digest_scoring.md`). The faults that set the rules below: `docs/reviews/periodicals-faults-2026-11-05.md`.

## 1. The week

- An ISO week, Monday to Sunday UTC, written on Sunday at 23:00 UTC (`.github/workflows/roundup.yml`). The masthead says how far the stories and the tables reach when they stop short of the week's end (row 59), and the weekend line says when no story of Saturday or Sunday is held (row 60).
- The stories are the week's scored stories, clustered and ranked as the Digest ranks them.

## 2. The opening number (`roundup.opening_number`)

In order, the first that holds: a benchmark's close a week apart that moved `WEEK_FUEL_PCT` = 3 percent or more and that a story of the week names; the deal of the week at `DEAL_USD_MIN` = USD 1 billion or more; the largest datacenter load first reported in the week at `DC_MW_MIN` = 500 MW or more; the top story's structural figure; an unnamed benchmark at 4.5 percent (`UNNAMED_FACTOR` = 1.5); a hub's weekly mean at 10 percent; the US48 peak. Its status is said: observed, calculated, or reported.

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
