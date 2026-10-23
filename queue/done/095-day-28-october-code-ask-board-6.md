# Chain of 28 October 2026: sessions 1307 to 1313, code machine (old laptop), unattended: Ask and the price board, sixth pass

machine: samueloldlaptop

Seven sessions for the old laptop (`samueloldlaptop`, C:\Users\lossa\Documents\erw), written by session 1300 at the start of chain 093 (`queue/done/093-day-27-october-code-ask-board-5.md`, sessions 1300 to 1306), to be updated by session 1306 from that chain's results. Numbered 095: 094 is the data machine's. Session numbers 1307 to 1313, the first free after chain 093's. Model: Opus 5.5, high effort. Goal: what chains 089 and 093 leave on Ask and the board. Nothing here waits for a ruling: no page's default figure moves, no held grid's rows are drawn, nothing goes public, no warehouse data is written.

**The next file is written first.** Session 1307 begins by reading `queue/next/` and writes this chain's successor there (`machine: samueloldlaptop`, at least five sessions, real work only, no ruling needed), its session numbers the first free ones it finds in `archive/sessions/` and every `queue/` file, commits it alone and pushes it to main with the snapshots before any other work. Session 1313 updates it. A session that finds its part done or blocked says so in two lines and moves on.

Read first: chains 089's and 093's notes (`docs/state/review_2026-10-27_code_ask_board.md`, `review_2026-10-28_code_ask_board.md`), `docs/methods/ask.md`, `docs/methods/price_board.md`, `docs/reviews/ask-board-rulings-2026-10-23.md`. Files this chain owns: as chain 085's.

## Rules for every session

As chain 085's, section "Rules for every session", word for word, with this chain's numbers (a build only with 3 GB of memory free; the build lock waited for at most 20 minutes; a landing's check-values failures read against production's; the snapshots before and after every push to main, each as its own command; model spend USD 0 except session 1307's item 2, cap USD 2.50).

## Session 1307: the next file, then what chain 093 left

Long end 2:00. First the next file. Then every item chain 093's sessions left under "To finish", in order, each said in the report; a landing that waited for memory first. Updated by session 1306 (`docs/state/review_2026-10-28_code_ask_board.md`), they are:
1. **Land `wip/1300-ask`** (chain 089's `wip/1190-ask` is in it: sessions 1190 to 1195 and 1300 to 1305), when 3 GB are free: merged with main, `python scripts/land_check.py --ref wip/1300-ask --task 1190-1305-ask-board --port 3708`, check-values' failures read against production's; on the same build `check-board.mjs` (with session 1193's check of the held lines), `check-links.mjs` with `CHECK_LINKS_PAGES=/board,/ask`, the board at 390 and 1280 with a held line closed and opened (`docs/brand/review-1307/`), and the keyboard walk of the board (chain 093's session 1303: the filters, a held line's toggle and its `aria-expanded`, the focus order, a row into the workbench); snapshots before and after.
2. **The second set's rest** (chain 093's session 1302) on the same build's server: `eval_s1133_s1114_run.json` read first so the asking goes on at t09, the keys computed again the same hour; spend cap USD 2.50 for this item only; `docs/reviews/ask-sixty-2026-10-25.md` extended, `warehouse/chat/eval/history.py`'s row brought to the whole set, `replay.py` and `refusals.py` written again.
3. **Chain 085's after snapshot**, once production carries `1ccf3c5e` or later.
4. **The board's new rows**, once a daily run's `board` step has built them (089's session 1192).

## Session 1308: the stored answers' replay in the gate

Long end 1:30. Spend USD 0. Chain 093's session 1301 replays the stored answers through today's checks with no model: its script run by `scripts/land_check.py` as a step of its own (after the suite, before the build), its failure a gate failure, with a test; `docs/methods/ask.md` says so.

## Session 1309: the site's checks on the stored answers

Long end 2:00. Spend USD 0. Changed by session 1306: chain 093's session 1304 found no refusal that is the loop's to fix (`docs/reviews/ask-refusals.md`). Instead: the site's number check, unit check and citations (`site/lib/chat/ask.ts`) run over the same stored answers `warehouse/chat/eval/replay.py` reads (157 on 23 October), each answer's verdict held equal to the Python checks' by a test, every difference said with its cause and fixed on the side that is wrong.

## Session 1310: Ask's panel and form at phone width

Long end 1:30. Spend USD 0. The Ask panel and the general form at 390 and 1280 on a build, with a stored answer drawn by a test page under the internal view or a fixture route that makes no model call (or, if none can be made without a model call, the empty form and the conversation's controls): the read lines, the sources, the nearest tables and the series' table wrap with no page scroll; each fault fixed. Screenshots under `docs/brand/review-1310/`.

## Session 1311: the board's CSV beside the held lines

Long end 1:00. Spend USD 0. The rows' CSV (`/board/rows`, session 1137) and the held lines of session 1193 say the same: a held grid's rows in the CSV each carry no figure and the hold's words, their count by grid in the header, as the page's lines count them; a test on the site's own file.

## Session 1312: the method notes and the rulings list

Long end 1:00. Spend USD 0. `docs/methods/ask.md`, `docs/methods/price_board.md` and the rulings list brought to this chain's work, dated. They land with the chain's code, or alone if it has none on a branch.

## Session 1313: the note, the next file updated, and the queue

Long end 1:00. Spend USD 0. `docs/state/review_2026-10-29_code_ask_board.md`; the successor file updated, committed and pushed to main; then `python scripts/chain_queue.py next` (taking this machine's own successor by name when the lowest file waiting is another chain's that is still running, as session 1141 did).
