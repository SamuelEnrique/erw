# Session 318: the finding cards, the share bars, the board and the thesis builder, off the canvas

Energy Research Warehouse (ERW), 19 October 2026. This folder is for shots at 1280 and 390 px, before (production,
as session 317's landing leaves it) and after (this session's local build), each of the page's `main` element, in
the internal view. The shots are taken by `runs/chain_oct19/s318_build.sh` (the session's report, "To finish"): the
machine stopped that script for low memory before it ran, so the folder holds this README alone until it is run.
A pair is `<name>_before_<width>.png` against `<name>_after_<width>.png`.

What to look at (the numbers are the same before and after; what changed is the drawing):

- `research_*`: `/research`, the library's cards: lines, bars, a stacked bar, a scatter with its fitted line, the
  five-grid multiples as a column of panels; "Shown as" redraws the same values; this week's chart; the picker's small
  examples under "Step 2". After: SVG, each series named on the chart in its own token color, the axis step by
  magnitude, a Chart | Table toggle on every chart.
- `card_lunch_*`: `/research/card/batteries_lunch_grids`, the panels and one grid large; the card's h1 is for a screen
  reader (the title line as it was).
- `card_curtailment_*`: `/research/card/batteries_curtailment`, the scatter with its fit.
- `grid_mix_*`: `/grid?grid=ercot`, the day's mix as one bar of named parts with its shares (the four share bars that
  session 317's detector still counted).
- `board_*`: `/board`, the price chart as time charts with the calculation's average a named line, the seasons as
  lines with the earlier years' range a band, the distribution as bars.
- `thesis_*`: `/thesis`, the trend and funnel charts as horizontal bars.

At 390 every chart is drawn for its width (the text keeps its size) and nothing scrolls sideways. The canvas detector
(`runs/chain_oct19/s303_canvas.mjs`, 28 pages in `s318_build.sh`) should read 0 canvas charts on every page but the
two maps (`/map`, `/resources`), which stay on the canvas by this session's decision.
