# Session 8225 report (chain 502, lab-desktop second window)

19 November 2026, 13:18 to 13:21 UTC (read from the clock). Opus 5.5. Model spend: USD 0. Parts B and C checked at 13:18: both still waiting.

## Part D: world_power, 3 drafts (France's grid)

- `rte_eco2mix_france_halfhourly` (RTE's eCO2mix national data, 2020 on, 1.4 million rows; no draft had read it): the year's mean output of each source and nuclear's share of production (`deep/rte502.py`). RTE's physical exchanges are not read: the table does not say which sign is an import.
  - Solar: a mean of 3,712 MW in 2025 against 1,419 MW in 2020.
  - Wind: 5,663 MW against 4,518 MW.
  - Gas-fired: 1,871 MW against 3,924 MW.
- Nuclear's mean output, its share and consumption did not pass the tests (no change larger than a typical yearly move).
- 3 of 3 reproduce (session 8223's 16 world_power drafts reproduced then); 3 of 3 do-files hold.

## Code

- `warehouse/analysis/findings/deep/rte502.py` on `wip/8202-findings` (`914604047`).

## Needs the key

- Nothing.
