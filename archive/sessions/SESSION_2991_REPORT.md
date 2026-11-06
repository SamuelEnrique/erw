# Session 2991 report: the reactor fleet and the gas balance, second pass

6 November 2026, about 11:42 UTC, on lab-desktop (the data machine, its first window), chain 162, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Neither table's inputs are newer, and both are behind their publishers:**
  - **`eia_gas_storage_weekly` ends at the week of 16 October 2026.** The supply refresh (`warehouse/refresh_supply.sh`) runs once a week, on Saturdays (UTC). `erw_health` shows its run of 24 October (all steps ok) and nothing on 31 October: that day's daily run stopped at its first step (the merge tests, chain 147). Saturday 7 November's run will fetch EIA's whole history again. Not a fault of this repository's code.
  - **`eia_nuclear_outages_generator_daily` ends at 21 October 2026.** Its connector (`eia_nuclear_outages_generator.py`, sessions 548 and 549) is on no schedule; the table was pulled by hand.
- **The cross-checks hold as chain 157 wrote them** (the fleet's available energy within 1 percent of EIA-923; the storage regions summing to the Lower 48 within 2 Bcf).

## Decisions made without you

- **No pull run here:** the step derives from held tables; the gas pull is the daily run's on Saturday.

## For Samuel's ruling

- **Whether the per-reactor outages table should be on a schedule** (it is pulled by hand; 16 days behind).
