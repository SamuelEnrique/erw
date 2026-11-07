# Session 3713 report: a bot's push to main refused when it would make main red

Energy Research Warehouse (ERW). Chain 208, session 14 of 20, portable laptop, 6 November 2026, about 22:55 to 23:00 UTC (during session 3706's gate). Branch `wip/3701-sellable`, commit `4788b3de4`.

- **`.github/workflows/daily-prices.yml`:** the daily commit and the health summary's commit pass `scripts/push_guard.py` before `git push origin HEAD:main`. A red suite:
  - names the failing tests in the log and the run's summary;
  - pushes the commit to `wip/red-daily-<day>` or `wip/red-health-<day>`;
  - records the step failed in `erw_health`. The email rule's one daily red email reads that row: no new notification.
  - The job stays green, so GitHub sends no email of its own.
- **`.github/workflows/weekly-vacuum.yml`:** the same before its push of `run_status.csv`.
- No secret or schedule was changed. The two steps were given the Supabase URL and service key the job already holds, for the one row the guard writes when it refuses.
- **Tests:** the 20 test files that read `daily-prices.yml` or `weekly-vacuum.yml`: 447 tests, OK.

## Decisions made without you

- A refused push does not fail the step: a red scheduled job would make GitHub email its owner, which the email rule does not allow.
- The guard runs on the health summary's first try only: a second try only rebases the same two files onto a main whose own commit was guarded.

## Not done

- **`warehouse/run_data_machine.sh` (the data machine's commit path): the edit was refused by this machine's permission classifier.** It was not tried another way. The exact change (four lines) is in `docs/state/main_red_2026-11-06.md` for the desktop's chain or for Samuel.
- **`.github/workflows/roundup.yml`:** the periodicals chain's file; the same change applies there.

## For Samuel's ruling

- Should the data machine's commit path take the guard (the four lines in `docs/state/main_red_2026-11-06.md`)? Spell 1's trigger was that path.
