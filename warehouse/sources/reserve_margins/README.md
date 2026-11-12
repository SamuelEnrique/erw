# Grid operators' reserve margins: the registry

Energy Research Warehouse (ERW), session 3798 (chain 215). One file a document, `<body>_<document>.yaml`, read by
`warehouse/connectors/reserve_margin_reports.py` into `iso_reserve_margin_reports` (series, one row a figure). It fills
the All grids tab's Headroom row "reserve margins by zone" where a grid operator publishes its own assessment and the
reader may read it (ERCOT's Capacity, Demand and Reserves report has its own table, `ercot_cdr_reserve_margins`).

A session fills a file by reading the document itself, after the host's robots file and terms. Each figure is written
as the document prints it, with its page and its words. Nothing is estimated, derived or converted but between units.

```yaml
body: California Independent System Operator (CAISO)   # who publishes the assessment
grid: CAISO                                            # the tab's grid name
publisher: CAISO                                       # the key of warehouse/metadata/license_verdicts.csv
source: caiso:summer_loads_and_resources_assessment    # the row's source in sources.csv
document: CAISO, 2026 Summer Loads and Resources Assessment, May 2026
document_url: https://...
period: summer 2026                                    # what the figures are for, in the document's words
ts: 2026-06-01                                         # the period's first day (ts_utc at 00:00:00Z)
retrieved_at: 2026-11-12T16:51:54Z
license: public
figures:
  - {variable: prm_achieved_pct, value: 30.8, page: 15, printed: "..."}
```

Variables: `prm_achieved_pct` (pct, the reserve margin the assessment finds in its tightest hour),
`prm_required_pct` (pct, the margin it finds is needed to meet its reliability target), `capacity_surplus_mw` (MW, the
capacity above that target), `peak_forecast_mw` (MW, the peak the assessment plans for), `ra_prm_load_weighted_pct`
(pct, the planning reserve margin the load-serving entities must carry, load-weighted).
