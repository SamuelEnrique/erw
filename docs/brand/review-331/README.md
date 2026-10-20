# Session 331: /demand (every view) and /curtailment, finished (lighter)

Each page's main at 1280 and 390 px, before (production, 20 October 2026 at about 07:50 UTC) and after (the local
build of `wip/331-demand-curtailment`, sessions 328 to 330's branches under it).

- `demand_*`, `weather_*`: the downloads line at the foot (it says every public table is on Data and methods: the
  views' tables are not public in the live set); the weather view's panel ends with "Reset to the defaults".
- `consumption_*`: "Method, sources and gaps" above the view (`docs/methods/consumption.md`); the two tables to
  download at the foot.
- `curtailment_*`: the grid's tables to download under the source line; the bar charts' names and the heat map's legend
  (below).
- `chart_battery_months_*`: the chart "By month: curtailed, what a 4-hour fleet could have absorbed, and what the fleet
  charged" alone. Before (390, the build before the fix, as production draws it): the three bar names in one row over
  the unit ("MWh" under "Curtailed"), the second cut at the edge and the third lost. After (390 and 1280): the names
  after the unit, in as many rows as the width needs, the plot under them. The same fix holds for every bar chart of the
  shared set, and the heat maps' legend is measured from its own words (it ran 42 px past a phone's drawing on
  `/curtailment`).

Every page reads 390 within 390, no element past it.
