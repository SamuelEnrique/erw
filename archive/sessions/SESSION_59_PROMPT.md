# SESSION 59: Multi-machine setup, and the fixes Samuel should not have to do

Machine: run this session on Samuel's portable laptop. Design roles as a per-machine
setting: the always-on home laptop will hold the data role once set up, the portable
laptop will be a code machine (it closes and sleeps, so any task it holds must survive
interruption: retried, never half-applied), and a faster lab machine arriving next week
will take the data role, with the home laptop switching to code. Make the switch one
setting.

## Read first
CLAUDE.md, PRIORITIES.md, docs/runbook.md, .github/workflows/, warehouse/archive/,
warehouse/supabase/, archive/sessions/SESSION_58_REPORT.md (open questions and "What
Samuel must do").

## Budget and rules
- Expected Anthropic API spend: USD 0 of its own (a dispatched daily run spends its
  normal ~USD 2). Hard cap: USD 4.
- Approved by Samuel (Oct 2): delete his own address's row in Supabase
  email_suppressions; create Supabase tables, functions and pg_cron jobs needed below;
  store a GitHub token in Supabase Vault (never in the repo); close or comment on
  GitHub issues; one workflow_dispatch of the daily job; branch protection and
  auto-merge settings on this repository if the token allows.
- Cloud cost must stay at USD 0: use only free tiers already in use (GitHub, the
  archive bucket, Supabase free plan, Redivis). Add no paid service and no paid plan.
  Raw files too large for the free tiers stay on the data machine only.
- Never wait idle: start long runs, keep working, check back between steps.
- Pull and merge if the daily job lands, never force push, commit after every step.
- Do everything you can yourself. Anything that truly needs Samuel goes in ONE list at
  the end of the report, each item with exact click-by-click steps and why it cannot be
  automated.

## Part 1: the fixes (first)
1. Delete DIGEST_RECIPIENTS' row from email_suppressions. Find what unsubscribed it on
   2026-09-29 00:32 UTC (likely a test of the unsubscribe link) and make every test use
   a fixed test address that can never be the real recipient.
2. The schedule: check whether the token in .env can dispatch workflows. If yes, set up
   Supabase pg_cron with pg_net calling workflow_dispatch (with once=1) for the daily
   job (14:00 UTC), latest prices (every 15 minutes), the hourly network, the Roundup
   (Sundays 23:00) and the weekly vacuum, with the token in Supabase Vault. Verify one
   call lands. If the token cannot, say exactly which permission is missing.
3. Close issues #6 to #14 with a comment naming the fix; keep #3, #4, #5 open. If the
   token cannot, say exactly which permission is missing.
4. The September 2022 page: read /events/caiso-heat-2022's text and check that the
   window's highest hour names 2022-09-06 at 51,104 MW; fix if not.
5. /network's stale ERCOT intensity: rebuild the hourly snapshot on the latest daily
   build (no EIA pull needed if the daily build already holds it).

## Part 2: make the ERW safe for several machines
1. The cloud is the source of truth: scripts/sync.py (and a .ps1 and .sh wrapper)
   that pulls main and restores the warehouse working files from the archive bucket,
   verified by counts against coverage. Every session prompt starts with it. Report
   where every cloud copy lives, its current size, the free-tier limit, and the
   monthly cost (expected USD 0).
2. Roles: "data" (pulls, warehouse writes, Supabase loads, Redivis uploads, archive
   writes) and "code" (site, docs, derived pages from loaded data, tests). A data lock:
   a Supabase table erw_locks (holder machine, task, acquired, expires), taken before
   any data write, released after, expiring after a set time so a machine that closes
   or crashes cannot hold it forever. Every data-writing script refuses to run without
   it.
3. Code work on branches: each code task works on its own branch and opens a pull
   request; a GitHub Action runs tests/ and check-routes; it auto-merges when they
   pass. Data tasks commit to main under the lock, as now.
4. The queue: queue/todo/, queue/doing/, queue/done/, one markdown file per task named
   NNN-<role>-<slug>.md, holding the full session prompt, its spend cap and its role.
   A task is claimed by moving it to doing/ in a commit; if the push loses a race, the
   machine picks the next one. A task left in doing/ by a machine that went to sleep is
   returned to todo/ after a timeout.
5. The worker: scripts/worker.ps1 (and worker.sh) runs on a machine with a role
   setting. Loop: sync, take the next task its role allows, run it with Claude Code in
   headless mode with this repo's permission settings, write the report, move the task
   to done/, repeat; stop when the queue is empty or a usage limit is hit (pause and
   retry later, never fail the task). A daily summary file: what each machine did.
6. docs/machines.md: how to add a machine (install, copy .env securely, run setup,
   choose a role) for Windows, Mac and Linux, and scripts/setup.ps1 / setup.sh that do
   everything after the installs, including keeping a Windows machine awake when
   plugged in.
7. Test it end to end on this laptop: a fake code task and a fake data task through the
   queue, the lock taken and released, a branch auto-merged.

## Part 3: seed the queue
Write the next five tasks into queue/todo/ from the open items in the session 58
report and PRIORITIES.md, labeled by role, each a full prompt with its spend cap.

## Report: archive/sessions/SESSION_59_REPORT.md
Part 1 in plain words (what is fixed, digest restored or not, schedule live or not);
Part 2 what each piece does, the end-to-end test, and the cloud sizes and costs; the
queue's first five tasks; ONE list of what Samuel must still do, with exact steps;
wall time; spend. Push. Stop.