---
role: code
spend_cap_usd: 0.1
timeout_minutes: 20
permission_mode: auto
---
# End-to-end check: a fake code task (session 59)

A test of the queue, not real work: run by scripts/worker.py with the stub runner (tests/worker_stub.py) in place of Claude, so it spends nothing. The worker claims it, makes the branch task/001-e2e-code, the stub commits one file there, the worker pushes the branch, and .github/workflows/code-branch.yml runs the tests and the site's checks and merges it into main.

STUB: write queue/e2e/code-task.md The fake code task of session 59's end-to-end check wrote this file on its branch; the code-branch workflow merged it into main after the tests and the site's checks passed.

## Queue log
- 2026-10-02T04:09:01Z claimed by portable-laptop
