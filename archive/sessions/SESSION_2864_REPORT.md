# Session 2864 report: the model calls, the health summary's blind spot

5 November 2026, about 21:20 to @@END@@ UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend: USD 0.0209 (one scoring call, 5 stories) plus the key probe of session 2862. Pulls: GitHub's API 3 requests (run 41067951705's jobs and log); the Claude API 2 requests (the model list, one scoring call); Supabase 3 reads (erw_health).

## Read these first

- **30 October's model calls failed on the account's spending limit, not on a model name or a key.** Every call returned HTTP 400 `invalid_request_error`: "You have reached your specified API usage limits. You will regain access on 2026-11-01 at 00:00 UTC." (run 41067951705, `news_brief digest`, request `req_011CgYgajfDRaoXmdB4eZYeV`). Scoring logged 0 of 400 stories (16 calls, 16 failed). The same failure ran on 28, 29 and 30 October. `deals`, `datacenters` and `policy_score` failed on the same day.
- **No model name is retired.** The API's list (one request, `runs/s2864/models.py`) includes `claude-haiku-4-5-20251001`, which the alias `claude-haiku-4-5` resolves to, and `claude-sonnet-5-5`. Those are the two names fixed in the code: news scoring, the shadow scorer and the Thesis gate use the first; the policy rereads and Texas delivery reads use the second. The other steps pick the newest Sonnet from the list. No commit was needed.
- **The path works with the owner's credit:** one scoring call on 5 stories (trial, `--out-dir runs/s2864/trial`): 1 call, 0 failed, 5 of 5 scored, USD 0.0209. The deals, policy and Digest steps go through the same client and key. They were not run here, because the runner's next run calls them.
- **The health summary now opens with "Stale on main"** (`wip/2864-health`, `warehouse/health.py`):
  - The line names every scheduled job whose last success is older than its schedule allows. The daily run is checked against its "Daily prices" commit on main (1 day), the Roundup against its commit (8 days), the hourly network against its last ok step in erw_health (3 hours). Each is given with its days stale.
  - Main's commits are read from git where the checkout holds the history, and from GitHub's API on the runner, whose checkout is shallow. The summary step now gets `GH_TOKEN`.
  - Read against 4 November's real rows: "**Stale on main:** daily prices, 6.2 days (its last commit on main, 'Daily prices ...', 2026-10-30 16:27 UTC; allowed 1 day)."
- **A job whose every run stopped at its first step now fails the whole day in the headline.** 4 November reads "**3 failures** over 658 recorded steps. **1 job failed for the whole day**, every run stopped at its first step: daily prices (merge tests)."
- **A library's warning is no longer a failed step's reason.** The merge tests were recorded as "Warning: The 'generic' unit for NumPy timedelta is deprecated ...", not as "FAILED (failures=5, errors=2)".
- **Tests:** `tests/test_session2864.py`, 13 tests, none of which makes a request. With the health tests of sessions 61, 202, 271 and 377: 85 pass. The chain watch's one-email rule is unchanged.
- **Landing:** @@LANDING@@

## Decisions made without you

- **The stale line is written only into the repository's own summary** (`queue/summary/`). A summary written elsewhere (a test, a trial) reads nothing.
- **The hourly network is read from erw_health, not from a commit.** It commits nothing to main.
- **No deals, policy or Digest call was run here.** The scoring call shows the key and the credit work, and the runner's next run makes the others.

## For Samuel's ruling

- **The account's spending limit stopped every model step from 28 October** until its reset on 1 November. If the limit stays as it is, the same thing will happen again the next time the month's spend reaches it.

## Files

- On `wip/2864-health`: `warehouse/health.py`, `.github/workflows/daily-prices.yml` (the summary step's `GH_TOKEN`), `tests/test_session2864.py`.
- On the data machine only: `runs/s2864/` (the jobs and log of run 41067951705, the model list, the scoring trial, the stale line's trial).
