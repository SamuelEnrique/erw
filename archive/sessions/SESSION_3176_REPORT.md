# Session 3176 report: emissions and climate (chain 166)

6 November 2026, about 14:15 to 14:25 UTC, on lab-desktop, second window, chain 166, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **7 drafts added to the review list** (module `deep.emissions_climate`, state draft), from `warehouse/analysis/findings/deep/emissions.py` (counted from 2001; the temperature from 2000):
  - **The power sector's CO2:** 1,532.0 million tCO2 in 2022, against 2,258.7 in 2001.
  - **Its CO2 per MWh:** 362 kg per MWh generated in the US in 2022, against 604 in 2001. In Iowa: 282, against 895.
  - **Shares of US energy-related CO2:**
    - Coal's: 19.2 percent in 2022, against 36.2 in 2001.
    - Power's: 31.0, against 39.3.
    - Transport's: 37.3, against 32.3.
  - **The contiguous US's average temperature:** 2.61 degrees F above its 1901 to 2000 mean in 2025, against 1.24 in 2000.
- **Checked:** all 7 reproduce from their own scripts, and all 171 do-files hold. Two sentences were reworded and corrected in place ("above the mean" said twice; "emissions was").

## What it did

- **`deep/emissions.py`:** six candidates, one of them across two families (CO2 over net generation). `tests/test_session3176.py` (1 test, passed).

## Decisions made without you

- **Counted from 2001,** although EIA's CO2 table runs from 1970: a claim from 1970 would set this century against a different economy.
- **DC is left out of the CO2 per MWh,** as small-scale solar left it out: it generates almost nothing.
- **Not hunted:**
  - NOAA's degree days, which begin in 2024.
  - The drought, wildfire, storm and disaster tables: their link to energy would be a cause this hunt does not state.

## For Samuel's ruling

- None new.
