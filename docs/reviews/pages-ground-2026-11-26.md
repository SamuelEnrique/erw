# The ground for the two new pages: `/forecast` (ERW forecast) and energy equities (`/equities`, a group on `/board`)

Energy Research Warehouse (ERW). Chain 720, part B, session 10400, 26 November 2026, the portable laptop's first window. Read on main at `093aa84e0`. No build was made for this part. What follows is what the site already has that the two pages reuse, so that nothing is built a second time, and then five real cases for each page, written before any code.

## 1. What is reused, and from where

| Need | What the site has | Where | How the new pages use it |
|---|---|---|---|
| The page's frame, header, sections, tables, chart frames, the fog input panel | `ToolPage`, `ToolHeader`, `ToolSection`, `ToolTable`, `ChartFrame`, `InputPanel`, `Fold`, `SourceLine`, inside `Brand` | `site/components/tool/ToolPage.tsx`, `site/components/Brand.tsx` | Both pages are built of these alone; no new frame |
| The operators' forecast beside what happened | "Forecast against actual", a section of the country view of `/demand`: EIA-930's day-ahead demand forecast against demand, by place, with its summary, by season, by hour and by event | `site/components/demand/CountryForecast.tsx`, files `site/data/regions/forecast/*.json` (13 regions) and `forecast/ba/*.json` | `/forecast` does not draw that section again. It reads the operator's forecast from its own contract's column `operator` and links to `/demand?view=country#forecast` for the operator's long record. The place ids agree (`region-<code>`, `ba-<code>`), so the link carries the place |
| A chart with a band | `CategoryChart` with `band={lo, hi, name}`: a shaded band between two arrays, named at its right edge, with the Chart and Table toggle and the hover card | `site/components/svgchart.tsx` (used by the board's seasons chart) | Tomorrow's 24 hours: the ERW forecast as a line, its band, the operator's forecast as a second line. Categories are the place's local hours, so a day of 23 or 25 hours draws as it is |
| A chart over time, two series, a second axis | `TimeChart` (`series[]`, `y2`, `unit2`, `refLines`, Chart and Table toggle) | `site/components/TimeChart.tsx` | A past day's forecast against what happened; a company or a segment over a window with an energy price on the second axis |
| The place picker and A beside B | A GET form of `AutoSubmitSelect`s (`a`, `b` with "None"), the page drawn on the server from the address, two columns in a grid with `min-w-0` | `site/components/AutoSubmit.tsx`; `site/components/demand/Country.tsx` line 333; `site/app/conditions/page.tsx` | Both pages: every choice is in the address, so a link carries it, the back button returns it (the fix of session 9601 is in `AutoSubmitSelect`), and the page works without script |
| Tabs that are links | `ToolTabs`, `ToolPicker` (`ChooseItem` with `href` and `on`) | `site/components/tool/Choose.tsx` | Demand and Price on `/forecast`; the views of `/equities` |
| A page file read when it is there, and not when it is not | `readRegionFile` (null while the data machine has not written the file; a fixture is read only under a test's own folder) | `site/lib/countryfiles.ts` | The same manner in a reader of each page's own (`site/lib/predictfiles.ts`, `site/lib/equitiesfiles.ts`): the real files land later and no code changes |
| A hover for a default, a source or a reason | `Hint` (dotted words with a `title`), `Tip` (the small mark), a cell's `title` | `site/components/demand/Hint.tsx`, `ToolPage.tsx` | Every source, default, method and "why blank" is a hover; no grey prose on the page |
| A held value | The board's `PLACEHOLDER` words in a blank cell with the reason on hover; a held grid's line (`heldLines`, `heldNote`); `/conditions`'s `Blank` strip | `site/lib/board.ts`, `site/components/board/BoardView.tsx`, `site/app/conditions/page.tsx` | A held price forecast is a blank chart box and blank cells that say "license needed" with the file's own `held` on hover; a held equity price likewise, with the fundamentals still drawn |
| The price board's rows and groups | `BoardFile` (`groups[]`, `rows[]`, `sources[]`), `GroupTable`, `PriceRow`, `Spark`, `MoveCell`; a group is drawn from the file alone, with its filters, its count and its lead row | `site/lib/board.ts`, `site/components/board/BoardView.tsx`, `site/app/board/page.tsx` | The equities group is the contract's `group` and `rows` appended to the board's file on the server (after the board's own groups, so nothing moves), each row turned into the board's `Row`. A held row needs no new code: `status` `licensed` and `not_held` are the board's own |
| A workbench that overlays two series | The board's markets workbench: a second series over the first, the spread or the ratio, windows from a week to all, seasons, a distribution, a CSV | `site/components/board/Workbench.tsx`, pure parts in `site/lib/board.ts` (`WINDOWS`, `windowed`, `joined`, `summary`, `csv`, `dateWords`, `fmt`, `signed`, `pct`) | The component itself reads `/board/s/<id>.json` for a row of the board's file and cannot be handed an equity series. `/equities` reuses its pure parts (the windows, the join, the summary, the CSV) and `TimeChart` with the second axis, which is what the workbench's own price chart is. `/prices` has no workbench of its own |
| Downloads | A route under the page, without an extension (the release gate covers it as it covers the page): `/board/rows` (CSV with a `#` header of provenance), `/board/rows/python`, `/board/rows/stata` (`rowsReader`: the Stata reader keeps the owner's rules); `TableDownloads` for a page's public tables | `site/app/board/rows/`, `site/app/companies/rows/`, `site/lib/board.ts`, `site/components/tool/TableDownloads.tsx` | `/forecast/rows` and `/equities/rows`, each with its Python and Stata reader, in the same form |
| A figure a script can check against the file | `Num` with `pfKey(file, path)`: the figure carries the path into its page file | `site/components/Num.tsx`, `site/lib/pagefile.ts` | The figures a page shows as it opens carry their keys where the file is under `site/data` |
| In review, in no menu | A path with no line in `site/lib/release.ts` is in review; a page not in `site/lib/pages.ts` is in no menu; `/in-review` answers its address | `site/lib/release.ts`, `site/lib/pages.ts`, `site/app/in-review/page.tsx` | Neither file is touched. Each page's address goes into `site/scripts/check-routes.mjs`, as `/conditions` did |
| A tour stop held by its flag | `NEW_STOPS` with `landed: false` | `site/lib/tour.ts` | One stop a page, held back until it lands |

## 2. What is not reused, and why

- `site/lib/forecast.ts`, `forecastdata.ts`, `forecastfiles.ts`, `forecastui.ts`, `site/data/forecast/`, `site/app/impact/`: the Economic impact tool's. Nothing of them is imported, edited or renamed; the new page's files are under `site/data/predict/` and its code under names with `predict`.
- The board's `Workbench` component, for the reason in the table.
- The 3D and map pieces of the Grid tool: neither page has a place on a map.

## 3. What the contracts leave open (asked of the owning window, never invented here)

- The board's rows of the equities contract carry `last`, `moves` and `spark`, and not the board's other cells (the 7-day, 30-day and 12-month means, the 30-day low and high, the one-year range). The chain asks for the last value, the five changes and the trend, which is what the contract holds. The group is drawn with those columns; the other columns are asked of window A in one line, and are drawn if they come.
- The forecast's example files hold no number at all, by the contract's own rule. The tests therefore pin the page against files of the contract's shape written in the tests' own folder and marked as a fixture, which the site's own folder never reads.

## 4. The ERW forecast: five cases, written before the page

**F1. A power trader, the evening before a hot day in Texas.**
She wants tomorrow's demand peak in ERCOT's region, the hour it falls, and how far the ERW's line stands from the operator's own.
She opens `/forecast`, leaves Texas chosen, reads the peak hour and both lines off the chart of tomorrow, then the band's width at that hour.
She must get: the two forecasts for each hour, the hour the ERW forecast was made, and the record of each on the ten highest-demand days, without leaving the page.

**F2. A battery operator choosing tomorrow's hours in California.**
He wants the hours tomorrow's price forecast is lowest and highest at the hub the page forecasts, and how wrong the price forecast has been at those hours.
He picks California, the Price tab, reads the lowest and highest hours, then the score by hour of day for the same hours.
He must get: the hub's name, the price by hour with its band, the mean error at each hour of the day, and a blank with "license needed" where a place's price is held.

**F3. A utility planner in the Carolinas.**
She wants to know whether the ERW forecast or her own balancing authority's filed forecast has been closer, month by month.
She picks her authority, opens "How it has done", and reads the score table by month: the ERW, the operator, the same hour yesterday, the same hour a week ago.
She must get: every month the backtest holds, the months the ERW lost drawn as the months it won, and the count of hours behind each figure.

**F4. A researcher who wants the score.**
He wants every place's mean absolute percent error for every method, to cite or to test, and the files behind it.
He opens the score table for all places at once, sorts nothing, and takes the CSV with its reader in Python or Stata.
He must get: every place and method in one table, nothing left out for scoring badly, the backtest's first and last day, and a download that carries the same figures.

**F5. A student.**
She wants to see what a forecast is: a line, a band, and what happened.
She opens the page, picks a past day, and sees the forecast made the day before beside the demand that came, hour by hour.
She must get: plain names ("ERW forecast", "Operator's forecast", "What happened"), the band explained on hover, and no word that lets the model's line be taken for a published figure.

## 5. Energy equities: five cases, written before the pages

**E1. An energy investor on a day oil falls.**
He wants to see which segments moved with the fall and by how much, against the day's change in WTI.
He opens the board's "Energy equities" group, reads each segment's change over a day, then opens `/equities` and lays WTI over the exploration and production segment for the last three months.
He must get: each segment's last value and its five changes, both weightings named plainly, and the oil price on the same chart with its own axis and source.

**E2. A lender comparing two utilities.**
She wants two regulated utilities side by side: debt, capital spending, revenue and income by quarter, each from the filing.
She picks company A and company B on `/equities` and reads the quarterly table of each.
She must get: the same lines for the same periods in two columns, the form and the day each was filed, and the filing's address on hover.

**E3. A developer looking up a counterparty.**
He wants to know whether the company across the table is listed, in which segment the ERW puts it, and its latest filed figures.
He types part of the name into the table's filter, finds the row, and opens the company.
He must get: the company's segment and the rule that put it there on hover, its filed figures, and, where the ERW may not show its share price, the fundamentals drawn and the price blank with "license needed".

**E4. A trader asking what moved with gas.**
She wants the independent power producers' line beside the Henry Hub price over a year.
She picks the segment, the window of a year, and Henry Hub as the price laid over it.
She must get: the two lines on one time axis, each with its unit, a monthly price drawn on its own dates and never spread over days, and no score or signal of any kind.

**E5. A student of one company.**
He wants one company from start to finish: what it is, its price over the years the files hold, what it earns and owes.
He picks the company, the widest window, and reads the chart and the quarterly table, then downloads the rows.
He must get: plain column names, every figure sourced on hover, and a CSV with a reader in Python and Stata.
