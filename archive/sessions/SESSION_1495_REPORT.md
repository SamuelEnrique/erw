# Session 1495 report: the explorers' filters and hovers; the screenshots left for the landing's build

Energy Research Warehouse (ERW), session 1495, chain 158, samueloldlaptop, 6 November 2026, 09:30 to 09:32 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1494-explorers`.

## What it found

- **The filters each explorer needs to answer its question** are there, a GET form each, so every view is an address:
  - The peak premium has the hub, the calendar month or the whole year, and the two years.
  - Demand growth has the grid and the window: the whole year's average hour or its highest hour, the year so far, a month, or a local hour of the day.
  - Interconnection has the queue, positions or MW, and the first and last entry year.
  - The pages saved from the gate's build hold 4, 2 and 4 form controls.
- **Hover on every point**: every figure carries its source in its title or a Tip (`lib/explore/source.ts`). Every chart draws the brand's hover card: the box plot, the line charts and the bar charts (`components/tool/BarsHover.tsx`). `site/scripts/check-explorers.mjs` reads each in a browser and judges tips, hovers and the width at 390 pixels.
- **Not done here: the screenshots at 390 and 1280 and the browser run of `check-explorers.mjs`.** No local server was up between the landing's gates: the gate stops its own. They go to session 1500's landing, on its kept build (its report).

## Decisions made without you

- No filter was added. Each question the thesis chart, the headline figure and the queue table answer is answered by the filters held.

## For Samuel's ruling

- None.

## Done later the same morning (during session 1499, on the local build of main at `04623251`)

- `site/scripts/check-explorers.mjs http://localhost:3897`: **exit 0, 14 of 14 explorer views read, 0 findings**. Every figure has its source in its hover, every chart answers a hover with a card, and every view fits 390 px.
- Screenshots of the three explorers' default views at 1280 and of the peak premium's at 390 (device metrics of a phone): `docs/brand/review-1497/explore-<pp|dg|ic>-1280.png`, `explore-pp-390.png`.
