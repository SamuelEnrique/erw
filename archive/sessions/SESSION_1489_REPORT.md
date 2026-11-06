# Session 1489 report: the generator's replication, in Python

Energy Research Warehouse (ERW), session 1489, chain 158, samueloldlaptop, 6 November 2026, 08:48 to 08:52 UTC (while session 1486's gate ran). Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1487-replication` (sessions 1487 to 1490 on one branch).

## What it did, with commits

- `0042bdf3f`: `replication/generator/`, in the battery's form.
  - `replicate.py` reads only the page's public hourly file (`site/public/seller/erw_2026_generator_hourly.csv`: ERCOT solar at `HB_HUBAVG` in real time, 2018-07 to 2026-10-03) and `assumptions.json`.
  - It recomputes with the page's published mirror (`erw_2026_generator_replication.py`) and prints each figure beside the page's, with the difference and the tolerance.
  - `assumptions.json`: the page's eleven defaults with their sources (Lazard LCOE+ June 2025 for solar; the hurdle at 12 percent; solar's 0.7 percent degradation, NREL ATB 2025, ruling 7a).
  - `page_figures.json`: the 13 figures the page shows for the file's months, each with its check key, read from a built page's data cells by session 582 (`docs/reviews/replications-2026-10-22.md`).
- Tests: `tests/test_session1489.py`. Every figure is inside its tolerance and the script exits 0. At no degradation, NPV is the method note's -74.16 million, the figure before ruling 7a. The assumptions file equals the mirror's defaults.

## Found

- **13 of 13**: USD 59.85 per kW over the last twelve months; 102.24 and 130.80 for the long-run averages; a price received of 23.27 USD per MWh against a flat 32.17 (72 percent); debt payments 7,078,769 at coverage 0.67; 2,580 MWh per MW; a contract price of 39.14 for 1.25 times; NPV -76.66 million; a breakeven PPA price of 58.36; the worst month (2024-02) 139,298.97.
- The public do-file's comment at line 71 still says "no degradation" (session 264's words). Its step at line 229 applies 0.7 percent a year since session 304, so the figures agree and only the comment is old. Not changed: the public file is the page's download, and its words are the page's.
- The public file is the model's snapshot of 4 October; the page's own last twelve months move with the live set (as for the battery).

## Decisions made without you

- The page's figures are session 582's reading of the built page on the file's months: the newest record of the page's data cells for those months.

## For Samuel's ruling

- None new (the battery's question on exporting the public files again applies here too).
