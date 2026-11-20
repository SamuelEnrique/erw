# Codebook: ferc714

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 2 public tables (2 series; tiers: 1 derived, 1 source); 1 documented in full.

- [`ferc714_forecast_growth`](#ferc714_forecast_growth): One planning area's revision of one forecast figure (summer peak, winter peak or net energy) for one forecast year, from one FERC-714 filing against the filing one or two years before.
- [`ferc714_planning_area_forecasts`](#ferc714_planning_area_forecasts): FERC Form 714, Part 3, Schedule 2, each planning area's ten-year forecast of summer peak, winter peak and net energy, every filing kept (session 3758)

### `ferc714_forecast_growth`

One planning area's revision of one forecast figure (summer peak, winter peak or net energy) for one forecast year, from one FERC-714 filing against the filing one or two years before.

Shape: series. Keys: `entity`, `variable`, `ts_utc`, `vintage`. License: public; tier: derived. Rows read on 2026-11-20: 198354.

- **Time:** ts_utc is the forecast year's first instant (freq P1Y); vintage is the later filing's due date.
- **Revisions:** Every revision kept, one row per vintage: the key is (entity, variable, ts_utc, vintage). Rebuilt whole by each run from the whole input.
- **Source:** erw:ferc714_forecast_growth Energy Research Warehouse (ERW), derived from ferc714_planning_area_forecasts (Catalyst Cooperative's PUDL, from FERC Form 714, Part 3, Schedule 2)
- **Method note:** [`docs/methods/ferc714_forecast_growth.md`](../methods/ferc714_forecast_growth.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. FERC-714 forecast revisions by planning area, filing and forecast year (docs/methods/ferc714_forecast_growth.md). Via the Energy Research Warehouse (ERW), table `ferc714_forecast_growth`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: ferc714:<PUDL's respondent id>, a planning area | none | text | for example ferc714:1, ferc714:10, ferc714:100; 168 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2008-01-01T00:00:00Z to 2047-01-01T00:00:00Z; 40 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -5783711498.0 to 5909938928.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 198354 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 198354 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ferc714_forecast_growth | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/ferc714_forecast_growth.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-12T11:29:00Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The later filing's due date, 1 June of the year after its report year (PUDL gives no submission time); part of the key | none | utc time | 2008-06-01T00:00:00Z, 2009-06-01T00:00:00Z, 2010-06-01T00:00:00Z, 2011-06-01T00:00:00Z, 2012-06-01T00:00:00Z, 2013-06-01T00:00:00Z, 2014-06-01T00:00:00Z, 2015-06-01T00:00:00Z, 2016-06-01T00:00:00Z, 2017-06-01T00:00:00Z, 2018-06-01T00:00:00Z, 2019-06-01T00:00:00Z, 2020-06-01T00:00:00Z, 2021-06-01T00:00:00Z, 2022-06-01T00:00:00Z, 2023-06-01T00:00:00Z, 2024-06-01T00:00:00Z, 2025-06-01T00:00:00Z, 2026-06-01T00:00:00Z | 0 |
| `x_report_year` | The report year of the later filing | none | integer | 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 | 0 |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_energy_revision_1y_mwh` | This filing's net energy forecast for the year less the figure for the same year in the filing one year before | MWh | 18335 | 2008-01-01T00:00:00Z | 2047-01-01T00:00:00Z |
| `net_energy_revision_1y_pct` | net_energy_revision_1y_mwh as a percent of the earlier figure (written only where that figure is above zero) | pct | 18091 | 2008-01-01T00:00:00Z | 2047-01-01T00:00:00Z |
| `net_energy_revision_2y_mwh` | This filing's net energy forecast for the year less the figure for the same year in the filing two years before | MWh | 14980 | 2009-01-01T00:00:00Z | 2045-01-01T00:00:00Z |
| `net_energy_revision_2y_pct` | net_energy_revision_2y_mwh as a percent of the earlier figure (written only where that figure is above zero) | pct | 14788 | 2009-01-01T00:00:00Z | 2045-01-01T00:00:00Z |
| `summer_peak_revision_1y_mw` | This filing's summer peak forecast for the year less the figure for the same year in the filing one year before | MW | 18335 | 2008-01-01T00:00:00Z | 2047-01-01T00:00:00Z |
| `summer_peak_revision_1y_pct` | summer_peak_revision_1y_mw as a percent of the earlier figure (written only where that figure is above zero) | pct | 18091 | 2008-01-01T00:00:00Z | 2047-01-01T00:00:00Z |
| `summer_peak_revision_2y_mw` | This filing's summer peak forecast for the year less the figure for the same year in the filing two years before | MW | 14980 | 2009-01-01T00:00:00Z | 2045-01-01T00:00:00Z |
| `summer_peak_revision_2y_pct` | summer_peak_revision_2y_mw as a percent of the earlier figure (written only where that figure is above zero) | pct | 14789 | 2009-01-01T00:00:00Z | 2045-01-01T00:00:00Z |
| `winter_peak_revision_1y_mw` | This filing's winter peak forecast for the year less the figure for the same year in the filing one year before | MW | 18335 | 2008-01-01T00:00:00Z | 2047-01-01T00:00:00Z |
| `winter_peak_revision_1y_pct` | winter_peak_revision_1y_mw as a percent of the earlier figure (written only where that figure is above zero) | pct | 17966 | 2008-01-01T00:00:00Z | 2047-01-01T00:00:00Z |
| `winter_peak_revision_2y_mw` | This filing's winter peak forecast for the year less the figure for the same year in the filing two years before | MW | 14980 | 2009-01-01T00:00:00Z | 2045-01-01T00:00:00Z |
| `winter_peak_revision_2y_pct` | winter_peak_revision_2y_mw as a percent of the earlier figure (written only where that figure is above zero) | pct | 14684 | 2009-01-01T00:00:00Z | 2045-01-01T00:00:00Z |

### `ferc714_planning_area_forecasts`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`, `vintage`. License: public; tier: source. Rows read on 2026-11-20: 67215.

- **Source:** pudl:core_ferc714__yearly_planning_area_demand_forecast Catalyst Cooperative (PUDL), from FERC Form 714, Part 3, Schedule 2 (stable release) (https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc714__yearly_planning_area_demand_forecast.parquet)
- **Method note:** [`docs/methods/ferc714_forecast_growth.md`](../methods/ferc714_forecast_growth.md)
- **Cite as:** Catalyst Cooperative (PUDL), from FERC Form 714. FERC Form 714, Part 3, Schedule 2: planning area demand forecasts (PUDL core table, stable release). Via the Energy Research Warehouse (ERW), table `ferc714_planning_area_forecasts`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example ferc714:1, ferc714:10, ferc714:100; 190 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2007-01-01T00:00:00Z to 2050-01-01T00:00:00Z; 44 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 5945307065.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MW, MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 67215 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 67215 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | pudl:core_ferc714__yearly_planning_area_demand_forecast | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://s3.us-west-2.amazonaws.com/pudl.catalyst.coop/stable/core_ferc714__yearly_planning_area_demand_forecast.parquet | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-12T11:26:38Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2007-06-01T00:00:00Z, 2008-06-01T00:00:00Z, 2009-06-01T00:00:00Z, 2010-06-01T00:00:00Z, 2011-06-01T00:00:00Z, 2012-06-01T00:00:00Z, 2013-06-01T00:00:00Z, 2014-06-01T00:00:00Z, 2015-06-01T00:00:00Z, 2016-06-01T00:00:00Z, 2017-06-01T00:00:00Z, 2018-06-01T00:00:00Z, 2019-06-01T00:00:00Z, 2020-06-01T00:00:00Z, 2021-06-01T00:00:00Z, 2022-06-01T00:00:00Z, 2023-06-01T00:00:00Z, 2024-06-01T00:00:00Z, 2025-06-01T00:00:00Z, 2026-06-01T00:00:00Z | 0 |
| `x_report_year` | not yet written |  | integer | 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025 | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `net_energy_forecast_mwh` |  | MWh | 22405 | 2007-01-01T00:00:00Z | 2050-01-01T00:00:00Z |
| `summer_peak_forecast_mw` |  | MW | 22405 | 2007-01-01T00:00:00Z | 2050-01-01T00:00:00Z |
| `winter_peak_forecast_mw` |  | MW | 22405 | 2007-01-01T00:00:00Z | 2050-01-01T00:00:00Z |

