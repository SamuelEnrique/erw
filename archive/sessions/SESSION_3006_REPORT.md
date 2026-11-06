# Session 3006 report: generation, the second part: the fleets

6 November 2026, about 11:46 to 11:55 UTC, on lab-desktop, second window, chain 164 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **11 drafts added to the review list** (module `deep.generation_pipeline`, state draft), from `warehouse/analysis/findings/deep/nuclear_fleet.py`:
  - **The gas-fired fleet's heat rate** (EIA-923): 8.30 MMBtu per MWh in 2024 for the US, against 10.84 in 2001 (strength 28.4). Florida's was 7.48, against 9.39.
  - **The coal-fired fleet's heat rate rose:** 11.02 MMBtu per MWh in 2024 for the US, against 10.63 in 2001. Pennsylvania's was 11.67, against 10.19.
  - **Nuclear's share of net generation:** 17.8 percent in the US in 2025, against 20.6 in 2001. Vermont's was 0.0, against 76.1.
  - **Conventional hydro's share:** Idaho's was 43.6 percent in 2025, against 77.3 in 2001. Vermont's was 49.7, against 16.1.
  - **US nuclear capacity** (EIA's daily figure, the year's mean): 98,276 MW in 2025, against 101,013 MW in 2007.
  - **Two reactors' outage days** (days at least half out): Sequoyah 2 had 186 in 2025, against 4 in 2007. McGuire 1 had 26, against 85.
- **Five reproduction scripts printed their expected figures exactly.**

## What it did

- **`deep/nuclear_fleet.py`:** seven candidates. 276 claims, 109 passed, 11 kept. **The US fleet's outage share** (9.6 percent of capacity in 2007, 9.0 in 2025) fails the typical-move floor.
- **Three faults found on the dry runs, and fixed before loading:**
  - **EIA-923 years were judged partial by their count of plant rows,** which grows over the years. An annual EIA-923 year is whole, so each now counts as one observation.
  - **States whose fleet showed a heat rate outside 6 to 15 MMBtu per MWh drafted first.** Montana's gas was at 70.6 and Idaho's coal at 73.1, where combined heat and power plants' fuel for heat outweighs their generation. Such a state is now left out, and the rest rank by strength.
  - **The reactor candidate drafted a retired reactor (Crystal River 3) and a new reactor's start-up (Watts Bar 2).** It now counts only reactors that report whole years in 2007 and in 2025.
- **`deep/generation.py`** now also knows nuclear (NUC) and conventional hydro (HYC) shares, for this module's two share candidates.
- **`tests/test_session3006.py`** (1 test). With session 3005's: 3 passed.

## Decisions made without you

- **EIA's capacity factors by technology are not hunted.** `eia_capacity_factors_monthly` holds 2023 to 2025 only.
- **A reactor's uprate is not a candidate.** It is a step, its typical yearly move is zero, and the hunt's strength cannot be computed. The US fleet's capacity is a candidate instead.
- **The heat rate uses EIA-923's total fuel consumed.** At combined heat and power plants it includes fuel for heat; the limits sentence says so.

## For Samuel's ruling

- None new.
