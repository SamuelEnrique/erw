# Session 2712 report: no held table left to describe (the unlanded chains' eight only)

25 October 2026, about 17:06 UTC, on lab-desktop (the data machine), chain 136, unattended. Precheck passed (`runs/c136/pre2712.out`). Model spend USD 0. Pulls: none.

## Read these first

- **8 of coverage's 589 tables have no note on this branch,** counted by code (`runs/c136/undescribed.py`, chain 135's, copied). A table counts if no note names it by its file name or on a `Tables:` line.
- **All eight are the unlanded chains' (118 to 120),** as session 2690 found: `cost_of_power_monthly`, `policy_actions`, `policy_reads`, `policy_reads_evidence`, `large_load_rule_reads`, `ercot_all_hub_prices_history`, `iso_hub_prices_history` and `iso_rtm_hub_prices`. They are left alone.
- **This chain's one table so far,** `nspower_ns_load_hourly` (session 2708), is not yet written: its write waits for the data lock, which this machine's daily task holds from 17:00 UTC. Its note is session 2717's, with the chain's other tables.

## Decisions made without you

- None.

## For Samuel's ruling

- None new.

## Files

- New: this report. On the data machine only: `runs/c136/undescribed.py`, `runs/c136/undescribed2712.out`.
