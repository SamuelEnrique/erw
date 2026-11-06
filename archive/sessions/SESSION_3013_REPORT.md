# Session 3013 report: oil and products, the first part

6 November 2026, about 12:23 to 12:40 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **8 drafts added to the review list** (module `deep.oil_products_world`, state draft), from `warehouse/analysis/findings/deep/oil.py`:
  - **Net imports of crude oil and petroleum products:** minus 2,850 thousand barrels a day in 2025 (net exports), against plus 9,440 in 2010.
  - **Canada's share of US crude imports:** 63.4 percent in 2025, against 30.9 in 1973. Nigeria's: 2.2, against 13.8.
  - **Texas's share of US crude production:** 42.2 percent in 2025, against 20.0 in 2001. Alaska's: 6.1, against 32.7.
  - **The gasoline crack** (Gulf Coast conventional gasoline less WTI): USD 19.33 a barrel in 2025, against 2.04 in 1987.
  - **The jet fuel crack:** USD 23.40 a barrel in 2025, against 3.99 in 1991.
  - **From the Gulf Coast to the pump:** the US retail price of regular gasoline was USD 1.080 a gallon above the Gulf Coast spot in 2025, against 0.462 in 1991.
- **Five reproduction scripts printed their expected figures exactly.**
- **Rejected by the tests:**
  - **The diesel crack** fails the half-change test: USD 17.82 in 2007, 27.95 in 2025, with 2022 carrying most of it.
  - **Crude's share of the pump price** (46.7 percent in 1991, 50.3 in 2025) fails the typical-move floor.

## What it did

- **`deep/oil.py`:** eight candidates. A crack is the product in dollars a barrel less WTI on the days that hold both, and its limits sentence says it is not a refiner's margin. `tests/test_session3013.py` (1 test, passed).

## Decisions made without you

- **Brent against WTI is not asked again** (session 3003 drafted it).
- **The import shares count from 1973,** the first year the table holds. Canada's share was lower in 2001 (14.5 percent) than in 1973, and the hunt's tests read every full year between, not only the two ends.

## For Samuel's ruling

- None new.
