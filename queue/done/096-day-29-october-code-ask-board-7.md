# Chain of 29 October 2026: sessions 1314 to 1319, code machine (old laptop), unattended: Ask and the price board, seventh pass

machine: samueloldlaptop

Six sessions for the old laptop (`samueloldlaptop`, C:\Users\lossa\Documents\erw), written by session 1307 at the start of chain 095 (`queue/done/095-day-28-october-code-ask-board-6.md`, sessions 1307 to 1313), to be updated by session 1313 from that chain's results. Numbered 096: 094 is the data machine's. Session numbers 1314 to 1319, the first free after chain 095's. Model: Opus 5.5, high effort. Goal: what chains 093 and 095 leave on Ask and the board. Nothing here waits for a ruling: no page's default figure moves, no held grid's rows are drawn, nothing goes public, no warehouse data is written.

**The next file is written first**, from a worktree of main (never from a branch that holds code not yet landed). Session 1314 begins by reading `queue/next/` and writes this chain's successor there (`machine: samueloldlaptop`, at least five sessions, real work only, no ruling needed), its session numbers the first free ones it finds in `archive/sessions/` and every `queue/` file, commits it alone and pushes it to main with the snapshots before any other work. If what is left of Ask and the board is only work that needs a build, and three chains in a row could not build for memory, the successor is not written: the session says so under "For Samuel's ruling" instead. Session 1319 updates it. A session that finds its part done or blocked says so in two lines and moves on.

Read first: chains 093's and 095's notes (`docs/state/review_2026-10-28_code_ask_board.md`, `review_2026-10-29_code_ask_board.md`), `docs/methods/ask.md`, `docs/methods/price_board.md`, `docs/reviews/ask-board-rulings-2026-10-23.md`. Files this chain owns: as chain 085's.

## Rules for every session

As chain 085's, section "Rules for every session", word for word, with this chain's numbers (a build only with 3 GB of memory free; the build lock waited for at most 20 minutes; a landing's check-values failures read against production's; the snapshots before and after every push to main, each as its own command; model spend USD 0 except session 1314's item 2, cap USD 2.50, and session 1316, cap USD 1).

## Session 1314: the next file, then what chain 095 left

Long end 2:00. First the next file. Then every item chain 095's sessions left under "To finish", in order, each said in the report; a landing that waited for memory first. Updated by session 1313 (`docs/state/review_2026-10-29_code_ask_board.md`), they are:
1. **Land `wip/1307-ask`** (chains 089, 093 and 095: sessions 1190 to 1195, 1300 to 1305, 1307 to 1312), when 3 GB are free: merged with main, `python scripts/land_check.py --ref wip/1307-ask --task 1190-1312-ask-board --port 3708` (its new step `ask_replay` included), check-values' failures read against production's; on the same build `check-board.mjs`, `check-links.mjs` with `CHECK_LINKS_PAGES=/board,/ask`, the board at 390 and 1280 with a held line closed and opened, the board's keyboard walk (chain 093's 1303), Ask's panel and the general form at 390 and 1280 (chain 095's 1310), under `docs/brand/review-1314/`; snapshots before and after.
2. **The second set's rest** (chain 093's 1302) on the same build's server, cap USD 2.50 for this item: `eval_s1133_s1114_run.json` read first, the keys computed again the same hour; the review, the history, the replay and the refusals written again.
3. **Chain 085's after snapshot**, once production carries `1ccf3c5e` or later.
4. **The board's new rows**, once a daily run's `board` step has built them.

## Session 1315: one list of the evaluation's runs

Long end 1:30. Spend USD 0. `warehouse/chat/eval/history.py`, `replay.py` and `refusals.py` each keep their own list of the stored runs. One file (`warehouse/chat/eval/runs.json`: each run's file, its grades and how a grade says right, its label, its day's call limit) read by the three, with a test that every run or grades file in the folder is in it or named there as left out, and the three documents written again unchanged.

## Session 1316: the board's five questions asked

Long end 1:30. Spend cap USD 1. On a build (3 GB free first), the five questions of `warehouse/chat/eval/questions_s1122.yaml` asked through `/api/ask` as an evaluation, their keys computed again from the live set the same hour (`expected_s1122.py` reads recorded rows: the keys of the hour, from the board's tables read with the anon key, beside them), graded; `docs/reviews/ask-board-questions.md`; the run in the history, the replay and the refusals.

## Session 1317: the general chat's chart in the Python loop

Long end 1:30. Spend USD 0. Since session 1142 the site's general chat returns the series an answer rests on (`site/lib/chat/generalseries.ts`); the Python loop records series only for a profile. The same in `warehouse/chat/ask.py` for the general chat, held equal to the site's by a scenario added to session 1300's turn-by-turn test.

## Session 1318: the method notes and the rulings list

Long end 1:00. Spend USD 0. `docs/methods/ask.md`, `docs/methods/price_board.md` and the rulings list brought to this chain's work, dated. They land with the chain's code, or alone if it has none on a branch.

## Session 1319: the note, the next file updated, and the queue

Long end 1:00. Spend USD 0. `docs/state/review_2026-10-30_code_ask_board.md`; the successor file updated, committed and pushed to main from a worktree of main; then `python scripts/chain_queue.py next` (taking this machine's own successor by name when the lowest file waiting is another chain's that is still running, as session 1141 did).
