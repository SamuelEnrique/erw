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

## Cross-check, eleven planning areas outside the ISOs: the 2025 forecast against EIA-930's 2025 peak (session 3796)

The utilities whose planning area is their own EIA-930 balancing authority, mapped by name (the respondent's name in `ferc714_respondents`, the balancing authority EIA-930 names for the same utility). The forecast is the higher of the summer and winter peak the 2024 filing gives for 2025 (`ferc714_planning_area_forecasts`). The actual is the balancing authority's highest hour of 2025 in EIA-930's hourly demand (type D, UTC hours), under the neighbour and range tests the ISO rows use (`warehouse/derived/demand_growth.py`: an hour is used when it is within 25 percent of the median of the four hours around it and within a third to three times the area's median hour).

- **Source:** EIA's API v2, `electricity/rto/region-data`, `frequency=hourly`, `facets[type][]=D`, `facets[respondent][]=<BA>`, 2025-01-01T00 to 2025-12-31T23.
  - Retrieved 2026-11-12T16:46:14Z in 22 requests; `replication/ferc714/ba_peaks.py` reproduces the table (with `--raw` from the saved pages, no request); the raw pages are under `warehouse/raw/eia930_ba_peaks/20261112T164614Z/` (not in git).
  - Not a warehouse table.
- **Two faulty hours were left out by the tests:** APS's 10,529 MW at 2025-02-13T23 (the hours beside it 7,850 and 4,210), and LADWP's 5,823 MW at 2025-02-01T00 (beside it 2,916 and 2,752).
- **Southern Company** (`ferc714:142`) has no 2024 filing in the table and is not in the table below.

| EIA-930 BA | FERC-714 respondent | Forecast of 2025, filed for 2024 (MW) | Actual peak 2025, EIA-930 (MW, hour UTC) | Forecast less actual (pct) |
|---|---|---|---|---|
| TVA | ferc714:152 (Tennessee Valley Authority) | 32,838 (winter) | 35,086 (2025-01-22T14) | -6.4 |
| DUK | ferc714:51 (Duke Energy Carolinas) | 21,216 (summer) | 21,931 (2025-06-25T20) | -3.3 |
| CPLE | ferc714:214 (Duke Energy Progress) | 14,457 (winter) | 14,209 (2025-01-23T13) | +1.7 |
| FPL | ferc714:63 (Florida Power & Light) | 26,306 (summer) | 28,963 (2025-07-28T21) | -9.2 |
| FPC | ferc714:215 (Duke Energy Florida) | 10,366 (winter) | 12,583 (2025-07-28T20) | -17.6 |
| AZPS | ferc714:16 (Arizona Public Service) | 8,491 (summer) | 8,499 (2025-08-08T01) | -0.1 |
| SRP | ferc714:133 (Salt River Project) | 8,528 (summer) | 8,784 (2025-08-08T02) | -2.9 |
| BPAT | ferc714:21 (Bonneville Power Administration) | 12,185 (winter) | 11,537 (2025-02-12T16) | +5.6 |
| PSCO | ferc714:124 (Public Service Company of Colorado) | 7,974 (summer) | 9,079 (2025-07-10T00) | -12.2 |
| NEVP | ferc714:99 (Nevada Power) | 7,226 (summer) | 9,239 (2025-07-15T01) | -21.8 |
| LDWP | ferc714:84 (Los Angeles Department of Water and Power) | 6,226 (summer) | 5,356 (2025-09-04T00) | +16.2 |

What it says, with its limits:

- **Six of the eleven are within about 6.5 percent:** TVA, the two Duke Carolinas areas, APS, SRP and BPA.
- **Where the gap is large, the two boundaries are not the same.** A balancing authority balances the load of every utility inside it, while a FERC-714 planning area is the respondent's own:
  - NV Energy's balancing authority (NEVP) holds Sierra Pacific's load as well as Nevada Power's, so Nevada Power's own forecast sits 21.8 percent under it.
  - Duke Energy Florida's (FPC), Public Service Company of Colorado's (PSCO) and FPL's authorities may also balance other utilities' loads; the table does not say how much.
  - LADWP's filed forecast sits 16.2 percent above its authority's 2025 peak. A mild summer or a planning area larger than the authority's load would each do it; the table does not say which.
  - So these rows are a check of order of magnitude, not of forecasting skill. The seven ISO rows above are the test of skill.
- **Nothing is apportioned or corrected:** each figure is the filing's and EIA-930's as published.

## Limits

- **A planning area is what its respondent files.** A respondent that merged, split or changed its footprint between filings moves its forecast with it, and a revision then measures the footprint as well as the load. The table does not detect this.
- **Units as filed.** A respondent that filed net energy in kWh one year and MWh the next shows a revision of a factor of 1,000. Such rows are left as filed, and a reader filters them.
- **No weather normalisation and no confidence band.** These are the utilities' own planning forecasts.
- **PUDL's release.** The figures are PUDL's reading of FERC's CSV (to 2020) and XBRL (2021 on) filings; a correction PUDL makes reaches the table at the next run.

## License

Public: the owner's ruling 1 of 6 November 2026. FERC-714 is a federal filing; PUDL's data are CC-BY-4.0, credited in each table's header and in `warehouse/metadata/sources.csv`.
