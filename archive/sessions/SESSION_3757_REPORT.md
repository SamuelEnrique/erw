# Session 3757 report: the daily run's three failing connectors

Energy Research Warehouse (ERW). Chain 211, session 8 of 24, data machine (lab-desktop), 12 November 2026. Opus 5.5. Model spend USD 0. Requests: 3 to IMF PortWatch's ArcGIS host (the service, its layer, one statistics query), no other.

- **`ercot_as_prices` under ruling 2** (`5af8b5e07` on `wip/c211-code`):
  - The connector's two reports (NP4-181-ER and NP4-188-CD) are listed and served under `/misapp` and `/misdownload`, which ERCOT's robots file disallows. The list answered HTTP 503 on 5 and 6 November.
  - The connector now asks ERCOT for nothing. It keeps the table as held (rebuilt from the ERW's own archive bucket when the machine has none, so the rollup, the board and the battery stack still read it) and exits `ERW_SKIP_EXIT` with "stale at source" and the ruling named. `warehouse/health.py` counts that as stale, not as a failure.
  - `--offline` still rebuilds from the saved raw files.
  - The method note (`docs/methods/capacity_and_ancillary.md`) says so.
  - `tests/test_session3757.py`.
- **`eia930`** (`a0a9f05e8`):
  - On 5 November EIA held no day-ahead forecast for CISO and PJM on 1 November (the clock change's day). The whole-window rule failed both demand tables every run (143 of 168 hours), as it had failed SWPP's in session 36A.
  - Every BA's demand table is now checked per UTC day: the day is a gap row, its earlier rows kept, the other days written, never filled.
  - `complete_days` also counts a core variable the window holds but a day lacks entirely as that day's hole. Before, a variable with no row at all that day was not seen.
  - Tested.
- **`portwatch`: no fault of ours.**
  - The 5 November failure was the ArcGIS host's HTTP 400 "Invalid URL", its generic answer: it gives the same to `/robots.txt`.
  - On 12 November the same query answered normally, and the publisher holds all three chokepoints to 8 November.
  - No code changed. The held table ends 25 October and catches up at the next run.
- **The next run's health** is read by session 3771.

## Decisions made without you

- **`ercot_as_prices` marks itself stale instead of failing.** "Stale at source" is the health table's word for a table that is not refreshed for a reason outside the run, here the ruling. A failure would count against the streak every day for a decision the owner made.
- **The demand rule was widened to every BA**, not just CISO and PJM, because the same publisher gap can hit any of them. That is session 36A's reasoning, applied once instead of BA by BA.

## For Samuel's ruling

- **ERCOT's other `/misapp` pulls** (ten connector files, `iso_prices.py` among them) are the "legacy the owner will review" of ruling 2. They are unchanged. Recommendation: register for ERCOT's public API key, after which they can move off `/misapp`. Default taken: unchanged.
