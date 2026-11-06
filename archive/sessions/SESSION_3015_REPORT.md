# Session 3015 report: oil and products, the third part: regions, the pump, propane, the chokepoints

6 November 2026, about 12:36 to 12:45 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **4 drafts added to the review list** (module `deep.oil_products_world`, state draft), from `warehouse/analysis/findings/deep/oil_regional.py`:
  - **California's pump premium:** regular gasoline in California was USD 1.312 a gallon above the US average in 2025, against 0.998 in 2019, the first year the ERW's regional table holds.
  - **The Gulf Coast's discount:** regular gasoline on the Gulf Coast (PADD 3) was USD 0.420 a gallon below the US average in 2025, against 0.320 below in 2019.
  - **Diesel against gasoline:** US retail diesel was USD 0.563 a gallon above regular gasoline in 2025, against 0.002 below in 1995.
  - **Propane against crude:** Mont Belvieu propane was 48.0 percent of WTI's price a barrel in 2025, against 71.0 percent in 1993.
- **The chokepoints: nothing drafted.**
  - Tanker transits through the Strait of Hormuz, the Suez Canal and the Panama Canal (IMF PortWatch, 2019 to 2025) fail the hunt's tests: Hormuz's rise from 15,325 in 2019 to 17,585 in 2025 fails the half-change test, and Suez and Panama fail the floor.
  - The table is held internal. Had a claim passed, its sentence and title would have begun "License needed", naming the table (`license_note` in the builder, with a test).

## What it did

- **`deep/oil_regional.py`:** four candidates.
  - California and PADD 5 tell one story (California is most of PADD 5), so the West is one area, and the gas premiums rank by strength.
  - `tests/test_session3015.py` (2 tests). With session 3001's: 9 passed.
- **`deep/builder.py`:** `license_note`, the words a held table's draft puts before its figure. They also go in front of its title and into `hunt.license`.

## Decisions made without you

- **The Gulf Coast's sentence reads "above the US average was -0.420".** It is correct but awkward, and session 3017's check can reword the template for a negative gap.

## For Samuel's ruling

- None new.
