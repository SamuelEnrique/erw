# Session 8217 report (chain 502, lab-desktop second window)

19 November 2026, 12:47 to 12:50 UTC (read from the clock). Opus 5.5. Model spend: USD 0.

## Part D, second round: gas, 10 drafts (pipeline capacity between states)

- `eia_state_to_state_capacity` (EIA's State-to-State Capacity, 1990 to 2025; no draft had read it): the summed capacity of the natural gas pipeline crossings into and out of each state (`deep/gas502.py`).
- The three strongest:
  - Out of Pennsylvania: 32.11 bcf a day in 2025 against 11.79 in 1990.
  - Out of West Virginia: 25.38 bcf a day in 2025 against 7.87 in 1990.
  - Into Louisiana: 48.23 bcf a day in 2025 against 21.94 in 1990.
- Not drafted: `eia_gas_consumers_state_annual`'s residential customer counts mix units across years (Arizona: 1 thousand in 1986, 1,396 thousand in 2024).
- Every gas draft reproduces (27 of 27); 10 of 10 new do-files hold.

## Code

- `warehouse/analysis/findings/deep/gas502.py` on `wip/8202-findings` (`0258ae10b`).

## For the data machine

- `eia_gas_consumers_state_annual`: the early years' residential customer counts are not in the unit of the later years (Alaska 66 in 1986).

## Needs the key

- Nothing.
