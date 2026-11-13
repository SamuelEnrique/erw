# Chain of 13 November 2026: sessions 5000 to 5049, portable laptop window P1, unattended: the five tools toward roadmap item 2

machine: portable-laptop-window1

Written by window P1 of the portable laptop on 13 November 2026 at about 09:45 UTC, from the owner's prompt of that morning. Only window P1 of the portable laptop takes this file; no worker and no other window may take it. The first queue number free on origin's main and every branch was 233 (230 and 231 are the desktop windows' next files; 232 is window P2's and the old laptop's). Sessions 5000 to 5049 (5050 upward for the next file), checked free on origin's main and on every branch; a taken number is skipped upward and said so. Model: Opus 5.5, high effort. Running about 13 hours, through the weekly reset; the weekly limit is the only stop.

## The laptop

Three windows on this 16 GB laptop: P1 (this chain, sessions 5000 to 5099, the five tools), P2 (security and analytics, 5100 to 5199), P3 (the AI chat over the warehouse, 5200 to 5299). P1 is the only window that builds the site, always through the build lock (`scripts/buildlock.py acquire p1` and `release p1`), one build at a time. Nobody on this laptop lands: the desktop's landing window lands every branch. P1 never changes the main checkout's branch or working files (except the queue commits `chain_queue.py` makes); all work happens in git worktrees beside `C:\Users\lossa\Documents\erw` named `erw-p1-<N>`, on `wip/5000-<topic>` stacks, with `C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe`.

## Rules for every session

The rules of `queue/done/225-day-18-november-code-continued.md` hold where they apply: precheck first; `git fetch origin` and `origin/main` merged before work; default-neutral; `site/lib/release.ts` untouched; nothing sent or posted; no warehouse data written; no backfill; no layout redesign; no brand work; every figure a check-values key traced to the warehouse; model spend under the owner's key at USD 2 a session and USD 20 the chain; the report in short bullets with "Decisions made without you" and "For Samuel's ruling"; no em or en dash. Never stop to ask: a reversible choice goes under "Decisions made without you", anything that waits for Samuel goes under "For Samuel's ruling" with a default. Plus:

- No landing gate and no full test suite here: run the test files a change touches. A stack ready to land gets a requested row in `docs/state/landing_request_portable.md` (its numbering continued: branch, head, task name, port 5000 upward, the tests run), committed and pushed.
- No step waits on a landing: the next step stacks on this chain's own branch; a step that truly needs main is skipped, said so, and the next taken.
- Files not touched: the Ask chat's engine and evaluation (P3's: `site/lib/ask*`, the Ask API route, `docs/reviews/ask-*`); the security and usage files (P2's: `site/proxy.ts`, `site/lib/guard.ts`, `site/components/Usage.tsx`, `docs/security.md`); the Digest and Roundup (the old laptop's); the datacenter tracker's grids view (`docs/reviews/datacenter-faults-2026-11-11.md` row 4).
- The queue step is always by name: `scripts\chain_queue.py next --file <name>`, never bare `next`.

## Session 5000: the next file, the ground

Long end 1:00. The next file first (`machine: portable-laptop-window1`, the same goal, sessions 5050 upward, at least 14 sessions), committed alone and pushed. Then precheck, `git fetch`, memory and disk free, and the ground for roadmap item 2 (`docs/roadmap.md`): for each of the five (battery `/cost-of-power/battery`, generator `/cost-of-power/seller`, datacenter `/cost-of-power`, Automated Analysis `/analysis`, Grid `/network` with `/mix` and `/ask`), what exists of its done line: a method note, a replication a reader can run, a cross-check table against published figures, a decisions block. A table of it in the report.

## Sessions 5001 to 5040: tool by tool

Long end 1:00 each, tool by tool in the order battery, generator, datacenter, Automated Analysis, Grid. Each tool: read as a reader on a local production build in the internal view at 1280 and 390 (the pattern of `docs/reviews/five-tools-read-2026-11-11.md`), every fault a numbered row in `docs/reviews/<tool>-faults-2026-11-13.md`, every open row fixed with a test; then the missing pieces of its done line built: the method note complete and ready for Samuel's signature (he signs, the chain does not), the replication (Stata do-file and Python, runnable from the downloads), the cross-check table against published figures with sources, the decisions block. Automated Analysis toward its final form (fully automatic, on its schedule); Grid toward one page (network, energy mix and Ask as one tool: page composition only, not the Ask engine). A landing request row after each tool's stack is ready.

## Sessions 5041 to 5047: what remains

In the same order.

## Session 5048: the note

`docs/state/note_<date>_portable_p1.md` (its name checked free): short bullets, per tool what is now done against its done line, what waits in which landing row, the rulings waiting with defaults.

## Session 5049: the next file and the queue

The next file updated with what is unfinished, pushed alone, and the queue step by name.
