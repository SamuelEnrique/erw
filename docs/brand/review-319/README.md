# Session 319: cold_2026, the prices page's day-ahead cells, the deals pages at a phone's width, the board's moves

Energy Research Warehouse (ERW), 19 October 2026. This folder is for shots at 1280 and 390 px, before (production,
as session 318's landing leaves it) and after (this session's local build), each of the page's `main` element, in
the internal view. The shots are taken by `runs/chain_oct19/s319_build.sh` (the session's report, "To finish"): the
machine stopped that script for low memory before it ran, so the folder holds this README alone until it is run.
A pair is `<name>_before_<width>.png` against `<name>_after_<width>.png`; the new page has no before.

What to look at:

- `cold2026_after_*`: `/events/cold-2026`, the ninth event page on the cold_2025 template: the window 23 January to
  2 February 2026, the six grids of the Elliott page, ERCOT's hub in full and the four hubs of the history table, the
  baseline the same weekdays 364 and 728 days earlier, the event study, the charts through the shared time chart.
- `events_*`: `/events`, the ninth card (PJM's highest hour, a Num).
- `prices_*`: `/prices`, the day-ahead column: where the table holds no row of the last day the cell says the newest
  hour held (ERCOT, NYISO, ISO-NE, MISO on 19 October), where it does the hour's price as before (CAISO, SPP).
- `deals_*` and `companies_*`: `/deals` and `/deals?tab=companies` at 390: no sideways scroll; the "Deal type",
  "Niche" and "Sector" selects no wider than the page (before: 534, 611 and 515 px).
- `board_*`: `/board`, every move in the ink with its sign written, as `docs/brand.md` says (before: a green down).

`runs/chain_oct19/probe_wide319.mjs` (run by `s319_build.sh` on five pages at 390) should list no element past the
viewport on either deals page.
