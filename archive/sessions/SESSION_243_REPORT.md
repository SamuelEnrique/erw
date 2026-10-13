# Session 243 report: the email rule

13 October 2026, 06:06 to 06:45 UTC (the night of 12 October, Pacific), unattended, on lab-desktop (the data machine), the first session of the chain of 12 to 13 October (sessions 243 to 250). Branch `task/243-email-rule`. Model spend USD 0: no model call. No pull, no warehouse table, no data write, no page changed.

## Read these first

- **The machinery now sends you two emails and no other.** One for a machine, 15 minutes after it went idle, saying it is ready for review. One a UTC day when the daily run is red.
- **Everything else still runs and still records, and emails nothing:** the chain watch, the 30-minute idle alarm, a lapsed mark, a failed step of any other job, the model cap's skips, the morning summary, a waiting session, a failed precheck's own line, a failed session's line, a failed Roundup's line.
- **The sender itself holds the rule.** `deliver()` in `scripts/alert.py` is the one function that reaches the sender; it sends only a line of the kind `ready` or `daily red`. In the workflow only those two steps are given the key that sends.
- **Three things you no longer hear of by email, which you may want back** (under "For Samuel's ruling"): a session stuck on a permission prompt, a failed Roundup, and a red job that is not the daily run.
- **The rule is live once this lands.** Tonight's own chain ends with the new idle step: you should get one email from lab-desktop, 15 to 30 minutes after CHAIN DONE. The code machine sends as its own checkout has it: the old immediate email if it has not merged this, the new one if it has. Never both.

## The two emails

| | Says | When | Sent by |
|---|---|---|---|
| Ready for review | "The machine lab-desktop is ready for review. Idle since 07:40 UTC: queue/next/ is empty: lab-desktop has nothing left to run after "chain of 12 to 13 October, sessions 243 to 250"." | 15 minutes after the machine went idle, at the first check after that (every 15 minutes, so 15 to 30 minutes after). Not at all when the machine is on duty again by then | `python scripts/alert.py ready`, a new step of `chain-watch.yml` |
| The daily run is red | "The daily run is red on 2026-10-13 UTC: 2 steps newly failed: isone (daily prices), caiso (daily prices). First: HTTP 500 from the publisher. One email a day: the rest is on /internal/health." | once a UTC day, at the first check that sees it | `python scripts/alert.py failures`, the same workflow |

- **A machine goes idle** when `python scripts/chain_queue.py next` finds nothing waiting on a machine on duty, or when its precheck fails. Each writes one row of `erw_health` (step `idle`) whose reason begins "ready for review: ". The check reads the newest such row of each machine.
- **The daily run** is the workflow `daily prices` and a data machine's own daily run (its `dm_` steps). Red is a step of either newly failed, or no step of the workflow recorded by 18:00 UTC.
- **"At most one" is remembered,** as session 202's lines were: rows of `erw_health`, workflow `alerts` (`ready|<machine>|<minute>`, `daily red|<day>`). A late check still sends; a doubled check does not send twice.

## What to review

- `docs/machines.md`, "The email rule (session 243)": the two tables (what is sent, what is only recorded).
- `runs/session243/dry_runs.out` on this machine: a dry run of each of the 13 paths, on stand-in rows. Paths 1 and 2 print the two emails; paths 3 to 13 each print "recorded, not emailed" or "would record, not email" and "emails sent: 0".
- `runs/session243/live_dry_runs.out`: the same checks, dry, against the live health table at 06:22 UTC. All quiet: nothing was due.
- After the landing: `/internal/health` shows the chain watch with its new step, "ready for review".

## The dry runs (each path)

| Path | What the dry run printed |
|---|---|
| 1. ready, 10 minutes after idle | quiet: its line goes 15 minutes after |
| 1. ready, 20 minutes after | the email above |
| 1. ready, the machine on duty again | quiet: on duty again since 07:48 UTC |
| 2. daily run, two steps newly failed | the email above; three lines "would record, not email" |
| 2. daily run, no step by 18:00 UTC | "the workflow "daily prices" recorded no step by 18:00 UTC, so it did not start" |
| 3. a failed step of another job | recorded, not emailed; emails sent: 0 |
| 4. the model cap skipped a step | recorded, not emailed; emails sent: 0 |
| 5. idle alarm, 40 minutes silent | would record, not email; then recorded, not emailed |
| 6. chain watch, 38 minutes silent | would record, not email |
| 7. morning summary | the summary in the log; "summary: recorded, not emailed"; emails sent: 0 |
| 8. a session waits (the hook) | recorded, not emailed; emails sent: 0 |
| 9. a failed precheck | the line printed (dry); for real, one idle row beginning "ready for review: Precheck failed on lab-desktop" |
| 10. the queue's last step, nothing waiting | would write the idle row; "would send nothing here"; would take the machine off duty |
| 11. `notify.py --failed` | not sent |
| 12. a failed Roundup (`health.py alert`) | recorded, not emailed |
| 13. any other caller of the sender | not emailed; emails sent: 0 |

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py` | 0 | six of six; the machine on duty at 06:07 UTC |
| `python scripts/freeze.py status` | 0 | no freeze |
| the twelve alert test modules (`tests.test_session243`, `91`, `116_alerts`, `119`, `188_queue`, `188_precheck`, `188_idle`, `202`, `82`, `176`, `199`, `test_planner`) | 0 | 291 tests |
| `python -m unittest discover -s tests` | 1 | 3,672 tests, 3 failures, the same three as in sessions 232 and 233 and none in what this session touched: `test_session51`, `test_session125`, `test_session165` compare tables on this machine with committed files and are skipped on GitHub's runner |
| `runs/session243/dry_runs.py` | 0 | the table above |
| the live dry runs | 0 (3 for the queue's dry run: nothing waits) | all quiet |

## Decisions made without you

1. **A failed precheck counts as the machine going idle.** It no longer emails its own line; it writes the idle row with the line as the reason, so the machine's one email, 15 minutes later, says it is ready for review and why. A precheck that passes in those 15 minutes cancels it. The other reading of your ruling (a failed precheck tells nobody) would leave a chain that never started unreported.
2. **"The daily run" is both daily runs:** GitHub's `daily prices` and this machine's own (`dm_` steps). One email a UTC day for the two together.
3. **Red means newly red.** A step that failed at its run before is the same failure and sends nothing (session 202's rule, kept: your ruling says no repeats). So a daily run that is red for the same reason every day emails once, on the first day.
4. **A daily run that did not start is red too:** no step of `daily prices` recorded by 18:00 UTC (it starts at 14:00). The health page already ends the green streak on such a day.
5. **"One per machine" is one per time it goes idle.** A machine that works again and goes idle again gets a new email. A machine that asks the queue again while off duty does not: its row says "idle already".
6. **The 15 minutes are counted on GitHub, not on the machine:** a step of the chain watch, every 15 minutes. So the email arrives 15 to 30 minutes after the machine went idle, and still arrives when the machine has been closed.
7. **The morning summary is no longer emailed.** It is still written once a day, into the log of the chain watch's run. Session 250's morning note is the document you read instead.
8. **A waiting session is now one row of `erw_health`** (workflow `local:<machine>`, step `session waits`), where it was an email. It was recorded nowhere but the inbox before.
9. **The Roundup's workflow was not edited.** Its last step still runs `warehouse/health.py alert`, which now prints the line and sends nothing.
10. **`scripts/notify.py` sends nothing at all,** with or without `--failed`. The flag is kept so a chain that names it still runs.
11. **The older tests that asserted an email were changed to the rule** (51 failed at first, in the tests of sessions 91, 116, 119, 188, 202 and the planner's). None was deleted; each now asserts the record and that no email goes. 19 new tests in `tests/test_session243.py` and three in `tests/test_session202.py`.
12. **The digest and the Roundup were not touched:** they are the product, not alerts.

## For Samuel's ruling

1. **A session stuck on a permission prompt now tells nobody.** The machine is not idle, so no "ready for review" comes either. Before, you got one email. Bring that one back as a third email, or leave it as a row on `/internal/health`?
2. **A failed Roundup sends no email.** It is weekly, not the daily run. Should "the daily run is red" also cover the Sunday Roundup?
3. **A red job that is not the daily run sends no email** (the hourly network, the latest prices, the chain watch itself). It shows on `/internal/health` only. Is that what you meant?
4. **The morning summary: gone from the inbox for good,** or one email a day worth keeping beside the two?
5. **Red every day for the same reason is one email, on the first day.** Would you rather hear once every day the daily run is red?

## Files

- New: `tests/test_session243.py`.
- Changed: `scripts/alert.py` (the two kinds, the gate in `deliver()`, `ready`, the daily run's one email, every other check records), `scripts/duty.py`, `scripts/chain_queue.py`, `scripts/precheck.py`, `scripts/notify.py`, `warehouse/health.py` (the `alert` command prints), `.github/workflows/chain-watch.yml` (one new step; the sending key in two steps only), `docs/machines.md` ("The email rule"), `queue/CHAIN_TEMPLATE.md`, `queue/README.md`.
- Tests changed to the rule: `tests/test_session91.py`, `tests/test_session116_alerts.py`, `tests/test_session119.py`, `tests/test_session188_queue.py`, `tests/test_session188_precheck.py`, `tests/test_session188_idle.py`, `tests/test_session202.py`, `tests/test_planner.py`.
- On this machine, not in git: `runs/session243/` (the dry runs' script and outputs, the test outputs).

## The landing

- Freeze: `python scripts/freeze.py status` exit 0, no freeze. Main pulled and merged before the push. Before snapshot `s243-before`, then the push of `task/243-email-rule`. The check run, the merge, the after snapshot and the comparison are in session 244's report. Expected: 0 differences on the 25 pages (no page, no site file and no table a page reads was changed).
