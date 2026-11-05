# Chain 089 on the old laptop: Ask and the price board, fourth pass (23 October 2026)

Energy Research Warehouse (ERW), session 1196, the note of chain 089 (`queue/done/089-day-26-october-code-ask-board-4.md`, sessions 1190 to 1196), run unattended on samueloldlaptop from 23:14 UTC on 23 October, straight after chain 085 (`docs/state/review_2026-10-26_code_ask_board.md`), beside chain 078 (the Grid tool). Model spend USD 0.

## Session by session

| Session | State |
|---|---|
| 1190 | the next file (`queue/next/093-day-27-october-code-ask-board-5.md`, pushed to main, 0 differences); session 1149's two runs in the evaluations' history (`docs/reviews/ask-history.md`, 8 rows); chain 085's after snapshot still waiting (Vercel refused every deploy from 21:03, "rate limited"); the board's new rows blocked |
| 1191 | the site's license hold for the Python chat behind `ASK_HOLD=on` (`warehouse/chat/license_hold.py`), its decisions tested equal to the site's over every table of the status file |
| 1192 | blocked: the board's file holds none of the new groups yet (the daily run of 16:19 came before their code) |
| 1193 | a group's held grid said once, its rows behind a toggle (`heldLines`; 10 lines, 20 rows on today's file); `check-board.mjs` checks the lines on a build |
| 1194 | an answer's sources and reads in the brand's source line, one component for every chat (`components/ask/AnswerSources.tsx`); AccessLint on a stored answer: no violations |
| 1195 | `docs/methods/ask.md`, `docs/methods/price_board.md`, the rulings list (items 13 and 14) |
| 1196 | this note; 093 updated |

Every session's work is on `wip/1190-ask`, pushed; nothing of it is on main but this note, the next file and the queue's move.

## Not landed

The landing needs a build, and the chain's rule is a build only with 3 GB of memory free: the machine had 1.9 to 2.1 GB free from 23:25 on, beside chain 078's session, under the 2.4 GB at which chain 085's landing had been let through. So the gate, the screenshots of the board's held lines and of an answer, `check-board.mjs`, `check-links.mjs` on `/board` and the keyboard walk are 093's session 1300's first item. The branch is merged with main up to `c7c257be`; main has moved since by documents and the data machine's merges.

## Decisions made without you

1. Session numbers 1300 to 1306 for 093 (1197 to 1199 too few; 1200 onward the personal laptop's).
2. The Python tools' hold off by default (`ASK_HOLD`), the CLI reading as before until the ruling.
3. The held rows kept in the page, hidden behind their grid's line, not left out.
4. One component for every chat's sources; the general form's "Sources" heading dropped.
5. The method notes ride with the landing, not pushed to main ahead of the code they describe.
6. No landing under the 3 GB line.

## Waiting for Samuel

`docs/reviews/ask-board-rulings-2026-10-23.md`, fourteen items; new: 13 (the CLI's hold by default) and 14 (the board's list of tables at phone width). The list's two new items are on `wip/1190-ask` until it lands; item 14's words are also in session 1149's report on main, item 13's in session 1191's report on the branch.

## The queue

`queue/next/093-day-27-october-code-ask-board-5.md` (sessions 1300 to 1306), updated by this session: its session 1300 lands `wip/1190-ask` first. `091` is chain 078's successor.
