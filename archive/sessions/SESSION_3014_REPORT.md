# Session 3014 report: oil and products, the second part: the US in the world, its refineries, its demand

6 November 2026, about 12:33 to 12:40 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **6 drafts added to the review list** (module `deep.oil_products_world`, state draft), from `warehouse/analysis/findings/deep/oil_world.py`:
  - **The US share of world liquids production:** 22.3 percent in 2025, against 14.5 in 1993.
  - **The US share of world natural gas plant liquids:** 50.6 percent in 2025, against 28.4 in 1993.
  - **US operable crude distillation capacity:** 18,181 thousand barrels a day in 2025, against 15,671 in 1985.
  - **The crude US refineries ran:**
    - Sulfur: 1.299 percent by weight in 2025, against 0.912 in 1985.
    - API gravity: 33.75 degrees, against 32.46 (a lighter crude).
  - **Finished motor gasoline supplied:** 8,933 thousand barrels a day in 2025, against 9,325 in 2017, the first year the ERW's table holds.
- **Four reproduction scripts printed their expected figures exactly.**
- **Rejected by the tests:** distillate, jet fuel, propane and residual fuel oil supplied all fail the typical-move floor or the window test; 2017 to 2025 holds 2020.

## What it did

- **`deep/oil_world.py`:** ten candidates built on two rules (`compute`: a series' yearly mean, or one series' months summed over another's, the months that hold both). The scripts follow the same rules. `tests/test_session3014.py` (1 test, passed).

## Decisions made without you

- **The US share of world crude alone (code 57) is not asked.** Its first year, 1973, and its last are near the same share, and liquids (code 53, from 1993) carry the change.

## For Samuel's ruling

- None new.
