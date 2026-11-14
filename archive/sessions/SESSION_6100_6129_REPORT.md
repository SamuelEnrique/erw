# Sessions 6100 to 6129 report: the AI chat over the warehouse, its evaluation finished (chain 280, samueloldlaptop)

14 November 2026, 18:49 to about 20:10 UTC. Chain file `queue/done/280-day-14-november-oldlaptop-ask.md`, written from the owner's instruction of the day and taken by name at about 18:52 UTC. Model: Fable, high effort. Branch `wip/6100-ask`, worktree `C:\Users\lossa\Documents\erw-6100`, cut from `origin/main` at `ade7b6245`. Sessions 6100 to 6113 used; 6114 to 6129 not used (the chain's USD 20 was spent on the askings).

## Read these first

- **Steps 1, 2 and 4 are done. Step 3 is asked once and fixed in part. Step 5 is not begun**: it is the next chain's (`queue/next/281-day-15-november-oldlaptop-ask-continued.md`, written with what is left).
- **The chat states no number it did not fetch.** 260 answers asked today; none that reached a reader held a number in no tool result. The loop's own check sent 12 first drafts back before a reader saw them: 11 came back right, and one (iv14) ended in the loop's fixed refusal over a percentile's name, since mended.
- **The scores by class, before and after the fixes** (correct, correctly refused, unsupported number, wrong): the platform set's 134: 85, 47, 0, 2, then 85, 49, 0, 0. The investor's twenty: 10, 9, 1, 0, then 11, 9, 0, 0. The lab's twenty: 13, 6, 0, 1, then 13, 7, 0, 0.
- **The week's new tables cannot be read by a visitor's chat, and that is the repository's own rule.** The three large-load research tables' license verdict is unsettled; `forecast_tool_parameters` is public and not loaded. A visitor's chat refuses them, rightly (6 of 6 asked). Read through their own files the chat answers 57 of 58 new questions right.
- **Two license files disagree on eight tables** (the large-load family and `usace_nid_dams`): public in `site/data/license_status.json`, unsettled in `site/data/table_verdicts.json`. For Samuel's ruling.
- **Model spend: USD 19.3211 of the chain's USD 20.** No session over USD 2; each estimate written before its asking; the site's ledger, read whole, agrees with the run files to the cent.

## What to review

- `docs/state/note_2026-11-14_oldlaptop_c280.md`: the scores, what is open, the four rulings asked.
- `docs/reviews/ask-eval-2026-11-13.md`, the three sections of chain 280: the whole set in four classes; the investor's and the lab's twenty; the week's new tables.
- `docs/methods/ask.md`, "The evaluation finished, in four classes": step 4.
- No page changed. `/api/ask` answers differently in the five ways listed under session 6107 to 6113 once row 14 lands.

## Session 6100 (18:49 to about 18:53 UTC): chain 277 closed, the queue, the ground

- **Chain 277 closed in its report** (`archive/sessions/SESSION_6092_6105_REPORT.md`, "Closed"): session 6092 alone used; 6100 to 6105 pass to this chain; the periodicals file 300 stays on hold.
- **Queue:** file 280 written, committed alone, pushed, taken by name. File 281 (sessions 6130 to 6159) written first by this session, committed alone, pushed.
- **Numbers:** 280 and 281 free on origin's main and all 506 remote branches; sessions 6106 to 6199 named by nothing; 6100 to 6105 by chain 277's file alone.
- **Precheck** passed. No freeze (`scripts/freeze.py status`, exit 0). Role: code.
- **Row 32 had landed** (`origin/wip/5200-ask-close` an ancestor of `origin/main`), so `wip/6100-ask` is cut from `origin/main`.
- **Keys:** `platform_questions.py --check`, `investor_questions.py --check`, `lab_questions.py --check`: exit 0 each.

## Sessions 6101 to 6107: step 1, the whole set

| Session | Estimate before | Asked | Actual |
|---|---|---:|---|
| 6101 | at most USD 2.00, about 24 questions from pw01 | 25 | USD 1.7927 |
| 6102 | at most USD 2.00, about 25 from pr13 | 31 | USD 1.9153 |
| 6103 | at most USD 2.00, of 78 due | 25 | USD 1.9142 |
| 6104 | at most USD 2.00, of 53 due | 22 | USD 1.7983 |
| 6105 | at most USD 2.00, of 31 due | 22 | USD 1.8483 |
| 6106 | about USD 0.90 for the last nine, cap USD 1.50 | 9 | USD 1.0065 |
| 6107, the two classes again | about USD 1.10 for 14, cap USD 1.50 | 14 | USD 1.3021 |

- **The whole set cost USD 10.2752** (P3 estimated about USD 9): USD 0.077 a question.
- **pw13, a refusal that states a figure:** both loops send such a draft back once. Of 134 stored refusals only pw13 stated one.
- **pj08, a held table said in other words:** both loops put "license needed" before an answer written after a table was refused for a license. Its figure came from Berkeley Lab's public table, which the license file allows: the grader's rule `hold_public_table`.
- **A fault of the runner, found before the first paid call:** it died in `process.exit()` on this machine after a clean dry run (exit 127) and would have graded nothing. Mended.

## Sessions 6108 to 6110: step 2, the investor's twenty and the lab's twenty through the site's loop

| Session | Estimate before | Asked | Actual |
|---|---|---:|---|
| 6108, the investor's twenty | about USD 1.50, cap USD 2.00 | 20 | USD 1.7279 |
| 6109, the lab's twenty | about USD 1.50, cap USD 2.00 | 20 | USD 1.1061 |
| 6110, the two classes again | about USD 0.60 for eight, cap USD 1.00, then USD 0.20 more for three the first caps left out | 8 | USD 0.5038 |

- **iv14, a percentile's name:** the chat had the figure; "the 75th percentile" was read as a number in no result and the reader got the fixed refusal. An ordinal before "percentile" is now that percentile's name when a tool names it.
- **l02, an answer cut in the middle of a sentence:** such a draft is sent back once; a refusal after a held table carries the hold's words.
- **My caps for two re-askings were under the runner's own reserve** (USD 0.30): three questions were not asked at the first try and were asked at the second. No money lost.

## Sessions 6111 to 6113: step 3, the week's new tables

| Session | Estimate before | Asked | Actual |
|---|---|---:|---|
| 6111, the Python loop over the tables' files | one question, about USD 0.05; then at most USD 2.00 | 28 | USD 1.7600 |
| 6112, the same, the rest | about USD 1.90 for 30, cap USD 2.00 | 30 | USD 1.7298 |
| 6113, the site's loop, a visitor's chat today | about USD 0.90 for 13 named, cap USD 1.20 | 6 | USD 0.9162 |

- **A new set, 58 questions** (`questions_newtables.yaml`, builder `scripts/ask_eval/newtables_questions.py`), keys from the tables' own files; 14 must be refused. Keyed a second time as a visitor's chat can answer on the day (`questions_newtables_live.yaml`).
- **Through their own files: 57 of 58.** The one wrong, ch09: a month outside the table's span answered "0 rule changes". Open.
- **A visitor's chat: 6 of 6 refused rightly; three took 12 tool calls.** One made a claim from a neighbour table. The tools now name a table of the record the catalogue does not list; not yet asked with a model.
- **Found with no model:** describing a large-load table returned 80 to 90 KB of prose. Now 7 to 10 KB, in both loops.
- **The six tables were restored to this machine's working files** by `scripts/sync.py --tables` (the archive; local files only, no data lock). Two more that landed (`ferc714_forecast_growth`, `ferc714_planning_area_forecasts`) are on no copy this machine can read.

## Step 4: the method note

- `docs/methods/ask.md`, "The evaluation finished, in four classes (14 November 2026, sessions 6101 to 6113, chain 280)": the scores before and after by class, each change to the loops and to the grading, the measure taken before each rule.

## Checks run (exit codes read, none piped)

- Every test file that names a changed module or record, each in its own process: 71 files (`runs/s6113/sweep.out`). 68 passed at the first run; the 3 that failed pinned counts or source lines this chain moved on purpose (`test_session1147`: the history's rows; `test_session1304`: the refusals' classes; `test_session5276`: the line that gives a refusal its words). Each updated with its reason, all pass.
- Both loops turn by turn, 22 scenarios, equal (`tests/test_session1300.py`); four are this chain's.
- New: `tests/test_session6106_ask.py` (20), `test_session6108_ask.py` (9), `test_session6111_ask.py` (18), `test_session6113_ask.py` (13); under Node `test-ask-refused.test.mjs` (10), `test-ask-longtext.test.mjs` (4), `test-ask-6108.mjs`, `test-ask-6113.mjs`.
- `replay.py --check`: exit 0 (no right stored answer would now be sent back).
- No site build, no type check, no lint, no whole suite: this machine's rule. Four TypeScript files changed and one is new.

## Pushes to main and their snapshots

| Push | What | Before, after | Differences |
|---|---|---|---|
| `67fa9732d`, `ade7b6245` | chain 277's close, files 280 and 281, the queue move | `s6100-before`, `s6100-after` | 25 pages, 0 (expected) |
| `f137da39a` | landing row 14 | `s6107-before`, `s6107-after` | 25 pages, 0 (expected) |
| the last push of the chain | file 281's list, row 14 moved, the note, the data requests, this report | `s6113-before`, `s6113-after` | in the chain's last message |

## Decisions made without you

- **Sessions 6100 to 6105 used though chain 277's file names them**: your instruction says "sessions 6100 upward" and closes chain 277 first.
- **`wip/6100-ask` is cut from `origin/main`**: row 32 had landed, so there was nothing to stack on.
- **The day's cap for the asking was USD 30.72**: P3 had spent USD 10.72 of the same UTC day under the same ledger step, and this chain's USD 20 is its own.
- **pj08's key follows the license file** (P3's ruling 9, default "as the file says"). Reversible: drop the rule `hold_public_table`.
- **The new tables were asked through the Python loop over their own files**, since no visitor's copy holds them; and through the site's loop only as far as to show what a visitor gets.
- **The chain stopped asking at USD 19.32** and used its last sessions for tests and records. Step 5 and the re-askings of step 3 are written into file 281.
- **Older tests' pins were moved** where this chain's runs or lines changed what they count (four files), each with its reason beside the new value.
- **The report, the note and the data requests are also copied to main** (documents only), so that you and the data machine read them before row 14 lands.

## For Samuel's ruling (default in brackets)

- **The three large-load research tables' license**: public in one file, unsettled in the other; while unsettled the chat cannot read them. [the data machine's default of chain 267: public, out of release v1; then they are loaded]
- **Berkeley Lab's queue table for a held grid's region** (P3's ruling 9, met again by pj08). [as the license file says: allowed, and named as Berkeley Lab's]
- **`deal_counterparties` is public and built from the held `energy_deals`**; the chat already names it as the other table that could answer a deals question. [not loaded until you say]
- **The hold's sentence before an answer that only touched a held table on its way** ("policy_actions: license needed, so no figure of it is given here."). [kept]
