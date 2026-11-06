# Session 1461 report: fault 41, the chart of the day with a hover on each point

Energy Research Warehouse (ERW), session 1461, chain 150, samueloldlaptop, 6 November 2026, 04:41 to 04:46 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; no web request. Branch `wip/1461-periodicals`, cut from `wip/1460-periodicals`.

## The fault

Fault 41 of `docs/reviews/periodicals-faults-2026-11-05.md`, "in part" after chain 149 (session 1449 gave the picture a hover with the caption's figures; the point-by-point hover needed the series on the page, which the record did not hold):

- Faulted: the chart of the day is a PNG on the page (`docs/digest/charts/<date>.png`); the owner's rule is that nothing reads as an image and a hover answers with values.
- Written instead: the page draws the chart from its record (an inline SVG), each point a circle whose hover reads, for 23 October's kind of chart, "2026-06-01: 251.0 kbbl".

## What it did, with commits

- `524932f41`:
  - `warehouse/analysis/findings/daily_chart.py`: `chart_points(chart, unit)` keeps the series the card draws (x labels, each series' values with a non-number as null, the unit from the flag, the chart's decimals; the last 400 points), or None for a chart of another shape. `section` writes it into the day's record as `points`.
  - `site/scripts/build-content.mjs`: a record's `points` passes to `digest_charts`.
  - `site/lib/digest.ts`: `chartSvg(points, alt)` draws one line per series (ink, then blue dashed), a circle per point with its `<title>` as the hover (the series' name first when there are two), the axis's highest and lowest value and first and last label, the brand's chart tokens with their values as fallbacks. No style attribute and no script, so the page's CSP holds. "" when nothing can be drawn.
  - `site/lib/markdown.ts`: the image renderer draws `chartSvg` for a chart of the day whose record holds points; otherwise the picture as before (every chart drawn before this session). `site/app/globals.css`: the SVG at the column's width.
- Tests: `tests/test_session815.py` `ThePointsForThePage` (the record keeps the chosen card's points; another shape keeps none; a non-number becomes null); `site/scripts/test-digest-numbers.mjs` "the chart is drawn with a hover on each point" (the hovers, the missing value, the axis, no style or script, two series, the empty cases).
- The faults file: row 41's state and a line for chain 150.

## Checks

| Check | Exit | Result |
|---|---|---|
| `pytest tests/test_session815 test_session232 test_session267 test_session805` | 0 | 74 passed |
| `pytest tests/test_session402 test_session177 test_periodicals` | 0 | 150 passed, 1 skipped |
| `node --import ./scripts/alias-register.mjs scripts/test-digest-numbers.mjs` | 0 | 15 passed |
| `tsc --noEmit` (the main copy's `node_modules` through a junction, removed after) | 2 | 15 errors, every one a module the build generates (`@/content/*.json`) or Next's generated `PageProps` and `LayoutProps`; none in the changed files. The landing gate's build is the type check. |

## Found

- The 25 chart records on main hold no points (each written before this session), so no page changes until the first chart drawn after the landing; the next weekday run's chart is the first. The record grows by the series (180 points in the fixture: about 4 KB).

## Decisions made without you

- 400 points at most on the page (the last ones); a record that cannot be drawn keeps the picture.
- The SVG shows only the lowest and highest values and the first and last labels on its axes: the hover carries each point's figure.

## For Samuel's ruling

- None.
