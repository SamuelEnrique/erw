# Session 3003 report: prices, the third part: the fuels and carbon

6 November 2026, about 11:35 to 11:50 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **11 drafts added to the review list** (module `deep.prices`, state draft), from `warehouse/analysis/findings/deep/fuels_carbon.py`:
  - **Europe's and Japan's gas against US gas** (World Bank Pink Sheet, counted from 2000). Europe's index was USD 8.44 per MMBtu above the US index in 2025, against 0.45 below in 2000. Japan's LNG import price was 8.51 above in 2025, against 0.40 in 2000.
  - **What homes pay above the citygate price:**
    - California: USD 15.51 per Mcf in 2024, against 3.96 in 2001. Strength 22.4 typical yearly moves, the strongest claim of the chain so far.
    - Vermont: 16.98 in 2025, against 6.54.
  - **What power plants pay against citygate:**
    - Nebraska: plus USD 2.34 per Mcf in 2025, against minus 0.23 in 2002.
    - West Virginia: minus 3.20 in 2024, against minus 0.39.
  - **What industry pays against citygate:**
    - California: 7.85 in 2024, against 0.47 in 2001.
    - Michigan: 4.56 in 2025, against 0.95.
  - **California's carbon allowance auctions:** USD 28.05 per tCO2 on average in 2025, against 12.83 in 2013.
  - **California's LCFS credits:** USD 59.26 per tCO2 on average in 2025, against 191.60 in 2019.
  - **Brent over WTI at Cushing:** USD 3.58 per barrel on average in 2025, against minus 1.04 in 1988.
- **Six reproduction scripts, one of each kind,** printed their expected figures exactly from the main checkout's tables.

## What it did

- **`deep/fuels_carbon.py`:** nine candidates on public tables with their Python and Stata scripts. Of 156 claims, 104 passed. Most of those were states, and two were kept for each candidate. **Henry Hub's winter premium** fails the typical-move floor.
- **`deep/builder.py`:** `first_words` says what the first year is when it is not the first year the ERW holds. The Pink Sheet comparisons are counted from 2000, and their sentence now says so.
- **`tests/test_session3003.py`** (2 tests). With sessions 3001 and 3002: 12 passed.

## Decisions made without you

- **The Pink Sheet comparisons are counted from 2000,** although the ERW holds both series from 1960. A claim from 1960 would compare two prices from before any LNG trade linked them. The sentence names the year as the comparison's first, not as the first the ERW holds.
- **No claim is about another country:** Europe's and Japan's prices appear only as a premium over the US price.
- **The industrial candidate's limits sentence says EIA's industrial price covers only gas sold by utilities.** I wrote it from EIA's definition as I know it; session 3017's check should confirm it against EIA's own notes.

## For Samuel's ruling

- None new.
