---
role: data
spend_cap_usd: 0.1
timeout_minutes: 20
permission_mode: auto
---
# End-to-end check: a fake data task, third run (session 59)

Task 003 failed: the stub's lock check ran under the system Python, not the .venv (no requests), because the worker started the runner's bare "python" from the system PATH. The worker now starts it with its own interpreter.

Task 002 ran this check first: the lock was taken and released and the usage-limit pause and resume worked, but the stub, which unlike Claude keeps no session, resumed without the task's lines, so its lock check and its commit never ran. The stub now keeps the prompt for the resume, as Claude keeps its session.

A test of the queue, not real work: run by scripts/worker.py with the stub runner (tests/worker_stub.py) in place of Claude, so it spends nothing. The worker takes the data lock, claims the task, and runs the stub on main. The stub first answers with a usage limit, so the worker pauses and resumes the same session. It then checks that a data write into warehouse/output would pass the lock (lock.require), and commits one file on main. The worker pushes main, moves the task to done, and releases the lock.

STUB: usage-limit-once
STUB: require-lock
STUB: write queue/e2e/data-task.md The fake data task of session 59's end-to-end check wrote this file on main under the data lock, after a usage-limit pause and a resume.

## Queue log
- 2026-10-02T04:13:19Z claimed by portable-laptop
