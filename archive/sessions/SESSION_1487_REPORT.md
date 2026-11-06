# Session 1487 report: the battery's replication, in Python

Energy Research Warehouse (ERW), session 1487, chain 158, samueloldlaptop, 6 November 2026, 08:46 to 09:00 UTC (while session 1486's gate ran). Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1487-replication`, cut from `wip/1486-ask`.

## What it did, with commits

- `55e715dfb`: `replication/battery/`.
  - `replicate.py` (standard library) reads only the page's public download, the default case's hourly dispatch (`site/public/battery/erw_2026_battery_dispatch.csv`, served at `/battery/erw_2026_battery_dispatch.csv`; a path or the address is accepted), and `assumptions.json`. It recomputes the page's headline figures with the page's own published mirror (`erw_2026_battery_replication.py`, the do-file's steps line for line), its constants set from the assumptions. It prints each figure beside the one the page shows for the same months, with the difference and whether it is inside the tolerance (half of the page's last shown digit). Exit 0 when all are inside.
  - `assumptions.json`: the page's ten defaults, each with its unit and source (Lazard LCOE+ June 2025; the owner's rulings of 12 October 2026).
  - `page_figures.json`: the 22 figures the page shows for the file's months (2023-10 to 2026-09, the last twelve 2025-10 to 2026-09), each with its check key's stat and its tolerance. The values are from the page and its library on those months (`docs/reviews/packs/battery.md`, part 8).
- Tests: `tests/test_session1487.py`. Every figure is inside its tolerance (22 of 22) and the script exits 0. The assumptions drive the figures: at the old 60 percent debt share the debt payment is the method note's 6,783,357, and the revenue does not move. The assumptions file equals the mirror's own defaults.

## Found

- **22 of 22**: the last twelve months USD 81.40 per kW (8,140,219 for 100 MW; energy 5,459,858, ancillary 2,680,361, each product to the dollar), 33 percent from ancillary services, debt payments 2,261,119, coverage 2.63, NPV USD -697.80 per kW, IRR -8.8 percent, toll 4.19, a bad month 475,477 (December 2024), the 2024 and 2025 bars.
- The public file's months end in September 2026. The page's own last twelve months move with the live set (October 2026 is now whole), so the page today may show a later window than the file. The replication meets the page's figures for the file's months, which is what a reader can rebuild. Exporting the file again needs the data machine's tables (`warehouse/derived/battery_dispatch_export.py`), and this chain writes no warehouse data.

## Decisions made without you

- The replication reuses the page's published mirror rather than writing the steps a second time: one set of steps, the do-file's, kept line for line.
- The page's figures are recorded for the public file's window (the figures a reader can check), not today's window.

## For Samuel's ruling

- Whether the public dispatch file should be exported again each month, by the data machine, so the page's window and the file's agree. It is a scheduled job, the owner's to add.
