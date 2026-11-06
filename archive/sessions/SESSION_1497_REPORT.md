# Session 1497 report: the trader path, walked again on a build

Energy Research Warehouse (ERW), session 1497, chain 158, samueloldlaptop, 6 November 2026, 09:56 to 10:05 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to the ERW's own database (the local build's reads) only. Branch `wip/1497-paths`, cut from `wip/1494-explorers`.

## What it did, with commits

- `5778e422a`, corrected in `b25ee38fb`:
  - `site/scripts/walk-paths-1497.mjs`, a reader's path walked in a real browser (the site's own `browser.mjs`, no package): each step's page in the internal view, a screenshot of its first screen at 1280, the first step at 390 by a phone's device metrics, and what the reader sees first (the heading, the first checked figures with their raw values, the "license needed" notes, any error in the page). It reads only.
  - The trader path's twelve steps (`docs/reviews/paths/trader-1497.json`) on a local production build of main at `04623251`; `docs/reviews/trader-path.md`'s section "Walked again on a build, 6 November 2026"; the screenshots in `docs/brand/review-1497/`.

## Found

- **Every figure is what session 585 read on 22 October**: the generator's 59.85, 83.57, 72.23 and 64.04 USD per kW; the battery's 81.40, 58.63, 73.00 and 65.22; the board's holds. The battery page's last twelve months are still October 2025 to September 2026 on 6 November: the page takes a month only when its table holds it whole, so the tables' October is not whole yet (the data machine's).
- No step failed to load or threw an error.
- **A finding withdrawn**: the first walk read the generator page at 481 px wide at 390. That came from a headless window, which does not go under about 480 px. Measured with a phone's device metrics (as `check-explorers.mjs` measures), the page is 390. Corrected in the script and in all three documents the same morning.

## Decisions made without you

- The steps that read the same address further down (04, 08, 12, 16) were read from their pages' figures rather than walked a second time.

## For Samuel's ruling

- None new (the trader path's open items stand as the document lists them).
