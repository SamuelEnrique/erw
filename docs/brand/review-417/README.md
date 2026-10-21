# Session 417: the shared year axis, before and after

Before: production (https://erw-flame.vercel.app, the internal view), 21 October 2026 at about 14:20 UTC. After: the
local build of `wip/416-417-charts` (21 October at about 14:45 UTC, the database gate open at 2.69 s). 1280 x 900 and 390 x 844, each chart scrolled to the top of the
window. Every chart `components/TimeChart.tsx` draws with `x="year"` (the callers, by grep): four charts on three pages.

| Shot | Address | Chart |
|---|---|---|
| `explore-peak-premium-years_*` | `/explore/ercot-peak-premium` | the peak block's spread by year |
| `explore-interconnection-withdrawn_*` | `/explore/interconnection` | withdrawn share of positions entered, by entry year |
| `explore-interconnection-wait_*` | `/explore/interconnection` | median wait from entry to operation (before: 1999, 2002, 2006, 2010, 2013, 2017, 2021, labels between whole years) |
| `explorer-peak-premium-years_*` | `/explorer/ercot-peak-premium` | the older explorer's year chart |

What to look at: after, every tick sits on 1 January of its year and no year is written twice; where the years do not
fit, every second, fifth or tenth year is written. Session 404's demand-growth explorer stays on bars (a change back
is Samuel's design choice).
