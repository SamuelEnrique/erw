# Session 9813: the security review's ground, the dependencies and the history

Energy Research Warehouse (ERW). 20 November 2026, 20:10 to 20:16 UTC. Chain 610, part B steps 1, 4 and 5, the desktop's third window.

## What was done

- **The ground** (step 1): [`docs/reviews/security-ground-2026-11-20.md`](https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/security-ground-2026-11-20.md). 45 route handlers and 61 pages that read the request, each with what it reads, what it checks, what it reaches and what it trusts; the site's writes and who may make them; the workflows. Made with `runs/c610w3/ground.py` (not in git), each row read by hand.
- **Dependencies** (step 4): `npm audit` on the site's lockfile: 0 on what the site ships; the linter's 7 moderate findings (one advisory) as on 13 November, now closable by a minor version (8.70.1 to 8.73.0, developer-only), listed for Samuel, not branched (the chain's rule: only a patch release goes on a branch). `pip-audit` 2.10.1 (installed apart under `runs/c610w3/pipaudit`, not into the shared venv) on `requirements-py314.txt`: the same four packages as on 13 November, each needing a major version.
- **History** (step 5): every commit on every ref searched for text shaped like a key, by eleven patterns, printing only commit and file (`runs/c610w3/history_scan.sh`): one hit, a test's made-up database address in `tests/test_session177.py` at `6ddef9609`, no longer in the file. Every commit since 12 November (4,318) searched for the exact values of this machine's eleven secrets, held in memory, never printed or passed on a command line (`runs/c610w3/exact_values.py`): none. Nothing to rotate.

## Needs the key

- Nothing.

## Decisions made without you

- The exact-value search reads the env files of the main folder (`C:\Users\Shared\Documents\erw\.env`, `site\.env.local`) without checking out, pulling or editing anything there; the values never leave the script's memory.
