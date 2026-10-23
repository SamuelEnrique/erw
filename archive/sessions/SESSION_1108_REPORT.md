# Session 1108 report: the next file, then the thirteen causes sorted

23 October 2026, 18:00 to 18:06 UTC, on samueloldlaptop, unattended, on `wip/1108-ask`. Chain `queue/done/075-morning-23-october-code-ask-board.md` (taken at 09:46 UTC by a session that died before its precheck; started again here). Model spend USD 0. A second Claude Code session runs chain 077 (sessions 1150 to 1163, the Grid tool) on this machine at the same time: this chain works only in its own worktrees and `wip/11xx-ask` or `wip/11xx-board` branches.

## Read these first

- `docs/reviews/ask-causes-2026-10-23.md`: the thirteen wrong answers and the four held, each placed (code, hold or ruling) with the function a fix would live in and the fixture that proves it.
- `queue/next/076-day-24-october-code-ask-board-2.md`: this chain's successor, sessions 1126 to 1141.

## What was done

- **Precheck**: exit 0 (it took the duty mark from "session 1150", the other chain's; the duty mark is per machine).
- **The next file first**: `queue/next/076-day-24-october-code-ask-board-2.md` (16 sessions, 1126 to 1141, Ask and the board's second pass, no ruling needed), read against `queue/next/` first (078 is chain 077's successor, the Grid tool's; 076 does not touch its files). Committed alone (`17930277`) and pushed to main at 18:04 UTC, with snapshot `s1108-before` taken before as its own command.
- **The causes**: of the thirteen wrong answers none has its cause in the code alone (8 wait for ruling 1, USD per kW; 3 for ruling 2, the keys' tolerance; 2 for ruling 3, the keys' tables); four questions are held (g07, g08, d05, d07). The code holds four faults on the way to the answers, none of which made a final answer wrong: the tool calls not recorded (30), the eight-call limit reached (11), a form name ("EIA-930") read as the figure 930 (4 first drafts sent back), and eight calls for one sum (b01). Sessions 1109 to 1111 take them; 1112 takes the held four.

## What to review

1. Open `https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/ask-causes-2026-10-23.md` once landed.
2. Read the first table's "Place" column: every wrong answer is a ruling, so the chain's "30 of 30" goal rests on rulings 1 to 3.
3. Read the second table: the four faults and the session each goes to.

## Checks

- No code changed. Em dashes in the new files: 0 (`grep -c` on each).

## The landing

Lands with the sessions after it in one push (below, "Decisions made without you" 2); the comparison is in the report of the session that pushes.

## Decisions made without you

1. **The successor is numbered 076**, as this chain file says, although 077 and 078 already exist. `chain_queue.py next` takes the lowest number first, so whichever of the two chains on this machine ends first takes 076. Reversible: a file can be renamed in one commit.
2. **One worktree for the chain, a branch a session, landed in combined pushes.** Each session's branch (`wip/<N>-ask` or `-board`) is cut from the one before it, not from origin/main, so the sessions can land together, as the chain allows; one `npm ci` serves them all. Reversible.
3. **A switch that is off for each ruling's change**, prepared where the code is, so that a ruling is one line: the chain does not turn any of them on.

## For Samuel's ruling

- Ruling 1 of session 320 (USD per kW: should the tools hand back the per-kW figure where the method names the conversion?): 8 of the 13 wrong answers wait on it.
- Rulings 2 and 3 (the keys' tolerance and tables): 5 of the 13.

## To finish

- The after snapshot of the 076 push and its comparison (taken in session 1109, below).
