# Session 1126 report: the next file, then what chain 075 left

23 October 2026, 19:25 to 19:58 UTC, on samueloldlaptop, unattended, on `wip/1126-ask` (cut from `wip/1128-ask`, which holds chain 075's sessions and session 1128). Chain `queue/done/076-day-24-october-code-ask-board-2.md`. Model spend USD 5.73 through the evaluation's own ledger step (`site_ask_eval`), under the session's cap of USD 12 (chain 075's two askings, USD 6 each), the spend read back from the ledger before every question.

## Read these first

- `docs/reviews/ask-thirty-2026-10-23.md`: session 320's thirty asked again: **19 of 30** under the hold (17 on 20 October, 14 under the hold on 21 October), 30 of 30 if session 320's three rulings went the answers' way.
- `docs/reviews/ask-sixty-2026-10-23.md`: the second set: **24 of 30** at its first asking; four of the six wrong state the right figure from another table; two causes in the code for session 1127.

## What was done

- **The next file first**: `queue/next/085-day-25-october-code-ask-board-3.md` (sessions 1142 to 1149), numbered 085 so that chain 078 keeps 079; committed alone, pushed to main 19:26 UTC with snapshots `s1126-before` and `s1126-after`: 0 differences on 25 pages, expected (a queue file).
- **Chain 075's records on main**: the note `docs/state/review_2026-10-24_code_ask_board.md` and the updated 076 were pushed by session 1125 (snapshots `s1125-before`, `s1125-after`: 0 differences). The queue move of 076 (`32a5ef8a`) was pushed after with no before snapshot of its own; compared against `s1125-after`, taken minutes before with nothing else pushed between: `s1125-queue-after`, 0 differences.
- **The build**: the build lock was free at 19:28 and taken (`s1126`); 2.7 GB free. `wip/1128-ask` merged with main and built (`ERW_READ_TIMING=1`), exit 0, no database timeout; served on port 3713 with the visitor salt and the evaluation's ceiling raised for that server only.
- **Session 1113's asking**: the keys again (19:29 UTC, all equal to session 539's), b01 alone as a probe of the route and the ledger, then the thirty, then two faults found and **fixed the same hour** (`site/lib/chat/tools.ts`, test `site/scripts/test-ask-1126.mjs` and `tests/test_session1126.py`): (1) a compare naming a held grid crashed the loop (g08: session 1112's held answer has no `result`); (2) MISO's scoped chat answered as a held grid where its pause must refuse (g10). Rebuilt, served again, g08 and g10 asked again, graded: 19 of 30 under the hold.
- **Session 1114's asking**: the keys again (the same thirty), the thirty asked, graded: 24 of 30.
- **`/deals`' check-values floor**: read again on this build and on production: both pages carry one checked number (`catalogue|energy_deals`), so the failure is production's own, as the other ten of the gate's eleven.
- **`check-board.mjs`** on this build: exit 0, 39 checks, session 1116's three new ones included (94 held rows blank with none of their figures in the page; the held grids' week lines; 12 stale rows marked).
- **Session 1121's reads**: the board is static, read from its own file, with no database read at build; `/prices` reads `latest_prices` once (54 ms); all 366 pages generated in 6.1 s. The build's slowest reads are other pages' (`storage_daily_cycle` 1.5 s, `cost_of_power_monthly` whole 1.3 s, `runs/slow1121.md`, not in git); no index is needed for the board.
- **Screenshots** of `/board` at 1280 and 390, production (before) and this build (after): `docs/brand/review-1116/`.
- **`/about`'s line on Ask** carries the scores of this asking.

## Not done here

- Session 1115's screenshots of an answer with its read lines (they need a question asked in a browser: one more model call), session 1119's AccessLint and link checks, session 1120's trader path: left to session 1138 of this chain (the board at a keyboard and a screen reader), which needs the same build.

## Checks

- `node --import ./scripts/alias-register.mjs scripts/test-ask-1126.mjs`: exit 0, 3 of 3; `tests.test_session1126`, `tests.test_session1113` (the stored grades are the grader's): exit 0; the tests that read `/about`: exit 0.
- The landing gate: below.

## Decisions made without you

1. **The two faults fixed in the session that found them**, then the two questions asked again (USD 0.15), rather than left to session 1127. Reversible.
2. **`nohup` once**: the first server was started with `nohup` from Git Bash; it was stopped by its process id (`taskkill /PID 15224 /T /F`) before the rebuild, and the second server was a background task of the session. No process was left running past the session's own steps.
3. **The 076 queue move pushed without a before snapshot of its own**; the comparison against the snapshot taken minutes before shows no difference.

## For Samuel's ruling

- Session 320's ruling 3 (every table that holds a figure accepted by a key): the second set's four "wrong" answers are of that kind too.
