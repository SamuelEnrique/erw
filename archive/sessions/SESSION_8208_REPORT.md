# Session 8208 report (chain 502, lab-desktop second window)

19 November 2026, 12:08 to 12:14 UTC. Opus 5.5. Model spend: USD 0. Parts B and C checked at the start: both still waiting.

## Part D, first pass: 20 drafts in the three families with the fewest

- The families with the fewest drafts were chain 164's emissions_climate (7), coal_uranium_metals (8) and gas (11). Their largest public tables no draft had read (`runs/c502/unread.py`) were read in part A's form (`deep/partd.py`); the drafts go into each family's folder.
- emissions_climate, 9 drafts (`epa_ghgrp_facility_emissions`): the direct emissions reported by each state's power plants in EPA's reporting program, 2015 to 2023 (five largest movers), and the emissions reported for onshore oil and gas production by basin (four).
  - The Permian Basin's reported production emissions: 29.2 million t CO2e in 2023 against 13.6 million in 2015.
  - Illinois's power plants: 38.4 million t CO2e in 2023 against 79.7 million in 2015.
- coal_uranium_metals, 5 drafts (`eia_coal_receipts_annual`): Central Appalachia's share of the coal US power plants received, 1.6 percent in 2025 against 6.1 percent in 2008; the Illinois Basin's, 14.1 against 9.4; truck and conveyor shares; the tonnage-weighted sulfur content, 1.12 percent in 2025 against 0.89 in 2008.
- gas, 6 drafts (`eia_gas_interstate_annual`): each state's net interstate receipts. Pennsylvania: minus 5,459 Bcf in 2024 (it sent that much more than it received) against plus 689 Bcf in 1997; Louisiana turned from a net sender (minus 3,681 Bcf) to a net receiver (plus 1,055).
- Every draft of the three families reproduces from its own script (16, 13 and 17 of them, chain 164's included); all do-files hold.

## Code

- `warehouse/analysis/findings/deep/partd.py` on `wip/8202-findings` (`3406b3257`).

## Needs the key

- Nothing.
