# Session 1128 report: the evaluation as one command

23 October 2026, 19:27 to 19:33 UTC, on samueloldlaptop, unattended, on `wip/1128-ask` (cut from `wip/1123-ask`, chain 075's last branch). Chain `queue/done/076-day-24-october-code-ask-board-2.md`. Taken before session 1126's landing and session 1127, which wait for a build (the build lock held by chain 077 and the machine low on memory). Model spend USD 0.

## What was done

- `warehouse/chat/eval/run_eval.py`: chain 075's nine steps as one command, each its own process whose exit is read: the database probe, at least 3 GB of memory free (the reason chain 075's wait was stopped), the build lock waited for at most 20 minutes, a production build with `ERW_READ_TIMING=1`, the build served with `ASK_VISITOR_SALT` from the root `.env` and the evaluation's day ceiling raised by the run's cap for that server only, the set's keys from the live set, the asking under the cap checked before each question, the grading, the server stopped by its process id and the lock released whatever happened. `--dry-run` prints every step with its command and starts nothing; `--only`, `--cap`, `--port`, `--no-build`.
- `docs/methods/ask.md`, "The evaluations": the one command and its steps, written once.

## Checks

- `python -m unittest tests.test_session1128`: exit 0, 3 tests (the plan's order, each set's keys, the asking's arguments; a dry run starts nothing).
- `python warehouse/chat/eval/run_eval.py --set s1114 --cap 6 --dry-run`: exit 0.
- Em dashes: 0.

## Decisions made without you

1. **The server's ceiling is its own value plus the run's cap**, for that local server only, so the route never refuses an evaluation the run's own cap allows. Reversible.

## For Samuel's ruling

- None new.
