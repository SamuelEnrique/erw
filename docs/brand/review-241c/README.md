# Session 241, batch C: the one datacenter tracker, and the charts whose colors became tokens

Screenshots in the internal view, a local build of branch `wip/241c-leftovers` at commit `bd780021`, 13 October 2026.
Each is the window (1280 by 900, or 390 by 844), not the whole page, as a JPEG at quality 70 (the folder is 1.7 MB).
`facts.txt` holds, for every page of the session's list at both widths, the page's width against the window's, its
height, and how many tables stand wider than the page outside a scroll frame.

| File | What it shows |
|---|---|
| `datacenters-top-1280.jpg`, `-390.jpg` | /datacenters: the tracker's own top block (three numbers, "What changed this week"), as session 240 left it |
| `datacenters-ercot-1280.jpg`, `-390.jpg` | the section folded in from /datacenters/v2: "ERCOT: large load approved and energized, over time", its sentence, three numbers and chart |
| `datacenters-texas-1280.jpg`, `-390.jpg` | "Beside it: the facilities the ERW holds": the sentence and the table of the 41 Texas sites |
| `grid-mix-years-1280.jpg`, `-390.jpg` | /grid, the Mix view "Year after year": a line a year, grey to cardinal, from the tokens `--color-year-1` to `7` |
| `grid-network-1280.jpg`, `-390.jpg` | /grid, the network: its palette read from the tokens |
| `deals-tracker-1280.jpg`, `-390.jpg` | /deals, the tracker tab: the bars of deals by month and the chosen view, from the tokens |
| `storage-owners-1280.jpg`, `-390.jpg` | /storage, the owners tab: the bars' labels in the ink token |
| `map-resources-1280.jpg`, `-390.jpg`, `map-projects-1280.jpg`, `-390.jpg` | /map, both tabs |
| `board-1280.jpg`, `-390.jpg` | /board, the top of the page. The chart whose greys moved ("Prior years", in the workbench of a row) is not in a picture: it opens on a click |
| `demand-consumption-1280.jpg`, `-390.jpg` | /demand, the consumption view, at "Where industrial and commercial load is growing fastest" |

**Three pages scroll sideways at 390 in these pictures' build** (`facts.txt`, the lines marked SIDEWAYS):

- `/demand?view=consumption`: the page is 448 px wide in a window of 390. `demand-consumption-390.jpg` shows it: the two
  tables run past the right edge. They stand in a scroll frame since this session, but inside a grid, whose items take
  the width of their content. The commit after these pictures adds `min-w-0` to the two items. It was not built and not
  looked at in a browser.
- `/deals` (534 px) and `/deals?tab=companies` (611 px): not diagnosed. No table stands outside a frame on either.

No "before" picture is here: the pages as they stood are on production, behind `/internal/open`.
