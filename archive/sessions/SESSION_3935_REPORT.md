# Session 3935 report: the five tools' requests 1 and 4

Energy Research Warehouse (ERW). Chain 267, data machine (lab-desktop), 14 November 2026, 09:56 to 10:09 UTC. Opus 5.5. Model spend USD 0. Requests: none to a publisher (the live set read with the anon key by `price_years.py --live`).

## Request 1: `battery_stack_monthly`, ERCOT's October 2026

- **The cause, found:** ERCOT's reserve prices (`ercot_as_prices`) end at 2026-10-31T04:00:00Z, 30 October in Texas. The daily run keeps them there: its step is skipped as "stale at source" under ruling 2 of 6 November (ERCOT's `/misapp` paths, which its robots file disallows, are not asked again).
- **The fault:** `build_market` went through local days only to the last ancillary day, so 31 October was never looked at and counted neither solved nor left out (day-ahead 30 + 0 of 31, foresight 29 + 1). Not the runner's rolling tables: a build on this machine's whole tables gave the same counts.
- **The fix:** the days run to the end of the local month of the last ancillary hour (no later than the energy), so a day the reserve prices do not reach is left out and counted ("ancillary"). Test 3935 (red on the old code, green now); the 33 test files that name the stack: 442 passed, 57 skipped.
- **Built under the data lock:** 11,634 rows, 12 changed (ERCOT's October counts: day-ahead 30 + 1, foresight 29 + 2, of 31, in all six cases); CAISO unchanged; validated, archived, in coverage.
- **Loaded** (`load.py --only '^battery_stack_monthly$'`): 12 rows changed. Snapshots `before-load-bstack` and `after-load-bstack`: 0 differences.
- **Not changed:** the reserve prices stay at 30 October (the ruling's). ERCOT's November has no ancillary day, so no November row is written.

## Request 4: `price_years_by_window`

- **Built under the data lock** after the stack's load (`price_years.py --live`): 2,754 rows (battery 234, generator 108, datacenter 2,412), **45 proofs equal** against the pages' own arithmetic and a second read of the live set; validated, archived (1,206 rows new or changed, 140 keys deleted), in coverage.
- **Loaded:** 1,346 rows changed. Snapshots `before-load-py` and `after-load-py`: 0 differences.
- **The daily run:** not joined. A daily build would need a load after the runner's; left as it is (built by hand).

## Decisions made without you

- **The loads used the branch's `coverage.csv`, copied in for the load and put back** (`runs/c267/load.sh`): main's coverage did not yet describe the new builds, and the loader refuses stale coverage.
- **`price_years_by_window` stays out of the daily run** (the request leaves it to window A): its build reads the live set, which only a load moves.

## For Samuel's ruling

- None new. (Ruling 2's hold on ERCOT's reserve prices is what ends ERCOT's stack at October.)
