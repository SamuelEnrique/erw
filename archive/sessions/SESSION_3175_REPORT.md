# Session 3175 report: coal and uranium (chain 166)

6 November 2026, about 14:08 to 14:15 UTC, on lab-desktop, second window, chain 166, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **8 drafts added to the review list** (module `deep.coal_uranium_metals`, state draft), from `warehouse/analysis/findings/deep/coal.py`:
  - **Uranium of US origin:** 7.3 percent of the uranium bought for US reactors in 2025, against 18.0 in 2003.
  - **What US reactors pay for uranium:** USD 58.46 a pound of U3O8 equivalent in 2025, against 10.81 in 2003.
  - **Enrichment done in the US:** 22.8 percent of the enrichment bought for US reactors in 2025, against 13.9 in 2003.
  - **The delivered price of coal to power plants:** USD 45.85 a short ton in 2025, against 24.68 in 2001.
  - **Wyoming's share of US coal:** 37.2 percent in 2024, against 32.7 in 2001. **Appalachia's:** 30.8, against 38.2.
  - **Coal mined underground:** 40.2 percent of US coal in 2024, against 33.8 in 2001.
  - **Coal per mine employee:** 11,633 short tons in 2024, against 14,629 in 2001.
- **The spot market's share of uranium purchases** fails the typical-move floor.
- **Checked:** all 8 reproduce from their own scripts (`check.py`), and all 164 do-files hold (`check_do.py`).

## What it did

- **`deep/coal.py`** reuses `oil_world.py`'s two rules and its script templates. `tests/test_session3175.py` (1 test, passed).

## Decisions made without you

- **USGS's critical minerals and MSHA's quarterly mines are not hunted this session:**
  - USGS's table holds a few years by mineral.
  - The national figure of MSHA's per-mine table is EIA's, which the production table already holds.

## For Samuel's ruling

- None new.
