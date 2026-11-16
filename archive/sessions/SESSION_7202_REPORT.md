# Session 7202 report: the scheduled model steps fail soft when the key refuses (chain 302, goal 3)

Energy Research Warehouse (ERW). 16 November 2026, samueloldlaptop (code role), unattended. Chain file: `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md`. Branch `wip/7202-key-refusal` from `origin/main` (worktree `erw-7202`), its own landing request row (16): it does not depend on the site stack. Model spend: USD 0.00. Every client in the tests is a stub; no request was made, nothing was sent, no issue was written.

## At the top

- **Until this lands, the daily run records the same failures each day.** The key is at its limit until 1 December. Today's 14:00 UTC run (Monday) is the first weekday run under it: the scoring fails as on 15 November, and the Digest's own call is refused, so no Digest is written and no email is sent (the email step already skips when the newest issue is not today's). Nothing wrong is published; the rows say "failed" where they should say "skipped".
- **Not run against GitHub's runner.** The change is tested here with stubs and with `run_other` run in bash; its first real run is the daily job after the landing.

## What changed

- **The refusal is known once, in the shared client** (`warehouse/llm.py`). A call the API answers with "You have reached your specified API usage limits ..." raises `KeyLimitReached`. The refusal is kept for the process: every later call (`messages.create`, `messages.stream`, `models.list`) raises it again and no request is sent. No retry.
- **A scheduled model step ends as skipped.** Ten scripts exit through `llm.finish(<step>, rc)`: news scoring, the shadow steps, policy scoring and reads, the deals and the datacenter extractors, the fun fact, the Digest, the Roundup, the chart's note. Under a refusal the step's status rows become `skipped` with "the key's limit: the Anthropic API key has reached its usage limit; access returns 2026-12-01 at 00:00 UTC; no model call is sent until then", one line `<step> SKIPPED: the key's limit: ...` is printed last, and the exit is 75.
- **One skipped row of `erw_health` a step,** with that reason and the API's own date: `run_other` in `warehouse/run_daily.sh` writes it for the daily steps (as it does for a pull stopped at its budget); `warehouse/health.py run` writes it for the Roundup's step. A skip is never retried.
- **No email for it.** `scripts/alert.py` tells failures, and the daily cap's skips by their own words ("daily model cap"); a key's-limit skip is neither. So nothing is sent beyond what the cap's rule sends.
- **The news scorer stops at the refused call.** No further batch is sent. Where nothing was scored the table and its header are left as they were (on 15 November the run rewrote the header with "calls 0 (16 failed)").
- **No issue on a day the scoring was refused.** The Digest and the Roundup ask `llm.refused_today("news_score")` (the scorer's status of the same run, or the day's newest row of `run_status.csv`) before they read a story, write nothing and exit 75. Their own refused call ends the same way, before anything is written. A run to `--out` is a person's own and is not stopped.
- **The Roundup's job needs no change.** Its commit step runs only after a step that ended `ok` or `retried`, and its email only after the commit; the test pins both lines.
- **No issue's words changed.** `--no-model` stays the daily cap's path and is not used for the key's limit.

## Tests

- `tests/test_session7202_key_refusal.py`, 21 tests, with a stub that raises the API's error:
  - the refusal is read with its date; one request, then none, across clients; the model list and a stream meet it too; another HTTP 400 is the SDK's own;
  - `finish`: ok and failed rows become skipped with the key's line, a gap row stays, an earlier run's status is not rewritten, and with no refusal nothing changes;
  - `health.run` records one skipped row and does not retry;
  - the scorer on a copy of the stories: one request for three batches, the table byte for byte as it was, status skipped, exit 75;
  - the Digest on a refused day writes nothing (no file, no `latest.md`) and ends skipped; a dry run to `--out` goes on; the Digest's own refused call writes no file at `--out`;
  - the Roundup on a refused day writes nothing and ends skipped;
  - `run_other` run in bash on a step that prints a FAILED line and then exits 75 with the key's line: the status file and one health row carry the key's reason.
- **The touched test files:** 131 files that name a changed module, each in its own process, 2,530 tests: all pass. Two need saying: `test_periodicals_3457` passes under the suite's own discovery (run alone by module name it cannot import its neighbour), and `test_session138_delivery` holds no test.

## What to review

- `docs/methods/api_cost_ledger.md`, the new section "The key's own usage limit".
- After the landing, the day's rows of `erw_health` for the daily job: `news_score`, `policy_score`, `policy_reads`, `deals`, `datacenters`, `news_funfact` and `news_brief`, each `skipped`, each reason beginning "the key's limit". On `/internal/health` these steps no longer make the day red (the day's record counts a failure only where a row says `failed`).
- `warehouse/metadata/run_status.csv` after that run: the same steps `skipped`, not `failed`.

## Needs the key

- Nothing in this goal. The first run against the real API is the daily job itself, which spends nothing while the key refuses.

## Decisions made without you

- **A step whose own call is refused is skipped, not written without the model.** The Digest could fall back to the publishers' own titles as it does at the daily cap. It does not: under the key's limit the day's stories are not ranked, and the chain's rule is that such a Digest is not an issue.
- **One row of `erw_health` a step, not one a day.** Seven daily steps are refused each day, so seven skipped rows. Each says which step did not run.
- **The key's refusal is recognised by the API's words** ("reached your specified API usage limits"), not by the HTTP status alone: the same status carries "temperature is not supported", which a step answers by asking again without it.
- **A refusal part way through a run keeps what was done.** Stories scored before it are written; the status says skipped, with what was done after the key's line.
- **"Credit balance" is not treated as the key's limit.** The extractors' own sorter (`warehouse/deals/calls.py`) stops a run on it; it names no date access returns, and it is a different fault. Left as it is.

## For Samuel's ruling

- **Whether a day under the key's limit should send you one line.** Default: nothing is sent (the chain's words: no second email beyond what the cap's rule sends). The skipped rows are in the day's health summary under "Skips, by reason".
