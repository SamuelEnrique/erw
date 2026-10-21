# Session 447 report: every open ruling, with a recommended answer

21 October 2026, about 07:15 to 07:35 UTC, unattended, on portable-laptop (code role), on `wip/441-450-third`. The chain of 21 October, night, third machine (`queue/done/017-night-21-october-third.md`, session 447). Model spend USD 0; no pull; no web request; no warehouse data written; no `site/` change, so no build.

## Read these first

- **The agenda is `docs/reviews/rulings-2026-10-21-draft.md`**: 57 items, each once, from the ruling sections of 45 reports of sessions 351 to 440 and the waiting lists of the eight notes in that run, 161 lines in all. Each item: who raised it, the evidence, the reversible choice made meanwhile, what each answer changes, one recommended ruling with its reason. Nothing is decided.
- **The first three follow the ledger's rule** (session 414: the newest note that says it ranks by value): session 389's `docs/state/note_2026-10-21_day_data.md`, items 1 to 3. They are the Redivis storage (raised by 358, 363, 376, 377 and 385), the database (383's statement timeouts merged with 387's pg_cron startup timeouts: the same hours) and the move under Ben's organization (385).
- **The groups are the ledger's**: money (items 1 and 2), a data pull (3 to 20), a ruling on a figure (21 to 34), a public page (35 to 52), none of the four (53 to 57).
- **Already answered, not counted**: sessions 406's and 407's ten items (Samuel's ruling of 21 October, no newsletter of any kind); the restore of the data machine (373); the sources check (374); the CLAUDE.md patch (`be202c6f`); the landing of 367 to 382 (`bb49c9e0`).
- **No report anywhere** for 390 and 391 (queued, not run), 401 and 408 (commits, no report), 411, 412 and 415 (reserved, no commit), 431 to 440 (the data machine's night chain, running), and 392 to 400, 416 to 419 and 421 to 430 (reserved by no chain file).

## What to review

- `https://github.com/SamuelEnrique/erw/blob/wip/441-450-third/docs/reviews/rulings-2026-10-21-draft.md`, top to bottom; the three first.
- `tests/test_session447.py`.

## Checks

Every gate redirected to a file under `runs/chain_oct21_third/s447/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `extract.py` (read-only git over `origin/main` and every `origin/wip/*` and `origin/task/*`) | 0 | 50 reports of 90 numbers; 118 list lines in the ruling sections (`extract.out`, `sections.md`, `coverage.csv`) |
| `tests.test_session447` | 0 | 7 tests OK: no em or en dash; the groups present in order; items numbered 1 to 57, the count the document states; each item's five fields once, the ruling line with its reason; each item cites a session in 351 to 440; the first three from the ranked note |
| The same tests against a copy with a dash and one field removed | 1 | 2 failures, as it should (`test_negative.out`) |
| The whole suite | not run | the parent runs it once for the chain; this session adds one test file and two documents |

## Decisions made without you

1. **Each report read from the branch whose newest commit touched it**: 402 to 414 from `origin/wip/015-land`, 420 from `origin/wip/findings-oct20`, the rest from `origin/main`.
2. **The notes' waiting lists were read with the reports**, since most report lines are restated there and four sessions (356, 380, 386, 389) put their waits only in a note.
3. **Merges by subject, written in each item**: the database (383, 387), the explorers drawn twice (403, 404, 405), the data machine's six rebuilds (370, 381, 382, 403, 404, 405), the machines' three settings (372, 384, 387), and the records' smaller questions (381, 409, 410, 413, 414, 420). Session 414's ledger kept the two Newey-West questions as two items; so does this list (items 22 and 23).
4. **An item is placed by what its answer blocks**, with the ledger's word rules as the guide; where the rules would place it elsewhere, the item says so (item 2).
5. **Items already answered are listed, not counted**, each with the commit or ruling that answered it.
6. **Session 420's four steps** (open the findings, run each `check.do`, the LinkedIn material, the Roundup draft) are kept with item 57 as steps, not rulings; its four rulings are items 32 to 34 and 57.
7. **Two claims were checked on main before writing**: the download route still lists no `ba` or `event` (item 46 stays open) and CLAUDE.md carries session 371's commit (listed as answered).

## For Samuel's ruling

- The 57 items of the agenda, the three first.
- Whether the five "Already answered" entries are answered as this list reads them (the CLAUDE.md patch in particular: main carries session 371's own CLAUDE.md commit; the patch file in `runs/chain_oct20d/s371/` is on the code machine and was not compared).

## To finish

- Land with the chain's other documents (a document and a test; no build needed).

## Files

- `docs/reviews/rulings-2026-10-21-draft.md` (new).
- `tests/test_session447.py` (new).
- This report.
- Not in git: `runs/chain_oct21_third/s447/` (`extract.py`, `extract.out`, `sections.md`, `coverage.csv`, `inventory.txt`, `test.out`, `test_negative.out`, `bad_copy.md`).
