"""Where the next gigawatts can go: every count the warehouse holds, set side by side for each place.

Writes site/data/siting/regions/ (index.json, one file a place, table.json) by the contract
docs/state/page_files_siting_regions.md. Method: docs/methods/siting_regions.md.

The places are EIA's 13 regions, the seven market operators and the balancing authorities of at least
5,000 MW, as the Grid tool (site/data/regions/index.json) and the forecast already name them.

No score, no rank, no advice: each count is what its publisher published, or a plain arithmetic of it
(a share, a sum, a mean, a percentile, a count of hours). A count the warehouse cannot show is written
null with its reason in `held`. No request is made: every figure comes from a table already held.

Usage:
  python warehouse/derived/siting_regions.py            # build from warehouse/output
  python warehouse/derived/siting_regions.py --example  # the contract's example files (every value null)
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT_DIR = os.path.join(ROOT, "site", "data", "siting", "regions")
CONTRACT = "docs/state/page_files_siting_regions.md"
METHOD = "docs/methods/siting_regions.md"
BA_FLOOR_MW = 5000

# The seven market operators: their EIA-930 authority and the ids the operator tables use.
OPERATORS = [
    ("op-caiso", "caiso", "CISO", "CAISO"),
    ("op-ercot", "ercot", "ERCO", "ERCOT"),
    ("op-spp", "spp", "SWPP", "SPP"),
    ("op-miso", "miso", "MISO", "MISO"),
    ("op-pjm", "pjm", "PJM", "PJM"),
    ("op-nyiso", "nyiso", "NYIS", "NYISO"),
    ("op-isone", "isone", "ISNE", "ISO-NE"),
]

# The sections and their counts, in the page's order (contract section 1, `sections[]`).
SECTIONS = [
    ("price", "Price", [
        ("mean", "Mean price", "USD/MWh"), ("p95", "95th percentile price", "USD/MWh"),
        ("hours_over_100", "Hours above USD 100", "hours"), ("hours_below_0", "Hours below zero", "hours"),
        ("hours", "Hours held", "hours")]),
    ("congestion", "Congestion", [
        ("congestion_share_pct", "Share of the price that was congestion", "pct"),
        ("congestion_mean", "Mean congestion part of the price", "USD/MWh")]),
    ("tightness", "How tight the grid runs", [
        ("peak_mw", "Peak demand", "MW"), ("peak_prior_mw", "Peak demand, the 12 months before", "MW"),
        ("peak_growth_pct", "Growth of the peak", "pct"), ("peak_hour", "Hour of the peak", "UTC"),
        ("alerts", "Alerts", "count"), ("watches", "Watches", "count"), ("emergencies", "Emergencies", "count"),
        ("alert_days", "Days with any notice", "days"), ("out_mw_at_peak", "Out of service at the peak hour", "MW"),
        ("reserve_margin_pct", "Planning reserve margin", "pct"), ("reserve_target_pct", "Reserve margin target", "pct")]),
    ("queue", "What is waiting to connect", [
        ("active_mw", "Active requests", "MW"), ("active_projects", "Active requests", "count"),
        ("withdrawn_share_pct", "Share withdrawn, historically", "pct"),
        ("median_years_to_operation", "Median years from request to operation", "years")]),
    ("large_load", "Large loads", [
        ("rules_n", "Large-load rules held", "count"), ("smallest_threshold_mw", "Smallest load a rule applies to", "MW")]),
    ("mix_carbon", "What the power is made of and what it emits", [
        ("intensity", "Carbon intensity, mean", "kgCO2/MWh")]),
    ("imports", "What it leans on its neighbours for", [
        ("net_import_share_pct", "Net imports as a share of demand", "pct"),
        ("net_import_share_peak_pct", "Net imports as a share of demand, 100 highest hours", "pct")]),
    ("spare", "What is spare", [
        ("curtailed_wind_mwh", "Wind curtailed", "MWh"), ("curtailed_solar_mwh", "Solar curtailed", "MWh"),
        ("negative_price_hours", "Hours of negative price", "hours")]),
    ("forecast", "How well its demand is forecast", [
        ("operator_mape_pct", "Operator's forecast error", "pct"), ("erw_mape_pct", "ERW forecast's error", "pct"),
        ("hours", "Hours scored", "hours")]),
    ("datacenters", "Datacenters already there", [
        ("facilities_n", "Facilities held", "count"), ("facilities_mw_stated", "Facilities' stated megawatts", "MW"),
        ("projects_n", "Announced projects held", "count"), ("projects_mw_stated", "Projects' stated megawatts", "MW")]),
]

# table.json's columns: (key, section, label, unit), each a count of the place file's own.
TABLE_COLUMNS = [
    ("price.mean_da", "price", "Day-ahead price, mean", "USD/MWh"),
    ("price.p95_da", "price", "Day-ahead price, 95th percentile", "USD/MWh"),
    ("price.hours_over_100_da", "price", "Day-ahead hours above USD 100", "hours"),
    ("price.hours_below_0_da", "price", "Day-ahead hours below zero", "hours"),
    ("price.mean_rt", "price", "Real-time price, mean", "USD/MWh"),
    ("congestion.share_pct", "congestion", "Share of the price that was congestion", "pct"),
    ("tightness.peak_mw", "tightness", "Peak demand", "MW"),
    ("tightness.peak_growth_pct", "tightness", "Growth of the peak", "pct"),
    ("tightness.alert_days", "tightness", "Days with any notice", "days"),
    ("tightness.out_mw_at_peak", "tightness", "Out of service at the peak hour", "MW"),
    ("tightness.reserve_margin_pct", "tightness", "Planning reserve margin", "pct"),
    ("queue.active_mw", "queue", "Active requests", "MW"),
    ("queue.withdrawn_share_pct", "queue", "Share withdrawn, historically", "pct"),
    ("queue.median_years_to_operation", "queue", "Median years from request to operation", "years"),
    ("large_load.rules_n", "large_load", "Large-load rules held", "count"),
    ("large_load.smallest_threshold_mw", "large_load", "Smallest load a rule applies to", "MW"),
    ("mix_carbon.intensity", "mix_carbon", "Carbon intensity, mean", "kgCO2/MWh"),
    ("imports.net_import_share_pct", "imports", "Net imports as a share of demand", "pct"),
    ("imports.net_import_share_peak_pct", "imports", "Net imports, 100 highest hours", "pct"),
    ("spare.curtailed_wind_mwh", "spare", "Wind curtailed", "MWh"),
    ("spare.curtailed_solar_mwh", "spare", "Solar curtailed", "MWh"),
    ("forecast.operator_mape_pct", "forecast", "Operator's forecast error", "pct"),
    ("forecast.erw_mape_pct", "forecast", "ERW forecast's error", "pct"),
    ("datacenters.facilities_n", "datacenters", "Facilities held", "count"),
    ("datacenters.projects_mw_stated", "datacenters", "Projects' stated megawatts", "MW"),
]

EXAMPLE_HELD = "not held: example file, written before the builder"

# EIA-930's sources of net generation, in words (done-line request 589: one form in the files, as the queue's fuels are)
FUEL_WORDS = {"natural_gas": "Natural gas", "coal": "Coal", "nuclear": "Nuclear", "hydro": "Hydro", "wind": "Wind",
              "solar": "Solar", "storage": "Battery storage", "petroleum": "Petroleum", "other": "Other"}


def now_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def cell(v, unit, period, src, held=None):
    """One count, in the contract's form. A held count never carries a figure."""
    if held:
        v = None
    return {"v": v, "unit": unit, "period": period, "src": src, "held": held}


def sections_catalogue():
    return [{"id": sid, "title": title, "counts": [{"key": k, "label": lab, "unit": u} for k, lab, u in counts]}
            for sid, title, counts in SECTIONS]


def write_json(path, doc):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(doc, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    os.replace(tmp, path)


def example_files(out_dir):
    """The contract's example files: three places, every value null with the example's reason."""
    built = now_utc()
    head = {"built": built, "example": True, "contract": CONTRACT, "method": METHOD, "license": "public"}
    places = [
        {"id": "region-tex", "kind": "region", "code": "TEX", "name": "Texas", "region": "TEX", "regions": ["TEX"],
         "operator": None, "members": ["ERCO"], "tz": "America/Chicago", "peak_mw": None, "ref_hub": None,
         "file": "region-tex.json"},
        {"id": "op-ercot", "kind": "operator", "code": "ERCOT", "name": "ERCOT", "region": None, "regions": ["TEX"],
         "operator": None, "members": ["ERCO"], "tz": "America/Chicago", "peak_mw": None, "ref_hub": None,
         "file": "op-ercot.json"},
        {"id": "ba-soco", "kind": "ba", "code": "SOCO", "name": "Southern Company Services, Inc. - Trans",
         "region": "SE", "regions": ["SE"], "operator": None, "members": ["SOCO"], "tz": "America/Chicago",
         "peak_mw": None, "ref_hub": None, "file": "ba-soco.json"},
    ]
    index = dict(head, ba_floor_mw=BA_FLOOR_MW, ba_floor_period=None, places=places, sections=sections_catalogue())
    write_json(os.path.join(out_dir, "index.json"), index)

    src = {"example": {"table": None, "publisher": None, "license": "public", "retrieved": None,
                       "report": "example file: no table read"}}
    nul = lambda unit: cell(None, unit, None, "example", EXAMPLE_HELD)  # noqa: E731
    secs = {}
    for sid, _title, counts in SECTIONS:
        secs[sid] = {"status": EXAMPLE_HELD}
        for k, _lab, u in counts:
            if sid in ("price", "congestion"):
                continue
            secs[sid][k] = nul(u)
    secs["price"]["hubs"] = [dict({"hub_id": None, "hub": None, "operator": "op-ercot", "market": m},
                                  **{k: nul(u) for k, _l, u in SECTIONS[0][2]}) for m in ("day-ahead", "real-time")]
    secs["congestion"].update({"hubs": [], "top_by_hours": [], "top_by_cost": [], "top_period": None,
                               "top_src": "example", "top_held": EXAMPLE_HELD})
    secs["queue"]["by_fuel"] = []
    secs["large_load"].update({"rules": [], "queue_totals": [], "laws": []})
    secs["mix_carbon"].update({"mix": [], "intensity_by_hour": [None] * 24, "intensity_by_hour_period": None,
                               "intensity_by_hour_src": "example", "intensity_by_hour_held": EXAMPLE_HELD})
    secs["imports"]["partners"] = []
    secs["datacenters"].update({"facilities_mw_n": nul("count"), "list": []})
    place = dict(head, id="op-ercot", kind="operator", code="ERCOT", name="ERCOT", tz="America/Chicago",
                 members=["ERCO"], sources=src, sections=secs)
    write_json(os.path.join(out_dir, "op-ercot.json"), place)

    cols = [{"key": k, "section": s, "label": lab, "unit": u, "period": None, "src": "example"}
            for k, s, lab, u in TABLE_COLUMNS]
    rows = [{"id": p["id"], "kind": p["kind"], "name": p["name"], "v": [None] * len(cols),
             "cell": {str(i): {"period": None, "src": "example", "held": EXAMPLE_HELD} for i in range(len(cols))}}
            for p in places]
    write_json(os.path.join(out_dir, "table.json"), dict(head, sources=src, columns=cols, rows=rows))
    print(f"example files written to {out_dir}: index.json (3 places), op-ercot.json, table.json")
    return 0


# ---------------------------------------------------------------------------------------------------------------
# The build. Every reader takes a table of warehouse/output whole or in chunks, kept to the rows it needs.
# ---------------------------------------------------------------------------------------------------------------

TABLES_DIR = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
REGIONS_INDEX = os.path.join(ROOT, "site", "data", "regions", "index.json")
SCORES = os.path.join(ROOT, "site", "data", "predict", "scores.json")
COVERAGE = os.path.join(ROOT, "warehouse", "metadata", "coverage.csv")

# Grids whose prices a license or a pause holds (the same words as conditions_page.py and congestion_page.py).
HELD_OP = {
    "pjm": "license needed: PJM's terms forbid non-members to republish its data (docs/licenses.md)",
    "nyiso": "license needed: NYISO's terms reserve its data; written permission needed (docs/licenses.md)",
    "isone": "license needed: ISO-NE's terms ask written permission (docs/licenses.md)",
    "miso": "paused: MISO's terms forbid automated access; the ERW paused it on 4 October 2026 (docs/methods/miso_pause.md)",
}
# The hubs held, by operator: (entity in the tables, name). ref_hub is the first.
HUBS = {
    "ercot": [("ercot:HB_HUBAVG", "ERCOT Hub Average"), ("ercot:HB_NORTH", "ERCOT North Hub"),
              ("ercot:HB_HOUSTON", "ERCOT Houston Hub"), ("ercot:HB_SOUTH", "ERCOT South Hub"),
              ("ercot:HB_WEST", "ERCOT West Hub"), ("ercot:HB_BUSAVG", "ERCOT Bus Average")],
    "caiso": [("caiso:TH_SP15_GEN-APND", "CAISO SP15 trading hub"), ("caiso:TH_NP15_GEN-APND", "CAISO NP15 trading hub"),
              ("caiso:TH_ZP26_GEN-APND", "CAISO ZP26 trading hub")],
    "spp": [("spp:SPPNORTH_HUB", "SPP North Hub"), ("spp:SPPSOUTH_HUB", "SPP South Hub")],
    "nyiso": [("nyiso:N.Y.C.", "NYISO New York City (Zone J)")],
    "isone": [("isone:.H.INTERNAL_HUB", "ISO-NE Internal Hub")],
    "miso": [("miso:INDIANA.HUB", "MISO Indiana Hub")],
    "pjm": [],
}
# Done-line request 590: one name a hub in every list; CAISO's load areas named as the congestion page names them.
HUB_NAME = {ent: name for hubs in HUBS.values() for ent, name in hubs}
ZONE_NAMES = {"DLAP_PGAE-APND": "CAISO PG&E default load area", "DLAP_SCE-APND": "CAISO SCE default load area",
              "DLAP_SDGE-APND": "CAISO SDG&E default load area", "DLAP_VEA-APND": "CAISO VEA default load area"}


def own_reports(report, match):
    """A table's reports kept to one operator's (done-line request 590): with match (column, prefix), the parts of the
    coverage row's report list that begin with that operator's id; otherwise the list as it stands."""
    if not report or not match:
        return report
    op = match[1].rstrip(":")
    mine = [p for p in report.split(";") if p.strip().startswith(op + ":")]
    return ";".join(mine) if mine else report


# The region each operator's authority belongs to (site/data/regions/index.json), for the regions' hubs.
OP_OF_BA = {ba: op for _pid, op, ba, _n in OPERATORS}
COVER_FLOOR = 0.8          # a hub's statistic is shown when it holds at least 80 percent of the period's hours
MIN_DURATIONS = 5          # the median years to operation needs at least five projects
STATE_SHARE = 0.85         # a state is one authority's when 85 percent of its retail sales are there
STATE_REACH = 0.10         # a place reaches a state at 10 percent of either's retail sales

# The three groups of notices, from each operator's own kinds (event_type of grid_all_alerts). Kinds left out
# (updates, statements, tests) are not notices of a condition.
NOTICE_GROUP = {
    "caiso": {"alerts": {"rmo", "alert", "flex_alert", "vlrp"}, "watches": {"warning", "eea_watch"},
              "emergencies": {"stage1", "stage2", "stage3", "eea1", "eea2", "eea3", "transmission_emergency",
                              "load_interruption"}},
    "ercot": {"alerts": {"ocn_weather", "advisory", "weather_watch", "conservation_appeal", "voluntary_conservation"},
              "watches": {"watch", "power_watch"}, "emergencies": {"eea1", "eea2", "eea3", "rotating_outages"}},
}
OUTAGE_ENTITY = {"caiso": "caiso:ISO", "spp": "spp:SPP"}
CURTAIL_ENTITY = {"caiso": "caiso:ISO", "spp": "spp:SPP"}

# Berkeley Lab's queue: its region for an operator, and its entity for an authority outside the markets.
LBNL_REGION = {"caiso": "CAISO", "ercot": "ERCOT", "spp": "SPP", "miso": "MISO", "pjm": "PJM", "nyiso": "NYISO",
               "isone": "ISO-NE"}
LBNL_ENTITY_BA = {"SOCO": "SOCO", "TVA": "TVA", "BPA": "BPAT", "FPL": "FPL", "APS": "AZPS", "NVE": "NEVP",
                  "PSCo": "PSCO", "SRP": "SRP", "LGE-KU": "LGEE", "TEC": "TEC", "S-C": "SC", "IP": "IPCO",
                  "PNM": "PNM", "LADWP": "LDWP", "PSE": "PSEI", "PGE": "PGE", "TEP": "TEPC", "Avista": "AVA",
                  "NWMT": "NWMT", "EPE": "EPE", "IID": "IID", "SMUD": "BANC", "JEA": "JEA", "SEC": "SEC",
                  "AEC": "AEC", "TPU": "TPWR", "GrantPUD": "GCPD", "Dominion": "SCEG"}
# Entities spanning authorities: split by the request's state.
LBNL_SPLIT = {"Duke": {"FL": "FPC", "NC": "DUK", "SC": "DUK"}, "PacifiCorp": {"UT": "PACE", "WY": "PACE", "ID": "PACE",
              "OR": "PACW", "WA": "PACW", "CA": "PACW"}}
# Interconnection durations: the grid column for an operator.
DUR_GRID = {"caiso": "CAISO", "ercot": "ERCOT", "spp": "SPP", "miso": "MISO", "pjm": "PJM", "nyiso": "NYISO"}

# The large-load tables' region words, to an authority (first match wins).
LL_REGION_BA = [("CAISO", "CISO"), ("ERCOT", "ERCO"), ("ISO-NE", "ISNE"), ("NYISO", "NYIS"), ("MISO", "MISO"),
                ("PJM", "PJM"), ("SPP", "SWPP"), ("AZPS", "AZPS"), ("Bonneville", "BPAT"), ("DUK, CPLE", "DUK"),
                ("CPLE", "CPLE"), ("DUK", "DUK"), ("FPC", "FPC"), ("FPL", "FPL"), ("GCPD", "GCPD"), ("IID", "IID"),
                ("IPCO", "IPCO"), ("LGEE", "LGEE"), ("NEVP", "NEVP"), ("PACE", "PACE"), ("PACW", "PACW"),
                ("PGE", "PGE"), ("PSCO", "PSCO"), ("SOCO", "SOCO"), ("Santee Cooper", "SC"), ("TEC", "TEC"),
                ("TEPC", "TEPC"), ("TVA", "TVA"), ("Seattle City Light", "SCL")]
DC_GRID_BA = {"CAISO": "CISO", "ERCOT": "ERCO", "SPP": "SWPP", "MISO": "MISO", "PJM": "PJM", "NYISO": "NYIS",
              "ISO-NE": "ISNE"}


def header_rows(path):
    n = 0
    with open(path, "rb") as fh:
        for line in fh:
            if line.startswith(b"#"):
                n += 1
            else:
                break
    return n


def read(name, cols, keep=None, chunk=1_000_000):
    """A table of warehouse/output as strings, its header comment skipped by count (a '#' inside a row is kept)."""
    import pandas as pd
    p = os.path.join(TABLES_DIR, name + ".csv")
    if not os.path.exists(p):
        return None
    fh = open(p, "rb")
    for _ in range(header_rows(p)):
        fh.readline()
    parts = []
    for c in pd.read_csv(fh, usecols=cols, dtype=str, keep_default_na=False, chunksize=chunk):
        parts.append(c if keep is None else c[keep(c)])
    fh.close()
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=cols)


def num(s):
    import pandas as pd
    return pd.to_numeric(s, errors="coerce")


def rnd(v, n=1):
    import math
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    if math.isnan(f) or math.isinf(f):
        return None
    return round(f, n) if n else int(round(f))


class Periods:
    """The last 12 whole months before the build's month, and the 12 before them (UTC)."""

    def __init__(self, today=None):
        t = today or datetime.now(timezone.utc).date()
        end = t.replace(day=1)
        start = end.replace(year=end.year - 1)
        self.start, self.end = start.isoformat(), end.isoformat()            # [start, end)
        self.prior_start = start.replace(year=start.year - 1).isoformat()
        last = (datetime.fromisoformat(self.end) - __import__("datetime").timedelta(days=1)).date()
        self.label = f"{self.start}..{last.isoformat()}"
        plast = (datetime.fromisoformat(self.start) - __import__("datetime").timedelta(days=1)).date()
        self.prior_label = f"{self.prior_start}..{plast.isoformat()}"
        self.hours = int((datetime.fromisoformat(self.end) - datetime.fromisoformat(self.start)).total_seconds() // 3600)
        # the trends: the 24 whole months of both periods
        y, m = int(self.prior_start[:4]), int(self.prior_start[5:7])
        self.months = []
        for _ in range(24):
            self.months.append(f"{y:04d}-{m:02d}")
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        self.trend_label = f"{self.prior_start}..{last.isoformat()}"
        # part F of chain 760: the five whole calendar years before the build's year
        y_end = end.year if end.month > 1 else end.year - 1
        self.years = [str(y) for y in range(y_end - 5, y_end)]
        self.deep_start = f"{self.years[0]}-01-01"
        self.years_label = f"{self.years[0]}-01-01..{self.years[-1]}-12-31"

    def inside(self, ts):
        return (ts >= self.start) & (ts < self.end)

    def wide(self, ts):
        return (ts >= self.prior_start) & (ts < self.end)

    def deep(self, ts):
        return (ts >= self.deep_start) & (ts < self.end)


YEAR_FLOOR = 0.8   # a year's figure needs 80 percent of the year's hours (twelve months for a monthly table)


def years_of(P, ts, v, how, monthly=False):
    """A count by calendar year over the five whole years (contract, dated line of 28 November, part F): 'mean',
    'max' or 'sum' of the year's values; null for a year holding under 80 percent of its hours (all twelve months for a
    monthly table)."""
    vals, n = {}, {}
    if len(ts):
        yr = ts.astype(str).str.slice(0, 4).values
        vals = getattr(v.groupby(yr), how)().to_dict()
        n = v.groupby(yr).count().to_dict()
    out = []
    for y in P.years:
        need = 12 if monthly else YEAR_FLOOR * (8784 if int(y) % 4 == 0 else 8760)
        out.append(rnd(vals.get(y), 2) if n.get(y, 0) >= need else None)
    return {"years": list(P.years), "period": P.years_label, "v": out}


def years_ratio(P, ts, top, bottom, scale=100.0):
    """A ratio of yearly sums, times `scale`, over the five whole years; null under 80 percent of a year's hours."""
    out = []
    if len(ts):
        yr = ts.astype(str).str.slice(0, 4).values
        a, b, n = top.groupby(yr).sum(), bottom.groupby(yr).sum(), bottom.groupby(yr).count()
    for y in P.years:
        need = YEAR_FLOOR * (8784 if int(y) % 4 == 0 else 8760)
        ok = len(ts) and n.get(y, 0) >= need and b.get(y)
        out.append(rnd(a[y] / b[y] * scale, 2) if ok else None)
    return {"years": list(P.years), "period": P.years_label, "v": out}


def trend(P, ts, v, how):
    """A count by month over the 24 whole months (contract, dated line of 28 November): `how` is 'mean', 'max',
    'sum' or a function of two series (a ratio of sums), month by month; a month with no hour is null."""
    vals = {}
    if len(ts):
        mon = ts.astype(str).str.slice(0, 7).values
        vals = getattr(v.groupby(mon), how)().to_dict()
    return {"months": list(P.months), "period": P.trend_label,
            "v": [rnd(vals.get(m), 2) for m in P.months]}


def trend_ratio(P, ts, top, bottom, scale=100.0):
    """A ratio of monthly sums, times `scale` (net imports over demand), by month over the 24 months."""
    vals = {}
    if len(ts):
        mon = ts.astype(str).str.slice(0, 7).values
        a, b = top.groupby(mon).sum(), bottom.groupby(mon).sum()
        vals = {m: a[m] / b[m] * scale for m in a.index if b.get(m)}
    return {"months": list(P.months), "period": P.trend_label, "v": [rnd(vals.get(m), 2) for m in P.months]}


def coverage_rows():
    import csv
    out = {}
    with open(COVERAGE, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh):
            out[r["table"]] = r
    return out


LICENSE_STATUS = os.path.join(ROOT, "site", "data", "license_status.json")
GRID_PUBLISHERS = {"CAISO", "ERCOT", "SPP", "MISO", "PJM", "NYISO", "ISO-NE"}
_URLS = {}


def license_holds():
    """Tables the site holds whole for a license (site/data/license_status.json, the owner's rule of 16 November
    2026: the holds stand), with their reason. A table held only for some grids' rows is not held whole: those
    grids are held here by HELD_OP."""
    if not os.path.exists(LICENSE_STATUS):
        return {}
    with open(LICENSE_STATUS, encoding="utf-8") as fh:
        d = json.load(fh)
    out = {}
    for t, v in (d.get("tables") or {}).items():
        if not isinstance(v, dict) or v.get("status") != "license needed":
            continue
        pubs = v.get("publishers") or []
        if pubs and set(pubs) <= GRID_PUBLISHERS:
            continue
        out[t] = (f"license needed: the site holds {t} for a license from {v.get('from')} "
                  "(site/data/license_status.json; the owner's rule of 16 November 2026)")
    return out


def table_url(table, match=None):
    """The publisher's address of a table's report: the source_url of the table's first row (a derived table's is
    its method note's address), or, with match (column, prefix), of its first row whose column starts with the prefix
    (one operator's rows of a table of several; done-line request 586). None for a table without the column, a file
    not held, or no row matching."""
    key = (table, match)
    if key in _URLS:
        return _URLS[key]
    url = None
    p = os.path.join(TABLES_DIR, table + ".csv")
    if os.path.exists(p):
        import csv
        with open(p, encoding="utf-8", newline="") as fh:
            rd = csv.reader(ln for ln in fh if not ln.startswith("#"))
            head = next(rd, [])
            if "source_url" in head and (match is None or match[0] in head):
                iu = head.index("source_url")
                im = head.index(match[0]) if match else None
                for row in rd:
                    if match is None or row[im].startswith(match[1]):
                        url = row[iu] or None
                        break
    _URLS[key] = url
    return url


class Sources:
    """The file's `sources`: one entry a key, from the table's coverage row."""

    def __init__(self, cov, holds=None):
        self.cov, self.used, self.holds = cov, {}, holds or {}

    def key(self, key, table, publisher, report=None, url="first", match=None):
        """url: "first" (the first row's source_url), "row" (each listed row carries its own: none here), with match
        (column, prefix) the first matching row's (done-line request 586)."""
        if key not in self.used:
            r = self.cov.get(table, {})
            held = r.get("license") == "internal" or table in self.holds
            self.used[key] = {"table": table, "publisher": publisher,
                              "license": "internal" if held else "public",
                              "retrieved": r.get("last_run") or None,
                              "report": report or own_reports(r.get("source_report"), match) or None,
                              "url": None if table.startswith("site/") or url != "first" else
                              table_url(table.replace("<year>", "2025"), match),
                              "held": self.holds.get(table)}
        return key


def apply_holds(secs, sources):
    """A count from an internal or held source is written null with the hold's reason; a list drawn from such a
    source (the datacenters') is emptied. Run on each place's sections before the file is written."""
    def walk(o):
        if isinstance(o, dict):
            if set(o) >= {"v", "unit", "period", "src", "held"}:
                s = sources.get(o["src"]) or {}
                if s.get("license") == "internal":
                    o["v"], o["held"] = None, s.get("held") or "license needed: the table is internal"
                    if "trend" in o:
                        o["trend"]["v"] = [None] * len(o["trend"]["v"])
                return
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(secs)
    dc = secs.get("datacenters", {})
    if any((sources.get(k) or {}).get("license") == "internal" for k in ("dc_facilities", "dc_projects")):
        dc["list"] = []
        dc["list_held"] = (sources.get("dc_facilities") or {}).get("held")
        dc["status"] = dc["list_held"] or dc.get("status")


def load_places(P, cov):
    """The places: 13 regions, 7 operators, the authorities of at least 5,000 MW (by their last 12 months)."""
    with open(REGIONS_INDEX, encoding="utf-8") as fh:
        idx = json.load(fh)
    bas = {b["code"]: b for b in idx["bas"]}
    dem = read("eia930_ba_demand_hourly", ["entity", "variable", "ts_utc", "value"],
               keep=lambda c: (c.variable == "demand_mw") & P.deep(c.ts_utc))
    dem["ba"] = dem.entity.str.replace("eia930:", "", regex=False)
    dem["v"] = num(dem.value)
    # a reader's case of session 11200: EIA-930 holds hours that did not happen (TVA at 44,377 MW on 20 October 2026,
    # against 35,086 the year before), and a peak is the one hour most likely to be one of them. The warehouse's own
    # rule for impossible hours (warehouse/derived/impossible_hours.py, docs/methods/impossible_hours.md) blanks them
    # before any count reads demand, as the forecast and the demand growth table do
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
    import impossible_hours as ih
    dem = dem.sort_values(["ba", "ts_utc"]).reset_index(drop=True)
    dem["v"] = dem.groupby("ba", group_keys=False).v.apply(lambda s: ih.screen(s.reset_index(drop=True)).set_axis(s.index))
    reg = read("eia930_region_hourly", ["entity", "variable", "ts_utc", "value"],
               keep=lambda c: (c.ts_utc >= P.prior_start) & (c.ts_utc < P.end))
    reg["code"] = reg.entity.str.replace("eia930:", "", regex=False)
    reg["v"] = num(reg.value)
    cur = dem[P.inside(dem.ts_utc)]
    peaks = cur.groupby("ba").v.max().to_dict()
    places = []
    for r in idx["regions"]:
        places.append({"id": "region-" + r["code"].lower(), "kind": "region", "code": r["code"], "name": r["name"],
                       "region": r["code"], "regions": [r["code"]], "operator": None, "members": list(r["bas"]),
                       "tz": r["tz"]})
    op_ids = {}
    for pid, op, ba, name in OPERATORS:
        b = bas[ba]
        places.append({"id": pid, "kind": "operator", "code": name, "name": name, "region": None,
                       "regions": [b["region"]], "operator": None, "members": [ba], "tz": b["tz"], "op": op})
        op_ids[ba] = pid
    for code, b in sorted(bas.items()):
        if not (b.get("us") and b.get("active")) or code in op_ids or b.get("generation_only"):
            continue
        pk = peaks.get(code)
        if pk is None or pk < BA_FLOOR_MW:
            continue
        places.append({"id": "ba-" + code.lower(), "kind": "ba", "code": code, "name": b["name"],
                       "region": b["region"], "regions": [b["region"]], "operator": None, "members": [code],
                       "tz": b["tz"]})
    # an operator spans the regions of the authorities it dispatches for EIA (its own authority's region)
    return places, bas, dem, reg


def members_sum(frame, members):
    """A region's hourly series: its member authorities summed. A member is counted when it reports in at least
    90 percent of the span's hours (a member that has stopped or barely files is left out, and said so in the
    method note); an hour is kept only when every counted member has a value in it."""
    import pandas as pd
    x = frame[frame.ba.isin(members) & frame.v.notna()]
    if x.empty:
        return pd.DataFrame(columns=["ts_utc", "v"])
    w = x.pivot_table(index="ts_utc", columns="ba", values="v", aggfunc="first")
    keep = [c for c in w.columns if w[c].notna().sum() >= 0.9 * len(w)]
    w = w[keep].dropna()
    return pd.DataFrame({"ts_utc": w.index, "v": w.sum(axis=1).values})


def region_years(frame, members, P):
    """A region's hourly series over the five whole years, each calendar year summed by members_sum on its own (so a
    member is counted in a year where it reports 90 percent of that year's hours)."""
    import pandas as pd
    parts = []
    for y in P.years:
        x = frame[(frame.ts_utc >= f"{y}-01-01") & (frame.ts_utc < f"{int(y) + 1}-01-01")]
        if len(x):
            parts.append(members_sum(x, members))
    return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["ts_utc", "v"])


def peak_of(frame, period_mask):
    x = frame[period_mask & frame.v.notna()]
    if x.empty:
        return None, None
    i = x.v.idxmax()
    return float(x.v[i]), x.ts_utc[i]


def build_tightness(place, P, S, dem, reg, alerts, outages, reserves):
    sec = {}
    src = S.key("eia930_demand", "eia930_ba_demand_hourly", "EIA")
    if place["kind"] == "region":
        f = members_sum(dem[P.wide(dem.ts_utc)], place["members"]).reset_index(drop=True)
        fy = region_years(dem, place["members"], P)
    else:
        f = dem[dem.ba == place["members"][0]].reset_index(drop=True)
        fy = f
    pk, pk_ts = peak_of(f, P.inside(f.ts_utc))
    pp, _ = peak_of(f, (f.ts_utc >= P.prior_start) & (f.ts_utc < P.start))
    sec["peak_mw"] = cell(rnd(pk, 0), "MW", P.label, src, None if pk is not None else "not held: no demand hour held")
    sec["peak_mw"]["trend"] = trend(P, f.ts_utc, f.v, "max")
    sec["peak_mw"]["years"] = years_of(P, fy.ts_utc, fy.v, "max")
    sec["peak_prior_mw"] = cell(rnd(pp, 0), "MW", P.prior_label, src, None if pp is not None else "not held: no demand hour held")
    g = (pk / pp - 1) * 100 if pk and pp else None
    sec["peak_growth_pct"] = cell(rnd(g, 1), "pct", f"{P.prior_label} to {P.label}", src,
                                  None if g is not None else "not held: a peak is missing")
    sec["peak_hour"] = cell(pk_ts, "UTC", P.label, src, None if pk_ts else "not held: no demand hour held")
    op = place.get("op")
    asrc = S.key(f"alerts_{op}" if op in NOTICE_GROUP else "alerts", "grid_all_alerts", {"caiso": "CAISO", "ercot": "ERCOT"}.get(op, "CAISO; ERCOT"),
                 match=("x_grid", op) if op in NOTICE_GROUP else None, url="first" if op in NOTICE_GROUP else "none")
    if op in NOTICE_GROUP:
        a = alerts[(alerts.x_grid == op) & (alerts.event_date >= P.start) & (alerts.event_date < P.end)]
        for grp in ("alerts", "watches", "emergencies"):
            days = a[a.event_type.isin(NOTICE_GROUP[op][grp])].event_date.nunique()
            sec[grp] = cell(int(days), "days", P.label, asrc)
        allk = set().union(*NOTICE_GROUP[op].values())
        sec["alert_days"] = cell(int(a[a.event_type.isin(allk)].event_date.nunique()), "days", P.label, asrc)
    else:
        why = "not held: the warehouse holds operator notices for CAISO and ERCOT only"
        for k in ("alerts", "watches", "emergencies", "alert_days"):
            sec[k] = cell(None, "days", P.label, asrc, why)
    osrc = S.key(f"outages_{op}" if op in OUTAGE_ENTITY else "outages", "generation_outages_hourly", {"caiso": "CAISO", "spp": "SPP"}.get(op, "CAISO; SPP"),
                 match=("entity", op + ":") if op in OUTAGE_ENTITY else None, url="first" if op in OUTAGE_ENTITY else "none")
    if op in OUTAGE_ENTITY and pk_ts:
        o = outages[(outages.entity == OUTAGE_ENTITY[op]) & (outages.ts_utc == pk_ts)]
        v = num(o.value).max() if not o.empty else None
        sec["out_mw_at_peak"] = cell(rnd(v, 0), "MW", pk_ts, osrc,
                                     None if v is not None and v == v else "not held: no outage row at the peak hour")
    else:
        sec["out_mw_at_peak"] = cell(None, "MW", P.label, osrc,
                                     "not held: the warehouse holds generation out of service for CAISO and SPP only")
    rm, rt, rper, rsrc = reserves.get(op, (None, None, None, None))
    rsrc = rsrc or S.key("reserves_none", "iso_reserve_margin_reports", "CAISO")
    held = None if rm is not None else "not held: the warehouse holds a published planning reserve margin for CAISO and ERCOT only"
    sec["reserve_margin_pct"] = cell(rm, "pct", rper, rsrc, held)
    sec["reserve_target_pct"] = cell(rt, "pct", rper, rsrc,
                                     None if rt is not None else (held or "not published: no target printed beside it"))
    sec["status"] = "shown"
    return sec, pk_ts


def reserves_by_op(S, today=None):
    out = {}
    r = read("iso_reserve_margin_reports", ["entity", "variable", "ts_utc", "value", "x_grid", "x_period"])
    if r is not None and not r.empty:
        c = r[r.x_grid.str.lower() == "caiso"]
        got = {row.variable: rnd(row.value, 1) for row in c.itertuples()}
        per = c.x_period.iloc[0] if not c.empty else None
        src = S.key("caiso_reserve", "iso_reserve_margin_reports", "CAISO")
        if got.get("prm_achieved_pct") is not None:
            out["caiso"] = (got.get("prm_achieved_pct"), got.get("prm_required_pct"), per, src)
    e = read("ercot_cdr_reserve_margins", ["entity", "variable", "ts_utc", "value", "vintage", "x_report"])
    if e is not None and not e.empty:
        # the newest report's reserve margin at the summer peak load hour, for the next summer to come
        m = e[(e.variable == "reserve_margin") & (e.entity == "ercot_cdr:summer:peak_load")]
        m = m[m.vintage == m.vintage.max()]
        nxt = m[m.ts_utc >= (today or datetime.now(timezone.utc).date()).isoformat()].sort_values("ts_utc")
        if not nxt.empty:
            first = nxt.iloc[0]
            src = S.key("ercot_cdr", "ercot_cdr_reserve_margins", "ERCOT")
            out["ercot"] = (rnd(first.value, 1), None, f"summer {first.ts_utc[:4]} (ERCOT's {first.x_report})", src)
    return out


def hourly_prices(op, P):
    """Hourly prices for an operator's hubs over the period: a frame of entity, market (da/rt), hour, price."""
    import pandas as pd
    ents = [h for h, _n in HUBS.get(op, [])]
    if not ents:
        return pd.DataFrame(columns=["entity", "market", "hour", "v"])
    if op == "ercot":
        f = read("ercot_all_hub_prices_history", ["entity", "variable", "ts_utc", "value"],
                 keep=lambda c: c.entity.isin(ents) & P.deep(c.ts_utc))
        f["market"] = f.variable.map({"spp_dam": "day-ahead", "spp_rtm": "real-time"})
    else:
        f = read("iso_hub_prices_history", ["entity", "variable", "ts_utc", "value", "market"],
                 keep=lambda c: c.entity.isin(ents) & P.deep(c.ts_utc))
        extra = []
        # part F: the years before July 2023 (SPP's North Hub from July 2018) are iso_hub_prices_history_2018's
        old = read("iso_hub_prices_history_2018", ["entity", "variable", "ts_utc", "value", "market"],
                   keep=lambda c: c.entity.isin(ents) & P.deep(c.ts_utc))
        if old is not None and not old.empty:
            extra.append(old)
        for t in ("iso_dam_hub_prices", "iso_rtm_hub_prices"):
            x = read(t, ["entity", "variable", "ts_utc", "value"], keep=lambda c: c.entity.isin(ents) & P.deep(c.ts_utc))
            if x is not None and not x.empty:
                x["market"] = "dam" if t == "iso_dam_hub_prices" else "rtm"
                extra.append(x)
        f = pd.concat([f] + extra, ignore_index=True)
        f["market"] = f.market.str.endswith("dam").map({True: "day-ahead", False: "real-time"})
    f = f[f.market.notna()].copy()
    f["v"] = num(f.value)
    f["hour"] = f.ts_utc.str.slice(0, 13)
    # an hour's price is the mean of its intervals; a table read twice for one hour keeps one mean
    g = f.groupby(["entity", "market", "hour"], as_index=False).v.mean()
    g["v"] = g.v.round(6)   # the hour's mean to 6 decimals, so that a mean of exactly zero is not read as below it
    return g


def build_price(place, P, S, prices, names):
    op = place.get("op")
    ops = [op] if op else [OP_OF_BA[b] for b in place["members"] if b in OP_OF_BA]
    hubs, neg_ref = [], None
    if not ops:
        why = (f"not a market: {place['name']} is not in one of the seven organised markets; no hub price is public"
               if place["kind"] == "ba" else "not a market: no member of this region is one of the seven organised markets")
        return {"status": why, "hubs": []}, None, None
    src_e = S.key("ercot_prices", "ercot_all_hub_prices_history", "ERCOT")
    ref_hub = None
    for o in ops:
        held = HELD_OP.get(o)
        if held and not HUBS.get(o):
            hubs.append({"hub_id": None, "hub": None, "operator": "op-" + o, "market": None, "status": held})
            continue
        for ent, hname in HUBS[o]:
            if ref_hub is None and not held:
                ref_hub = ent
            for mk in ("day-ahead", "real-time"):
                h = {"hub_id": ent, "hub": hname, "operator": "op-" + o, "market": mk}
                src = src_e if o == "ercot" else S.key(
                    f"iso_prices_{o}", "iso_hub_prices_history", {"isone": "ISO-NE"}.get(o, o.upper()),
                    match=("entity", o + ":"))   # one operator's rows: its own report's address (request 586)
                if held:
                    for k, _l, u in SECTIONS[0][2]:
                        h[k] = cell(None, u, P.label, src, held)
                    hubs.append(h)
                    continue
                xa = prices[o]
                xa = xa[(xa.entity == ent) & (xa.market == mk) & xa.v.notna()]
                x = xa[P.inside(xa.hour)]
                n = len(x)
                low = n < COVER_FLOOR * P.hours
                why = f"too few: {n:,} of the period's {P.hours:,} hours held (the floor is 80 percent)" if low else None
                first = x.hour.min() if n else None
                per = P.label if not low or not n else f"{first[:10]}..{x.hour.max()[:10]}"
                h["mean"] = cell(rnd(x.v.mean(), 2) if n else None, "USD/MWh", per, src, why if n else "not held: no hour held")
                h["mean"]["trend"] = trend(P, xa.hour, xa.v, "mean")
                h["mean"]["years"] = years_of(P, xa.hour, xa.v, "mean")
                h["p95"] = cell(rnd(x.v.quantile(0.95), 2) if n else None, "USD/MWh", per, src, why if n else "not held: no hour held")
                h["hours_over_100"] = cell(int((x.v > 100).sum()), "hours", per, src, why if n else "not held: no hour held")
                h["hours_below_0"] = cell(int((x.v < 0).sum()), "hours", per, src, why if n else "not held: no hour held")
                h["hours"] = cell(int(n), "hours", per, src, None if n else "not held: no hour held")
                hubs.append(h)
    if ref_hub:
        r = [h for h in hubs if h.get("hub_id") == ref_hub and h["market"] == "day-ahead"]
        neg_ref = r[0]["hours_below_0"] if r else None
    status = "shown" if ref_hub else (HELD_OP.get(ops[0]) or "not held")
    return {"status": status, "hubs": hubs}, ref_hub, neg_ref


def build_congestion(place, P, S, cong, cons, ref_hub):
    op = place.get("op")
    ops = [op] if op else [OP_OF_BA[b] for b in place["members"] if b in OP_OF_BA]
    src = S.key("congestion", "price_congestion_monthly", "CAISO; SPP")
    tsrc = S.key("constraints", "constraints_binding_monthly", "CAISO; SPP")
    sec = {"hubs": [], "top_by_hours": [], "top_by_cost": [], "top_period": P.label, "top_src": tsrc, "top_held": None}
    if not ops:
        why = "not a market: no hub price, so no congestion part of one"
        sec.update(status=why, top_held=why)
        return sec, None
    shown = [o for o in ops if o in ("caiso", "spp")]
    if not shown:
        o = ops[0]
        why = HELD_OP.get(o) or "not held: the warehouse holds the congestion part of hub prices for CAISO and SPP only"
        sec.update(status=why, top_held=why)
        return sec, None
    ref_share = None
    for o in shown:
        c = cong[cong.entity.str.startswith(o + ":")]
        for ent, g in c.groupby("entity"):
            w = g.pivot_table(index="ts_utc", columns="variable", values="v", aggfunc="first")
            if "hours_held" not in w or "lmp_mean" not in w or "congestion_mean" not in w:
                continue
            hrs = w["hours_held"].sum()
            lmp = (w["lmp_mean"] * w["hours_held"]).sum() / hrs if hrs else None
            cm = (w["congestion_mean"] * w["hours_held"]).sum() / hrs if hrs else None
            share = cm / lmp * 100 if lmp and lmp > 0 and cm is not None else None
            low = hrs < COVER_FLOOR * P.hours
            why = f"too few: {int(hrs):,} of the period's {P.hours:,} hours held (the floor is 80 percent)" if low else None
            code = ent.split(":", 1)[1]
            sec["hubs"].append({"hub_id": ent, "hub": HUB_NAME.get(ent) or ZONE_NAMES.get(code, code), "code": code,
                                "congestion_share_pct": cell(rnd(share, 1), "pct", P.label, src,
                                                             why or (None if share is not None else "not held: the mean price was not above zero")),
                                "congestion_mean": cell(rnd(cm, 2), "USD/MWh", P.label, src, why)})
            if ent == ref_hub and not why:
                ref_share = rnd(share, 1)
        k = cons[cons.entity.str.startswith(o + ":")]
        if not k.empty:
            w = k.pivot_table(index=["entity", "ts_utc"], columns="variable", values="v", aggfunc="first").reset_index()
            w["cost"] = w.get("shadow_price_abs_mean", 0) * w.get("hours_bound", 0)
            agg = w.groupby("entity").agg(hours=("hours_bound", "sum"), cost=("cost", "sum")).reset_index()
            agg["abs_mean"] = agg.cost / agg.hours
            for col, key in (("hours", "top_by_hours"), ("cost", "top_by_cost")):
                for r in agg.sort_values(col, ascending=False).head(10).itertuples():
                    name, _sep, cont = r.entity.split(":", 1)[1].partition("|")
                    sec[key].append({"operator": "op-" + o, "name": name, "contingency": cont or None,
                                     "hours": int(r.hours), "cost": rnd(r.cost, 0), "abs_mean": rnd(r.abs_mean, 2)})
    sec["status"] = "shown"
    return sec, ref_share


def build_queue(place, P, S, q, dur, ba_of_entity):
    src = S.key("lbnl_queue", "lbnl_interconnection_queue", "Berkeley Lab", "Berkeley Lab, Queued Up, 2026 edition (through 2025)")
    dsrc = S.key("durations", "interconnection_durations", "Berkeley Lab")
    op = place.get("op")
    if place["kind"] == "operator":
        rows = q[q.region == LBNL_REGION[op]]
        d = dur[dur.grid == DUR_GRID[op]] if op in DUR_GRID else dur.iloc[0:0]
    else:
        bas = set(place["members"])
        rows = q[q.place_ba.isin(bas)]
        d = dur[dur.place_ba.isin(bas)]
    edition = "2025-12-31"
    act = rows[rows.q_status == "active"]
    sec = {"status": "shown" if len(rows) else "not held: no request of this place in Berkeley Lab's file"}
    held = None if len(rows) else sec["status"]
    sec["active_mw"] = cell(rnd(act.mw.sum(), 0), "MW", edition, src, held)
    sec["active_projects"] = cell(int(len(act)), "count", edition, src, held)
    ended = rows[(rows.q_year >= 2000) & (rows.q_year <= 2020) & rows.q_status.isin(["withdrawn", "operational"])]
    tot = ended.mw.sum()
    share = ended[ended.q_status == "withdrawn"].mw.sum() / tot * 100 if tot else None
    sec["withdrawn_share_pct"] = cell(rnd(share, 1), "pct", "requests entered 2000 to 2020", src,
                                      None if share is not None else (held or "not held: no request entered 2000 to 2020 has ended"))
    d5 = d[(d.operation_year >= 2021) & (d.operation_year <= 2025)]
    med = d5.months.median() / 12 if len(d5) >= MIN_DURATIONS else None
    why = None if med is not None else f"too few: {len(d5)} projects reached operation 2021 to 2025 (the floor is {MIN_DURATIONS})"
    sec["median_years_to_operation"] = cell(rnd(med, 1), "years", "projects operating 2021 to 2025", dsrc, why)
    by = act.groupby("type_clean").agg(mw=("mw", "sum"), n=("mw", "size")).reset_index().sort_values("mw", ascending=False)
    sec["by_fuel"] = [{"fuel": r.type_clean, "active_mw": cell(rnd(r.mw, 0), "MW", edition, src),
                       "active_projects": cell(int(r.n), "count", edition, src)} for r in by.itertuples()]
    return sec


def place_bas(place, bas_index):
    """The authorities a place covers (an operator: its own; a region: its members)."""
    return set(place["members"])


def build_large_load(place, S, rules, totals, laws, place_states):
    src = S.key("ll_rules", "utility_large_load_rules", "US utilities, commissions and legislatures (the ERW's research pass)",
                url="row")
    qsrc = S.key("ll_totals", "utility_large_load_queue_totals", "US utilities and operators (the ERW's research pass)",
                 url="row")
    lsrc = S.key("ll_laws", "state_large_load_laws", "US state legislatures (the ERW's research pass)", url="row")
    bas = set(place["members"])
    r = rules[rules.place_ba.isin(bas)]
    thr = r.x_threshold_mw.map(threshold_mw)
    sec = {"status": "shown"}
    sec["rules_n"] = cell(int(len(r)), "count", "as read to " + (rules.event_date.max() or ""), src)
    sm = thr.min() if thr.notna().any() else None
    sec["smallest_threshold_mw"] = cell(rnd(sm, 1), "MW", "as read", src,
                                        None if sm is not None else "not held: no rule of this place prints a threshold")
    sec["rules"] = [{"id": x.x_row_id, "utility": x.x_utility, "state": x.x_state, "status": x.status,
                     "threshold_mw": rnd(threshold_mw(x.x_threshold_mw), 1),
                     "threshold_text": x.x_threshold_mw or None, "contract_term": x.x_contract_term or None,
                     "collateral": x.x_collateral or None, "exit_fee": x.x_exit_fee or None,
                     "study_timeline": x.x_study_timeline or None, "source_url": x.source_url}
                    for x in r.sort_values(["x_state", "x_utility"]).itertuples()]
    t = totals[totals.place_ba.isin(bas)]
    sec["queue_totals"] = [{"utility": x.x_utility, "state": x.x_state, "date": x.event_date, "mw": rnd(x.mw, 1),
                            "figure": x.x_figure, "source_url": x.source_url}
                           for x in t.sort_values("event_date", ascending=False).itertuples()]
    lw = laws[laws.state.isin(place_states)]
    sec["laws"] = [{"state": x.state, "bill": x.bill, "status": x.status, "title": x.title}
                   for x in lw.sort_values(["state", "bill"]).itertuples()]
    sec["queue_totals_src"], sec["laws_src"], sec["rules_src"] = qsrc, lsrc, src
    sec["states"] = sorted(place_states)
    return sec


def build_mix_carbon(place, P, S, fuel, carbon):
    src = S.key("eia930_fuel", "eia930_region_fuel_hourly", "EIA")
    csrc = S.key("carbon", "carbon_intensity_hourly", "EIA (ERW's derivation, docs/methods/emissions.md)")
    code = place["code"] if place["kind"] != "operator" else place["members"][0]
    # done-line request 589: a region whose one member is an operator's own authority (Texas and ERCOT, New York and
    # NYISO, New England and ISO-NE) is the same grid: the region takes the authority's carbon intensity and the
    # operator the region's fuel mix, so neither file holds half of the section
    mix_code = place.get("mix_code") or code
    carbon_code = place.get("carbon_code") or code
    f = fuel[fuel.code == mix_code]
    sec = {"status": "shown"}
    tot = f.v.sum()
    sec["mix"] = []
    for var, v in (f.groupby("variable").v.sum().sort_values(ascending=False).items() if tot else []):
        key = var.replace("net_generation_", "").replace("_mw", "")
        sec["mix"].append({"fuel": FUEL_WORDS.get(key, key.replace("_", " ").capitalize()), "key": key,
                           "share_pct": cell(rnd(v / tot * 100, 2), "pct", P.label, src)})
    if mix_code != code and sec["mix"]:
        sec["mix_from"] = mix_code
    if not sec["mix"]:
        sec["mix_held"] = ("not held: the warehouse's table of net generation by source (eia930_region_fuel_hourly) holds "
                           "EIA's 13 regions only" if place["kind"] != "region" else
                           "not held: no net generation by source held for this region in the period")
    ca = carbon[carbon.ba == carbon_code]
    c = ca[P.inside(ca.ts_utc)]
    if carbon_code != code and not c.empty:
        sec["intensity_from"] = carbon_code
    if c.empty:
        why = "not held: carbon_intensity_hourly covers the seven operators' authorities and the US 48 only"
        sec["intensity"] = cell(None, "kgCO2/MWh", P.label, csrc, why)
        sec.update(intensity_by_hour=[None] * 24, intensity_by_hour_period=P.label, intensity_by_hour_src=csrc,
                   intensity_by_hour_held=why)
        return sec
    import pandas as pd
    sec["intensity"] = cell(rnd(c.v.mean(), 1), "kgCO2/MWh", P.label, csrc)
    sec["intensity"]["trend"] = trend(P, ca.ts_utc, ca.v, "mean")
    sec["intensity"]["years"] = years_of(P, ca.ts_utc, ca.v, "mean")
    hrs = pd.to_datetime(c.ts_utc, utc=True).dt.tz_convert(place["tz"]).dt.hour
    byh = c.v.groupby(hrs.values).mean()
    sec.update(intensity_by_hour=[rnd(byh.get(h), 1) for h in range(24)], intensity_by_hour_period=P.label,
               intensity_by_hour_src=csrc, intensity_by_hour_held=None)
    return sec


def build_imports(place, P, S, dem, reg, ti, pairs, rpairs, names):
    src = S.key("eia930_interchange", "eia930_ba_interchange_hourly_<year>", "EIA")
    sec = {"status": "shown"}
    if place["kind"] == "region":
        d = members_sum(dem[P.wide(dem.ts_utc)], place["members"])   # members counted over the two years, as for the peak
        t = members_sum(ti[P.inside(ti.ts_utc)], place["members"])
        tw = members_sum(ti[P.wide(ti.ts_utc)], place["members"])
        jy = region_years(dem, place["members"], P).merge(region_years(ti, place["members"], P), on="ts_utc",
                                                           suffixes=("_d", "_t")).dropna()
        tsrc = S.key("eia930_supply", "eia930_ba_supply_hourly", "EIA")
    else:
        code = place["members"][0]
        d = dem[dem.ba == code][["ts_utc", "v"]]
        tw = ti[ti.ba == code][["ts_utc", "v"]]
        t = tw[P.inside(tw.ts_utc)]
        tsrc = S.key("eia930_supply", "eia930_ba_supply_hourly", "EIA")
        jy = None
    jw = d.merge(tw, on="ts_utc", suffixes=("_d", "_t")).dropna()
    if jy is None:
        jy = jw
    j = d[P.inside(d.ts_utc)].merge(t, on="ts_utc", suffixes=("_d", "_t")).dropna()
    if j.empty:
        why = "not held: no hour with both demand and total interchange"
        sec["net_import_share_pct"] = cell(None, "pct", P.label, tsrc, why)
        sec["net_import_share_peak_pct"] = cell(None, "pct", P.label, tsrc, why)
    else:
        share = -j.v_t.sum() / j.v_d.sum() * 100
        top = j.sort_values(["v_d", "ts_utc"], ascending=[False, True]).head(100)   # ties: the earlier hour first
        sp = -top.v_t.sum() / top.v_d.sum() * 100
        sec["net_import_share_pct"] = cell(rnd(share, 1), "pct", P.label, tsrc)
        sec["net_import_share_peak_pct"] = cell(rnd(sp, 1), "pct", P.label + " (the 100 highest-demand hours)", tsrc)
        sec["net_import_share_pct"]["trend"] = trend_ratio(P, jw.ts_utc, -jw.v_t, jw.v_d)
        sec["net_import_share_pct"]["years"] = years_ratio(P, jy.ts_utc, -jy.v_t, jy.v_d)
    if place["kind"] == "region":
        rp = rpairs
        c = place["code"]
        a = rp[rp.a == c].groupby("b").v.sum() * -1
        b = rp[rp.b == c].groupby("a").v.sum()
        net = a.add(b, fill_value=0)
        psrc = S.key("eia930_region_pairs", "eia930_region_pair_hourly", "EIA")
    else:
        code = place["members"][0]
        net = pairs[pairs.a == code].groupby("b").v.sum() * -1
        psrc = src
    net = net.sort_values(ascending=False)
    sec["partners"] = [{"ba": k, "name": names.get(k, k), "net_import_mwh": cell(rnd(v, 0), "MWh", P.label, psrc)}
                       for k, v in net.head(3).items() if v > 0]
    return sec


def build_spare(place, P, S, curt, neg_ref, price_status=None):
    src = S.key("curtailment", "iso_curtailment_monthly", "CAISO; SPP")
    op = place.get("op")
    ops = [op] if op else [OP_OF_BA[b] for b in place["members"] if b in OP_OF_BA]
    o = next((x for x in ops if x in CURTAIL_ENTITY), None)
    sec = {"status": "shown"}
    if o:
        cw = curt[(curt.entity == CURTAIL_ENTITY[o]) & P.wide(curt.ts_utc)]
        c = cw[P.inside(cw.ts_utc)]
        months = c.ts_utc.str.slice(0, 7).nunique()
        why = None if months == 12 else f"too few: {months} of 12 months held"
        for var, key in (("curtailed_wind_mwh", "curtailed_wind_mwh"), ("curtailed_solar_mwh", "curtailed_solar_mwh")):
            v = c[c.variable == var].v.sum()
            sec[key] = cell(rnd(v, 0), "MWh", P.label, src, why)
            x = cw[cw.variable == var]
            sec[key]["trend"] = trend(P, x.ts_utc, x.v, "sum")
            xd = curt[(curt.entity == CURTAIL_ENTITY[o]) & P.deep(curt.ts_utc) & (curt.variable == var)]
            sec[key]["years"] = years_of(P, xd.ts_utc, xd.v, "sum", monthly=True)
    else:
        why = "not held: the warehouse holds curtailment for CAISO and SPP only"
        sec["curtailed_wind_mwh"] = cell(None, "MWh", P.label, src, why)
        sec["curtailed_solar_mwh"] = cell(None, "MWh", P.label, src, why)
    if neg_ref is not None:
        sec["negative_price_hours"] = dict(neg_ref)
    else:
        # done-line request 590: a market whose price is held says why, as its price section does
        why = price_status if price_status and price_status != "shown" else "not a market: no public hub price for this place"
        sec["negative_price_hours"] = cell(None, "hours", P.label, src, why)
    return sec


def build_forecast(place, S, scores):
    src = S.key("predict_scores", "site/data/predict/scores.json", "ERW (from EIA-930)",
                "the ERW forecast's score file, cut last_2_years (docs/methods/predict.md)")
    pid = place["id"] if place["kind"] != "operator" else "ba-" + place["members"][0].lower()
    got = scores.get(pid)
    sec = {"status": "shown"}
    if not got:
        why = "not held: the ERW forecast does not cover this place"
        for k, u in (("operator_mape_pct", "pct"), ("erw_mape_pct", "pct"), ("hours", "hours")):
            sec[k] = cell(None, u, None, src, why)
        return sec
    per = got["period"]
    sec["operator_mape_pct"] = cell(got.get("operator"), "pct", per, src,
                                    None if got.get("operator") is not None else "not held: no operator forecast scored")
    sec["erw_mape_pct"] = cell(got.get("erw"), "pct", per, src)
    sec["hours"] = cell(got.get("hours"), "hours", per, src)
    return sec


def load_scores():
    if not os.path.exists(SCORES):
        return {}
    with open(SCORES, encoding="utf-8") as fh:
        d = json.load(fh)
    cols = d["rows_columns"]
    ix = {c: i for i, c in enumerate(cols)}
    last = d.get("span", {}).get("demand", {}).get("last_day")
    out = {}
    for r in d["rows"]:
        if r[ix["series"]] != "demand" or r[ix["cut"]] != "last_2_years":
            continue
        m = r[ix["method"]]
        if m not in ("erw", "operator"):
            continue
        e = out.setdefault(r[ix["place"]], {"period": f"the 730 days to {last}" if last else "the last 730 days"})
        e[m] = rnd(r[ix["mape"]], 2)
        if m == "erw":
            e["hours"] = r[ix["hours"]]
    return out


def build_datacenters(place, S, fac, proj):
    fsrc = S.key("dc_facilities", "datacenter_facilities", "news and company sources (the ERW's datacenter tracker)",
                 url="row")
    psrc = S.key("dc_projects", "datacenter_projects", "news sources (the ERW's datacenter tracker)", url="row")
    bas = set(place["members"])
    f = fac[fac.place_ba.isin(bas)]
    p = proj[proj.place_ba.isin(bas)]
    sec = {"status": "shown"}
    fm = f.mwv.dropna()
    pm = p.mwv.dropna()
    sec["facilities_n"] = cell(int(len(f)), "count", "as held", fsrc)
    sec["facilities_mw_stated"] = cell(rnd(fm.sum(), 0), "MW", "as held", fsrc)
    sec["facilities_mw_n"] = cell(int(len(fm)), "count", "as held", fsrc)
    sec["projects_n"] = cell(int(len(p)), "count", "as held", psrc)
    sec["projects_mw_stated"] = cell(rnd(pm.sum(), 0), "MW", "as held", psrc)
    lst = []
    for frame, kind in ((f, "facility"), (p, "project")):
        for x in frame.itertuples():
            lst.append({"kind": kind, "name": x.name or None, "operator": (x.operator or x.developer or None),
                        "state": x.state or None, "county": x.county or None, "mw": rnd(x.mwv, 1),
                        "status": x.status or None, "source_url": x.source_url or None})
    lst.sort(key=lambda r: -(r["mw"] or 0))
    sec["list"] = lst[:25]
    return sec


def threshold_mw(text):
    """The size a large-load rule applies from, as the table prints it in words: the first figure written in MW,
    megawatts or kW (kW divided by 1,000) within the text's first 80 characters. Not read (None): a text that
    begins by saying there is no threshold ("no ..."), "not published", a figure in MVA or GW, or no figure."""
    import re
    if not text or text.strip().lower().startswith(("no ", "no:", "not ")):
        return None
    text = text[:80]
    m = re.search(r"(\d[\d,]*(?:\.\d+)?)\s*(MW|megawatts?|kW)\b", text)
    if not m:
        m2 = re.search(r"\b(two|five|ten)\s+megawatts", text, re.I)
        return {"two": 2.0, "five": 5.0, "ten": 10.0}[m2.group(1).lower()] if m2 else None
    v = float(m.group(1).replace(",", ""))
    return v / 1000 if m.group(2) == "kW" else v


def place_rules_ba(text, state, state_ba):
    for pat, ba in LL_REGION_BA:
        if pat in (text or ""):
            return ba
    return state_ba.get(state)


def state_maps(P):
    """From EIA-861: each state's retail sales by authority (the newest year), the authority a state is wholly
    in (STATE_SHARE), and the states each authority reaches (STATE_REACH)."""
    s = read("eia861_utility_sales", ["variable", "ts_utc", "value", "x_state", "x_ba_code"],
             keep=lambda c: c.variable == "total_sales")
    s["v"] = num(s.value)
    yr = s.ts_utc.max()
    s = s[s.ts_utc == yr]
    g = s.groupby(["x_state", "x_ba_code"]).v.sum().reset_index()
    st_tot = g.groupby("x_state").v.sum()
    ba_tot = g.groupby("x_ba_code").v.sum()
    whole, reach = {}, {}
    for r in g.itertuples():
        if st_tot.get(r.x_state) and r.v / st_tot[r.x_state] >= STATE_SHARE:
            whole[r.x_state] = r.x_ba_code
    return g, st_tot, ba_tot, whole, yr[:4]


def states_reached(bas, g, st_tot):
    x = g[g.x_ba_code.isin(bas)]
    tot = x.v.sum()
    out = set()
    for stt, v in x.groupby("x_state").v.sum().items():
        if (st_tot.get(stt) and v / st_tot[stt] >= STATE_REACH) or (tot and v / tot >= STATE_REACH):
            out.add(stt)
    return out


def build(out_dir, today=None):
    import pandas as pd
    P = Periods(today)
    cov = coverage_rows()
    holds = license_holds()
    built = now_utc()
    places, bas_index, dem, reg = load_places(P, cov)
    names = {c: b["name"] for c, b in bas_index.items()}
    names.update({"CAN": "Canada", "MEX": "Mexico"})
    for r in json.load(open(REGIONS_INDEX, encoding="utf-8"))["regions"]:
        names[r["code"]] = r["name"]
    sel = sorted({b for p in places for b in p["members"]})
    print(f"places: {len(places)} ({sum(p['kind'] == 'ba' for p in places)} authorities of at least {BA_FLOOR_MW} MW); "
          f"period {P.label}", flush=True)

    ti = read("eia930_ba_supply_hourly", ["entity", "variable", "ts_utc", "value"],
              keep=lambda c: (c.variable == "total_interchange_mw") & P.deep(c.ts_utc))
    ti["ba"] = ti.entity.str.replace("eia930:", "", regex=False)
    ti["v"] = num(ti.value)
    pp = []
    for yr in sorted({P.start[:4], str(int(P.end[:4]) - (1 if P.end[5:7] == "01" else 0))}):
        x = read(f"eia930_ba_interchange_hourly_{yr}", ["entity", "ts_utc", "value"], keep=lambda c: P.inside(c.ts_utc))
        if x is not None:
            pp.append(x)
    pairs = pd.concat(pp, ignore_index=True)
    ab = pairs.entity.str.replace("eia930:", "", regex=False).str.split("-", n=1, expand=True)
    pairs["a"], pairs["b"], pairs["v"] = ab[0], ab[1], num(pairs.value)
    pairs = pairs[pairs.a.isin(sel)]
    rp = read("eia930_region_pair_hourly", ["entity", "ts_utc", "value"], keep=lambda c: P.inside(c.ts_utc))
    ab = rp.entity.str.replace("eia930:", "", regex=False).str.split("-", n=1, expand=True)
    rp["a"], rp["b"], rp["v"] = ab[0], ab[1], num(rp.value)
    codes = set(sel) | {p["code"] for p in places if p["kind"] == "region"}
    fuel = read("eia930_region_fuel_hourly", ["entity", "variable", "ts_utc", "value"],
                keep=lambda c: P.inside(c.ts_utc) & c.entity.str.replace("eia930:", "", regex=False).isin(codes))
    fuel["code"] = fuel.entity.str.replace("eia930:", "", regex=False)
    fuel["v"] = num(fuel.value)
    carbon = read("carbon_intensity_hourly", ["entity", "variable", "ts_utc", "value"],
                  keep=lambda c: (c.variable == "intensity_demand") & P.deep(c.ts_utc))
    carbon["ba"] = carbon.entity.str.replace("eia930:", "", regex=False)
    carbon["v"] = num(carbon.value)
    print("EIA-930 read", flush=True)

    prices = {op: hourly_prices(op, P) for _pid, op, _ba, _n in OPERATORS if op not in HELD_OP}
    cong = read("price_congestion_monthly", ["entity", "variable", "ts_utc", "value"], keep=lambda c: P.inside(c.ts_utc))
    cong["v"] = num(cong.value)
    cons = read("constraints_binding_monthly", ["entity", "variable", "ts_utc", "value"], keep=lambda c: P.inside(c.ts_utc))
    cons["v"] = num(cons.value)
    alerts = read("grid_all_alerts", ["event_date", "event_type", "x_grid"])
    outages = read("generation_outages_hourly", ["entity", "variable", "ts_utc", "value"],
                   keep=lambda c: (c.variable == "outage_mw_total") & P.inside(c.ts_utc))
    curt = read("iso_curtailment_monthly", ["entity", "variable", "ts_utc", "value"])
    curt["v"] = num(curt.value)
    print("operator tables read", flush=True)

    g861, st_tot, _ba_tot, state_ba, yr861 = state_maps(P)
    q = read("lbnl_interconnection_queue", ["entity_id", "capacity_mw", "q_status", "q_year", "region", "lbnl_entity",
                                            "state", "type_clean"])
    q["mw"], q["q_year"] = num(q.capacity_mw), num(q.q_year)

    def lbnl_ba(ent, st):
        if ent in LBNL_SPLIT:
            return LBNL_SPLIT[ent].get(st)
        return DC_GRID_BA.get(ent) or LBNL_ENTITY_BA.get(ent)
    q["place_ba"] = [lbnl_ba(e, s) for e, s in zip(q.lbnl_entity, q.state)]
    dur = read("interconnection_durations", ["entity_id", "grid", "state", "months_to_operation", "operation_year"])
    dur["months"], dur["operation_year"] = num(dur.months_to_operation), num(dur.operation_year)
    dur["lbnl_entity"] = dur.entity_id.str.split(":").str[1]
    dur["place_ba"] = [lbnl_ba(e, s) for e, s in zip(dur.lbnl_entity, dur.state)]
    rules = read("utility_large_load_rules", ["event_date", "status", "source_url", "x_row_id", "x_utility", "x_state",
                                              "x_iso_region", "x_threshold_mw", "x_contract_term", "x_collateral",
                                              "x_exit_fee", "x_study_timeline"])
    rules["place_ba"] = [place_rules_ba(t, s, state_ba) for t, s in zip(rules.x_iso_region, rules.x_state)]
    totals = read("utility_large_load_queue_totals", ["event_date", "mw", "source_url", "x_utility", "x_state",
                                                       "x_iso_region", "x_figure"])
    totals["place_ba"] = [place_rules_ba(t, s, state_ba) for t, s in zip(totals.x_iso_region, totals.x_state)]
    laws = read("state_large_load_laws", ["x_state", "x_bill", "status", "x_title"]).rename(
        columns={"x_state": "state", "x_bill": "bill", "x_title": "title"})
    fac = read("datacenter_facilities", ["name", "operator", "developer", "state", "county", "mw", "status", "grid",
                                         "source_url"])
    proj = read("datacenter_projects", ["name", "operator", "developer", "state", "county", "mw", "project_status",
                                        "grid", "source_url"]).rename(columns={"project_status": "status"})
    for fr in (fac, proj):
        fr["mwv"] = num(fr.mw)
        fr["place_ba"] = [DC_GRID_BA.get(gd) or state_ba.get(st) for gd, st in zip(fr.grid, fr.state)]
    scores = load_scores()
    reserves = {}
    print("queue, large-load, datacenter and forecast tables read", flush=True)

    # done-line request 589: a region whose one member is an operator's authority, and that operator, share a grid
    one_member = {p["members"][0]: p["code"] for p in places if p["kind"] == "region" and len(p["members"]) == 1}
    for p in places:
        if p["kind"] == "operator" and p["members"][0] in one_member:
            p["mix_code"] = one_member[p["members"][0]]
        if p["kind"] == "region" and len(p["members"]) == 1 and p["members"][0] in OP_OF_BA:
            p["carbon_code"] = p["members"][0]
    os.makedirs(out_dir, exist_ok=True)
    index_places, table_rows = [], []
    all_sources = {}
    for place in places:
        S = Sources(cov, holds)
        if not reserves:
            reserves = reserves_by_op(Sources(cov), today)
        res = {k: (v[0], v[1], v[2], S.key(v[3], "iso_reserve_margin_reports" if k == "caiso" else "ercot_cdr_reserve_margins",
                                           "CAISO" if k == "caiso" else "ERCOT")) for k, v in reserves.items()}
        tight, _pk_ts = build_tightness(place, P, S, dem, reg, alerts, outages, res)
        price, ref_hub, neg_ref = build_price(place, P, S, prices, names)
        congestion, ref_share = build_congestion(place, P, S, cong, cons, ref_hub)
        bas = set(place["members"])
        pstates = states_reached(bas, g861, st_tot)
        secs = {
            "price": price, "congestion": congestion, "tightness": tight,
            "queue": build_queue(place, P, S, q, dur, None),
            "large_load": build_large_load(place, S, rules, totals, laws, pstates),
            "mix_carbon": build_mix_carbon(place, P, S, fuel, carbon),
            "imports": build_imports(place, P, S, dem, reg, ti, pairs, rp, names),
            "spare": build_spare(place, P, S, curt, neg_ref, price["status"]),
            "forecast": build_forecast(place, S, scores),
            "datacenters": build_datacenters(place, S, fac, proj),
        }
        apply_holds(secs, S.used)
        doc = {"built": built, "example": False, "contract": CONTRACT, "method": METHOD, "license": "public",
               "id": place["id"], "kind": place["kind"], "code": place["code"], "name": place["name"],
               "tz": place["tz"], "members": place["members"], "sources": S.used, "sections": secs}
        write_json(os.path.join(out_dir, place["id"] + ".json"), doc)
        all_sources.update(S.used)
        pk = tight["peak_mw"]["v"]
        index_places.append({"id": place["id"], "kind": place["kind"], "code": place["code"], "name": place["name"],
                             "region": place["region"], "regions": place["regions"],
                             "operator": place.get("operator"), "members": place["members"], "tz": place["tz"],
                             "peak_mw": pk, "ref_hub": ref_hub, "file": place["id"] + ".json"})
        table_rows.append(table_row(place, secs, ref_hub, ref_share, P))
    index = {"built": built, "example": False, "contract": CONTRACT, "method": METHOD, "license": "public",
             "ba_floor_mw": BA_FLOOR_MW, "ba_floor_period": P.label, "places": index_places,
             "sections": sections_catalogue()}
    write_json(os.path.join(out_dir, "index.json"), index)
    cols = [{"key": k, "section": s, "label": lab, "unit": u, "period": None, "src": None} for k, s, lab, u in TABLE_COLUMNS]
    rows = []
    for r in table_rows:
        v, cellmap = [], {}
        for i, (k, _s, _lab, _u) in enumerate(TABLE_COLUMNS):
            c = r.get(k)
            v.append(c["v"] if c else None)
            cellmap[str(i)] = {"period": c["period"], "src": c["src"], "held": c["held"]} if c else \
                {"period": None, "src": None, "held": "not held: no such count for this place"}
        rows.append({"id": r["id"], "kind": r["kind"], "name": r["name"], "v": v, "cell": cellmap})
    # done-line request 586: a column's period and source are the ones most of its shown cells share (the contract's
    # section 3); a cell keeps its own entry only where it is held or differs from its column
    for i, col in enumerate(cols):
        shown = [(rw["cell"][str(i)]["period"], rw["cell"][str(i)]["src"]) for rw in rows if not rw["cell"][str(i)]["held"]]
        # done-line request 590: a column names a period or a source only when every shown cell shares it; a column
        # of several sources (CAISO's, SPP's and ERCOT's prices) names none, and each cell keeps its own
        if shown:
            periods, srcs = {p for p, _s in shown}, {s for _p, s in shown}
            col["period"] = next(iter(periods)) if len(periods) == 1 else None
            col["src"] = next(iter(srcs)) if len(srcs) == 1 else None
        for rw in rows:
            c = rw["cell"][str(i)]
            if not c["held"] and (c["period"], c["src"]) == (col["period"], col["src"]):
                del rw["cell"][str(i)]
    write_json(os.path.join(out_dir, "table.json"),
               {"built": built, "example": False, "contract": CONTRACT, "method": METHOD, "license": "public",
                "sources": all_sources, "columns": cols, "rows": rows})
    stale = [f for f in os.listdir(out_dir) if f.endswith(".json") and f not in
             {"index.json", "table.json"} | {p["id"] + ".json" for p in places}]
    for f in stale:
        os.remove(os.path.join(out_dir, f))
    print(f"wrote {len(places)} place files, index.json and table.json to {out_dir}"
          + (f"; removed {len(stale)} files of places no longer listed: {stale}" if stale else ""))
    return 0


def table_row(place, secs, ref_hub, ref_share, P):
    def hub(market, key):
        for h in secs["price"]["hubs"]:
            if h.get("hub_id") == ref_hub and h.get("market") == market:
                return h.get(key)
        return None
    out = {"id": place["id"], "kind": place["kind"], "name": place["name"]}
    held_price = secs["price"]["status"] if secs["price"]["status"] != "shown" else None
    for key, mk, k in (("price.mean_da", "day-ahead", "mean"), ("price.p95_da", "day-ahead", "p95"),
                       ("price.hours_over_100_da", "day-ahead", "hours_over_100"),
                       ("price.hours_below_0_da", "day-ahead", "hours_below_0"), ("price.mean_rt", "real-time", "mean")):
        out[key] = hub(mk, k) or cell(None, "USD/MWh", P.label, None, held_price or "not held: no hub price")
    cs = [h for h in secs["congestion"]["hubs"] if h["hub_id"] == ref_hub]
    out["congestion.share_pct"] = cs[0]["congestion_share_pct"] if cs else cell(
        None, "pct", P.label, secs["congestion"]["top_src"],
        secs["congestion"]["status"] if secs["congestion"]["status"] != "shown" else "not published: no congestion split at this hub")
    for sec, k in (("tightness", "peak_mw"), ("tightness", "peak_growth_pct"), ("tightness", "alert_days"),
                   ("tightness", "out_mw_at_peak"), ("tightness", "reserve_margin_pct"), ("queue", "active_mw"),
                   ("queue", "withdrawn_share_pct"), ("queue", "median_years_to_operation"), ("large_load", "rules_n"),
                   ("large_load", "smallest_threshold_mw"), ("mix_carbon", "intensity"),
                   ("imports", "net_import_share_pct"), ("imports", "net_import_share_peak_pct"),
                   ("spare", "curtailed_wind_mwh"), ("spare", "curtailed_solar_mwh"),
                   ("forecast", "operator_mape_pct"), ("forecast", "erw_mape_pct"),
                   ("datacenters", "facilities_n"), ("datacenters", "projects_mw_stated")):
        out[f"{sec}.{k}"] = secs[sec].get(k)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--example", action="store_true", help="write the contract's example files")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--today", help="build as on this UTC day (YYYY-MM-DD), for a test or a replication")
    a = ap.parse_args(argv)
    if a.example:
        return example_files(a.out_dir)
    today = datetime.fromisoformat(a.today).date() if a.today else None
    return build(a.out_dir, today)


if __name__ == "__main__":
    sys.exit(main())
