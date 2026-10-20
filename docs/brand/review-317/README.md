# Session 317: the heat maps, bands, scatter, box plot and category charts, off the canvas

Energy Research Warehouse (ERW), 19 October 2026. Shots at 1280 and 390 px, before (production, as session 314's
landing left it) and after (this session's local build), each of one section of a page (the element named in the
file name), in the internal view.

What to look at (the numbers are the same before and after; what changed is the drawing):

- `curtailment_before_*.png` against `curtailment_after_*.png`: `/curtailment`, its bars and lines over the days,
  months and hours, and the heat map of free hours (months by hour of the day). After: SVG, each series named on the
  chart in its own color, the axis step by magnitude, a Chart | Table toggle on every chart, the heat map one color at
  a strength by value over the panel with a hatched cell where no hour is held and the scale's ends named; the range
  slider is gone (the table holds every row).
- `supply_before_*.png` against `supply_after_*.png`: `/supply`, the seasonal bands: the five-year range as a band in
  the rule color, the five-year average dashed, last year thin, this year bold, each named at the right edge.
- `costgrids_before_*.png` against `costgrids_after_*.png`: `/cost-of-power?view=grids`, the rank bars (a partial
  month hatched), each grid's heat grid (months by hour), and the cost against carbon scatter with each grid named
  beside its point.
- `datacenter_before_*.png` against `datacenter_after_*.png`: `/cost-of-power`, the year bars of what a datacenter
  pays (a year short of twelve months hatched; the perfectly foreseen cost a diamond mark when the load is flexible).
- `mix_before_*.png` against `mix_after_*.png`: the Grid tool's Mix tab for ERCOT, the hour stack, the lines and the
  bars.
- `ercot_before_*.png` against `ercot_after_*.png`: the ERCOT peak-premium explorer's box plot (the ERCOT tab of
  `/prices`): five-number boxes on one scale, the median in the accent, named with its value.

At 390 every chart is drawn for its width (the text keeps its size) and nothing scrolls sideways. The canvas detector
(`runs/chain_oct19/s303_canvas.mjs`) reads 0 canvas charts on these pages: the session's report.

The 1280 "after" shots of `costgrids`, `datacenter`, `mix`, `supply` and `ercot` were taken on the build of the
session's second commit (`0fc62fa4`, 22:39 UTC), after a first pass at 1280 had failed on the internal door; the
heat legend there still reads "not held", the words the last commit (`1a0a97da`) changed to "no value held". The
rebuild of that commit was stopped by the machine (low memory) before it could retake them: the session's report.

Retaken on the last commit (the chain of 19 to 20 October, night): `runs/chain_oct19/s317_build.sh` built `1a0a97da`
in `erw-296` (23:04 to 23:17 UTC on 19 October) and took every pair at 1280 and 390 again; the shots in this folder
are those. The heat legend now reads "no value held". The detector on that build read 4 canvas charts on the Mix tab
(`/grid?grid=ercot&view=mix`); session 318's build (`0e6aace9`) read 0 there.
