# The old laptop's chat chain: the evaluation finished, and the week's new tables (chain 280, 14 November 2026)

Energy Research Warehouse (ERW). Written by session 6113 of chain 280 (`queue/done/280-day-14-november-oldlaptop-ask.md`, sessions 6100 to 6129, samueloldlaptop, Fable high). This machine never builds and never lands. The work is on `wip/6100-ask`, landing row 14 of `docs/state/landing_request_oldlaptop.md`. The full record is `docs/reviews/ask-eval-2026-11-13.md`; the report `archive/sessions/SESSION_6100_6129_REPORT.md`.

- **For a reader of the chat:** it still states no number it did not fetch. In 260 answers asked today, none that reached a reader held a number in no tool result.
- **Steps 1 and 2 are done**, step 3 is asked once and fixed in part, step 4 is written. **Step 5 (the fresh read for three audiences) is not begun**: the chain's USD 20 was spent on the askings. It is the next chain's, file 281.
- **The week's new tables cannot be read by a visitor's chat.** That is the repository's own rule, not a fault: the three large-load research tables' license verdict is unsettled, and the forecast tool's parameters are not loaded. A visitor's chat refuses them, rightly. Read through their own files, the chat answers 57 of 58 questions about them right.
- **Model spend: USD 19.3211 of the chain's USD 20**, no session over USD 2, each estimate written before its asking.

## The scores, before and after, by class

Before: the chat as chain 256 left it, asked on 14 November. After: the same questions' classes asked again on the mended chat. Every count is from the stored runs (`warehouse/chat/eval/class_scores.py`).

| Set | Asked | Correct | Correctly refused | Unsupported number | Wrong | After the fixes |
|---|---:|---:|---:|---:|---:|---|
| The platform set, whole | 134 | 85 | 47 | 0 | 2 | 85, 49, 0, 0 |
| The investor's twenty, the site's loop | 20 | 10 | 9 | 1 | 0 | 11, 9, 0, 0 |
| The lab's twenty, the site's loop | 20 | 13 | 6 | 0 | 1 | 13, 7, 0, 0 |
| The new tables, read through their own files (the Python loop) | 58 | 44 | 13 | 0 | 1 | not asked again yet |
| The new tables, as a visitor's chat meets them today (a slice) | 6 | 0 | 6 | 0 | 0 | not asked again yet |

- **The one "unsupported number" was not one.** The loop refused a right answer because it named a percentile in words ("the 75th percentile") and 75 stood in no result as a number. Fixed.
- **Cost by set:** USD 10.2752, 1.7279, 1.1061, 3.4898 and 0.9162; USD 1.8059 for the 22 questions asked again.

## Faults closed, each with its test, in both loops

| Fault | Found by | Where it is |
|---|---|---|
| A refusal went on to state a fetched figure of something else | pw13 | row 14 |
| An answer after a table refused for a license said so in other words | pj08 | row 14 |
| A percentile named in words was read as a number in no result, and a right answer became the fixed refusal | iv14 | row 14 |
| An answer reached the reader cut off in the middle of a sentence | l02 | row 14 |
| A refusal after a held table said only "not in the warehouse" | l02 | row 14 |
| Describing a large-load table returned 80 to 90 KB of prose | found with no model | row 14 |
| The evaluation's runner died at exit on this machine and graded nothing | found before the first paid call | row 14 |
| A call that named a table of the record the catalogue does not list was answered "no public table named" | the visitor's slice | row 14, not yet asked with a model |

- Three keys or graders were at fault and are corrected: a held grid answered from another publisher's public table (pj08, the rule `hold_public_table`); a bill's number read as a figure (lw09); a pinned status of pj08 (`tests/test_session5260_ask.py`).

## Open, for the next chain (file 281)

1. **A period outside an events table's span is answered as a count of zero** (ch09: "The warehouse holds 0 rule changes dated March 2026 ... its first change is dated 2026-08-18"). Honest, and not the refusal rule 3 asks for. The mend: the query tool says when a bounded period lies outside the table's own span, as it says for a series' window. Then ask the class again.
2. **The visitor's chat spends 12 calls looking for a table it cannot list** (3 of 6), and once made a claim from a neighbour table ("No large-load rule has the status denied", said of a table of statements). The tools now name such a table and the list's note says how to answer; not yet asked with a model. Ask the slice again and the 52 questions not yet asked through the site's loop (about USD 4.50).
3. **Step 5:** a fresh read of the replies for the trader, the developer and the AI lab, 20 questions each (about USD 5), faults fixed the same way.
4. **The method note** (`docs/methods/ask.md`) carries today's scores; add the next chain's.

## For Samuel's ruling (each with its default)

1. **The three large-load research tables' license.** `license_status.json` says public, `table_verdicts.json` and the chat's briefing say unsettled. While unsettled the chat cannot read them and refuses. **Default: the data machine's of chain 267, public and out of release v1**; then they are loaded and the chat answers (data request row 3 of `docs/state/data_requests_ask.md`).
2. **Berkeley Lab's queue table for a held grid's region** (P3's ruling 9, met again by pj08). The chat says ISO-NE's own table is license needed and gives Berkeley Lab's figure, named as Berkeley Lab's. **Default: as the license file says, allowed.** To reverse: the tools leave a held grid's region out of that table, and the grader's rule `hold_public_table` is dropped.
3. **`deal_counterparties` is public and built from the held `energy_deals`.** Asked about a held deal, the chat already names it as the other table that could answer. **Default: not loaded until you say** (data request row 4).
4. **"policy_actions: license needed, so no figure of it is given here."** The loop now puts that sentence before any answer written after a table was refused for a license, also when the question was about something else and the chat only touched the held table on its way. True, and sometimes beside the point. **Default: kept**; the alternative is to say it only when the answer names the table.

## For the data machine

- `docs/state/data_requests_ask.md`, six rows: load `forecast_tool_parameters` and `iso_reserve_margin_reports`; the research tables after the ruling; `deal_counterparties` after the ruling; the two license files; a row count.
- **The platform set's pj10 will change key** the day `forecast_tool_parameters` is loaded (it asks the cost of a combined-cycle plant, keyed "not in the warehouse").

## Not done, and why

- **No build, no type check, no lint, no whole suite**: this machine's rule. Four TypeScript files changed and one is new; the gate's build is the first. Node ran them with types stripped, and both loops agree on 22 scripted scenarios.
- **The mends of session 6113 have not met a model**: the chain's budget was spent. They are held by tests that ask the tools with no model.
- **The whole new set was not asked through the site's loop**: 6 of 58, enough to see the class and its cost.
