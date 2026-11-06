# Session 3129: chain 169's eighth session (its 3073): out of scope, marked (class 9)

Personal laptop, second window, 6 November 2026, 13:51 to 13:58 UTC. Opus 5.5. Branch `wip/3129-policy` cut from `wip/3128-policy`.

## What it did

- `warehouse/policy/fields.py`: a field `scope` (a new column of `policy_actions`, beside the others, widened as the earlier ones), by a written list: personnel boards, a laboratory's security boundary, electronic reporting rules, fellowships and scholarships. Marked, never dropped.
- `warehouse/policy/monitor_site.py`, `site/lib/policymonitor.ts`, `MonitorView.tsx`: the record carries its newest document's `scope`, shown under its status with the rule as hover.
- A test (`test_out_of_scope_is_marked_by_a_written_list`); `site/data/policy/monitor.json` rebuilt; the audit's class 9 rows and a section.

## What it found

- 12 documents (10 records) of the archive's copy marked, every one scored 0 to 2. The second read's totals: 206 before, 22 left.
- **The backspace trap again**: the regular expressions of the list, written through a Python heredoc whose string was not raw, got backspace characters for `\\b`; the test caught it (nothing marked), they were replaced, and every file this chain changed was scanned for control and dash characters (none).
- Tests: 60 passed, 1 skipped (fields, monitor site and page, session 157, check_policy); Node 52 of 52; `check_policy.py` 288 of 288.

## Decisions made without you

- **Mark, not drop**, until you rule (chain 166's question 6).

## For Samuel's ruling

- None new.

## Cost

- Model: none (USD 0.00).
