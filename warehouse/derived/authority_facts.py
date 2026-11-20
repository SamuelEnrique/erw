"""ERW: every balancing authority's own facts, and each region's (site/data/regions/authority/).

Session 8012, chain 505 (part C). For each balancing authority of site/data/regions/index.json that files Form
EIA-930 in the lower 48, and summed for each of EIA's thirteen regions, one file of what the authority owns, what is
coming and going, what it generates and how clean it is, whom it trades with, how large its demand is, and what the
public record says of large loads there. Contract: section 10 of docs/state/page_files_regions.md. Method:
docs/methods/authority_facts.md. Every part names its ERW table, its vintage and its source; a part a source does not
cover is present with null values and a reason, never a zero. No figure of the ERW's own beyond sums, shares and the
one ratio the method names (EIA's CO2 over the same hours' net generation).

Inputs (all on the data machine): eia860m_operating_generators, eia860m_planned_generators,
eia860m_retired_generators, eia930_all_emissions, ba_trade_partners, large_load_public (warehouse/output); the saved
six-month Form EIA-930 files (warehouse/raw/eia930_region_hourly, read with the region fuel connector's reader); the
demand, trade and index page files under site/data/regions.

    python warehouse/derived/authority_facts.py [--site-dir PATH] [--only CODE ...]
"""
import argparse
import datetime as dt
import json
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402
import eia930_region_fuel_hourly as rf  # noqa: E402

OUT = os.path.join(ROOT, "warehouse", "output")
SITE = os.path.join(ROOT, "site", "data", "regions")
SOURCES = rf.SOURCES
METHOD = "docs/methods/authority_facts.md"
TABLES = ["eia860m_operating_generators", "eia860m_planned_generators", "eia860m_retired_generators", "eia930_all_emissions",
          "ba_trade_partners", "large_load_public", "eia930_ba_demand_hourly"]
EMISSIONS_BAS = {"CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"}
# large_load_public: a row's grid of the seven names its authority; for the rest, the utility group's authority as EIA
# names it (EIA-861's balancing authority of the utility in the row's state). A group that spans several authorities
# in its rows is not placed (null with its reason).
GRID_BA = {"pjm": "PJM", "ercot": "ERCO", "caiso": "CISO", "miso": "MISO", "spp": "SWPP", "nyiso": "NYIS", "isone": "ISNE"}
GROUP_BA = {
    "Arizona Public Service": "AZPS", "El Paso Electric": "EPE", "Georgia Power (Southern Company)": "SOCO", "JEA": "JEA",
    "NextEra Energy (Florida Power & Light)": "FPL", "PPL": "LGEE", "PacifiCorp": "PACE", "Tampa Electric": "TEC",
    "Tucson Electric Power": "TEPC", "Xcel Energy": "PSCO",
}
NOT_PLACED = {
    "Duke Energy": "Duke Energy's rows are for South Carolina, where its two authorities (DUK and CPLE) both serve; the rows do not say which",
    "American Electric Power": "its rows span eleven states and several authorities",
    "Federal Energy Regulatory Commission": "a federal regulator's rows, for the whole country",
    "National Grid": "its rows are classed as spanning more than one grid",
    "Wabash Valley Power Alliance": "a cooperative whose members lie in more than one authority",
}


def read_table(name, usecols=None):
    p = os.path.join(OUT, name + ".csv")
    if not os.path.exists(p):
        raise SystemExit(f"no table {name} at {p}")
    fh = open(p, "rb")
    for _ in range(ip.header_rows(p)):
        fh.readline()
    d = pd.read_csv(fh, dtype=str, keep_default_na=False, usecols=usecols, engine="pyarrow" if usecols else "c")
    head = [ln.decode("utf-8", "replace") for ln in open(p, "rb").readlines()[: ip.header_rows(p)]]
    return d, head


def vintage_of(d):
    v = sorted(set(d["vintage"]) - {""}) if "vintage" in d else []
    return v[-1] if v else None


def num(s):
    return pd.to_numeric(s, errors="coerce")


def none_if_nan(x, nd=1):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), nd)


def by_year(frame, year_col, nd=1):
    if frame.empty:
        return []
    g = frame.groupby([year_col, "technology_group"]).agg(mw=("mw", "sum"), generators=("mw", "size")).reset_index()
    return [{"year": int(r[year_col]), "technology_group": r["technology_group"], "mw": round(float(r["mw"]), nd), "generators": int(r["generators"])}
            for _, r in g.sort_values([year_col, "technology_group"]).iterrows()]


def owns_coming(op, pl, rt, bas, vint):
    o = op[op["balancing_authority"].isin(bas)]
    cap = o.groupby("technology_group")["mw"].sum().sort_values(ascending=False)
    plants = o.groupby("plant_id").agg(mw=("mw", "sum"), name=("name", "first"), state=("state", "first"), operator=("operator", "first")).reset_index()
    main = o.sort_values("mw", ascending=False).groupby("plant_id")["technology_group"].first()
    plants["technology_group"] = plants["plant_id"].map(main)
    top = plants.sort_values("mw", ascending=False).head(10)
    src = "U.S. Energy Information Administration, Form EIA-860M (Preliminary Monthly Electric Generator Inventory)"
    owns = {"table": "eia860m_operating_generators", "vintage": vint, "source": src, "basis": "net summer capacity (capacity_mw) by the plant's balancing authority",
            "generators": int(len(o)), "total_mw": round(float(o["mw"].sum()), 1),
            "capacity_mw": {k: round(float(v), 1) for k, v in cap.items()},
            "largest_plants": [{"plant_id": r["plant_id"], "name": r["name"], "state": r["state"], "mw": round(float(r["mw"]), 1),
                                "technology_group": r["technology_group"], "operator": r["operator"]} for _, r in top.iterrows()]}
    if o.empty:
        owns.update({"generators": None, "total_mw": None, "capacity_mw": None, "largest_plants": None,
                     "why": "EIA-860M names no operating generator with this balancing authority"})
    p = pl[pl["balancing_authority"].isin(bas)].copy()
    p["year"] = num(p["planned_operation_date"].str[:4])
    r_ = o[o["planned_retirement_date"].str.len() >= 4].copy()
    r_["year"] = num(r_["planned_retirement_date"].str[:4])
    gone = rt[rt["balancing_authority"].isin(bas)].copy()
    gone["year"] = num(gone["retirement_date"].str[:4])
    coming = {"table": "eia860m_planned_generators, eia860m_operating_generators, eia860m_retired_generators", "vintage": vint, "source": src,
              "additions": by_year(p.dropna(subset=["year"]), "year"), "retirements": by_year(r_.dropna(subset=["year"]), "year"),
              "retired_recent": by_year(gone.dropna(subset=["year"]), "year")}
    return owns, coming


def generation(months_first, months_last, log):
    """Hourly net generation by source for every authority over the months, from the saved six-month files."""
    first, last = pd.Timestamp(months_first + "-01", tz="UTC"), pd.Timestamp(months_last + "-01", tz="UTC") + pd.offsets.MonthBegin(1)
    frames = []
    for name in rf.files_between(first=(first.year, 1 if first.month <= 6 else 2)):
        got = rf.saved_copy(name)
        if not got:
            log(f"  {name}: no saved copy")
            continue
        d = rf.read_file(got[0])
        d = d[(d["ts"] >= first) & (d["ts"] < last)]
        frames.append(d)
        log(f"  {name}: {len(d):,} rows in the months")
    d = pd.concat(frames, ignore_index=True)
    return d.drop_duplicates(subset=["ba", "ts"], keep="last")


def burns_of(gen, bas, months, co2):
    g = gen[gen["ba"].isin(bas)]
    src = "U.S. Energy Information Administration, Form EIA-930, the six-month BALANCE files (net generation by source; EIA's adjusted values where it prints them)"
    out = {"table": "eia930_region_fuel_hourly (the same six-month files)", "vintage": f"{months[0]} to {months[1]}", "source": src, "months": list(months)}
    if g.empty:
        out.update({"generation_mwh": None, "share_pct": None, "hours_held": None, "why": "Form EIA-930 holds no net generation for this authority in the months"})
    else:
        gen_mwh = {s: g[s].sum(min_count=1) for s in SOURCES}
        tot = sum(v for v in gen_mwh.values() if pd.notna(v))
        out["generation_mwh"] = {s: none_if_nan(v, 0) for s, v in gen_mwh.items()}
        out["share_pct"] = {s: (None if pd.isna(v) or not tot else round(100 * float(v) / tot, 2)) for s, v in gen_mwh.items()}
        out["hours_held"] = int(g.groupby("ts")["ng"].count().gt(0).sum())
        out["net_generation_mwh"] = none_if_nan(g["ng"].sum(min_count=1), 0)
    if co2 is None:
        out["co2"] = {"tco2_generated": None, "intensity_kg_per_mwh": None,
                      "why": "EIA's hourly CO2 estimates held by the ERW (eia930_all_emissions, from EIA's Grid Monitor workbooks) cover the seven ISOs and the Lower 48 only"}
    else:
        out["co2"] = co2
    return out


def co2_for(em, gen, ba, months):
    e = em[em["entity"] == f"eia930:{ba}"]
    if e.empty:
        return None
    first, last = pd.Timestamp(months[0] + "-01", tz="UTC"), pd.Timestamp(months[1] + "-01", tz="UTC") + pd.offsets.MonthBegin(1)
    e = e[(e["ts"] >= first) & (e["ts"] < last)].set_index("ts")["value"]
    g = gen[gen["ba"] == ba].set_index("ts")["ng"]
    both = pd.concat([e, g], axis=1, keys=["co2", "ng"]).dropna()
    both = both[both["ng"] > 0]
    if both.empty:
        return None
    return {"table": "eia930_all_emissions", "vintage": f"{months[0]} to {months[1]}",
            "source": "U.S. Energy Information Administration, Hourly Electric Grid Monitor, CO2 emissions estimates (CO2 Emissions Generated)",
            "tco2_generated": round(float(both["co2"].sum()), 0), "hours": int(len(both)),
            "intensity_kg_per_mwh": round(1000 * float(both["co2"].sum()) / float(both["ng"].sum()), 1),
            "basis": "EIA's CO2 Emissions Generated over the hours that also hold net generation, divided by that net generation"}


def trades_ba(tp, ba, names):
    t = tp[tp["x_ba"] == ba]
    if t.empty:
        return {"table": "ba_trade_partners", "year": None, "partners": None, "net_import_share_of_demand_pct": None,
                "why": "ba_trade_partners holds no interchange for this authority"}
    full = t[(t["variable"] == "exchange_gross_mwh") & (num(t["x_hours"]) >= 8700)]
    years = sorted(set(full["ts_utc"].str[:4]))
    year = years[-1] if years else sorted(set(t["ts_utc"].str[:4]))[-1]
    y = t[t["ts_utc"].str[:4] == year]
    gross = y[y["variable"] == "exchange_gross_mwh"].assign(v=lambda x: num(x["value"])).sort_values("v", ascending=False).head(5)
    net = y[y["variable"] == "net_import_mwh"].set_index("x_partner")["value"]
    share = y[y["variable"] == "net_import_share_of_demand_pct"]
    return {"table": "ba_trade_partners", "vintage": year, "year": int(year),
            "source": "U.S. Energy Information Administration, Form EIA-930, interchange as the authority filed it (summed by year)",
            "partners": [{"code": r["x_partner"], "name": names.get(r["x_partner"], r["x_partner"]), "exchange_gross_mwh": none_if_nan(num(r["value"]), 0),
                          "net_import_mwh": none_if_nan(num(net.get(r["x_partner"])), 0)} for _, r in gross.iterrows()],
            "net_import_share_of_demand_pct": none_if_nan(num(share["value"]).iloc[0], 2) if len(share) else None,
            **({} if len(share) else {"why": "no share for the year: the authority's demand is not held for the whole year"})}


def trades_region(code, matrix, trade, names):
    yrs = [y for y in matrix.get("years", []) if str(y) < str(matrix.get("upto", "9999"))[:4]]
    year = yrs[-1] if yrs else None
    pairs = [p for p in matrix.get("region_pairs", []) if p["year"] == year and code in (p["a"], p["b"])]
    rows = []
    for p in pairs:
        other = p["b"] if p["a"] == code else p["a"]
        v = p.get("mean_mwh")
        if v is None:
            continue
        # mean_mwh is power from a to b (positive from a to b, the contract's section 7); into the region is its sign seen from the region
        into = float(v) if p["b"] == code else -float(v)
        rows.append({"code": other, "name": names.get(other, other), "flow_mwh": round(abs(into), 0), "direction": "into" if into > 0 else "out of"})
    rows = sorted(rows, key=lambda r: -r["flow_mwh"])[:5]
    share = None
    if trade and year is not None:
        months = [i for i, m in enumerate(trade["months"]) if m.startswith(str(year))]
        vals = [trade["net_imports_mwh"][i] for i in months]
        share = {"net_imports_mwh": round(float(sum(vals)), 0) if len(vals) == 12 and all(v is not None for v in vals) else None}
    return {"table": "eia930_region_pair_hourly (trade_matrix.json, trade/<region>.json)", "vintage": str(year), "year": year,
            "source": "U.S. Energy Information Administration, Form EIA-930, each side's report of the flow; the mean of the two reports",
            "partners": rows, "net_imports_mwh": share["net_imports_mwh"] if share else None,
            "net_import_share_of_demand_pct": None, "why": "the share is given for an authority (ba_trade_partners); a region's net imports are in trade/<region>.json"}


def size_of(demand):
    if not demand:
        return {"table": "eia930_ba_demand_hourly", "peak_mw": None, "peak_at": None, "growth_since_2019_pct": None, "why": "no demand file for this authority"}
    d = demand["daily"]
    pk = [(v, d["peak_at"][i]) for i, v in enumerate(d["peak_mw"]) if v is not None]
    v, at = max(pk, key=lambda x: x[0]) if pk else (None, None)
    local = pd.Timestamp(at).tz_convert(demand["tz"]).strftime("%Y-%m-%d %H:%M") if at else None
    g = demand.get("growth") or {}
    yrs = g.get("years") or {}
    last = str(g.get("last_year")) if g.get("last_year") else None
    base = yrs.get("2019", {}).get("avg_demand_mw")
    now = yrs.get(last, {}).get("avg_demand_mw") if last else None
    out = {"table": "eia930_ba_demand_hourly", "vintage": f"{demand.get('first_hour', '')[:10]} to {demand.get('last_hour', '')[:10]}",
           "source": "U.S. Energy Information Administration, Form EIA-930, demand (adjusted where EIA prints it; screened as the demand file's method says)",
           "peak_mw": v, "peak_at": at, "peak_local": local, "tz": demand["tz"],
           "growth_year": int(last) if last else None, "growth_since_2019_pct": round(100 * (now / base - 1), 2) if base and now else None}
    if out["growth_since_2019_pct"] is None:
        out["why"] = "2019 or the newest whole year is not held whole in the demand file"
    return out


def large_loads_of(ll, bas):
    rows, how = [], ("a row whose grid is one of the seven is placed in that grid's authority; a utility group's rows in the authority EIA names for "
                     "it (the builder's GROUP_BA); groups spanning several authorities are not placed (NOT_PLACED)")
    for _, r in ll.iterrows():
        ba = GRID_BA.get(r["grid"]) or GROUP_BA.get(r["entity_group"])
        if ba in bas:
            rows.append({"date": r["event_date"], "group": r["entity_group"], "row_kind": r["row_kind"], "mw": none_if_nan(num(r["mw"]), 1),
                         "mw_low": none_if_nan(num(r["mw_low"]), 1), "mw_high": none_if_nan(num(r["mw_high"]), 1),
                         "document_title": r["document_title"], "source_url": r["source_url"], "stage_class": r["stage_class"]})
    rows = sorted(rows, key=lambda x: x["date"], reverse=True)
    return {"table": "large_load_public", "source": "the public documents each row names (filings, statements, presentations)", "how": how,
            "count": len(rows), "rows": rows, **({} if rows else {"why": "large_load_public holds no public row placed in this authority"})}


def write(path, doc):
    text = json.dumps(doc, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    if chr(0x2014) in text:
        raise SystemExit(f"an em dash in {path}")
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return len(text)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-dir", default=SITE)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    os.makedirs(ip.LOG_DIR, exist_ok=True)
    log = ip.Log(os.path.join(ip.LOG_DIR, f"authority_facts_{run_id}.log"))
    index = json.load(open(os.path.join(a.site_dir, "index.json"), encoding="utf-8"))
    names = {b["code"]: b["name"] for b in index["bas"]}
    names.update({r["code"]: r["name"] for r in index["regions"]})
    bas = [b for b in index["bas"] if b.get("us") and b.get("files_eia930")]
    if a.only:
        bas = [b for b in bas if b["code"] in a.only]
    cols = ["plant_id", "name", "state", "operator", "balancing_authority", "technology_group", "capacity_mw", "vintage"]
    op, _ = read_table("eia860m_operating_generators")
    pl, _ = read_table("eia860m_planned_generators")
    rt, _ = read_table("eia860m_retired_generators")
    for t in (op, pl, rt):
        t["mw"] = num(t["capacity_mw"]).fillna(0.0)
        t["technology_group"] = t["technology_group"].replace("", "other")
    vint = vintage_of(op)
    # the twelve complete months: the newest month whose last day is held by the demand files' last hour, and eleven before
    last_hour = max(pd.Timestamp(b["last_hour"]) for b in bas if b.get("last_hour"))
    end = (last_hour + pd.Timedelta(hours=1)).tz_convert("UTC")
    last_month = (end - pd.offsets.MonthBegin(1)).strftime("%Y-%m") if end.day == 1 and end.hour == 0 else (end - pd.offsets.MonthBegin(2)).strftime("%Y-%m")
    first_month = (pd.Timestamp(last_month + "-01") - pd.DateOffset(months=11)).strftime("%Y-%m")
    months = (first_month, last_month)
    log(f"months {months}")
    gen = generation(first_month, last_month, log)
    em, _ = read_table("eia930_all_emissions", usecols=["entity", "variable", "ts_utc", "value"])
    em = em[em["variable"] == "co2_emissions_generated"].copy()
    em["ts"] = pd.to_datetime(em["ts_utc"], utc=True)
    em["value"] = num(em["value"])
    tp, _ = read_table("ba_trade_partners")
    ll, _ = read_table("large_load_public")
    matrix = json.load(open(os.path.join(a.site_dir, "trade_matrix.json"), encoding="utf-8"))
    outdir = os.path.join(a.site_dir, "authority")
    os.makedirs(outdir, exist_ok=True)
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    total = 0
    for b in bas:
        code = b["code"]
        dpath = os.path.join(a.site_dir, "demand", "ba", code.lower() + ".json")
        demand = json.load(open(dpath, encoding="utf-8")) if os.path.exists(dpath) else None
        owns, coming = owns_coming(op, pl, rt, {code}, vint)
        co2 = co2_for(em, gen, code, months) if code in EMISSIONS_BAS else None
        doc = {"built": built, "tables": TABLES, "method": METHOD, "license": "public", "code": code, "name": b["name"], "region": b["region"],
               "level": "ba", "active": b.get("active"), "owns": owns, "coming": coming, "burns": burns_of(gen, {code}, months, co2),
               "trades": trades_ba(tp, code, names), "size": size_of(demand), "large_loads": large_loads_of(ll, {code})}
        total += write(os.path.join(outdir, code.lower() + ".json"), doc)
    if not a.only:
        for r in index["regions"]:
            code = r["code"]
            members = {b["code"] for b in bas if b["region"] == code}
            if not members:
                continue
            dpath = os.path.join(a.site_dir, "demand", code.lower() + ".json")
            demand = json.load(open(dpath, encoding="utf-8")) if os.path.exists(dpath) else None
            tpath = os.path.join(a.site_dir, "trade", code.lower() + ".json")
            trade = json.load(open(tpath, encoding="utf-8")) if os.path.exists(tpath) else None
            owns, coming = owns_coming(op, pl, rt, members, vint)
            doc = {"built": built, "tables": TABLES, "method": METHOD, "license": "public", "code": code, "name": r["name"], "region": code,
                   "level": "region", "bas": sorted(members), "owns": owns, "coming": coming, "burns": burns_of(gen, members, months, None),
                   "trades": trades_region(code, matrix, trade, names), "size": size_of(demand), "large_loads": large_loads_of(ll, members)}
            total += write(os.path.join(outdir, f"region-{code.lower()}.json"), doc)
    n = len(os.listdir(outdir))
    log(f"{n} files under {outdir}, {total:,} bytes")
    log.close()
    print(f"{n} files under {os.path.relpath(outdir, ROOT)}, {total:,} bytes; months {months[0]} to {months[1]}; EIA-860M {vint}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
