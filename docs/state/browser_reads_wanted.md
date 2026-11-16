# Browser reads wanted: what the old laptop changed and could not see in a browser

Energy Research Warehouse (ERW). Started by session 7500 (chain 304, samueloldlaptop, 16 November 2026). The old laptop cannot build the site (it has under 2.5 GB of memory free), so a page change there is held by tests and by the component drawn to HTML with the site's own code. Every change that needs a browser to be believed (a hover, a layout at 390 px, an A and B, a chart) is one row here. The portable laptop's chain 305 reads each row on production once the row's stack has landed, or on a build of the row's branch, and marks it `seen` with what was seen, or `fault` with a row in that tool's faults file (`docs/reviews/<tool>-faults-2026-11-16.md`). No screenshot is claimed that was not taken.

States: `wanted`, `seen`, `fault`.

| # | Asked (UTC) | Session | Branch (landing row) | Address | What to look at | What should be seen | State |
|---:|---|---|---|---|---|---|---|
