# Session 303: one chart library, the first step: the time-series chart as SVG

Screenshots in the internal view at 1280 and 390 px, quantized to 32 colors, 19 October 2026, each page in its default
state. "Before" is production serving session 302 (the time-series chart on the chart library's canvas: a legend
line above the plot, a range slider under it); "after" is the local build of branch `wip/303-one-chart-library`, where
`components/TimeChart.tsx` is plain SVG in the brand's manner: each series named at the end of its line in its own
color, grid lines in the rule color and the zero line in ink, axis text 12 px that does not shrink, a hover card on
fog, and a Chart | Table toggle above every chart. Taken with `runs/chain_oct19/capture300.mjs`, which also kept each
page's checked numbers and visible text under `runs/chain_oct19/s303/` (not in git).

| File | Address | What it shows |
|---|---|---|
| `*_events_uri_*.png` | `/events/uri-2021` | four line charts (price, demand served, net generation, carbon intensity), each with 2019, 2020 and 2021 named at the line ends; the estimates' chart was SVG before |
| `*_events_covid_*.png` | `/events/covid-2020` | ten charts: the weekly demand of seven grids and US48 on one chart, each named at its end, the eight labels pushed apart |
| `*_grid_mix_*.png` | `/grid?grid=ercot` | the Mix tab: the latest-hour demand and forecast lines, the fuel stack of the last 24 hours (areas named at the right edge) and the monthly carbon line are SVG; the Mix view's own four charts (hour stack, lines, bars, heat) are still on the canvas |
| `*_grid_clean_*.png` | `/grid?grid=ercot&view=clean` | the Clean tab: the carbon lines since 2018 and of the last 24 hours are SVG; the Mix view's two clean charts are still on the canvas |
| `*_explorer_*.png` | `/prices?tab=ercot` | the ERCOT tab: the year and month lines are SVG; the box plot is still on the canvas |
| `*_storage_*.png` | `/storage` | the three battery lines of the fleet tab (24 hours by ISO, 30 days by ISO, the Lower 48) |

What to look at, after:

1. No legend box: each series is named at the right end of its line (or at the right edge of its band), in its color; the names are pushed apart where lines end close together.
2. The toggle at the top right of every chart; Table shows every value the chart holds (500 rows a page for a long series), with the unit in the header and the figures in mono.
3. Hover anywhere on a chart: the card on fog names the period and every series' figure in mono.
4. At 390 px the chart is drawn for its width (12 px axis text, not shrunk); nothing scrolls sideways except `/events/covid-2020`, whose table was already wider than a phone before (434 px, before and after).

Every checked number on these pages is the same before and after (the chart carries none: its data are the tables' rows the pages fetch, unchanged).
