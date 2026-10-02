---
role: code
spend_cap_usd: 2
timeout_minutes: 90
permission_mode: auto
---
# Bring the core documents up to date with session 59's machines

Source: PRIORITIES.md layer 1, order 3 (reach: documentation a person or agent needs to work correctly). Session 59 built the multi-machine setup; docs/machines.md describes it, but the documents an agent reads first do not mention it yet.

Read docs/machines.md and archive/sessions/SESSION_59_REPORT.md, then update the files below, without deleting anything that is still true:

1. `CLAUDE.md`:
   - **The stack table's "Schedules" row:** the jobs are GitHub Actions workflows, but since session 59 pg_cron in Supabase starts them (migration 015, `warehouse/supabase/scheduler.py`). "No crontabs on anyone's machine" stays true.
   - **"Running things":** add `python scripts/sync.py` as the first command of a session, and `python warehouse/lock.py` (role, status).
   - **Non-negotiables or Key conventions:** add one short bullet each:
     - every data write needs the data lock, and only a data machine takes it;
     - code tasks go through a `task/` branch and the code-branch workflow.
   - **The repository layout table:** add `scripts/`, `queue/` and `exports/`.
2. `ARCHITECTURE.md`: in the section on how a dataset travels, add one paragraph on the lock and on sync's restore from Redivis. Link docs/machines.md.
3. `docs/runbook.md`:
   - Where it describes the outside trigger as a step for Samuel, say it is done (pg_cron, session 59), and point to docs/machines.md "The schedule".
   - Keep the GitHub-side steps as the fallback.
4. `package/llms.txt`: only if it describes how the warehouse is refreshed; then one sentence.

Keep each document's voice: plain words, no em dashes. Commit after each document. Run `python -m unittest discover -s tests` before your last commit.
