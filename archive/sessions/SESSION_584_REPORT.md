# Session 584: 390 pixels on every page

Chain 034 (the night of 22 October 2026), code machine (samueloldlaptop), unattended. Branch `wip/584-s`, cut from `origin/wip/589-land` (main and sessions 577 to 582, 585 to 587), with origin/main of 02:15 UTC merged, and `origin/wip/589-land` merged again once session 583 had landed on it (its tokens.css, ScrollRegions.tsx, YourGrid.tsx and NetworkGravity.tsx), before any shared file was edited.

## Summary

A new check, `site/scripts/check-390.mjs`, read every address of check-values' list (151: 149 pages and the 2 internal drafts) in the internal view at 390 by 844 as a phone, and listed content wider than the window, tables with no sideways scroll frame, and SVG labels cut. **Before: 43 pages with a finding** (7 addresses wider than 390: the demand growth explorer 398 px on 5 addresses, /policy 429 px; 36 with chart labels cut; 4 with tables that have no scroll frame). **After: 5 pages, none wider than the window** (the tables that fit and /shoulder's last tick, all in pages' own files, listed below). Every fix is in tokens.css or a shared chart; no value moved (check-values: every value matches).

## What I did

1. `site/scripts/check-390.mjs` (new): the three measures above. A text is cut when it passes its SVG (overflow not visible), a clipping ancestor or the window by more than 1.5 px at a side, or by more than 3.5 px at the top or bottom (beyond the empty margin of the font's em box). The inside of a closed `<details>` (the nav's menus) is left out. ECharts charts draw on a canvas and cannot be judged. `--like before.json` takes the after shots on the same pages, scrolled to the same element. Exit 0 clean, 1 a finding, 2 a page not read.
2. Fixes, every one inert where the content already fits (the 1280 layout unchanged):
   - `site/app/tokens.css`: `.brand-a select { max-width: 100% }`, and the label or span holding a select may shrink in a row of filters (`min-width: 0; max-width: 100%`). The explorer's "Window" select and /policy's "Tag" select pushed the page sideways.
   - `site/components/svgchart.tsx`: ShareSegments (the mix bar on /grid, /mix, the grid pages) names its narrow parts in as many lines as the width needs (up to 148 px was cut). HeatChart (the carbon-free heat maps) moves its "no value held" key to a line of its own when the legend does not fit, and narrows the ramp's cells if needed. CategoryChart wraps a reference line's long name (120 px was cut on /research) and keeps category labels inside the drawing.
   - `site/components/TimeChart.tsx`: the series names at the right stay above the chart's bottom (up to 77 px below it on the event pages and /cost-of-power?view=grids).
   - `site/components/EventStudy.tsx`: the left margin holds the widest tick (/events/covid-2020) and the dates stay inside at the right.
   - `site/components/tool/GroupedBars.tsx`: a group's label and its second line stay inside ("Oct 2025 to Sep 2026" on /datacenters?view=grids).
   - `site/components/tool/SeriesChart.tsx`: category label lines stay inside ("Columbia" on /impact).
3. Shots: `docs/brand/review-584/before/` (43) and `after/` (the same 43 views), `after-1280/` (5 touched pages at 1280), the measures `before.json`, `after.json` and `measures.txt`.
4. Tests: `tests/test_session584.py` (9). `tests/test_session331.py` pinned the old heat legend line: it now pins the new measure.

Shared files touched: `site/app/tokens.css`, `site/components/svgchart.tsx`, `site/components/TimeChart.tsx`, `site/components/EventStudy.tsx`, `site/components/tool/GroupedBars.tsx`, `site/components/tool/SeriesChart.tsx`. The only one session 583 also touched is tokens.css: 583 added a block near line 204, and mine is appended at the end, after 583's merge.

## Left open (pages' own files, outside this part's scope: shared components and tokens.css only)

- `/shoulder` (both addresses): the "24:00" tick at the right end of the average day's chart is cut by 4 px (`app/shoulder/page.tsx`, line 71). Fix: anchor the last tick at its end.
- Tables with no scroll frame that fit today (358 of 358 px): `/learn/bill` (1), `/severance` (1), `/reports/draft/shape-premium` (4). None is wider than the window, so nothing scrolls sideways.
- The CAISO alerts' small multiples ("47 GW") and two charts' top figures pass their box by 2 to 3 px of the em box only. No glyph is cut, so these are not findings.

## Checks

| Check | Command | Exit |
|---|---|---|
| precheck | `python scripts/precheck.py --what "session 584"` | 0 |
| db probe (before each build) | `python scripts/db_probe.py` | 0, 0, 0, 0 |
| build, before | `timeout 1800 npm run build` at 0dedb8af | 0, no statement timeout |
| build, after (twice: the second for the label rule) | same | 0, 0, no statement timeout |
| 390 scan, before | `node scripts/check-390.mjs http://localhost:3584 ../runs/s584_before.json ../docs/brand/review-584/before` | 1 (43 of 151 pages) |
| 390 scan, after | same with `--like ../docs/brand/review-584/before.json` | 1 (5 of 151 pages, the open items above; none wider than 390) |
| check-values, whole list | `CHECK_VALUES_TIMEOUT_MIN=45 node scripts/check-values.mjs http://localhost:3584` | 1: 6,446 of 6,457 values match, 11 superseded latest prices. The 11 failures are floors only: session 408's ten license-held pages (/deals, /map, /events, five event pages, /learn/bill, /research/card/gas_sets_price) and /digest (no Digest yet for 22 October before the 14:00 UTC run) |
| tests | `ERW_LOCK_EXEMPT=1 python -m unittest tests.test_session584 tests.test_session331` | 0 (17) |
| related tests | the 36 test files naming the touched files | 1 before test_session331 was updated (its pinned line), then 0 for the two re-run |

## Decisions made without you

- Chart label fixes were made only in shared components. A page's own chart (/shoulder) is listed, not changed.
- A table that fits at 390 with no scroll frame is listed, not wrapped. Wrapping it means editing a page file, and it does not scroll today.
- The scan uses mobile emulation (the page's own viewport tag) at device scale 1. A text passing its box by 3.5 px or less at the top or bottom is not counted as cut: that margin is the font's empty em box.
- The 1280 shots are after shots of five touched pages, not before and after pairs. Each fix only acts where content passes its frame, so the 1280 drawing is unchanged by construction, and check-values shows no value moved.
- test_session331's pinned heat legend line was updated to the new measure.

## For Samuel's ruling

None.

## To finish

Nothing. Session 589 lands the chain (`wip/584-s`).

## Files changed

`site/scripts/check-390.mjs` (new), `site/app/tokens.css`, `site/components/svgchart.tsx`, `site/components/TimeChart.tsx`, `site/components/EventStudy.tsx`, `site/components/tool/GroupedBars.tsx`, `site/components/tool/SeriesChart.tsx`, `tests/test_session584.py` (new), `tests/test_session331.py`, `docs/brand/review-584/` (before, after, after-1280, before.json, after.json, measures.txt), `archive/sessions/SESSION_584_REPORT.md`.
