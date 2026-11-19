# Session 8205 report (chain 502, lab-desktop second window)

19 November 2026, 11:36 to 11:50 UTC. Opus 5.5. Model spend: USD 0. Parts B and C checked at the start: both still waiting.

## Family 5, balancing authorities one by one: 19 drafts

- `docs/findings/authorities/`, loaded in state draft; second pass 19 of 19 reproduce; 19 of 19 do-files hold.
- Every authority with a mean demand of at least 500 MW: the mean hour, the peak hour (a lone spike, an hour more than 10 percent above both neighbouring hours, dropped first), net generation against demand; and the mix as EIA-930 can show it since 2018, the CO2 per MWh generated and coal's share of that CO2 (`eia930_all_emissions`, which holds the seven grids' authorities only).
- 135 claims, 69 pass, the five largest movers of each measure kept.
- The three strongest:
  - Grant County PUD's mean hour of demand: 769 MW in 2025 against 612 MW in 2019; its peak 1,053 MW against 846 MW.
  - Arizona Public Service's mean hour: 4,433 MW in 2025 against 3,385 MW in 2019.
  - ERCOT's generators emitted 315 kg of CO2 per MWh in 2025 against 408 kg in 2019.

## Checked by hand and left out

- Arizona Public Service's 2025 highest hour, 10,529 MW on 13 February at 22:00 UTC, stands 24 percent above the next hour of the year (8,499 MW in August): a lone spike. The spike rule drops it; the draft reads 8,499 MW.
- WAPA's Rocky Mountain region stepped up about 700 MW of mean demand from 2022 to 2023 while Public Service of Colorado fell about 440 MW. A change of footprint cannot be ruled out from these rows, so neither is drafted.

## A duplicate of chain 164 found after loading (for Samuel's ruling)

- Session 8202 drafted the Southeast's and Tennessee's winter peak against summer's (`scan-deep-52399852db2c`, `scan-deep-31425ae0f32b`). Chain 164 already holds the same story for Southern Company and TVA, the same authorities, by top days (`docs/findings/demand/winter-vs-summer-ba-soco.md`, `-tva.md`). This window does not change a draft's state or delete a row by hand. Default: the two are dismissed at `/internal/findings` by Samuel; later runs skip them (`regions.py`, `SKIP`).

## Code

- `warehouse/analysis/findings/deep/authorities.py`, and the fold in `regions.py`, on `wip/8202-findings` (`1dac16e73`).

## Needs the key

- Nothing.
