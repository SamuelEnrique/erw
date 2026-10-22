#!/usr/bin/env python3
"""Where can a large load go: the site's own files for the All grids tab of /cost-of-power (session 700).

Energy Research Warehouse (ERW). No warehouse table is written and no request is made: this reads tables this machine
holds and writes the tab's files under site/data/siting/. Method: docs/methods/siting.md. The hub and zone rows and
their prices are "Your load"'s own files (site/data/datacenter, warehouse/derived/datacenter_page.py), never rebuilt here.

    python warehouse/derived/siting_page.py                                  # the tables from warehouse/output
    python warehouse/derived/siting_page.py --in-dir runs/archive_restore    # a table not in warehouse/output is read
                                                                             # from these directories, in order
    python warehouse/derived/siting_page.py --out-dir DIR                    # a trial: the files under DIR

Files:
    nodes.json    every settlement point of node_basis_daily that is neither a hub nor a load zone: its id, its class and
                  ERCOT's resource types at it (x_class, x_resource_type), and its day-ahead basis to HB_HUBAVG by Central
                  month, {"YYYY-MM": [mean of the daily basis, days held]}, USD/MWh to four decimals. The node's
                  twelve-month price on the page is the hub's own twelve-month mean plus the mean of these days.
                  Session 711: "pct", the 10th, 50th and 90th percentile of the node's daily day-ahead basis over the
                  last twelve whole months the table holds ("pct_from", "pct_to" at the file's top), and the days in it.
    ercot_4cp.json  (session 702) ERCOT's four coincident-peak intervals by summer from ercot_4cp_intervals: each
                  interval's start in UTC, its local time as ERCOT prints it, and ERCOT's load in it (MW); the summers
                  held and the table's own note of what is not held.
    capacity.json (session 704) the capacity table's newest delivery period of each market, its auction, unit and
                  license, and the zones that auction priced; NO PRICE. iso_all_capacity_prices is internal (the
                  publishers' terms bar republishing) and the repository is public: the tab draws each price as
                  "license needed". With --internal FILE the prices are computed here, per row of the tab, in USD per
                  MWh for a load that runs every hour, and written to FILE (outside the repository; never committed).
    connect.json  (session 705) from lbnl_interconnection_queue (public): by grid, the median, quartiles and count of the
                  months from queue entry (q_date) to commercial operation (on_date) of the requests operational and
                  online in the last three whole years of the file's edition; no median under five requests.
    headroom.json (session 706) from eia860m_planned_generators (public): by grid (balancing authority), the MW and
                  count of generators due to operate in the twelve months after the table's vintage month, by EIA's
                  status: under construction or complete (U, V, TS), approvals received (T), and the rest (P, L); and
                  from eia_state_capacity_annual (public) the newest year's installed net summer capacity of the grids
                  that are whole states (NYISO: New York; ISO-NE: the six New England states).
    carbon.json   (session 707) from egrid_power_plants (public): each eGRID subregion's CO2 (tons, CHP-adjusted as eGRID
                  gives it) and net generation (MWh) summed over its plants, and PJM's over the plants eGRID places in PJM
                  (ISORTO); and from carbon_intensity_hourly (public), intensity_demand in kg CO2 per MWh, each priced
                  grid's hours of the years its price window covers, in the grid's standard time (as the price files),
                  {"s": the first hour held, "v": the values}, to one decimal; an hour not held is null.
    utility.json  (session 708) from eia861_utility_sales (public): for each state and balancing authority the tab needs,
                  the utility with the most industrial sales in the newest year, among the rows of EIA's service types
                  Bundled and Energy (Delivery rows are wires charges), with its industrial sales and revenue that year
                  and its sales the year before.
    facilities.json (session 719) where a place sits on the tab, for the datacenter tracker's link: each state whose
                  retail sales are 85 percent or more inside one grid (eia861_utility_sales, Bundled and Energy rows, by
                  balancing authority), and every county whose utilities (utility_service_territories) bill inside one
                  grid only; the tab's row a county is placed at (ROW_COUNTY). Public tables only: nothing of
                  datacenter_facilities (held whole) is written.
    gaps.json     (session 713) the table of docs/reviews/siting-gaps.md, each cell as written, for /internal/siting-gaps.

Each file names the table it was read from, the table's first and last day and when it was built. A table that cannot
be found stops the run (exit 1): no file is written from part of a table.
"""

import argparse
import datetime as dt
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SITE_DIR = os.path.join(ROOT, "site", "data", "siting")
OUTPUT = os.path.join(ROOT, "warehouse", "output")
NODE_TABLE = "node_basis_daily"
CP_TABLE = "ercot_4cp_intervals"
CAP_TABLE = "iso_all_capacity_prices"
CAP_MARKETS = ["pjm_bra", "isone_fca", "miso_pra", "nyiso_icap_spot"]
LBNL_TABLE = "lbnl_interconnection_queue"
LBNL_GRIDS = {"ERCOT": "ercot", "CAISO": "caiso", "NYISO": "nyiso", "ISO-NE": "isone", "SPP": "spp", "MISO": "miso", "PJM": "pjm"}
MIN_N = 5
UTILITY_TABLE = "eia861_utility_sales"
# session 718: the data machine's tables of chain 043, wired in where they answer a column better
DURATIONS_TABLE, PEAKCAP_TABLE, TERRITORY_TABLE = "interconnection_durations", "grid_peak_vs_capacity", "utility_service_territories"
DURATION_GRIDS = {"ercot": "ercot", "caiso": "caiso", "nyiso": "nyiso", "isone": "isone", "spp": "spp", "miso": "miso", "pjm": "pjm"}
# a county the row's name is a place in, where it names one: the county's own utilities serve the row there. The hubs'
# counties are the data machine's choice in session 681 (Harris, Los Angeles, New York, Suffolk, Allegheny, Marion,
# Sedgwick); a zone takes the county of the city it is named for
ROW_COUNTY = {
    "ercot:HB_HOUSTON": ("TX", "Harris"), "ercot:LZ_HOUSTON": ("TX", "Harris"), "ercot:LZ_AEN": ("TX", "Travis"), "ercot:LZ_CPS": ("TX", "Bexar"),
    "caiso:TH_SP15_GEN-APND": ("CA", "Los Angeles"),
    "nyiso:N.Y.C.": ("NY", "New York"), "nyiso:LONGIL": ("NY", "Suffolk"), "nyiso:CAPITL": ("NY", "Albany"), "nyiso:WEST": ("NY", "Erie"),
    "nyiso:GENESE": ("NY", "Monroe"), "nyiso:CENTRL": ("NY", "Onondaga"), "nyiso:DUNWOD": ("NY", "Westchester"), "nyiso:MILLWD": ("NY", "Westchester"),
    "isone:.H.INTERNAL_HUB": ("MA", "Suffolk"), "isone:.Z.NEMASSBOST": ("MA", "Suffolk"),
    "spp:SPPNORTH_HUB": ("KS", "Sedgwick"), "miso:INDIANA.HUB": ("IN", "Marion"), "pjm:grid": ("PA", "Allegheny"),
}
UTILITY_STATES = [("TX", "ERCO"), ("CA", "CISO"), ("NY", "NYIS"), ("CT", "ISNE"), ("ME", "ISNE"), ("MA", "ISNE"), ("NH", "ISNE"), ("RI", "ISNE"), ("VT", "ISNE"),
                  ("KS", "SWPP"), ("OK", "SWPP"), ("AR", "MISO"), ("IL", "MISO"), ("IN", "MISO"), ("LA", "MISO"), ("MI", "MISO"), ("MN", "MISO"), ("MS", "MISO"), ("TX", "MISO")]
EGRID_TABLE, HOURLY_TABLE, HOURLY_VAR = "egrid_power_plants", "carbon_intensity_hourly", "intensity_demand"
SUBREGIONS = ["ERCT", "CAMX", "NYUP", "NYCW", "NYLI", "NEWE", "SPNO", "SPSO", "MROW", "SRMW", "RFCW", "RFCM", "SRMV"]
HOURLY_GRIDS = {"ercot": "ERCO", "caiso": "CISO", "nyiso": "NYIS", "isone": "ISNE", "spp": "SWPP"}
PLANNED_TABLE, STATECAP_TABLE = "eia860m_planned_generators", "eia_state_capacity_annual"
BA_GRIDS = {"ERCO": "ercot", "CISO": "caiso", "NYIS": "nyiso", "ISNE": "isone", "SWPP": "spp", "MISO": "miso", "PJM": "pjm"}
WHOLE_STATES = {"nyiso": ["NY"], "isone": ["CT", "MA", "ME", "NH", "RI", "VT"]}
CONSTRUCTION, APPROVED = {"U", "V", "TS"}, {"T"}
PER_MW_YEAR = {"USD/MW-day": 365.0, "USD/kW-month": 12000.0}   # to USD per MW a year


def header_rows(path):
    """The count of the file's leading '#' lines (its provenance header)."""
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n


def find(table, dirs, first=False):
    """The table's file: warehouse/output first, then the --in-dir directories in order; with --in-dir-first (session
    712), the --in-dir directories before warehouse/output (a copy rebuilt from the archive that is newer than this
    machine's own)."""
    for d in ([*dirs, OUTPUT] if first else [OUTPUT, *dirs]):
        p = os.path.join(d, f"{table}.csv")
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"{table}.csv is in none of: {', '.join([OUTPUT, *dirs])}")


def nodes_file(path):
    """nodes.json's content from node_basis_daily."""
    cols = ["entity", "variable", "ts_utc", "value", "x_resource_type", "x_class"]
    keep = []
    for ch in pd.read_csv(path, skiprows=header_rows(path), usecols=cols, dtype={"value": float, "x_resource_type": str}, chunksize=500_000):
        keep.append(ch[ch["variable"].isin(["dam_basis", "dam_mean", "dam_spread_4h"])])
    d = pd.concat(keep, ignore_index=True)
    first, last = d["ts_utc"].min()[:10], d["ts_utc"].max()[:10]
    points = d["entity"].nunique()
    kinds = d.drop_duplicates("entity").set_index("entity")["x_class"]
    hubs, zones = int((kinds == "hub").sum()), int((kinds == "zone").sum())
    b = d[(d["variable"] == "dam_basis") & ~d["x_class"].isin(["hub", "zone"])].copy()
    b["m"] = b["ts_utc"].str[:7]
    g = b.groupby(["entity", "m"])["value"].agg(["mean", "count"]).reset_index()
    # session 711: the last twelve whole months the table holds (a month is whole when the table's last day is past it)
    months = sorted(b["m"].unique())
    last_whole = months[-1] if last[8:10] == str(pd.Period(months[-1]).days_in_month) else months[-2]
    p_to = last_whole
    p_from = (pd.Period(last_whole, "M") - 11).strftime("%Y-%m")
    w = b[(b["m"] >= p_from) & (b["m"] <= p_to)]
    pct = w.groupby("entity")["value"].quantile([0.1, 0.5, 0.9]).unstack()
    # session 746 (chain 063): the node's intraday swing, dam_spread_4h (each day's four dearest day-ahead hours' mean
    # less the four cheapest), over the same twelve months: its mean, its 10th and 90th percentile, and its days
    sw = d[(d["variable"] == "dam_spread_4h") & ~d["x_class"].isin(["hub", "zone"]) & (d["ts_utc"].str[:7] >= p_from) & (d["ts_utc"].str[:7] <= p_to)]
    swing = sw.groupby("entity")["value"].agg(["mean", "count"])
    swq = sw.groupby("entity")["value"].quantile([0.1, 0.9]).unstack()
    pdays = w.groupby("entity")["value"].count()
    meta = b.drop_duplicates("entity").set_index("entity")[["x_class", "x_resource_type"]]
    # session 795 (chain 065): the nodes that settle alike: the same day-ahead basis on every day, and the same days, over
    # everything the table holds for them (exact equality of the table's values; no reason inferred)
    srt = b.sort_values(["entity", "ts_utc"])
    sig = srt.groupby("entity").apply(lambda g: hash(tuple(zip(g["ts_utc"].tolist(), g["value"].tolist()))), include_groups=False)
    same = {}
    for _, ents in sig.groupby(sig):
        ids = sorted(e.split(":", 1)[1] for e in ents.index)
        if len(ids) > 1:
            for e in ents.index:
                same[e] = [i for i in ids if i != e.split(":", 1)[1]]
    nodes = []
    for ent, rows in g.groupby("entity"):
        nodes.append({
            "id": ent.split(":", 1)[1], "cls": str(meta.at[ent, "x_class"]), "types": "" if pd.isna(meta.at[ent, "x_resource_type"]) else str(meta.at[ent, "x_resource_type"]),
            "dam_basis": {r.m: [round(float(r.mean), 4), int(r.count)] for r in rows.itertuples()},
            **({"pct": [round(float(pct.at[ent, 0.1]), 4), round(float(pct.at[ent, 0.5]), 4), round(float(pct.at[ent, 0.9]), 4), int(pdays[ent])]} if ent in pct.index else {}),
            **({"swing": [round(float(swing.at[ent, "mean"]), 4), round(float(swq.at[ent, 0.1]), 4), round(float(swq.at[ent, 0.9]), 4), int(swing.at[ent, "count"])]} if ent in swing.index else {}),
            **({"same": same[ent]} if ent in same else {}),
        })
    # a node with no day-ahead basis day is still a node of the table (a point held only in real time)
    for ent in sorted(set(kinds.index[~kinds.isin(["hub", "zone"])]) - set(g["entity"])):
        nodes.append({"id": ent.split(":", 1)[1], "cls": str(kinds[ent]), "types": "", "dam_basis": {}})
    nodes.sort(key=lambda n: n["id"])
    return {"table": NODE_TABLE, "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "first": first, "last": last,
            "points": int(points), "hubs": hubs, "zones": zones, "pct_from": p_from, "pct_to": p_to, "nodes": nodes}


def cp_file(path):
    """ercot_4cp.json's content from ercot_4cp_intervals (session 702)."""
    d = pd.read_csv(path, skiprows=header_rows(path), dtype=str)
    d = d[d["variable"] == "cp4_load_mw"].sort_values("ts_utc")
    with open(path, encoding="utf-8") as f:
        head = [ln[2:].rstrip() for ln in f if ln.startswith("#")]
    held = next((h for h in head if h.startswith("Years held:")), "")
    summers = {}
    for r in d.itertuples():
        summers.setdefault(str(r.x_year), []).append({"ts": r.ts_utc, "local": r.x_interval_local, "mw": round(float(r.value), 3)})
    return {"table": CP_TABLE, "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "note": held,
            "summers": [{"year": int(y), "intervals": v} for y, v in sorted(summers.items())]}


def cap_frame(path):
    d = pd.read_csv(path, skiprows=header_rows(path), dtype=str)
    d = d[d["market"].isin(CAP_MARKETS) & (d["variable"] == "capacity_price")]
    return d


def cap_file(path):
    """capacity.json's content (session 704): the newest period of each market and its zones, no price."""
    d = cap_frame(path)
    markets = {}
    for m in CAP_MARKETS:
        x = d[d["market"] == m]
        last = x["ts_utc"].max()
        y = x[x["ts_utc"] == last]
        markets[m] = {"market": m, "table": CAP_TABLE, "license": "internal", "unit": str(y["unit"].iloc[0]), "period_start": last,
                      "period_end": str(y["x_period_end"].iloc[0]), "auction": str(y["x_auction"].iloc[0]), "zones": sorted(y["entity"].unique().tolist())}
    return {"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tables": [CAP_TABLE], "markets": markets}


def cap_internal(path, rows):
    """The tab's capacity figures, USD per MWh for a load that runs every hour, per row: never written to the site."""
    d = cap_frame(path)
    out = {}
    for r in rows:
        m = d[(d["market"] == r["market"]) & (d["entity"] == r["entity"]) & (d["ts_utc"] == r["period_start"])]
        if len(m) != 1:
            continue
        v = float(m["value"].iloc[0]) * PER_MW_YEAR[m["unit"].iloc[0]]
        out[r["row"]] = {"entity": r["entity"], "auction": r["auction"], "as_published": float(m["value"].iloc[0]), "unit": m["unit"].iloc[0], "usd_per_mw_year": v, "usd_per_mwh_every_hour": v / 8760}
    return out


def connect_file(path):
    """connect.json's content (session 705)."""
    d = pd.read_csv(path, skiprows=header_rows(path), dtype=str, usecols=["region", "q_status", "q_date", "on_date", "vintage"])
    vintage = str(d["vintage"].dropna().iloc[0])
    o = d[d["q_status"] == "operational"].copy()
    o["q"], o["on"] = pd.to_datetime(o["q_date"], errors="coerce"), pd.to_datetime(o["on_date"], errors="coerce")
    o = o.dropna(subset=["q", "on"])
    last = int(o["on"].dt.year.max())
    first = last - 2
    o = o[(o["on"].dt.year >= first) & (o["on"].dt.year <= last) & (o["on"] >= o["q"])]
    o["months"] = (o["on"] - o["q"]).dt.days / 30.4375
    grids = {}
    for region, g in LBNL_GRIDS.items():
        m = o.loc[o["region"] == region, "months"]
        n = int(len(m))
        ok = n >= MIN_N
        grids[g] = {"n": n, "median": round(float(m.median()), 2) if ok else None, "p25": round(float(m.quantile(0.25)), 2) if ok else None,
                    "p75": round(float(m.quantile(0.75)), 2) if ok else None}
    return {"table": LBNL_TABLE, "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "vintage": vintage, "from": first, "to": last, "min_n": MIN_N, "grids": grids}


def connect_from_durations(path):
    """connect.json's content from interconnection_durations (session 718): the data machine's per-project months to
    operation (to one decimal), the same requests as connect_file's, pooled over the newest three whole years."""
    d = pd.read_csv(path, skiprows=header_rows(path), dtype=str, usecols=["grid", "months_to_operation", "operation_year", "vintage"])
    vintage = str(d["vintage"].dropna().iloc[0])
    d["y"] = pd.to_numeric(d["operation_year"], errors="coerce")
    d["m"] = pd.to_numeric(d["months_to_operation"], errors="coerce")
    d = d.dropna(subset=["y", "m"])
    last = int(d["y"].max())
    first = last - 2
    d = d[(d["y"] >= first) & (d["y"] <= last)]
    grids = {}
    for g in DURATION_GRIDS:
        m = d.loc[d["grid"].str.lower() == g, "m"]
        n = int(len(m))
        ok = n >= MIN_N
        grids[g] = {"n": n, "median": round(float(m.median()), 2) if ok else None, "p25": round(float(m.quantile(0.25)), 2) if ok else None,
                    "p75": round(float(m.quantile(0.75)), 2) if ok else None}
    return {"table": DURATIONS_TABLE, "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "vintage": vintage, "from": first, "to": last, "min_n": MIN_N, "grids": grids}


def peak_capacity(path):
    """Each grid's peak against its balancing authority's generators (grid_peak_vs_capacity, session 718)."""
    g = pd.read_csv(path, skiprows=header_rows(path), dtype=str)
    out = {}
    for ent, x in g.groupby("entity"):
        v = {r.variable: float(r.value) for r in x.itertuples()}
        first = x.iloc[0]
        out[ent.split(":", 1)[1]] = {"year": int(first["ts_utc"][:4]), "peak_mw": v.get("peak_demand_mw"), "capacity_mw": v.get("capacity_mw"),
                                    "over_peak_pct": v.get("capacity_over_peak_pct"), "solar_mw": v.get("capacity_solar_mw"), "wind_mw": v.get("capacity_wind_mw"),
                                    "storage_mw": v.get("capacity_storage_mw"), "list": str(first.get("x_vintage", "")), "states": str(first.get("x_states", "")),
                                    "split_states": "" if pd.isna(first.get("x_split_states")) else str(first.get("x_split_states"))}
    return out


SUBBA_TABLE = "eia930_subba_demand_hourly"
# session 728 (chain 062): the tab's rows whose zone EIA-930 names as a sub-region, by the sub-region's own name. NYISO's
# eleven zones (ZONA West to ZONK Long Island) and ISO-NE's eight load zones (4001 Maine to 4008 Northeast Mass.) are the
# same areas under two names. ERCOT's sub-regions are its weather zones, not its load zones, and CAISO's are utilities,
# not trading hubs: those rows keep their grid's figure.
SUBBA_ROW = {
    "nyiso:WEST": "NYIS:ZONA", "nyiso:GENESE": "NYIS:ZONB", "nyiso:CENTRL": "NYIS:ZONC", "nyiso:NORTH": "NYIS:ZOND",
    "nyiso:MHK VL": "NYIS:ZONE", "nyiso:CAPITL": "NYIS:ZONF", "nyiso:HUD VL": "NYIS:ZONG", "nyiso:MILLWD": "NYIS:ZONH",
    "nyiso:DUNWOD": "NYIS:ZONI", "nyiso:N.Y.C.": "NYIS:ZONJ", "nyiso:LONGIL": "NYIS:ZONK",
    "isone:.Z.MAINE": "ISNE:4001", "isone:.Z.NEWHAMPSHIRE": "ISNE:4002", "isone:.Z.VERMONT": "ISNE:4003",
    "isone:.Z.CONNECTICUT": "ISNE:4004", "isone:.Z.RHODEISLAND": "ISNE:4005", "isone:.Z.SEMASS": "ISNE:4006",
    "isone:.Z.WCMASS": "ISNE:4007", "isone:.Z.NEMASSBOST": "ISNE:4008",
}


def zone_growth(dirs, first):
    """headroom.json's `zones` (session 728): for each row of SUBBA_ROW, its sub-region's mean hourly demand in the newest
    whole year a yearly table holds against the year before, over the hours each year holds (EIA gives some hours
    blank; nothing is filled). The live table (90 days) is not a year, so the yearly tables are read."""
    years = sorted(int(n[len(SUBBA_TABLE) + 1:-4]) for d in [*dirs, OUTPUT] if os.path.isdir(d)
                   for n in os.listdir(d) if n.startswith(SUBBA_TABLE + "_") and n.endswith(".csv") and n[len(SUBBA_TABLE) + 1:-4].isdigit())
    years = sorted(set(years))
    if len(years) < 2 or years[-1] - 1 not in years:
        raise FileNotFoundError(f"two consecutive years of {SUBBA_TABLE}_<year> are not on this machine")
    y, p = years[-1], years[-1] - 1
    want = {f"eia930_subba:{v}" for v in SUBBA_ROW.values()}
    means = {}
    for yr in (y, p):
        path = find(f"{SUBBA_TABLE}_{yr}", dirs, first)
        d = pd.read_csv(path, skiprows=header_rows(path), dtype=str, usecols=["entity", "variable", "value", "node"])
        d = d[(d["variable"] == "demand_mw") & d["entity"].isin(want)].copy()
        d["v"] = pd.to_numeric(d["value"], errors="coerce")
        d = d.dropna(subset=["v"])
        g = d.groupby("entity").agg(mean=("v", "mean"), hours=("v", "size"), name=("node", "first"))
        means[yr] = g
    out = {}
    for row, sub in SUBBA_ROW.items():
        e = f"eia930_subba:{sub}"
        if e in means[y].index and e in means[p].index and means[p].loc[e, "mean"] > 0:
            a, b = means[y].loc[e], means[p].loc[e]
            out[row] = {"subba": sub, "name": str(a["name"]), "year": y, "prior": p, "mean_mw": round(float(a["mean"]), 2),
                        "prior_mean_mw": round(float(b["mean"]), 2), "hours": int(a["hours"]), "prior_hours": int(b["hours"]),
                        "pct": round(100 * (float(a["mean"]) / float(b["mean"]) - 1), 4)}
    return {"table": SUBBA_TABLE, "year": y, "prior": p, "rows": out}


def headroom_file(ppath, cpath):
    """headroom.json's content (session 706)."""
    with open(ppath, encoding="utf-8") as fh:
        head = [ln for ln in fh if ln.startswith("#")]
    vintage = next((h.split("vintage")[-1].strip() for h in head if "vintage" in h), "")
    p = pd.read_csv(ppath, skiprows=header_rows(ppath), dtype=str, usecols=["balancing_authority", "eia_status", "planned_operation_date", "nameplate_mw"])
    v0 = pd.Period(vintage, "M")
    first, last = (v0 + 1).strftime("%Y-%m"), (v0 + 12).strftime("%Y-%m")
    p["m"] = p["planned_operation_date"].str[:7]
    p = p[(p["m"] >= first) & (p["m"] <= last)]
    p["mw"] = pd.to_numeric(p["nameplate_mw"], errors="coerce").fillna(0.0)
    planned = {}
    for ba, g in BA_GRIDS.items():
        x = p[p["balancing_authority"] == ba]
        c, a = x[x["eia_status"].isin(CONSTRUCTION)], x[x["eia_status"].isin(APPROVED)]
        o = x[~x["eia_status"].isin(CONSTRUCTION | APPROVED)]
        planned[g] = {"construction_mw": round(float(c["mw"].sum()), 1), "construction_n": int(len(c)), "approved_mw": round(float(a["mw"].sum()), 1),
                      "approved_n": int(len(a)), "other_mw": round(float(o["mw"].sum()), 1), "other_n": int(len(o))}
    s = pd.read_csv(cpath, skiprows=header_rows(cpath), dtype=str, usecols=["entity", "ts_utc", "value"])
    s = s[s["entity"].str.endswith(":TOT:ALL")]
    s["state"] = s["entity"].str.split(":").str[1]
    year = int(s["ts_utc"].max()[:4])
    s = s[s["ts_utc"].str[:4] == str(year)]
    cap = {}
    for g, states in WHOLE_STATES.items():
        x = s[s["state"].isin(states)]
        if len(x) == len(states):
            cap[g] = {"states": states, "year": year, "mw": round(float(pd.to_numeric(x["value"]).sum()), 1)}
    return {"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "planned_table": PLANNED_TABLE, "vintage": vintage, "from": first, "to": last,
            "planned": planned, "capacity_table": STATECAP_TABLE, "capacity": cap}


def carbon_file(epath, hpath, index):
    """carbon.json's content (session 707)."""
    e = pd.read_csv(epath, skiprows=header_rows(epath), dtype=str, usecols=["egrid_subregion", "iso_rto", "co2_tons", "net_generation_mwh", "data_year", "vintage"])
    e["co2"] = pd.to_numeric(e["co2_tons"], errors="coerce")
    e["gen"] = pd.to_numeric(e["net_generation_mwh"], errors="coerce")
    # eGRID's own subregion rate is the plants' CO2 summed over their net generation summed: a plant that reports no CO2
    # (wind, solar, hydro, nuclear: the cell is blank) adds its generation and no CO2. Nothing is filled
    e = e.dropna(subset=["gen"])

    def area(x):
        return {"co2_tons": round(float(x["co2"].sum(skipna=True)), 1), "gen_mwh": round(float(x["gen"].sum()), 1), "plants": int(len(x)),
                "plants_no_co2": int(x["co2"].isna().sum())}
    areas = {sub: area(e[e["egrid_subregion"] == sub]) for sub in SUBREGIONS}
    areas["PJM"] = area(e[e["iso_rto"] == "PJM"])
    hourly = {}
    want = {f"eia930:{ba}": g for g, ba in HOURLY_GRIDS.items()}
    keep = []
    for ch in pd.read_csv(hpath, skiprows=header_rows(hpath), dtype=str, usecols=["entity", "variable", "ts_utc", "value"], chunksize=500_000):
        keep.append(ch[(ch["variable"] == HOURLY_VAR) & ch["entity"].isin(want)])
    h = pd.concat(keep, ignore_index=True)
    h["t"] = pd.to_datetime(h["ts_utc"], utc=True)
    for ent, g in want.items():
        gi = index["grids"].get(g)
        if not gi:
            continue
        behind = int(gi["std_hours_behind_utc"])
        x = h[h["entity"] == ent].copy()
        x["std"] = x["t"] - pd.Timedelta(hours=behind)
        x["y"] = x["std"].dt.year
        x["i"] = ((x["std"] - pd.to_datetime(x["y"].astype(str) + "-01-01", utc=True)) / pd.Timedelta(hours=1)).astype(int)
        hourly[g] = {}
        for y in (2025, 2026):
            z = x[x["y"] == y].drop_duplicates("i").set_index("i")["value"].astype(float)
            if not len(z):
                continue
            s, last = int(z.index.min()), int(z.index.max())
            hourly[g][str(y)] = {"s": s, "v": [None if pd.isna(z.get(i)) else round(float(z.get(i)), 1) for i in range(s, last + 1)]}
    return {"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "egrid_table": EGRID_TABLE, "vintage": str(e["vintage"].iloc[0]),
            "data_year": int(e["data_year"].iloc[0]), "areas": areas, "hourly_table": HOURLY_TABLE, "hourly_variable": HOURLY_VAR, "hourly": hourly}


def county_utilities(tpath, spath):
    """For each row of ROW_COUNTY, the utilities EIA-861's territories list for the county, and among them the one with
    the most industrial sales in the state that year, of the rows that bill a customer (Bundled or Delivery: the wires
    utility; an energy-only retailer has no territory) (session 718)."""
    t = pd.read_csv(tpath, skiprows=header_rows(tpath), dtype=str, usecols=["name", "x_utility_number", "x_state", "x_county", "x_data_year"])
    keep = []
    for ch in pd.read_csv(spath, skiprows=header_rows(spath), dtype=str, chunksize=500_000,
                          usecols=["variable", "ts_utc", "value", "node", "x_utility_number", "x_state", "x_service_type", "x_ba_code"]):
        keep.append(ch[ch["variable"].isin(["industrial_sales", "industrial_revenue"]) & ch["x_service_type"].isin(["Bundled", "Delivery"])])
    s = pd.concat(keep, ignore_index=True)
    s["v"] = pd.to_numeric(s["value"], errors="coerce")
    s["y"] = s["ts_utc"].str[:4].astype(int)
    year = int(s["y"].max())
    out = {}
    ba_of = {g: ba for ba, g in BA_GRIDS.items()}
    for row, (st, county) in ROW_COUNTY.items():
        c = t[(t["x_state"] == st) & (t["x_county"].str.lower() == county.lower())]
        nums = sorted(set(c["x_utility_number"]))
        # inside the row's grid: a county can hold utilities of two grids (Harris: CenterPoint's ERCOT and Entergy Texas's MISO)
        x = s[(s["x_state"] == st) & s["x_utility_number"].isin(nums) & (s["x_ba_code"] == ba_of[row.split(":")[0]])]
        sales = x[(x["variable"] == "industrial_sales") & (x["y"] == year) & (x["v"] > 0)].groupby(["x_utility_number", "x_service_type"])["v"].sum().reset_index()
        # every utility the territories list for the county, with the grid (balancing authority) its sales rows in the
        # state name, or none where it files no sales row (Texas's wires utilities: CenterPoint in Harris)
        allrows = s[(s["x_state"] == st) & s["x_utility_number"].isin(nums)]
        bas = allrows.groupby("x_utility_number")["x_ba_code"].agg(lambda v: sorted(set(v.dropna())))
        utils = [{"name": str(r.name), "number": str(r.x_utility_number), "ba": bas.get(r.x_utility_number, [])} for r in c.drop_duplicates("x_utility_number").sort_values("name").itertuples()]
        entry = {"state": st, "county": county, "ba": ba_of[row.split(":")[0]], "territory_year": int(c["x_data_year"].iloc[0]) if len(c) else None,
                 "utilities": utils, "top": None}
        if len(sales):
            top = sales.sort_values(["v", "x_utility_number"], ascending=[False, True]).iloc[0]
            num, svc = top["x_utility_number"], top["x_service_type"]
            sel = x[(x["x_utility_number"] == num) & (x["x_service_type"] == svc)]
            rev = sel[(sel["variable"] == "industrial_revenue") & (sel["y"] == year)]["v"].sum()
            prior = sel[(sel["variable"] == "industrial_sales") & (sel["y"] == year - 1)]["v"].sum()
            name = sel["node"].dropna().iloc[0]
            entry["top"] = {"utility": str(name), "number": str(num), "service": str(svc), "sales_mwh": float(top["v"]), "revenue_usd": float(rev),
                            "sales_prior_mwh": float(prior) if prior > 0 else None, "year": year}
        out[row] = entry
    return out


def utility_file(path):
    """utility.json's content (session 708)."""
    keep = []
    for ch in pd.read_csv(path, skiprows=header_rows(path), dtype=str, chunksize=500_000,
                          usecols=["entity", "variable", "ts_utc", "value", "node", "x_utility_number", "x_state", "x_part", "x_service_type", "x_ba_code"]):
        keep.append(ch[ch["variable"].isin(["industrial_sales", "industrial_revenue"]) & ch["x_service_type"].isin(["Bundled", "Energy"])])
    d = pd.concat(keep, ignore_index=True)
    d["v"] = pd.to_numeric(d["value"], errors="coerce")
    d["y"] = d["ts_utc"].str[:4].astype(int)
    year = int(d["y"].max())
    prior = year - 1
    by = {}
    for st, ba in UTILITY_STATES:
        x = d[(d["x_state"] == st) & (d["x_ba_code"] == ba)]
        s = x[(x["variable"] == "industrial_sales") & (x["y"] == year) & (x["v"] > 0)]
        if not len(s):
            by[f"{st}|{ba}"] = None
            continue
        top = s.sort_values(["v", "entity"], ascending=[False, True]).iloc[0]
        rev = x[(x["entity"] == top["entity"]) & (x["variable"] == "industrial_revenue") & (x["y"] == year)]
        pri = x[(x["entity"] == top["entity"]) & (x["variable"] == "industrial_sales") & (x["y"] == prior)]
        if not len(rev):
            by[f"{st}|{ba}"] = None
            continue
        by[f"{st}|{ba}"] = {"utility": str(top["node"]), "number": str(top["x_utility_number"]), "part": str(top["x_part"]), "service": str(top["x_service_type"]),
                            "sales_mwh": float(top["v"]), "revenue_usd": float(rev["v"].iloc[0]),
                            "sales_prior_mwh": float(pri["v"].iloc[0]) if len(pri) and pri["v"].iloc[0] > 0 else None, "sellers": int(s["entity"].nunique())}
    return {"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "table": UTILITY_TABLE, "year": year, "prior": prior, "by": by}


GAPS_MD = os.path.join(ROOT, "docs", "reviews", "siting-gaps.md")
STATE_SHARE = 0.85


def county_key(state, county):
    """A county's key as the tab matches it: the state, and the county's name without "County" or "Parish", lower case."""
    c = str(county or "").strip()
    for suf in (" County", " Parish", " county", " parish"):
        if c.endswith(suf):
            c = c[: -len(suf)]
    return f"{str(state).strip().upper()}|{c.strip().lower()}"


def facilities_file(spath, tpath):
    """facilities.json's content (session 719), from the two public tables only: datacenter_facilities is held whole
    (license needed since 21 October 2026), so nothing of its rows is written here. Every county of the service
    territories whose utilities' sales rows sit inside one grid only, and each state 85 percent or more inside one."""
    s = pd.read_csv(spath, skiprows=header_rows(spath), dtype=str, usecols=["variable", "ts_utc", "value", "x_utility_number", "x_state", "x_service_type", "x_ba_code"])
    s = s[s["x_ba_code"].notna()]
    year = int(s["ts_utc"].str[:4].max())
    tot = s[(s["variable"] == "total_sales") & (s["ts_utc"].str[:4] == str(year)) & s["x_service_type"].isin(["Bundled", "Energy"])].copy()
    tot["v"] = pd.to_numeric(tot["value"], errors="coerce").fillna(0.0)
    g = tot.groupby(["x_state", "x_ba_code"])["v"].sum().reset_index()
    g["share"] = g["v"] / g.groupby("x_state")["v"].transform("sum")
    states = {}
    for st, x in g.groupby("x_state"):
        top = x.sort_values("share", ascending=False).iloc[0]
        grid = BA_GRIDS.get(top["x_ba_code"])
        if grid and top["share"] >= STATE_SHARE:
            states[st] = {"grid": grid, "share": round(float(top["share"]), 4)}
    t = pd.read_csv(tpath, skiprows=header_rows(tpath), dtype=str, usecols=["x_utility_number", "x_state", "x_county"])
    t = t.dropna(subset=["x_state", "x_county", "x_utility_number"])
    bas = s.groupby(["x_state", "x_utility_number"])["x_ba_code"].agg(lambda v: sorted(set(v))).to_dict()
    counties = {}
    for (st, county), nums in t.groupby(["x_state", "x_county"])["x_utility_number"]:
        nums = sorted(set(nums))
        b = {x for n in nums for x in bas.get((st.strip().upper(), n), [])}
        grids = sorted({BA_GRIDS[x] for x in b if x in BA_GRIDS})
        if len(grids) == 1 and not (b - set(BA_GRIDS)):
            counties[county_key(st, county)] = {"grid": grids[0], "utilities": len(nums)}
    rows = {county_key(st, c): row for row, (st, c) in ROW_COUNTY.items()}
    return {"built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "tables": [UTILITY_TABLE, TERRITORY_TABLE],
            "year": year, "state_share": STATE_SHARE, "states": states, "counties": counties, "county_rows": rows}


TARIFF_TABLE = "utility_large_load_tariffs"


def tariffs_file(path):
    """tariffs.json's content (session 730, chain 062), when the data machine's table has landed: each utility's (EIA
    id) large-load rates as warehouse/connectors/openei_large_load_tariffs.py documents them, one series row a rate and
    a variable (energy_charge USD/MWh, demand_charge USD/kW-month, fixed_charge USD a month, min_demand_mw MW), keyed by
    the rate (entity) and its start (ts_utc). NOT WIRED into the tab: the table had not landed when this was written.
    Its license is the table's own; a table held under a license is never written to the site's files."""
    d = pd.read_csv(path, skiprows=header_rows(path), dtype=str)
    need = {"entity", "variable", "ts_utc", "value", "x_eia_id", "x_utility", "x_sector"}
    if not need <= set(d.columns):
        raise ValueError(f"{TARIFF_TABLE} lacks {sorted(need - set(d.columns))}")
    d["v"] = pd.to_numeric(d["value"], errors="coerce")
    rates = {}
    for (ent, start), g in d.groupby(["entity", "ts_utc"]):
        v = {r.variable: (None if pd.isna(r.v) else float(r.v)) for r in g.itertuples()}
        first = g.iloc[0]
        rates.setdefault(str(first["x_eia_id"]), []).append({
            "rate": ent, "name": str(first.get("node") or ""), "start": str(start)[:10], "utility": str(first["x_utility"]),
            "sector": str(first["x_sector"]), "energy": v.get("energy_charge"), "demand": v.get("demand_charge"),
            "fixed": v.get("fixed_charge"), "min_mw": v.get("min_demand_mw")})
    for k in rates:
        rates[k].sort(key=lambda r: (r["start"], r["rate"]), reverse=True)
    return {"table": TARIFF_TABLE, "built": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "utilities": rates}


def gaps_file(path=GAPS_MD):
    """gaps.json's content (session 713): the markdown table's rows, each cell as written."""
    with open(path, encoding="utf-8") as fh:
        lines = [ln.rstrip("\n") for ln in fh]
    table = [ln for ln in lines if ln.startswith("| ")]
    if len(table) < 3:
        raise ValueError(f"{path} holds no table")
    cells = lambda ln: [c.strip() for c in ln.strip().strip("|").split(" | ")]
    columns = cells(table[0])
    rows = [dict(zip(columns, cells(ln))) for ln in table[2:]]
    bad = [r for r in rows if len(r) != len(columns)]
    if bad:
        raise ValueError(f"{len(bad)} rows of {path} do not have {len(columns)} cells")
    return {"source": "docs/reviews/siting-gaps.md", "columns": columns, "rows": rows}


def write(name, obj, out_dir):
    """Write a file, unless it holds the same content but for its build time (no change, no new commit)."""
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, name)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            old = json.load(f)
        if {k: v for k, v in old.items() if k != "built"} == {k: v for k, v in obj.items() if k != "built"}:
            print(f"kept {p}: the same content")
            return
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, separators=(",", ":"), ensure_ascii=False)
        f.write("\n")
    print(f"wrote {p} ({os.path.getsize(p):,} bytes)")


def main(argv=None):
    ap = argparse.ArgumentParser(description="The All grids tab's files for /cost-of-power")
    ap.add_argument("--in-dir", action="append", default=[], help="a directory to read a table from when warehouse/output lacks it")
    ap.add_argument("--out-dir", default=SITE_DIR, help="where the files go (default site/data/siting)")
    ap.add_argument("--in-dir-first", action="store_true", help="session 712: read the --in-dir directories before warehouse/output")
    ap.add_argument("--internal", help="session 704: write the capacity prices per row to this file (outside the repository)")
    ap.add_argument("--rows", help="with --internal: the tab's rows and their capacity zones as JSON (node scripts/siting-files.mjs capzones)")
    a = ap.parse_args(argv)
    try:
        path = find(NODE_TABLE, a.in_dir, a.in_dir_first)
        print(f"reading {path}")
        f = nodes_file(path)
    except Exception as e:  # loud: no file from part of a table
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{NODE_TABLE}: {f['points']} points, {f['hubs']} hubs, {f['zones']} zones, {len(f['nodes'])} nodes, {f['first']} to {f['last']}")
    try:
        cpath = find(CP_TABLE, a.in_dir, a.in_dir_first)
        print(f"reading {cpath}")
        cp = cp_file(cpath)
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{CP_TABLE}: {len(cp['summers'])} summers, {sum(len(s['intervals']) for s in cp['summers'])} intervals")
    try:
        kpath = find(CAP_TABLE, a.in_dir, a.in_dir_first)
        print(f"reading {kpath}")
        cap = cap_file(kpath)
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{CAP_TABLE}: " + "; ".join(f"{m['auction']} ({len(m['zones'])} zones)" for m in cap["markets"].values()))
    write("nodes.json", f, a.out_dir)
    write("ercot_4cp.json", cp, a.out_dir)
    write("capacity.json", cap, a.out_dir)
    try:
        try:
            dpath = find(DURATIONS_TABLE, a.in_dir, a.in_dir_first)
            print(f"reading {dpath}")
            con = connect_from_durations(dpath)
        except FileNotFoundError:
            lpath = find(LBNL_TABLE, a.in_dir, a.in_dir_first)
            print(f"reading {lpath} ({DURATIONS_TABLE} is not on this machine)")
            con = connect_file(lpath)
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{LBNL_TABLE}: " + "; ".join(f"{g} {v['median']} ({v['n']})" for g, v in con["grids"].items()))
    write("connect.json", con, a.out_dir)
    try:
        ppath, spath = find(PLANNED_TABLE, a.in_dir, a.in_dir_first), find(STATECAP_TABLE, a.in_dir, a.in_dir_first)
        print(f"reading {ppath} and {spath}")
        hr = headroom_file(ppath, spath)
        try:
            gpath = find(PEAKCAP_TABLE, a.in_dir, a.in_dir_first)
            print(f"reading {gpath}")
            hr["peak_capacity"] = peak_capacity(gpath)
            hr["peak_capacity_table"] = PEAKCAP_TABLE
        except FileNotFoundError:
            print(f"{PEAKCAP_TABLE} is not on this machine: capacity over peak stays the whole states'")
        try:
            hr["zones"] = zone_growth(a.in_dir, a.in_dir_first)
            print(f"{SUBBA_TABLE}: {len(hr['zones']['rows'])} zones, {hr['zones']['year']} over {hr['zones']['prior']}")
        except FileNotFoundError as e:
            print(f"{e}: every row keeps its grid's demand growth")
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{PLANNED_TABLE} {hr['from']} to {hr['to']}: " + "; ".join(f"{g} {v['construction_mw']}" for g, v in hr["planned"].items()))
    write("headroom.json", hr, a.out_dir)
    try:
        epath, hpath = find(EGRID_TABLE, a.in_dir, a.in_dir_first), find(HOURLY_TABLE, a.in_dir, a.in_dir_first)
        print(f"reading {epath} and {hpath}")
        with open(os.path.join(ROOT, "site", "data", "datacenter", "index.json"), encoding="utf-8") as fh:
            index = json.load(fh)
        cb = carbon_file(epath, hpath, index)
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{EGRID_TABLE}: " + "; ".join(f"{k} {round(v['co2_tons'] * 2000 / v['gen_mwh'], 1) if v['gen_mwh'] else None}" for k, v in cb["areas"].items()))
    write("carbon.json", cb, a.out_dir)
    try:
        upath = find(UTILITY_TABLE, a.in_dir, a.in_dir_first)
        print(f"reading {upath}")
        ut = utility_file(upath)
        try:
            tpath = find(TERRITORY_TABLE, a.in_dir, a.in_dir_first)
            print(f"reading {tpath}")
            ut["county"] = county_utilities(tpath, upath)
            ut["territory_table"] = TERRITORY_TABLE
        except FileNotFoundError:
            print(f"{TERRITORY_TABLE} is not on this machine: the state's largest seller stands in")
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"{UTILITY_TABLE} {ut['year']}: " + "; ".join(f"{k} {v['utility'] if v else None}" for k, v in ut["by"].items()))
    write("utility.json", ut, a.out_dir)
    try:
        gp = gaps_file()
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"siting-gaps.md: {len(gp['rows'])} rows")
    write("gaps.json", gp, a.out_dir)
    try:
        fac = facilities_file(find(UTILITY_TABLE, a.in_dir, a.in_dir_first), find(TERRITORY_TABLE, a.in_dir, a.in_dir_first))
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        return 1
    print(f"facilities.json: {len(fac['states'])} states, {len(fac['counties'])} counties in one grid")
    write("facilities.json", fac, a.out_dir)
    if a.internal:
        if not a.rows:
            print("FAILED: --internal needs --rows", file=sys.stderr)
            return 1
        with open(a.rows, encoding="utf-8") as fh:
            rows = json.load(fh)
        got = cap_internal(kpath, rows)
        with open(a.internal, "w", encoding="utf-8") as fh:
            json.dump({"table": CAP_TABLE, "license": "internal: never in the repository", "rows": got}, fh, indent=1)
        print(f"wrote {a.internal}: {len(got)} rows (internal, outside the repository)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
