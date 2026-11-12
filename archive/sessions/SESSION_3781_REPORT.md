# Session 3781 report: the queues, the reactor fleet, the gas balance, second pass (parked 193)

Energy Research Warehouse (ERW). Chain 212, data machine (lab-desktop), 12 November 2026 14:08 to 14:10 UTC. Opus 5.5. Model spend USD 0. Requests: none to any publisher; the archive's bucket under the data lock.

## Read these first

- **One input moved; its table was rebuilt and nothing changed.** `nrc_reactor_status` was refreshed by the data machine's run of 10 November, after `nuclear_fleet_status` was built (6 November).
  - The table was rebuilt under the data lock (14:10 UTC): 15,048 rows, 123 reactors, 2007-01-01 to 2026-10-21, the same rows.
  - Its newest day is set by `eia_nuclear_outages_generator_daily`, which ends 21 October; no step refreshes it (chain 211's session 3767).
  - Validated, put in coverage, archived (`20261112T141027Z-local`, 0 new rows).
- **The other inputs did not move** (the ISO queue snapshots of 20 and 26 October, EIA's storage of 16 October). The catch-up run, which would have brought newer ones, committed nothing (session 3777). `interconnection_queue_summary` and `gas_balance_weekly` are unchanged.
  - `eia_gas_storage_weekly` still ends 16 October. Its refresh is the daily run's Saturday step (14 November).
- **The siting gaps' two rows read against the queue table:**
  - "Generation with a signed interconnection agreement" stays filled from Berkeley Lab's file (the ISO snapshots carry no agreement date).
  - "A large load's own wait" stays open: the queue table is the generators' queue (session 2958's reading holds).
- **`iso_queue_snapshot_summary`'s live-set load,** carried by chain 211's session 3767, was not done. The live set is loaded with the catalogue copied from the branch at the landing (rule 8's snapshot around it), so it waits for this chain's landing.

## Decisions made without you

- **No rebuild on unchanged inputs,** as in session 3780.

## For Samuel's ruling

- None.
