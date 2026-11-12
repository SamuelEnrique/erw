# Session 3712 report: the merge gate runs the suite on what lands

Energy Research Warehouse (ERW). Chain 208, session 13 of 20, portable laptop, 6 November 2026, about 22:50 to 22:55 UTC (during session 3706's gate). Branch `wip/3701-sellable`, commit `dca33ee78`.

- **`scripts/suite_gate.py`:** the whole suite as GitHub's runner runs it (`--ref` gives a clean copy of a commit: no `warehouse/output`, no key, the lock exemption). Every failing test is named, one a line, and the list goes into the run's summary. Exit 0 or 1.
- **`.github/workflows/code-branch.yml`:**
  - the checks merge the main the branch lands on before the suite, and run `suite_gate.py`;
  - the merge job, when main moved since the checks, runs the suite again on the branch merged with the new main before it merges.
  - The merge job's limit is 45 minutes (10 until now).
- **`scripts/push_guard.py`** (session 3713 uses it): the suite on a clean copy of a commit. Passed: exit 0. Red: the tests are named, the commit goes to a `wip/` branch, and the step is recorded failed. It refuses `main` and `task/` as the red branch.
- **Test:** `tests/test_session3712.py` (8 tests, OK); `tests/test_session301.py`, `88` and `90` (they read `code-branch.yml`): 46 tests, OK.

## Decisions made without you

- The re-test in the merge job runs only when main moved, not every time: about 10 minutes added to a landing only then. A move during the re-test is the window left, and the next branch's checks see it.
- The checks build and check the site on the merged tree as well, the closer copy of what lands.

## For Samuel's ruling

- None new.
