# Session 3714 report: the thin page-file rebuild

Energy Research Warehouse (ERW). Chain 208, session 15 of 20, portable laptop, 6 November 2026, about 23:00 to 23:04 UTC (during session 3706's gate). Branch `wip/3701-sellable`, commit `c868a4035`.

- **The root cause, in the runner's restore step:**
  - `warehouse/scheduled.py` lists each builder's input tables; the runner restores the named ones it may and skips a builder whose inputs are missing.
  - `mix_profile` reads `caiso_fuel_supply_history` for California's hydro gap (October 2019 to August 2020), and the list did not name it.
  - On the runner it was absent and unnamed, so on 6 November the builder wrote CAISO's mix from 90 months to 80.
- **The fix:**
  - `mix_profile` names `caiso_fuel_supply_history`, so a machine without it skips the step and the page keeps its copy. It is not asked of the archive: session 114's rule for this builder, which `tests/test_session114_part2.py` holds.
  - `scripts/never_thinner.py --staged` in the daily commit step puts back, as main has it, any staged page file whose first period moved later or that lost a month main holds (the energy mix, Clean, the curtailment profile, the board's hourly files). Each is named in the log.
- **Test:** `tests/test_session3714.py` (6 tests, OK). It fails on a shorter history, including the real thinned `site/data/mix/caiso.json` of `e2794ff06` against its parent's (skipped in a shallow clone). With the 10 files that read `scheduled.py`: 187 tests, OK.

## Decisions made without you

- My first fix also restored the table from the archive. `test_session114_part2` refused it: this builder's inputs are never asked of the archive. The restore was dropped and the rule kept.
- A file whose newest month alone is withdrawn is not "thinner": a month rebuilt as not yet whole may leave.

## For Samuel's ruling

- None new.
