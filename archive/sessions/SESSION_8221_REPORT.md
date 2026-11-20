# Session 8221 report (chain 502, lab-desktop second window)

19 November 2026, 13:02 to 13:06 UTC (read from the clock). Opus 5.5. Model spend: USD 0. Parts B and C checked at 13:01: both still waiting.

## Part D, second round: other_us 2 drafts, markets_operations 3 drafts

- `usgs_comcat_earthquakes_south_central` (USGS ComCat, magnitude 2.5 and above, 2010 to October 2026; 16,000 rows, the true count, not a cap): the year's earthquakes of magnitude 3 and above by the state the catalog names (`deep/misc502.py`). No sentence says why.
  - New Mexico: 83 in 2025 against 5 in 2010.
  - Texas: 67 in 2025 against 9 in 2010.
- `nrc_reactor_status` (the NRC's daily status, 2020 on): the year's mean daily power level.
  - The US reactor fleet: 91.1 percent of full power in 2025 against 89.4 in 2020.
  - Watts Bar 1: 68.5 percent in 2025 against 90.1; Surry 1: 76.7 against 100.0.
- Folded: Sequoyah 2 (chain 164's reactor outage days).
- Every draft of both families reproduces (26 and 20 of them); every new do-file holds.

## Code

- `warehouse/analysis/findings/deep/misc502.py` on `wip/8202-findings`.

## Needs the key

- Nothing.
