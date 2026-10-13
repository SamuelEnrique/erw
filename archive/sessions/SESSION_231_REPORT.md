# Session 231 report: the findings pipeline, proven end to end

13 October 2026, 04:06 to 04:20 UTC (the night of 12 October, Pacific), unattended, on lab-desktop (the data machine), the first session of the chain of 12 October, night. Branch `task/231-232-pipeline-daily-chart` (it lands with session 232). Model spend USD 0 (no model call). No table was written; the only writes to Supabase were queue rows and one throwaway copy of a draft, removed again (below).

## Read these first

- **The pipeline works from end to end, with two things that were dead, both fixed.** (1) The worker was alive but had been running the scanner of 10 October (version 1.0.0) since it started on 11 October 07:10 UTC: a running process keeps the code it imported, so session 191's version 1.1.0 (the lineage guard) never ran in it. The worker now loads the findings and the scanner again when their files change, and it was restarted at 04:17 UTC. (2) An approved scanner draft chosen for the Roundup was never found: the Roundup's pick reads committed card files only, and a draft's card is in its row. `roundup_pick.py` now reads an approved draft's card from the review list.
- **The scanner has added no draft since its first run.** 10 October: 8 drafts added (one load, 18:01 UTC). 11, 12 and 13 October: 7 drafts computed by every scan, 0 added, because all 7 are the same flags as on 10 October and each still has an open draft. All 8 drafts are in state "draft": none has been ruled on.
- **Nothing real was approved or chosen.** Approve and "Use in Roundup" were proven on the live site with a copy of the weakest draft under a proof id; the copy and its Roundup choice were deleted afterwards. The review list holds the same 8 drafts, all "draft"; the only Roundup choice held is yours of 11 October (W41, `peak_hour_moved`).
- **One gap is left for session 233:** the site has no "Use in Roundup" button on an approved draft (the card on `/analysis` under "Found by the scanner" is drawn without it), so today the choice of a draft can be made only by a request to `/api/analysis`. Session 233 adds the button at `/internal/findings`.

## What ran, step by step

| Step | How it was proven today | Result |
|---|---|---|
| The runner's `scanner_request` | the health table `erw_health`, step `scanner_request`, and the queue rows it wrote | ok on 11 October 15:48 UTC and 12 October 15:14 UTC (workflow "daily prices", under a second each); rows `scanner-20261011`, `scanner-20261012`, both done. The run of 13 October has not happened yet (about 15:00 UTC) |
| The findings worker | `worker.py --status`; the scheduled task; a scan queued now | task "ERW findings worker" registered, state Running, triggers at log-on and at startup (principal S4U, so it starts with nobody logged on), restart on failure every minute (999 times), no time limit, one instance. Process alive (pid 10068 since 11 October 07:10 UTC; 3 requests done, 0 failed). A scan queued at 04:09:27 as `scanner-20261013-s231` was taken at 04:10:12 and done at 04:13:35 |
| Surviving a reboot | the task's triggers and principal, read from the Task Scheduler | configured to (startup trigger, S4U). Not tested by a reboot: the machine was last started on 10 October 18:20 UTC, before the task was registered on 11 October, and this chain did not restart it |
| `findings_scanner.py --daily` | run here, in the foreground of a background shell | exit 0 in 115 s: 116 tables, 7,246 series, 15 flags, 25 suppressed by known faults, 7 drafts, 0 added; kept under `runs/scanner/2026-10-13/`. The scheduled step (`dm_scanner` in `run_data_machine.sh`) ran ok on 11 October 17:27 and 12 October 17:29 UTC (114 s each) |
| Drafts in `public.scanner_drafts` | read with the service role | 8 rows, all raised 10 October 18:01:40 UTC, all in state "draft" |
| Drafts visible at `/internal/findings` | a GET of the live page with the internal cookie | HTTP 200, 9 draft blocks (the 8 and the proof copy), counts draft 9, approved 0; without the cookie HTTP 404 |
| Approve | POST `/internal/findings/state` on the live site, for the proof copy | HTTP 200, `{"ok":true,"state":"approved","from":"draft"}`; GET `/internal/findings/approved` then listed it (1 approved) |
| "Use in Roundup" | POST `/api/analysis` `{kind: "roundup", card_id}` on the live site, as the button does | HTTP 200, `{"ok":true,"week":"2026-W42"}` |
| `roundup_pick.py` | `roundup_pick.chosen("2026-W42")` | before the fix: "chosen but no card file is committed for it; the rule's chart stands". After it: the card's title, subtitle, three callouts, footnote and source line, 11 lines |

## What was dead, and what was fixed

1. **The worker ran old code.** The worker's scans of 11 to 13 October say "16 flags"; the same scan in a fresh process says 15. The difference is session 191's lineage guard (Indiana's "oil and other" in the derived table repeats Indiana's "other gases" in EIA's): the file with it reached this machine on 11 October 10:15 UTC, three hours after the worker had imported the scanner. Every draft in the list is marked version 1.0.0. Fixed in `warehouse/analysis/findings/worker.py`: before each request the worker compares the newest change time of the folder's code with the one it loaded, and imports the findings and the scanner again when it moved (one log line says so). A change to `worker.py` itself still needs a restart; the same line says that. The worker was stopped through its stop file and its task started again at 04:17:15 UTC (pid 22264).
2. **A chosen draft never reached the Roundup.** `roundup_pick.load_card` read `site/data/findings/<card_id>.json` only. It now reads an approved draft's card from `public.scanner_drafts` (state approved only, service role), and the Roundup's lines for a draft say "approved by a person at the review list" in place of "not reviewed" and link `/analysis`, not a card page that does not exist.
3. **Not dead, but worth knowing:** the review list has not moved because nothing was ruled on. A flag with an open draft is never raised again, so the list stays at these 8 until they are approved or dismissed.

## Drafts by day

| Day (UTC) | Scans | Drafts computed by each scan | Added to the review list |
|---|---|---|---|
| 10 October | the first run (session 181) | 8 | 8 |
| 11 October | 3 (session 191's request 07:55, the runner's 15:48, the data machine's 17:27) | 7 | 0 |
| 12 October | 2 (the runner's 15:15, the data machine's 17:29) | 7 | 0 |
| 13 October, to 04:20 | 2 (this session's request, this session's `--daily`) | 7 | 0 |

The one draft of 10 October no later scan computes: the CFTC's managed-money long position in natural gas, week of 29 September (its week is no longer fresh).

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py` | 0 | lab-desktop on duty; USD 0.00 spent today |
| `python -m unittest tests.test_session231 tests.test_session170 tests.test_session181` | 0 | 88 tests, 1 skipped |
| `findings_scanner.py --daily` | 0 | `runs/session231/daily.out` |
| `worker.py --status` after the restart | 0 | alive, pid 22264 |

## Decisions made without you

1. **Approve and "Use in Roundup" were proven on a copy, not on a real draft.** The copy (`scan-record-000000000231`, the card of the weakest draft under a proof id) was written at 04:09:28, approved at 04:09:31, chosen for W42 at 04:09:32, and both rows were deleted at 04:10:36. No real draft's state or history changed.
2. **The scan queued for the worker has its own id** (`scanner-20261013-s231`), so the runner's request of 13 October is not taken as a duplicate.
3. **The worker was restarted** (stop file, then the task), which the prompt allows when it is not alive; it was alive but running old code.
4. **No reboot** to test the startup trigger: the chain was running on this machine.

## For Samuel's ruling

1. The 8 drafts of 10 October wait at `/internal/findings`. Until they are approved or dismissed the scanner adds nothing that is the same flag.
2. Whether the startup trigger should be tested by a restart of lab-desktop at a time you choose.

## Files

- Changed: `warehouse/analysis/findings/worker.py` (the code it runs), `warehouse/analysis/findings/roundup_pick.py` (an approved draft's card).
- New: `tests/test_session231.py`.
- On this machine, not in git: `runs/session231/` (`prove.py`, `health.py`, their outputs), `runs/scanner/2026-10-13/`.
