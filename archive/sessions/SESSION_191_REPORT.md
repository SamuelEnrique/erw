# Session 191 report: the scanner on a schedule on lab-desktop, and its thresholds against the first run

11 October 2026, 07:13 to about 08:25 UTC (beside sessions 185, 192 and 193), unattended, on `lab-desktop`. Branch `wip/191-scanner-review` (`5c68bc8f` and this report) in `C:\Users\Shared\Documents\erw-191`, on this machine only. Model spend USD 0, no model call. No pull. Outputs: `runs/session191/` of the data checkout.

## Read these first

- **NOT LANDED**: this machine cannot push to GitHub (session 185's report, first bullet). Until the branch lands, the scheduled scans run main's version 1.0.0. The difference is one flag and no draft.
- **The scanner is on a schedule here, two ways, both proven today without waiting for the clock.**
  - The data machine's daily run (`ERW data machine daily`, registered by session 185, 10:00 Pacific, 17:00 UTC today) has the step `dm_scanner` after its sync.
  - The runner's daily run (14:00 UTC) queues the day's scan; the worker on this machine takes it.
- **Drafts land in `/internal/findings`, and today none was new.** Today's scan raises 16 flags and 7 drafts, and all 7 are already in the list, so 0 were added. The list still shows 8 (the eighth is last week's CFTC flag, below). The insert of a new draft from this machine was therefore not exercised.
- **Of the artifact and the three uncertain flags, one was caused by a setting, and that one is fixed.** Indiana's "oil and other gases" is the derived sum that holds Indiana's "other gases": one event flagged twice, because the repeat guard asked for the same value. Version 1.1.0 follows a derived table's lineage. No number in `scanner.yaml` changed.
- **The other three are not threshold faults.** The artifact is a price for one customer. The two uncertain records are true of the table as published. The table below says what the rows show.

## The schedule on this machine

| Path | When | Proven today |
|---|---|---|
| `dm_scanner`, a step of `warehouse/run_data_machine.sh` | daily at 10:00 Pacific, after the sync, by the task `ERW data machine daily` | the step's own command by hand, 07:34 to 07:36 UTC: "scan of 2026-10-11: 117 tables, 6813 series, 16 flags, 25 suppressed by known faults, 7 drafts, 0 added, 103.3 s". The run is kept in `runs/scanner/2026-10-11/` |
| `scanner_request` in the runner's daily run, taken by `ERW findings worker` here | the runner starts at 14:00 UTC; the worker asks the queue every minute | one proof request (`scanner-20261011-s191`): queued 07:54:33, taken 07:55:01 by `SU-4QC3QR3`, done 07:59:04 UTC, the same line, 0 added |

- The queue held no scanner request before today, and `erw_health` no row of either step: the runner's run of 10 October came before the scanner landed. Today's 14:00 UTC run writes the first real one (`scanner-20261011`); the proof used another id so that one is still the runner's.
- A day's scan runs twice on this machine (the worker when the runner's daily run queues it, the daily run at 17:00 UTC). The second adds nothing: a flag already raised is never raised twice.
- The worker had stopped before this session and was started again (session 185's report). It starts at log-on only.

## The 17 flags of the first run, read again

- This machine's tables, scan date 10 October: **16 flags, 7 drafts** under 1.0.0. The flag missing against the first run's 17 is the CFTC one (managed money's Henry Hub longs, week to 29 September). The table here already holds the week to 6 October, and the weekly rule looks at the newest settled week only. Its draft is in the list from the first run.
- The 13 flags session 181 judged real: the same rows, the same values. They stand.

| Flag | What the rows say | Raised by a threshold? | Change |
|---|---|---|---|
| DC industrial retail price, record high, USD 321.5 per MWh (the artifact) | The class has **one customer** (`eia:customers:DC:IND` is 1 in every month, 0 in a few). The "price" is one bill over one customer's sales: 38.4 to 321.5 within 26 months; it moved 159.4 in one month. The US industrial price never moved more than 14.3 in a month | No. It passed the old record by 1.84 sigma of the levels (0.5 asked) and 3.2 sigma of its yearly changes. A margin that drops it drops every record of the run but Wyoming's gas | None. Dismiss it at review |
| Utah residential sales, record high, 1.66 TWh (uncertain) | 11.7 percent above July 2024. Customers: 1,283,692 against 1,273,943, up 0.8 percent. Use per customer 1,292 kWh against 1,204 in the highest earlier July (2022). Colorado's residential sales set their own all-time record the same month; Idaho, Wyoming and Montana their highest July; Nevada, Arizona and New Mexico did not | No | None. Not growth: customers explain under a tenth. Heat is likely and not shown: no Utah temperature is held |
| Indiana, other gases, record low, 65,787 MWh in June (uncertain) | Not one low month: 269,327 (March), 268,928 (April), 125,902 (May), 65,787 (June), 133,037 (July). The second month under 100,000 in 25 years (May 2009: 88,633). June still stands at that value after July's release | No. 0.61 sigma where 0.5 is asked; seven real records of the run stand between 0.52 and 0.80 | None |
| Indiana, oil and other gases, record low (uncertain) | The derived sum that holds the row above; the rest of the sum was 42,979 MWh, as in other months | **Yes**: the repeat guard asked for the same value in the two tables | `repeat_follows_lineage`, version 1.1.0 |

- I tried three other measures of a record's margin on all twelve records (the yearly change, the monthly change, the largest swing of 24 months): none separates the one-customer price from the real records without dropping real ones (`record_flags_study.out`).

## What changed (version 1.1.0)

- `findings_scanner.py`: a flag is also a repeat when a table its own table is derived from has a flag of the same rule, date and direction in the same place. The lineage is the header line `# Derived from:` (56 of 77 derived tables carry it), followed through the tables between; the place is the series' `geo` value; a series without one place is never dropped. Each repeat is kept with the flag it repeats in `scan_summary.json` (`repeats_by_lineage`). A flag now stores its `geo`.
- `scanner.yaml`: the key `repeat_follows_lineage: true`, and `version: "1.1.0"`. Every other number is as it was (a test holds that).
- `docs/methods/automated_analysis_scanner.md`: the rule, and a section "The review of the first run (session 191)" with the table above.
- `tests/test_session191.py`: 12 tests.
- Effect, same tables and date: 15 flags in place of 16 (Indiana's sum), the same 7 drafts. The week of Winter Storm Uri over every table (`--date 2021-02-22`): 275 flags and 12 drafts under both versions.

## Checks run

| Check | Exit | Result |
|---|---|---|
| Scan of 10 October, 1.0.0, read only | 0 | 16 flags, 20 suppressed, 7 drafts, 108.7 s |
| The same, 1.1.0 | 0 | 15 flags, 20 suppressed, 7 drafts; 1 repeat by lineage |
| Uri week, 1.0.0 and 1.1.0 | 0, 0 | 275 and 275 flags; 12 and 12 drafts, the same ids |
| `findings_scanner.py --daily` (the step's command) | 0 | 0 added |
| The proof request through the queue | 0 | done in 243 s |
| `tests.test_session191`, `test_session181`, `test_session181_worker` | 1, then 0 | first run: 2 of my new tests failed on their own made-up series (a weekly flag I had not counted on); then 89 tests, 2 skipped |

- **Not run:** the whole test suite; the site build and the review list's browser check (no site file changed).
- **Not verified:** a new draft's insert from this machine (none was new today); the two scheduled starts themselves (14:00 and 17:00 UTC are after this session).

## Found, not changed

- **A one-customer class is not guarded against.** The customers table says which classes are one bill; DC's industrial class is the only one under 200 customers. A guard would be a rule about EIA's retail tables alone. For your ruling.
- **A relabeled series is a new series to the scanner.** The CFTC row's `node` reads "NAT GAS NYME ..." in the first run's flag and "NATURAL GAS ..." in today's table. `node` is part of the key, so the id and the "never twice" guard do not carry across a relabel.
- **The method note says "the newest value"; the record rule takes the extreme among the fresh points** (a month is fresh for 130 days). In a daily scan they are the same point. On a first run they were not: Indiana's June was flagged with July already held and back above the old record.

## Pulls and spend

- Outside hosts: none. Supabase: reads; one row of `analysis_requests` (the proof request), done.
- Model spend: USD 0.

## Decisions made without you

- **No threshold number was tuned.** Each change tried on the twelve records lost real ones. The one cause that was a setting was a rule's reach, and it got a switch.
- **The proof request used its own id**, so today's real request is still the runner's to write.
- **The daily step was run by hand once**, as the task runs it. It reads tables and wrote no table.

## To finish

After the sign-in (session 185's report), and after `wip/192-roundup-repeat`:

```bash
cd /c/Users/Shared/Documents/erw && git fetch origin
.venv/Scripts/python.exe scripts/freeze.py status; echo "exit=$?"
git -C ../erw-191 merge origin/main
node site/scripts/snapshot-live.mjs take before191
git -C ../erw-191 push origin wip/191-scanner-review
git -C ../erw-191 push origin wip/191-scanner-review:task/191-scanner-review
node site/scripts/snapshot-live.mjs take after191        # after the workflow's merge and the deploy
node site/scripts/snapshot-live.mjs compare before191 after191
```

- No site file changes: the comparison should list 0 differences.
- At `/internal/findings`: dismiss the DC industrial price (the artifact). The other seven are yours to rule on.

## The prompt

"Session 191 (long end 1:30): the scanner on a schedule here, daily after the data refresh; its thresholds reviewed against the 17 flags of its first run (the artifact and the three uncertain ones explained and, where a threshold caused them, tuned); drafts land in /internal/findings." Unattended; the rules of CHAIN_OCT8_PROMPT.md; model spend USD 0, no model call; deploys allowed; this is the data machine.
