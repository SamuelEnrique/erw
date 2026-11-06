# Session 2220 (chain 152, Ask) report: Ask's faults read from the sixty's newest run

5 to 6 November 2026, 00:52 to 01:10 UTC, on portable-laptop (code role), unattended. Chain `queue/done/152-night-5-november-portable-ask-quality.md` (sessions 2220 to 2228). Model spend USD 0 (no model call: every line read from the stored runs). The report's name carries `ASK` because `SESSION_2220_REPORT.md` to `SESSION_2228_REPORT.md` are the data machine's (chain 098, 24 October 2026); nothing of theirs is touched.

- **The prompt saved**: `queue/done/152-night-5-november-portable-ask-quality.md`, the owner's prompt word for word, committed alone (`77f13b5bd`) and pushed to main. 152 is the first free number at or above 152 on origin's main and every branch (the highest in use was 150, on `queue/next` and `queue/done` across every remote branch; 146 waits in the main checkout's `queue/next`, uncommitted).
- **The machine**: precheck passed (on duty until 16:52 UTC). Memory stood at 0.5 GB free of 15.6; the Claude desktop app (ten `claude.exe` processes under PID 40132, started at 13:11 local, not this session's) was stopped by PID; 2.09 GB free after, and the only `claude` or `node` process left is this session's CLI (PID 404). Disk: 104 GB free.
- **Worktree**: `C:\Users\samen\Documents\erw-2220` on `wip/2220-ask`, cut from `origin/main` at `f6279cc9d` after `git fetch` (the queue commit is on both). No `.venv` in a worktree: every python command used the main checkout's `.venv\Scripts\python.exe`.
- **Read**: `docs/reviews/ask-sixty-2026-10-25.md`, `runs.json`, `eval_s1133_s320_run.json` and its grades and keys, `eval_s1133_s1114_run.json`, `refusals.py` and `docs/reviews/ask-refusals.md`, the runs the ten refusals come from (sessions 267, 302, 1113, 1149), `docs/reviews/ask-board-rulings-2026-10-23.md`, `docs/methods/ask.md`, `eval_s1113.py`'s grading.
- **Written**: `docs/reviews/ask-faults-2026-11-05.md` (`2daa5bf0b`), numbered 1 to 21: the eleven failures of the first set (b01 to b06, b08, b09, g03, g06, d10), each with its question, the answer given, the answer expected and its class; the ten classed refusals the same way; a table by class; what sessions 2221 to 2223 do with each class; the count table the next sessions fill.
- **Found**: the eleven are session 320's three open rulings unmoved since 20 October: eight unit faults (USD per kW asked of a table in USD per MW; the loop rightly stated no unfetched number, `ASK_PER_KW` off), two form faults (a five-digit sum written "about 50,424" against a key to the cent), one fault of the key (PJM's right refusal graded on a cited table). None is of the classes table or hold proper. Found on the way: in five records the loop repeated the same tool call with the same arguments up to seven times (g03, g06, g10 twice, q26), spending the limit of 12; a form fault of the loop to fix in session 2222.
- Pushed to `wip/2220-ask`.

## Decisions made without you

1. The Claude desktop app was stopped by PID as "a stray claude process": the prompt names no exception, memory was at 0.5 GB and the app was not this session's. Nothing of it was this chain's.
2. The queue file carries a four-line head (title, `machine: code`, the taking line) before the prompt's words; the prompt itself is unchanged, word for word, from "Run this as a chain" to "stops here".
3. The reports' names: `SESSION_<N>_ASK_REPORT.md`, since the plain names 2220 to 2228 exist on main (chain 098's) and nothing is overwritten. The branches, the worktrees and the gate's task name keep the prompt's numbers.
4. d10's class: the five classes name no "fault of the key"; the file says so and puts it nearest "hold" (a licensed source's question rightly refused). The loop is not changed for it; session 2223 changes the grader.
5. Session 320's three rulings are taken as decided the chain's way ("takes Ask from 19 of 30 to 30 of 30", "never by adding a number the loop did not fetch"): per kW through the tool's own conversion, a figure written as returned, a refusal graded on refusing. Nothing in `docs/state` since 25 October records a ruling on items 1 to 3.
6. The worktree's python is the main checkout's interpreter (the worktree has no `.venv`), as `docs/machines.md` says.

## For Samuel's ruling

1. Whether stopping the Claude desktop app at the start of a night chain is wanted every night (it held about 0.9 GB), or only when memory is under the build's line.
2. Items 1 to 3 of `docs/reviews/ask-board-rulings-2026-10-23.md`, which this chain carries out as recommended there.
