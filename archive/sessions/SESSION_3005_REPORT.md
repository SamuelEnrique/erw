# Session 3005 report: generation, the first part: the mix

6 November 2026, about 11:45 to 12:00 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **13 drafts added to the review list** (module `deep.generation_pipeline`, state draft), from `warehouse/analysis/findings/deep/generation.py`.
- **From EIA's net generation by state, 2001 to 2025** (each candidate keeps the United States and the state that moved most):
  - **Coal:** 16.6 percent of US net generation in 2025, against 51.0 in 2001. In New Mexico, 20.7 against 84.5.
  - **Natural gas:** 40.9 percent of US net generation in 2025, against 17.1. In Delaware, 86.1 against 23.1.
  - **Wind:** 10.4 percent of US net generation in 2025, against 0.2. In South Dakota, 58.2 against 0.0.
  - **Utility-scale solar:** 6.8 percent of US net generation in 2025, against 0.0. In Nevada, 30.8 against 0.0.
  - **Small-scale solar** (EIA's estimate, 2014 on): 2.1 percent of US net generation in 2025, against 0.3 in 2014. In Massachusetts, 18.7 against 2.0.
- **From the ERW's hourly mix profile (EIA-930), 2019 to 2025:**
  - **Solar from 11 AM to 4 PM:** 32.4 percent of ERCOT's generation in 2025, against 2.5 in 2019. In CAISO, 47.9 against 37.0.
  - **Gas from 5 PM to 10 PM in CAISO:** 38.0 percent in 2025, against 51.2 in 2019. ERCOT's and PJM's evening gas shares fail the window test.
- **Five reproduction scripts printed their expected figures exactly** (three state shares, the two hourly shares).

## What it did

- **`deep/generation.py`:** seven candidates. Of 265 claims, 221 passed; most of them were states.
- **`deep/builder.py`:** a candidate may put a region first by its name (`rank_region`). The state candidates put the United States first, then rank the states by the size of the move.
  - The cap was 13 for this module, so that each of the five state candidates keeps the US and one state.
- **`tests/test_session3005.py`** (2 tests). With sessions 3001 and 3004: 12 passed.

## Decisions made without you

- **A share is of what a state generates, not of what it uses.** The limits sentence says so. DC is left out of small-scale solar: its estimate is about twice what DC generates, which is true but says nothing about the mix.
- **The pipeline is not hunted by year.** `generator_pipeline_by_grid` holds August and September 2026 only, and the hunt's tests need four full years. Session 3007 hunts the pipeline from EIA-860M's operating and retired generators by year instead.

## For Samuel's ruling

- None new.
