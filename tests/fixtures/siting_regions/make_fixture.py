"""The fixture of the regions section's tests (chain 780, session 11600): files in the shape of
docs/state/page_files_siting_regions.md, with MADE-UP values. They are for tests and a local look only: no figure in
them is real, none is deployed, and the section never reads this folder on the site (it reads site/data/siting/regions,
or the folder ERW_SITING_REGIONS_DIR names in a test).

    python tests/fixtures/siting_regions/make_fixture.py

Writes siting/regions/index.json, table.json and one file a place beside this script, the same bytes each run.
Four places, chosen for what the section must draw: a region, an operator whose every count is shown (ERCOT), an
operator whose prices are held for a license (NYISO), and an authority that is not a market and whose file is left
out (so a place with no file of its own is drawn as such).
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "siting", "regions")
NOTE = "MADE-UP values for the regions section's tests (tests/fixtures/siting_regions/make_fixture.py); not real, never deployed"
BUILT = "2026-11-28T12:00:00Z"
P12 = "2025-11-01..2026-10-31"
HEAD = {"built": BUILT, "example": False, "fixture": NOTE, "contract": "docs/state/page_files_siting_regions.md", "method": "docs/methods/siting_regions.md", "license": "public"}

SOURCES = {
    "ercot_prices": {"table": "ercot_all_hub_prices_history", "publisher": "ERCOT", "license": "public", "retrieved": "2026-11-28T06:10:00Z", "report": "ERCOT settlement point prices at hubs, day-ahead and real-time"},
    "iso_prices": {"table": "iso_hub_prices_history", "publisher": "NYISO", "license": "internal", "retrieved": "2026-11-28T06:12:00Z", "report": "NYISO zonal prices"},
    "congestion": {"table": "price_congestion_monthly", "publisher": "CAISO, SPP", "license": "public", "retrieved": "2026-11-27T06:00:00Z", "report": "the congestion part of the hub price, by month"},
    "constraints": {"table": "constraints_binding_monthly", "publisher": "CAISO, SPP", "license": "public", "retrieved": "2026-11-27T06:00:00Z", "report": "binding constraints by month"},
    "eia930_demand": {"table": "eia930_ba_demand_hourly", "publisher": "U.S. Energy Information Administration", "license": "public", "retrieved": "2026-11-28T05:00:00Z", "report": "Form EIA-930, hourly demand by balancing authority"},
    "alerts": {"table": "grid_all_alerts", "publisher": "ERCOT, CAISO, DOE", "license": "public", "retrieved": "2026-11-28T05:30:00Z", "report": "operators' notices and DOE's emergency orders"},
    "outages": {"table": "generation_outages_hourly", "publisher": "CAISO, SPP", "license": "public", "retrieved": "2026-11-27T06:00:00Z", "report": "generation out of service by hour"},
    "cdr": {"table": "ercot_cdr_reserve_margins", "publisher": "ERCOT", "license": "public", "retrieved": "2026-11-20T06:00:00Z", "report": "ERCOT's Capacity, Demand and Reserves report"},
    "queue": {"table": "lbnl_interconnection_queue", "publisher": "Lawrence Berkeley National Laboratory", "license": "public", "retrieved": "2026-11-01T06:00:00Z", "report": "Queued Up, 2026 edition, through 2025"},
    "durations": {"table": "interconnection_durations", "publisher": "Lawrence Berkeley National Laboratory", "license": "public", "retrieved": "2026-11-01T06:00:00Z", "report": "Queued Up, 2026 edition: years from request to operation"},
    "rules": {"table": "utility_large_load_rules", "publisher": "utilities and state commissions", "license": "public", "retrieved": "2026-11-26T06:00:00Z", "report": "large-load tariffs, contracts and orders, each read in its own document"},
    "carbon": {"table": "carbon_intensity_hourly", "publisher": "U.S. Energy Information Administration; the ERW's arithmetic", "license": "public", "retrieved": "2026-11-28T05:00:00Z", "report": "carbon intensity of demand by hour, from Form EIA-930 generation by fuel"},
    "supply": {"table": "eia930_ba_supply_hourly", "publisher": "U.S. Energy Information Administration", "license": "public", "retrieved": "2026-11-28T05:00:00Z", "report": "Form EIA-930, hourly net generation by fuel"},
    "interchange": {"table": "eia930_ba_interchange_hourly_2026", "publisher": "U.S. Energy Information Administration", "license": "public", "retrieved": "2026-11-28T05:00:00Z", "report": "Form EIA-930, hourly interchange between authorities"},
    "curtailment": {"table": "iso_curtailment_monthly", "publisher": "CAISO, ERCOT, SPP", "license": "public", "retrieved": "2026-11-27T06:00:00Z", "report": "wind and solar curtailed, by month"},
    "scores": {"table": "eia930_ba_demand_hourly", "publisher": "the ERW forecast's report card", "license": "public", "retrieved": "2026-11-27T14:39:36Z", "report": "site/data/predict/scores.json: the operator's filed forecast and the ERW forecast against what happened"},
    "dc_facilities": {"table": "datacenter_facilities", "publisher": "news and company pages", "license": "public", "retrieved": "2026-11-26T06:00:00Z", "report": "datacenter facilities"},
    "dc_projects": {"table": "datacenter_projects", "publisher": "news and company pages", "license": "public", "retrieved": "2026-11-26T06:00:00Z", "report": "announced datacenter projects"},
}


# the contract's dated line of 28 November 2026: a source carries the address of its table's report and its hold
for _k, _s in SOURCES.items():
    _s["url"] = f"https://example.org/made-up-source/{_k}"
    _s["held"] = None
MONTHS24 = [f"{2024 + (10 + i) // 12}-{(10 + i) % 12 + 1:02d}" for i in range(24)]   # 2024-11 to 2026-10
P24 = "2024-11-01..2026-10-31"


def trend(first, step, missing=()):
    """24 made-up months: a line that rises by `step` a month; the months named in `missing` are not held (null)."""
    return {"months": MONTHS24, "period": P24, "v": [None if i in missing else round(first + step * i, 2) for i in range(24)]}


def cell(v, unit, src, period=P12, held=None, months=None):
    c = {"v": None if held else v, "unit": unit, "period": period, "src": src, "held": held}
    if months is not None:
        c["trend"] = months
    return c


SECTIONS = [
    {"id": "price", "title": "Price", "counts": [{"key": "mean", "label": "Mean price", "unit": "USD/MWh"}, {"key": "p95", "label": "95th percentile price", "unit": "USD/MWh"}, {"key": "hours_over_100", "label": "Hours above USD 100", "unit": "hours"}, {"key": "hours_below_0", "label": "Hours below zero", "unit": "hours"}, {"key": "hours", "label": "Hours held", "unit": "hours"}]},
    {"id": "congestion", "title": "Congestion", "counts": [{"key": "congestion_share_pct", "label": "Share of the price that was congestion", "unit": "pct"}, {"key": "congestion_mean", "label": "Mean congestion part of the price", "unit": "USD/MWh"}]},
    {"id": "tightness", "title": "How tight the grid runs", "counts": [{"key": "peak_mw", "label": "Peak demand", "unit": "MW"}, {"key": "peak_prior_mw", "label": "Peak demand, the 12 months before", "unit": "MW"}, {"key": "peak_growth_pct", "label": "Growth of the peak", "unit": "pct"}, {"key": "peak_hour", "label": "Hour of the peak", "unit": "UTC"}, {"key": "alerts", "label": "Alerts", "unit": "count"}, {"key": "watches", "label": "Watches", "unit": "count"}, {"key": "emergencies", "label": "Emergencies", "unit": "count"}, {"key": "alert_days", "label": "Days with any notice", "unit": "days"}, {"key": "out_mw_at_peak", "label": "Out of service at the peak hour", "unit": "MW"}, {"key": "reserve_margin_pct", "label": "Planning reserve margin", "unit": "pct"}, {"key": "reserve_target_pct", "label": "Reserve margin target", "unit": "pct"}]},
    {"id": "queue", "title": "What is waiting to connect", "counts": [{"key": "active_mw", "label": "Active requests", "unit": "MW"}, {"key": "active_projects", "label": "Active requests", "unit": "count"}, {"key": "withdrawn_share_pct", "label": "Share withdrawn, historically", "unit": "pct"}, {"key": "median_years_to_operation", "label": "Median years from request to operation", "unit": "years"}]},
    {"id": "large_load", "title": "Large loads", "counts": [{"key": "rules_n", "label": "Large-load rules held", "unit": "count"}, {"key": "smallest_threshold_mw", "label": "Smallest load a rule applies to", "unit": "MW"}]},
    {"id": "mix_carbon", "title": "What the power is made of and what it emits", "counts": [{"key": "intensity", "label": "Carbon intensity, mean", "unit": "kgCO2/MWh"}]},
    {"id": "imports", "title": "What it leans on its neighbours for", "counts": [{"key": "net_import_share_pct", "label": "Net imports as a share of demand", "unit": "pct"}, {"key": "net_import_share_peak_pct", "label": "Net imports as a share of demand, 100 highest hours", "unit": "pct"}]},
    {"id": "spare", "title": "What is spare", "counts": [{"key": "curtailed_wind_mwh", "label": "Wind curtailed", "unit": "MWh"}, {"key": "curtailed_solar_mwh", "label": "Solar curtailed", "unit": "MWh"}, {"key": "negative_price_hours", "label": "Hours of negative price", "unit": "hours"}]},
    {"id": "forecast", "title": "How well its demand is forecast", "counts": [{"key": "operator_mape_pct", "label": "Operator's forecast error", "unit": "pct"}, {"key": "erw_mape_pct", "label": "ERW forecast's error", "unit": "pct"}, {"key": "hours", "label": "Hours scored", "unit": "hours"}]},
    {"id": "datacenters", "title": "Datacenters already there", "counts": [{"key": "facilities_n", "label": "Facilities held", "unit": "count"}, {"key": "facilities_mw_stated", "label": "Facilities' stated megawatts", "unit": "MW"}, {"key": "projects_n", "label": "Announced projects held", "unit": "count"}, {"key": "projects_mw_stated", "label": "Projects' stated megawatts", "unit": "MW"}]},
]

PLACES = [
    {"id": "region-tex", "kind": "region", "code": "TEX", "name": "Texas", "region": "TEX", "regions": ["TEX"], "operator": None, "members": ["ERCO"], "tz": "America/Chicago", "peak_mw": 85111.0, "ref_hub": "ercot:HB_HUBAVG", "file": "region-tex.json"},
    {"id": "op-ercot", "kind": "operator", "code": "ERCOT", "name": "ERCOT", "region": None, "regions": ["TEX"], "operator": None, "members": ["ERCO"], "tz": "America/Chicago", "peak_mw": 85111.0, "ref_hub": "ercot:HB_HUBAVG", "file": "op-ercot.json"},
    {"id": "op-nyiso", "kind": "operator", "code": "NYISO", "name": "NYISO", "region": None, "regions": ["NY"], "operator": None, "members": ["NYIS"], "tz": "America/New_York", "peak_mw": 31005.5, "ref_hub": "nyiso:N.Y.C.", "file": "op-nyiso.json"},
    {"id": "ba-soco", "kind": "ba", "code": "SOCO", "name": "Southern Company Services, Inc. - Trans", "region": "SE", "regions": ["SE"], "operator": None, "members": ["SOCO"], "tz": "America/Chicago", "peak_mw": 40711.0, "ref_hub": None, "file": "ba-soco.json"},
]

COLUMNS = [
    ("price.mean_da", "price", "Day-ahead price, mean", "USD/MWh", "ercot_prices"),
    ("price.p95_da", "price", "Day-ahead price, 95th percentile", "USD/MWh", "ercot_prices"),
    ("price.hours_over_100_da", "price", "Day-ahead hours above USD 100", "hours", "ercot_prices"),
    ("price.hours_below_0_da", "price", "Day-ahead hours below zero", "hours", "ercot_prices"),
    ("price.mean_rt", "price", "Real-time price, mean", "USD/MWh", "ercot_prices"),
    ("congestion.share_pct", "congestion", "Share of the price that was congestion", "pct", "congestion"),
    ("tightness.peak_mw", "tightness", "Peak demand", "MW", "eia930_demand"),
    ("tightness.peak_growth_pct", "tightness", "Growth of the peak", "pct", "eia930_demand"),
    ("tightness.alert_days", "tightness", "Days with any notice", "days", "alerts"),
    ("tightness.out_mw_at_peak", "tightness", "Out of service at the peak hour", "MW", "outages"),
    ("tightness.reserve_margin_pct", "tightness", "Planning reserve margin", "pct", "cdr"),
    ("queue.active_mw", "queue", "Active requests", "MW", "queue"),
    ("queue.withdrawn_share_pct", "queue", "Share withdrawn, historically", "pct", "queue"),
    ("queue.median_years_to_operation", "queue", "Median years from request to operation", "years", "durations"),
    ("large_load.rules_n", "large_load", "Large-load rules held", "count", "rules"),
    ("large_load.smallest_threshold_mw", "large_load", "Smallest load a rule applies to", "MW", "rules"),
    ("mix_carbon.intensity", "mix_carbon", "Carbon intensity, mean", "kgCO2/MWh", "carbon"),
    ("imports.net_import_share_pct", "imports", "Net imports as a share of demand", "pct", "interchange"),
    ("imports.net_import_share_peak_pct", "imports", "Net imports as a share of demand, 100 highest hours", "pct", "interchange"),
    ("spare.curtailed_wind_mwh", "spare", "Wind curtailed", "MWh", "curtailment"),
    ("spare.curtailed_solar_mwh", "spare", "Solar curtailed", "MWh", "curtailment"),
    ("forecast.operator_mape_pct", "forecast", "Operator's forecast error", "pct", "scores"),
    ("forecast.erw_mape_pct", "forecast", "ERW forecast's error", "pct", "scores"),
    ("datacenters.facilities_n", "datacenters", "Facilities held", "count", "dc_facilities"),
    ("datacenters.projects_mw_stated", "datacenters", "Projects' stated megawatts", "MW", "dc_projects"),
]
NYISO_PRICE = "license needed: NYISO's prices need a paid data license (docs/licenses.md); none is held"
NOT_MARKET = "not a market: Southern Company's area has no organised market whose hub prices the warehouse holds"
NOT_PUBLISHED = "not published: the operator prints no such figure in the files read"
# one value a column, or a reason. A tuple (value, period, src) is a cell whose period and source are its own.
ROWS = {
    "region-tex": [46.31, 118.7, 312, 41, 44.02, NOT_PUBLISHED, 85111.0, 3.42, 9, NOT_PUBLISHED, 12.1, 204512.5, 71.3, 3.8, 6, 75, 372.44, 0.14, 0.31, 3104220, 2987003, 2.19, 6.1, 141, 23450],
    "op-ercot": [46.31, 118.7, 312, 41, 44.02, NOT_PUBLISHED, 85111.0, 3.42, 9, NOT_PUBLISHED, 12.1, 204512.5, 71.3, 3.8, 6, 75, 372.44, 0.14, 0.31, 3104220, 2987003, 2.19, 6.1, 141, 23450],
    "op-nyiso": [NYISO_PRICE, NYISO_PRICE, NYISO_PRICE, NYISO_PRICE, NYISO_PRICE, NYISO_PRICE, 31005.5, -1.2, NOT_PUBLISHED, NOT_PUBLISHED, (18.6, "summer 2027 (NYISO's made-up report)", "cdr"), 118040.0, 78.9, 4.6, 2, 20, 248.9, 12.75, 21.4, NOT_PUBLISHED, NOT_PUBLISHED, 1.96, 3.05, 38, 4100],
    "ba-soco": [NOT_MARKET, NOT_MARKET, NOT_MARKET, NOT_MARKET, NOT_MARKET, NOT_MARKET, 40711.0, 5.05, NOT_PUBLISHED, NOT_PUBLISHED, NOT_PUBLISHED, 61220.0, 64.0, 5.2, 4, 100, 401.07, -2.6, -0.8, NOT_PUBLISHED, NOT_PUBLISHED, 1.44, 4.9, 96, 18200],
}


def write(name, doc):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=True)
        f.write("\n")


def table():
    cols = [{"key": k, "section": s, "label": lab, "unit": u, "period": "2026" if k.startswith(("queue.", "large_load.", "datacenters.")) else P12, "src": src} for k, s, lab, u, src in COLUMNS]
    # both forms the section reads. The contract's first: a column carries its period and source, a cell its own only
    # where it differs. The builder's (its first files of 28 November): the "tightness" columns here carry none, and
    # every cell of them carries its own.
    by_cell = [i for i, c in enumerate(cols) if c["section"] == "tightness"]
    rows = []
    for p in PLACES:
        vals, own = [], {}
        for i, x in enumerate(ROWS[p["id"]]):
            if isinstance(x, str):
                vals.append(None)
                own[str(i)] = {"period": cols[i]["period"], "src": "iso_prices" if x == NYISO_PRICE else cols[i]["src"], "held": x}
            elif isinstance(x, tuple):
                vals.append(x[0])
                own[str(i)] = {"period": x[1], "src": x[2], "held": None}
            else:
                vals.append(x)
                if i in by_cell:
                    own[str(i)] = {"period": cols[i]["period"], "src": cols[i]["src"], "held": None}
        rows.append({"id": p["id"], "kind": p["kind"], "name": p["name"], "v": vals, "cell": own})
    for i in by_cell:
        cols[i]["period"] = None
        cols[i]["src"] = None
    return {**HEAD, "sources": SOURCES, "columns": cols, "rows": rows}


def ercot():
    hub = lambda market, mean, p95, over, below, hours: {"hub_id": "ercot:HB_HUBAVG", "hub": "ERCOT Hub Average", "operator": "op-ercot", "market": market, "mean": cell(mean, "USD/MWh", "ercot_prices", months=trend(30.5, 0.75)), "p95": cell(p95, "USD/MWh", "ercot_prices"), "hours_over_100": cell(over, "hours", "ercot_prices"), "hours_below_0": cell(below, "hours", "ercot_prices"), "hours": cell(hours, "hours", "ercot_prices")}
    constraints = [{"name": f"MADE-UP CONSTRAINT {i + 1}", "contingency": "Base Case" if i % 2 == 0 else f"MADE-UP OUTAGE {i}", "hours": 900 - 70 * i, "cost": 41250.5 - 3100.25 * i, "abs_mean": round(45.83 - 2.5 * i, 2)} for i in range(10)]
    by_hour = [398.2, 396.4, 395.1, 394.8, 395.9, 399.3, 401.7, 392.6, 371.4, 352.8, 341.9, 336.2, 333.5, 334.1, 338.7, 347.3, 361.9, 380.4, 392.2, 397.8, 400.3, 401.1, 400.6, 399.4]
    return {**HEAD, "id": "op-ercot", "kind": "operator", "code": "ERCOT", "name": "ERCOT", "tz": "America/Chicago", "members": ["ERCO"], "sources": SOURCES, "sections": {
        # the third hub is listed with a status of its own and no figures, as the builder lists an operator held whole
        "price": {"status": "shown", "hubs": [hub("day-ahead", 46.31, 118.7, 312, 41, 8760), hub("real-time", 44.02, 131.25, 298, 187, 8758),
                                              {"hub_id": "made-up:HELD", "hub": "A made-up hub held whole", "operator": "op-ercot", "market": "day-ahead", "status": "license needed: a made-up hub whose prices need a license"}]},
        "congestion": {"status": "shown", "hubs": [{"hub_id": "ercot:HB_HUBAVG", "hub": "ERCOT Hub Average", "congestion_share_pct": cell(None, "pct", "congestion", held=NOT_PUBLISHED), "congestion_mean": cell(None, "USD/MWh", "congestion", held=NOT_PUBLISHED)}],
                       "top_by_hours": constraints, "top_by_cost": list(reversed(constraints)), "top_period": P12, "top_src": "constraints", "top_held": None},
        "tightness": {"status": "shown", "peak_mw": cell(85111.0, "MW", "eia930_demand", months=trend(61000, 1000)), "peak_prior_mw": cell(82296.5, "MW", "eia930_demand", "2024-11-01..2025-10-31"), "peak_growth_pct": cell(3.42, "pct", "eia930_demand", "2024-11-01..2025-10-31 to 2025-11-01..2026-10-31"),
                      "peak_hour": cell("2026-08-20T21:00:00Z", "UTC", "eia930_demand"), "alerts": cell(4, "count", "alerts"), "watches": cell(11, "count", "alerts"), "emergencies": cell(0, "count", "alerts"), "alert_days": cell(9, "days", "alerts"),
                      "out_mw_at_peak": cell(None, "MW", "outages", held=NOT_PUBLISHED), "reserve_margin_pct": cell(12.1, "pct", "cdr", "summer 2027 (ERCOT's made-up report)"), "reserve_target_pct": cell(13.75, "pct", "cdr", "summer 2027 (ERCOT's made-up report)")},
        "queue": {"status": "shown", "active_mw": cell(204512.5, "MW", "queue", "2025"), "active_projects": cell(1412, "count", "queue", "2025"), "withdrawn_share_pct": cell(71.3, "pct", "queue", "2000..2020"), "median_years_to_operation": cell(3.8, "years", "durations", "2021..2025"),
                  "by_fuel": [{"fuel": "Solar", "active_mw": cell(81200.0, "MW", "queue", "2025"), "active_projects": cell(520, "count", "queue", "2025")}, {"fuel": "Battery", "active_mw": cell(74310.5, "MW", "queue", "2025"), "active_projects": cell(610, "count", "queue", "2025")}, {"fuel": "Wind", "active_mw": cell(21002.0, "MW", "queue", "2025"), "active_projects": cell(104, "count", "queue", "2025")}]},
        "large_load": {"status": "shown", "rules_n": cell(6, "count", "rules", "2026-11-26"), "smallest_threshold_mw": cell(75, "MW", "rules", "2026-11-26"),
                       # three ways a rule comes: with its document's address (the contract's first text); with its id alone (the
                       # builder's files: the tab's own rule of that id); with an address that is no web address (never a link)
                       "rules": [{"id": "made-up-rule-1", "utility": "Made-up Wires Company", "state": "TX", "status": "in effect", "threshold_mw": 75, "threshold_text": "75 MW or more at a single site, as the made-up rule prints it", "contract_term": "ten years, as the made-up document prints it", "collateral": None, "exit_fee": "made-up exit fee words", "study_timeline": "90 days", "source_url": "https://example.org/made-up-rule-1"},
                                 {"id": "made-up-rule-2", "utility": "Made-up Electric Cooperative", "state": "TX", "status": "proposed", "threshold_mw": None, "threshold_text": "no threshold printed in the made-up tariff", "contract_term": None, "collateral": "made-up collateral words", "exit_fee": None, "study_timeline": None, "source_url": "javascript:alert(1)"},
                                 {"id": "made-up-rule-3", "utility": "Made-up Power and Light", "state": "TX", "status": "in effect", "threshold_mw": 20.0, "threshold_text": "20 MW", "contract_term": "a made-up contract term that runs on for well over ninety-six characters so that the table cuts it at a word and gives the whole of it on hover, as the tab's own rules table does", "collateral": None, "exit_fee": None, "study_timeline": None}],
                       "queue_totals": [{"utility": "Made-up Wires Company", "state": "TX", "date": "2026-09-30", "mw": 12500, "figure": "12.5 GW of requests, as the made-up filing prints it", "source_url": "https://example.org/made-up-queue-total"}],
                       "laws": [{"state": "TX", "bill": "SB 0000", "status": "enacted", "title": "A made-up act on large loads"}],
                       "rules_src": "rules", "queue_totals_src": "rules", "laws_src": "rules", "states": ["TX"]},
        "mix_carbon": {"status": "shown", "intensity": cell(372.44, "kgCO2/MWh", "carbon", months=trend(410.0, -1.5)), "mix": [{"fuel": "Natural gas", "share_pct": cell(44.1, "pct", "supply")}, {"fuel": "Wind", "share_pct": cell(24.3, "pct", "supply")}, {"fuel": "Solar", "share_pct": cell(11.25, "pct", "supply")}, {"fuel": "Coal", "share_pct": cell(12, "pct", "supply")}, {"fuel": "Nuclear", "share_pct": cell(8.35, "pct", "supply")}],
                       "intensity_by_hour": by_hour, "intensity_by_hour_period": P12, "intensity_by_hour_src": "carbon", "intensity_by_hour_held": None},
        "imports": {"status": "shown", "net_import_share_pct": cell(0.14, "pct", "interchange", months=trend(-0.4, 0.05)), "net_import_share_peak_pct": cell(0.31, "pct", "interchange", "2025-11-01..2026-10-31 (the 100 highest-demand hours)"),
                    "partners": [{"ba": "SWPP", "name": "Southwest Power Pool", "net_import_mwh": cell(412300.5, "MWh", "interchange")}, {"ba": "CEN", "name": "Centro Nacional de Control de Energia", "net_import_mwh": cell(88120, "MWh", "interchange")}, {"ba": "MISO", "name": "Midcontinent Independent System Operator, Inc.", "net_import_mwh": cell(-1204.25, "MWh", "interchange")}]},
        # a trend with months not held (the first twelve): the line is drawn over the months it has; one with a single month: no line
        "spare": {"status": "shown", "curtailed_wind_mwh": cell(3104220, "MWh", "curtailment", months=trend(180000, 9000, missing=range(12))), "curtailed_solar_mwh": cell(2987003, "MWh", "curtailment", months=trend(200000, 0, missing=range(23))), "negative_price_hours": cell(41, "hours", "ercot_prices")},
        "forecast": {"status": "shown", "operator_mape_pct": cell(2.19, "pct", "scores", "the 730 days to 2026-11-25"), "erw_mape_pct": cell(6.1, "pct", "scores", "the 730 days to 2026-11-25"), "hours": cell(17520, "hours", "scores", "the 730 days to 2026-11-25")},
        "datacenters": {"status": "shown", "facilities_n": cell(141, "count", "dc_facilities", "2026-11-26"), "facilities_mw_stated": cell(9120.5, "MW", "dc_facilities", "2026-11-26"), "projects_n": cell(58, "count", "dc_projects", "2026-11-26"), "projects_mw_stated": cell(23450, "MW", "dc_projects", "2026-11-26"), "facilities_mw_n": cell(77, "count", "dc_facilities", "2026-11-26"),
                        "list": [{"name": "Made-up Campus One", "operator": "Made-up Operator", "state": "TX", "county": "Made-up County", "mw": 1200, "status": "announced", "source_url": "https://example.org/made-up-campus"}]},
    }}


def nyiso():
    lic = lambda unit: cell(None, unit, "iso_prices", held=NYISO_PRICE)
    hub = {"hub_id": "nyiso:N.Y.C.", "hub": "New York City", "operator": "op-nyiso", "market": "day-ahead", "mean": lic("USD/MWh"), "p95": lic("USD/MWh"), "hours_over_100": lic("hours"), "hours_below_0": lic("hours"), "hours": lic("hours")}
    np_ = lambda unit, src: cell(None, unit, src, held=NOT_PUBLISHED)
    return {**HEAD, "id": "op-nyiso", "kind": "operator", "code": "NYISO", "name": "NYISO", "tz": "America/New_York", "members": ["NYIS"], "sources": SOURCES, "sections": {
        "price": {"status": NYISO_PRICE, "hubs": [hub]},
        "congestion": {"status": NYISO_PRICE, "hubs": [], "top_by_hours": [], "top_by_cost": [], "top_period": None, "top_src": "constraints", "top_held": NOT_PUBLISHED},
        "tightness": {"status": "shown", "peak_mw": cell(31005.5, "MW", "eia930_demand"), "peak_prior_mw": cell(31382.0, "MW", "eia930_demand", "2024-11-01..2025-10-31"), "peak_growth_pct": cell(-1.2, "pct", "eia930_demand"), "peak_hour": cell("2026-07-16T21:00:00Z", "UTC", "eia930_demand"),
                      "alerts": np_("count", "alerts"), "watches": np_("count", "alerts"), "emergencies": np_("count", "alerts"), "alert_days": np_("days", "alerts"), "out_mw_at_peak": np_("MW", "outages"), "reserve_margin_pct": cell(18.6, "pct", "cdr", "2027"), "reserve_target_pct": np_("pct", "cdr")},
        "queue": {"status": "shown", "active_mw": cell(118040.0, "MW", "queue", "2025"), "active_projects": cell(602, "count", "queue", "2025"), "withdrawn_share_pct": cell(78.9, "pct", "queue", "2000..2020"), "median_years_to_operation": cell(4.6, "years", "durations", "2021..2025"), "by_fuel": []},
        "large_load": {"status": "shown", "rules_n": cell(2, "count", "rules", "2026-11-26"), "smallest_threshold_mw": cell(20, "MW", "rules", "2026-11-26"), "rules": [], "queue_totals": [], "laws": []},
        "mix_carbon": {"status": "shown", "intensity": cell(248.9, "kgCO2/MWh", "carbon"), "mix": [], "mix_held": "not held: no net generation by source is held for this place (made-up)", "intensity_by_hour": [None] * 24, "intensity_by_hour_period": None, "intensity_by_hour_src": "carbon", "intensity_by_hour_held": "too few: fewer than 300 days of the last 12 months hold every hour"},
        "imports": {"status": "shown", "net_import_share_pct": cell(12.75, "pct", "interchange"), "net_import_share_peak_pct": cell(21.4, "pct", "interchange"), "partners": []},
        "spare": {"status": NOT_PUBLISHED, "curtailed_wind_mwh": np_("MWh", "curtailment"), "curtailed_solar_mwh": np_("MWh", "curtailment"), "negative_price_hours": lic("hours")},
        "forecast": {"status": "shown", "operator_mape_pct": cell(1.96, "pct", "scores"), "erw_mape_pct": cell(3.05, "pct", "scores"), "hours": cell(17500, "hours", "scores")},
        "datacenters": {"status": "shown", "facilities_n": cell(38, "count", "dc_facilities", "2026-11-26"), "facilities_mw_stated": cell(1210, "MW", "dc_facilities", "2026-11-26"), "projects_n": cell(9, "count", "dc_projects", "2026-11-26"), "projects_mw_stated": cell(4100, "MW", "dc_projects", "2026-11-26"), "facilities_mw_n": cell(12, "count", "dc_facilities", "2026-11-26"), "list": [], "list_held": "license needed: the list is held with its tables (made-up words of the builder)"},
    }}


if __name__ == "__main__":
    write("index.json", {**HEAD, "ba_floor_mw": 5000, "ba_floor_period": P12, "places": PLACES, "sections": SECTIONS})
    write("table.json", table())
    e = ercot()
    write("op-ercot.json", e)
    write("region-tex.json", {**e, "id": "region-tex", "kind": "region", "code": "TEX", "name": "Texas"})
    write("op-nyiso.json", nyiso())
    # ba-soco.json is left out on purpose: a place of the index with no file of its own
    print(f"written: index.json, table.json, op-ercot.json, region-tex.json, op-nyiso.json under {OUT}")
