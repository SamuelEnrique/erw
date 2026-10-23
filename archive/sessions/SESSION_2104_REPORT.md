# Session 2104 report: the gate's own item, and the rulings' state

23 October 2026, about 19:13 to 19:22 UTC, unattended, on portable-laptop (the code machine), from the main checkout. Chain `queue/done/084-day-23-october-portable-deals-4.md`, session 2104. Model Fable 5.1. Precheck 0. Model spend USD 0. No warehouse data written; no request but GitHub.

## Read these first

- **Rulings item 10 was done before this chain**: `tests/test_session705.py` on main already carries session 718's mechanics (lines 56 to 70): it looks for `interconnection_durations.csv` in `runs/archive_restore` and `warehouse/output` of this checkout and of the main one, falls back to Berkeley Lab's file, and skips when neither is on the machine. Run alone on this machine, where the table is not held, it passes (5 passed, 2.0 s). No branch was cut; the chain's `wip/2104-deals` was not needed.
- **The rulings' state** is a new dated section at the end of `docs/reviews/deals-rulings-2026-10-23.md`: 7 items open and unchanged (1, 2, 4, 5, 6, 7, 9), item 3 open and done by hand once (session 2101), item 8 answered in practice (chains 083 and 084 write the next file at the end), item 10 done. No owner's answer found: no rulings file newer than 11 October, no reply in a report, the license files unchanged for these publishers.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 2104"` | 0 | on duty |
| `pytest tests/test_session705.py` | 0 | 5 passed |

## Decisions made without you

1. No test change and no branch: the chain's item was already on main, and a change for its own sake would be noise.

## For Samuel's ruling

- The seven open items of `docs/reviews/deals-rulings-2026-10-23.md`, item 7 first.

## Files

- Changed: `docs/reviews/deals-rulings-2026-10-23.md` (the state section).
- New: this report.
