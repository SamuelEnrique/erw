# FERC-714 forecasts and their revisions: `ferc714_planning_area_forecasts`, `ferc714_forecast_growth`

Energy Research Warehouse (ERW), sessions 3758 and 3759 (chain 211), under the owner's ruling 1 of 6 November 2026 (`docs/state/rulings_2026-11-06.md`: the pull of FERC Form 714, Part 3, Schedule 2 is allowed; license public).

## What the utilities forecast, in their own filings

Every planning area that files FERC Form 714 states, in Part 3, Schedule 2, its forecast of summer peak demand, winter peak demand and net energy for each of the next ten years. It files again every year, so the same forecast year is forecast up to ten times, once a filing. How a planning area's forecast of one year moves from filing to filing is the large-load signal written by the utilities themselves: a utility that signs datacenter load raises the years it lands in.

## The tables

**`ferc714_planning_area_forecasts`** (`warehouse/connectors/ferc714_forecasts.py`): every row of PUDL's `core_ferc714__yearly_planning_area_demand_forecast` (Catalyst Cooperative's Public Utility Data Liberation project, stable release; FERC's own site refuses automated requests, session 484).

- One row a planning area (`entity` `ferc714:<respondent id>`, the entity of `ferc714_area_demand` and `ferc714_respondents`), variable, forecast year (`ts_utc`, its first instant, `freq` P1Y) and filing.
- Variables:
  - `summer_peak_forecast_mw` and `winter_peak_forecast_mw` (MW);
  - `net_energy_forecast_mwh` (MWh).
- The filing:
  - `x_report_year` is the report year;
  - `vintage` is the filing's due date, 1 June of the year after it. PUDL gives no submission time.
- Report years 2006 to 2025: 22,405 forecast rows in PUDL, 67,215 rows here once the three figures are unpivoted, 190 planning areas.
- A blank in the filing is no row. Values are as filed, including figures that are plainly in the wrong unit (a net energy of billions of MWh); they are not corrected.

**`ferc714_forecast_growth`** (`warehouse/derived/ferc714_forecast_growth.py`): for each planning area, filing and forecast year, the change of the area's forecast of that same year against the filing one year and two years before:

| Variable | Unit | What |
|---|---|---|
| `summer_peak_revision_1y_mw`, `_2y_mw` | MW | this filing's summer peak for the year less the filing one (two) years before |
| `summer_peak_revision_1y_pct`, `_2y_pct` | pct | that change in percent of the earlier filing's figure |
| `winter_peak_revision_...` | MW, pct | the same for the winter peak |
| `net_energy_revision_1y_mwh`, `_2y_mwh`, `_1y_pct`, `_2y_pct` | MWh, pct | the same for net energy |

- A row is written only where both filings hold the figure.
- A percent is written only where the earlier figure is above zero.
- Nothing is filled, smoothed or adjusted for weather.
- First build: 198,354 rows, 168 planning areas, filings 2007 to 2025 compared with the one and two before.

**Both tables keep every filing** (`docs/datastandard.md`, decision 77). Their headers say "Revisions: kept, one row per vintage", and the validator keys them by `(entity, variable, ts_utc, vintage)`.

## The ten largest upward revisions, 2025 filing against 2024, summer peak of 2030

From the first build (12 November 2026). 88 planning areas hold a 2030 summer peak in both filings; the median revision is +8.5 MW.

| Rank | Planning area (respondent) | Revision, MW | Revision, percent | 2025 filing's 2030 summer peak, MW |
|---|---|---|---|---|
| 1 | Southwest Power Pool (`ferc714:146`) | +7,235 | +10.9 | 73,521 |
| 2 | MISO (`ferc714:203`) | +5,485 | +3.8 | 151,025 |
| 3 | Sierra Pacific Resources (`ferc714:138`) | +2,736 | +73.3 | 6,469 |
| 4 | Duke Energy Carolinas, LLC (`ferc714:51`) | +1,848 | +7.9 | 25,229 |
| 5 | Florida Power & Light Company (`ferc714:63`) | +1,487 | +5.3 | 29,352 |
| 6 | Arizona Public Service Company (`ferc714:16`) | +1,330 | +13.7 | 11,057 |
| 7 | Nevada Power Company (`ferc714:99`) | +1,118 | +14.4 | 8,896 |
| 8 | Tennessee Valley Authority (`ferc714:152`) | +957 | +2.8 | 34,777 |
| 9 | Public Service Company of New Mexico (`ferc714:125`) | +769 | +35.7 | 2,924 |
| 10 | El Paso Electric Company (`ferc714:53`) | +760 | +23.8 | 3,949 |

- The upward revisions of the 88 areas sum to 28,963 MW.
- The net of all 88 is +6,861 MW: some areas lowered their 2030 forecast.
- An area's revision is its own filing's change. Two planning areas can overlap: an ISO's forecast holds the load its member utilities also file. So the rows are not added across areas into a national figure.

## Cross-check: the forecast a year ahead against EIA-930's actual peak (session 3759)

For the seven ISO planning areas whose respondent is the ISO itself, the forecast of a year filed the year before (the higher of its summer and winter peak) is set beside that year's actual peak from `eia930_demand_growth` (EIA-930, the balancing authority's highest hour).

- The map, by name and EIA code:
  - CISO `ferc714:24` (California Independent System Operator Corporation);
  - ERCO `ferc714:58` (ERCOT);
  - ISNE `ferc714:76` (ISO New England Inc.);
  - NYIS `ferc714:100` (New York Independent System Operator);
  - PJM `ferc714:119` (PJM Interconnection, LLC);
  - SWPP `ferc714:146` (Southwest Power Pool);
  - MISO `ferc714:203` (MISO).
- Not mapped: the other planning areas. They are utilities whose EIA-930 balancing authority is either an ISO (a member's load inside it) or a balancing authority the warehouse holds no demand-growth row for. PJM's six hub respondents (`ferc714:188` to `193`) are pricing hubs, not planning areas of their own.

| EIA-930 BA | FERC-714 respondent | Year | Forecast peak, filed the year before (MW) | Actual peak, EIA-930 (MW) | Forecast less actual (pct) |
|---|---|---|---|---|---|
| CISO | ferc714:24 | 2023 | 46,829 | 44,007 | +6.4 |
| CISO | ferc714:24 | 2024 | 46,244 | 47,571 | -2.8 |
| CISO | ferc714:24 | 2025 | 46,094 | 43,860 | +5.1 |
| ERCO | ferc714:58 | 2023 | 82,308 | 85,432 | -3.7 |
| ERCO | ferc714:58 | 2024 | 82,239 | 85,544 | -3.9 |
| ERCO | ferc714:58 | 2025 | 85,759 | 83,597 | +2.6 |
| ISNE | ferc714:76 | 2023 | 26,575 | 23,475 | +13.2 |
| ISNE | ferc714:76 | 2024 | 26,327 | 24,255 | +8.5 |
| ISNE | ferc714:76 | 2025 | 24,803 | 25,898 | -4.2 |
| NYIS | ferc714:100 | 2023 | 32,048 | 30,206 | +6.1 |
| NYIS | ferc714:100 | 2024 | 31,541 | 28,990 | +8.8 |
| NYIS | ferc714:100 | 2025 | 31,471 | 31,857 | -1.2 |
| PJM | ferc714:119 | 2023 | 149,059 | 147,605 | +1.0 |
| PJM | ferc714:119 | 2024 | 151,247 | 153,121 | -1.2 |
| PJM | ferc714:119 | 2025 | 154,144 | 160,560 | -4.0 |
| SWPP | ferc714:146 | 2023 | 54,733 | 56,010 | -2.3 |
| SWPP | ferc714:146 | 2024 | 56,202 | 54,247 | +3.6 |
| SWPP | ferc714:146 | 2025 | 57,871 | 54,411 | +6.4 |
| MISO | ferc714:203 | 2023 | 131,510 | 120,781 | +8.9 |
| MISO | ferc714:203 | 2024 | 129,313 | 118,635 | +9.0 |
| MISO | ferc714:203 | 2025 | 129,961 | 120,343 | +8.0 |

What it says:
- **The forecasts land near the actual peaks.** Six of the seven are within about 9 percent in every year, and most are within 5. Forecasting a peak a year ahead is a weather call; a hot or a mild summer moves the actual peak by more than the forecast moves.
- **MISO's filed forecast runs 8 to 9 percent above its actual peak every year.** That is consistent with a forecast built from its members' own peaks, which do not all fall in the same hour, against EIA-930's single highest hour. MISO's figures are kept as filed, and a revision between two MISO filings compares like with like.
- **PJM's actual peak passed its forecast by 4 percent in 2025.** In `ferc714_forecast_growth`:
  - PJM's 2024 filing raised its summer peak forecast against the 2023 filing by 16,010 MW for 2030 and 30,431 MW for 2034;
  - its 2025 filing lowered 2026 to 2032 by 875 to 4,564 MW, and raised 2033 (+1,887) and 2034 (+4,629).

## Limits

- **A planning area is what its respondent files.** A respondent that merged, split or changed its footprint between filings moves its forecast with it, and a revision then measures the footprint as well as the load. The table does not detect this.
- **Units as filed.** A respondent that filed net energy in kWh one year and MWh the next shows a revision of a factor of 1,000. Such rows are left as filed, and a reader filters them.
- **No weather normalisation and no confidence band.** These are the utilities' own planning forecasts.
- **PUDL's release.** The figures are PUDL's reading of FERC's CSV (to 2020) and XBRL (2021 on) filings; a correction PUDL makes reaches the table at the next run.

## License

Public: the owner's ruling 1 of 6 November 2026. FERC-714 is a federal filing; PUDL's data are CC-BY-4.0, credited in each table's header and in `warehouse/metadata/sources.csv`.
