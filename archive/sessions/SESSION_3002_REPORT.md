# Session 3002 report: prices, the second part

6 November 2026, about 11:20 to 11:35 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **12 drafts added to the review list** (module `deep.prices`, state draft), from `warehouse/analysis/findings/deep/prices_markets.py`:
  - **The cheapest hour:** the day's cheapest real-time hour at ERCOT's South hub fell, on average, 10.6 hours after local midnight in 2025, against 5.7 in 2015. At the North hub it was 10.7, against 6.0. Strength 10.4 and 8.9 typical yearly moves, the strongest of the chain so far.
  - **Midday against night:** at the West load zone, the midday price (11 AM to 4 PM) less the night price (midnight to 6 AM) was minus USD 27.76 per MWh in 2025, against plus 15.80 in 2015. The sign changed.
  - **The four-hour spread:** the median day's four dearest hours less its four cheapest at the West hub were USD 45.88 per MWh in 2025, against 15.53 in 2015. At the hub average, 36.53 against 14.39.
  - **Wide days:** at the West load zone, 84.1 percent of 2025's days had their highest hour at least USD 50 above their lowest, against 28.8 percent in 2015. North load zone: 54.0 percent in 2025.
  - **Winter's dearest hours:** December to February held 64.8 percent of the West load zone's dearest one percent of hours in 2025, against 12.5 percent in 2015. North load zone: 42.0 percent, against 12.5.
  - **Day-ahead above real time:** the share of hours the day-ahead price was the higher fell to 59.3 percent at the West load zone in 2025, from 66.2 in 2015. South load zone: 60.9, from 67.9.
  - **Henry Hub's daily move:** the median absolute change between trading days was 3.19 percent in 2025, against 2.01 in 1997.
- **Seven reproduction scripts, one of each kind that drafted,** printed their expected figures exactly from the main checkout's tables.

## What it found that is not drafted

- **ERCOT's reserve prices fell steeply** but fail the typical-move floor, because 2021 to 2023 moved more than the change. The day-ahead responsive reserve averaged USD 18.46 per MW-hour in 2018 and 2.76 in 2025. Regulation up went from 13.71 to 2.98. ECRS has three full years.
- **The weekend discount** (81 to 85 percent of the weekday mean in 2025, against 92 to 102 in 2015) and **the morning shoulder** fail the window test or the floor at every hub and zone.
- **Midday against night went negative at every hub except Houston**, but only the West load zone passes the floor.

## What it did

- **`deep/prices_markets.py`:** ten candidates with their Python and Stata reproduction scripts, and `tests/test_session3002.py` (3 tests, every candidate's script against the module on small tables). With session 3001's tests: 10 passed.
- **The hunt's tests decide,** as in session 3001. Seven candidates drafted. Of 78 claims, 36 passed, and 12 were kept by consequence, then strength, two regions a candidate, one story an area.

## Decisions made without you

- **The ERW's own derived peak premium (`ercot_peak_premium_annual`) is not hunted.** It is the measure of a page of the site, so a draft from it would restate the page.
- **Twelve kept rather than ten.** The check sessions (3017 to 3019) fold any two that tell one story.

## For Samuel's ruling

- **ERCOT's reserve prices** (above) fail the hunt's typical-move floor although the fall is about 80 percent. Should a family whose middle years hold one event (Uri, the 2022 to 2023 summers) be tested without them? The hunt's rule says no, so they are not drafted.
