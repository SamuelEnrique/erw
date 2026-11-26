"""Session 10205 (chain 710, part D): the Grid tool's figures restated from the page's own files, with none of the
site's code, then one rule changed at a time. Reads only files on disk: the worktree's site/data/grid_network.json and
the main copy's warehouse/output tables (read only, never written). No network request, no model call.

    C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe runs/c710_grid_audit.py OUT_DIR

Writes OUT_DIR/grid_audit.json and prints a summary.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

WT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_OUT = "C:/Users/lossa/Documents/erw/warehouse/output"
EXTRACT_DIR = "C:/Users/lossa/Documents/erw/warehouse/raw/eia930_emissions/20261004T021545Z"
SNAP = os.path.join(WT, "site", "data", "grid_network.json")
ISO = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"]
REGIONS = {"CAL", "CAR", "CENT", "FLA", "MIDA", "MIDW", "NE", "NY", "NW", "SE", "SW", "TEN", "TEX", "US48", "CAN", "MEX"}
H = pd.Timedelta(hours=1)
res = {}


def skip_rows(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return n


def read_table(name, usecols, keep, chunks=400_000):
    """A table read in chunks, keeping only the rows keep(df) selects (memory: about 1 GB free on this machine)."""
    path = os.path.join(MAIN_OUT, name + ".csv")
    out = []
    for c in pd.read_csv(path, skiprows=skip_rows(path), usecols=usecols, chunksize=chunks):
        c = c[keep(c)]
        if len(c):
            out.append(c)
    return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=usecols)


# ------------------------------------------------------------------ A. the default view: /grid (the Lower 48, Mix tab), the Now blocks
def part_a():
    a = {}
    dem = read_table("eia930_all_demand", ["entity", "variable", "ts_utc", "value"],
                     lambda c: (c["entity"] == "eia930:US48") & (c["variable"] == "demand_mw"))
    dem = dem.sort_values("ts_utc")
    d = dem.iloc[-1]
    wk = (pd.Timestamp(d["ts_utc"]) - 7 * 24 * H).strftime("%Y-%m-%dT%H:%M:%SZ")
    dw = dem[dem["ts_utc"] == wk]
    a["demand"] = {"hour": d["ts_utc"], "mw": float(d["value"]), "week_earlier_hour": wk,
                   "week_earlier_mw": float(dw["value"].iloc[0]) if len(dw) else None}
    gen = read_table("eia930_all_generation", ["entity", "variable", "ts_utc", "value"], lambda c: c["entity"] == "eia930:US48")
    tot = gen[gen["variable"] == "net_generation_mw"].sort_values("ts_utc").iloc[-1]
    fu = gen[(gen["ts_utc"] == tot["ts_utc"]) & (gen["variable"] != "net_generation_mw") & gen["variable"].str.startswith("net_generation_")]
    fu = fu.sort_values("value", ascending=False)
    a["generation"] = {"hour": tot["ts_utc"], "total_mw": float(tot["value"]),
                       "fuels": {r.variable: float(r.value) for r in fu.itertuples()},
                       "sum_of_fuels_mw": float(fu["value"].sum())}
    ci = read_table("carbon_intensity_hourly", ["entity", "variable", "ts_utc", "value"],
                    lambda c: (c["entity"] == "eia930:US48") & (c["ts_utc"] >= "2025-10-01"))
    cg = ci[ci["variable"] == "intensity_generation"].sort_values("ts_utc").iloc[-1]
    cd = ci[(ci["variable"] == "intensity_demand") & (ci["ts_utc"] == cg["ts_utc"])]
    a["carbon"] = {"hour": cg["ts_utc"], "of_generation": float(cg["value"]), "of_demand": float(cd["value"].iloc[0]) if len(cd) else None}
    # independent restatement of the carbon hour: EIA's CO2 (eia930_all_emissions) over a denominator. The workbook's own
    # denominator for 2 November is in an extract this machine does not hold (20261105T...); the API's net generation and
    # demand (eia930_all_generation, eia930_all_demand) are session 32's denominators: the one rule changed.
    h = cg["ts_utc"]
    em = read_table("eia930_all_emissions", ["entity", "variable", "ts_utc", "value"],
                    lambda c: (c["entity"] == "eia930:US48") & (c["ts_utc"] >= "2026-10-20"))
    co2g = em[(em["variable"] == "co2_emissions_generated") & (em["ts_utc"] == h)]["value"]
    co2c = em[(em["variable"] == "co2_emissions_consumed") & (em["ts_utc"] == h)]["value"]
    ng = gen[(gen["variable"] == "net_generation_mw") & (gen["ts_utc"] == h)]["value"]
    dd = dem[dem["ts_utc"] == h]["value"]
    a["carbon_restated_api_denominators"] = {
        "co2_generated_t": float(co2g.iloc[0]) if len(co2g) else None, "co2_consumed_t": float(co2c.iloc[0]) if len(co2c) else None,
        "api_net_generation_mw": float(ng.iloc[0]) if len(ng) else None, "api_demand_mw": float(dd.iloc[0]) if len(dd) else None}
    r = a["carbon_restated_api_denominators"]
    if r["co2_generated_t"] and r["api_net_generation_mw"]:
        r["of_generation"] = round(r["co2_generated_t"] * 1000 / r["api_net_generation_mw"], 4)
        r["implied_workbook_net_generation_mwh"] = round(r["co2_generated_t"] * 1000 / a["carbon"]["of_generation"], 1)
    if r["co2_consumed_t"] and r["api_demand_mw"]:
        r["of_demand"] = round(r["co2_consumed_t"] * 1000 / r["api_demand_mw"], 4)
        r["implied_workbook_demand_mwh"] = round(r["co2_consumed_t"] * 1000 / a["carbon"]["of_demand"], 1)
    # the same table of emissions over the whole 2 weeks: how far the API denominators move the figure, hour by hour
    ngs = gen[gen["variable"] == "net_generation_mw"].set_index("ts_utc")["value"]
    g2 = em[em["variable"] == "co2_emissions_generated"].set_index("ts_utc")["value"]
    j = pd.concat([g2.rename("co2"), ngs.rename("ng"), ci[ci["variable"] == "intensity_generation"].set_index("ts_utc")["value"].rename("ci")], axis=1).dropna()
    j["alt"] = j["co2"] * 1000 / j["ng"]
    a["api_denominator_vs_table_hours"] = {"hours": int(len(j)), "mean_abs_diff": round(float((j["alt"] - j["ci"]).abs().mean()), 4),
                                         "max_abs_diff": round(float((j["alt"] - j["ci"]).abs().max()), 4),
                                         "first": str(j.index.min()), "last": str(j.index.max())}
    # restatement to the digit where the inputs are the same vintage: the Oct 4 extract (workbook denominators) over its
    # hours, against the table (built from the 5 November extract): equal where EIA did not revise
    x = pd.read_csv(os.path.join(EXTRACT_DIR, "us48_hours.csv"), comment="#")
    x = x[(x["ts_utc"] >= "2026-09-01") & (x["ts_utc"] < "2026-10-03")]
    ci2 = read_table("carbon_intensity_hourly", ["entity", "variable", "ts_utc", "value"],
                     lambda c: (c["entity"] == "eia930:US48") & (c["ts_utc"] >= "2026-09-01") & (c["ts_utc"] < "2026-10-03"))
    k = x.merge(ci2[ci2["variable"] == "intensity_generation"][["ts_utc", "value"]].rename(columns={"value": "g"}), on="ts_utc") \
        .merge(ci2[ci2["variable"] == "intensity_demand"][["ts_utc", "value"]].rename(columns={"value": "d"}), on="ts_utc")
    k["g2"] = (k["co2_emissions_generated"] * 1000 / k["net_generation_mwh"]).round(4)
    k["d2"] = (k["co2_emissions_consumed"] * 1000 / k["demand_mwh"]).round(4)
    a["extract_restatement_sep2026"] = {"hours": int(len(k)), "generation_equal_to_4dp": int((k["g2"] - k["g"]).abs().lt(0.00005).sum()),
                                        "demand_equal_to_4dp": int((k["d2"] - k["d"]).abs().lt(0.00005).sum()),
                                        "max_abs_diff_generation": round(float((k["g2"] - k["g"]).abs().max()), 4),
                                        "max_abs_diff_demand": round(float((k["d2"] - k["d"]).abs().max()), 4)}
    return a


# ------------------------------------------------------------------ B. the snapshot: the exchange figures, restated
def complete_hour(hours, links, quiet=48):
    n = len(hours)
    def last(l):
        for h in range(n - 1, -1, -1):
            if l["mw"][h] is not None:
                return h
        return -1
    reporting = [l for l in links if last(l) >= n - quiet]
    for h in range(n - 1, -1, -1):
        if reporting and all(l["mw"][h] is not None for l in reporting):
            return h, len(reporting)
    return -1, len(reporting)


def part_b():
    s = json.load(open(SNAP, encoding="utf-8"))
    hours, links = s["hours"], s["links"]
    idx, reporting = complete_hour(hours, links)
    hour = hours[idx]
    net, ties, maxflow = {}, {}, {}
    for l in links:
        v = l["mw"][idx]
        if v is None:
            continue
        for me, sign in ((l["a"], 1), (l["b"], -1)):
            net[me] = net.get(me, 0) + sign * v
            ties[me] = ties.get(me, 0) + 1
            maxflow[me] = max(maxflow.get(me, 0), abs(v))
    top = sorted(net.items(), key=lambda kv: (-kv[1], kv[0]))[0]
    lag = round((pd.Timestamp(s["built"]) - pd.Timestamp(hour)) / H)
    b = {"built": s["built"], "hours": [hours[0], hours[-1]], "complete_hour": hour, "complete_index": idx, "pairs": len(links),
         "reporting_pairs": reporting, "lag_hours_vs_refresh": lag,
         "isos": {c: {"net_export_mw": round(net.get(c, 0), 1), "ties": ties.get(c, 0), "max_flow_mw": maxflow.get(c)} for c in ISO},
         "top_exporter": {"id": top[0], "mw": top[1]}, "nodes": len(s["nodes"])}
    # one rule changed: the newest hour of the snapshot, whatever reported
    n = len(hours) - 1
    b["newest_hour"] = {"hour": hours[n], "pairs_reporting": sum(1 for l in links if l["mw"][n] is not None)}
    # sum of the seven at the complete hour, and what the Lower 48's own exchange would be (ties to CAN and MEX nodes)
    b["sum_of_seven_net_export_mw"] = round(sum(net.get(c, 0) for c in ISO), 1)
    # nodes of Canada and Mexico in the snapshot (names hold the country words)
    foreign = [n_["id"] for n_ in s["nodes"] if any(w in (n_.get("name") or "") for w in ("Canada", "Mexico", "Ontario", "Quebec", "Hydro", "Alberta", "Manitoba", "Brunswick", "Saskatchewan", "British Columbia", "Centro Nacional", "Comision"))]
    b["foreign_nodes_by_name"] = foreign
    # node demand: which nodes carry it
    b["nodes_with_demand"] = [n_["id"] for n_ in s["nodes"] if n_.get("demand_mw") is not None]
    return b, s


# ------------------------------------------------------------------ C. how interchange is netted: four rules over the table's hours
def part_c():
    x = read_table("eia930_all_interchange", ["ts_utc", "value", "ba", "x_to_ba"], lambda c: c["value"].notna())
    x["a"], x["b"] = x["ba"].str.upper(), x["x_to_ba"].str.upper()
    allx = x
    x = x[~x["a"].isin(REGIONS) & ~x["b"].isin(REGIONS)].copy()
    c = {"hours": [str(x["ts_utc"].min()), str(x["ts_utc"].max())], "reports": int(len(x))}
    # each tie, both sides, in the first-code direction
    x["first"] = np.where(x["a"] < x["b"], x["a"], x["b"])
    x["second"] = np.where(x["a"] < x["b"], x["b"], x["a"])
    x["flow"] = np.where(x["a"] < x["b"], x["value"], -x["value"])
    x["by_first"] = x["a"] < x["b"]
    x = x.drop_duplicates(["first", "second", "ts_utc", "by_first"], keep="last")
    p = x.pivot_table(index=["first", "second", "ts_utc"], columns="by_first", values="flow", aggfunc="first")
    p.columns = ["second_report" if not k else "first_report" for k in p.columns]
    p = p.reset_index()
    p["rule"] = p["first_report"].where(p["first_report"].notna(), p["second_report"])  # the page's pair rule
    p["mean2"] = p[["first_report", "second_report"]].mean(axis=1)                      # interchange_pairs.py's rule
    both = p.dropna(subset=["first_report", "second_report"])
    c["pair_hours"] = int(len(p))
    c["pair_hours_both"] = int(len(both))
    gap = (both["first_report"] - both["second_report"]).abs()
    c["gap_both_reported"] = {"mean_abs_mw": round(float(gap.mean()), 2), "median": round(float(gap.median()), 2),
                              "p95": round(float(gap.quantile(0.95)), 1), "share_over_10mw_pct": round(float((gap > 10).mean() * 100), 2),
                              "sign_disagrees_pct": round(float(((both["first_report"] * both["second_report"]) < 0).mean() * 100), 2)}
    per = {}
    for iso in ISO:
        mine = p[(p["first"] == iso) | (p["second"] == iso)].copy()
        sgn = np.where(mine["first"] == iso, 1, -1)
        mine["own"] = sgn * np.where(mine["first"] == iso, mine["first_report"], mine["second_report"])
        mine["nbr"] = sgn * np.where(mine["first"] == iso, mine["second_report"], mine["first_report"])
        mine["rule_s"] = sgn * mine["rule"]
        mine["mean_s"] = sgn * mine["mean2"]
        # how many of its ties the rule reads from the neighbour (the neighbour's code sorts first)
        ties = mine.groupby(["first", "second"]).size()
        read_from_nbr = sorted({(a if a != iso else b) for (a, b) in ties.index if a != iso})
        g = mine.groupby("ts_utc")
        t = pd.DataFrame({"rule": g["rule_s"].sum(), "own": g["own"].sum(min_count=1), "mean": g["mean_s"].sum(),
                          "own_all": g["own"].apply(lambda s: s.notna().all())})
        t = t[t["own_all"]]  # hours where the grid reported every tie it has a report on
        d_own = (t["rule"] - t["own"])
        d_mean = (t["rule"] - t["mean"])
        per[iso] = {"ties": int(len(ties)), "ties_read_from_neighbour": read_from_nbr, "hours_compared": int(len(t)),
                    "rule_minus_own_mean_abs_mw": round(float(d_own.abs().mean()), 1), "rule_minus_own_max_abs_mw": round(float(d_own.abs().max()), 1),
                    "rule_minus_own_mean_mw": round(float(d_own.mean()), 1),
                    "rule_minus_mean2_mean_abs_mw": round(float(d_mean.abs().mean()), 1),
                    "sign_differs_rule_vs_own_hours": int(((t["rule"] * t["own"]) < 0).sum()),
                    "mean_abs_net_rule_mw": round(float(t["rule"].abs().mean()), 1)}
    c["per_iso"] = per
    # D. the Lower 48's own exchange, as EIA's region rows give it (US48 with CAN and MEX), against the seven grids' sum
    us = allx[(allx["a"] == "US48")]
    c["us48_rows_partners"] = sorted(us["b"].unique().tolist())
    usn = us.groupby("ts_utc")["value"].sum()
    seven = {}
    for iso in ISO:
        mine = p[(p["first"] == iso) | (p["second"] == iso)]
        sgn = np.where(mine["first"] == iso, 1, -1)
        seven[iso] = pd.Series(sgn * mine["rule"].values, index=mine["ts_utc"].values).groupby(level=0).sum()
    s7 = pd.concat(seven, axis=1).dropna().sum(axis=1)
    j = pd.concat([usn.rename("us48"), s7.rename("seven")], axis=1).dropna()
    c["us48_vs_seven"] = {"hours": int(len(j)), "us48_net_export_mean_mw": round(float(j["us48"].mean()), 1),
                          "seven_sum_net_export_mean_mw": round(float(j["seven"].mean()), 1),
                          "mean_abs_diff_mw": round(float((j["us48"] - j["seven"]).abs().mean()), 1),
                          "sign_differs_hours": int(((j["us48"] * j["seven"]) < 0).sum())}
    return c


# ------------------------------------------------------------------ the seven grids' share of the Lower 48's demand
def part_share():
    dem = read_table("eia930_all_demand", ["entity", "variable", "ts_utc", "value"],
                     lambda c: (c["variable"] == "demand_mw") & (c["ts_utc"] >= "2025-11-01") & (c["ts_utc"] < "2026-11-01"))
    p = dem.pivot_table(index="ts_utc", columns="entity", values="value", aggfunc="first").dropna()
    seven = p[[f"eia930:{c}" for c in ISO]].sum(axis=1)
    sh = seven / p["eia930:US48"] * 100
    return {"hours": int(len(p)), "first": str(p.index.min()), "last": str(p.index.max()), "seven_share_of_us48_demand_pct_mean": round(float(sh.mean()), 2),
            "min": round(float(sh.min()), 2), "max": round(float(sh.max()), 2)}


# ------------------------------------------------------------------ E. average against marginal carbon, and F. imports' carbon
def part_e():
    out = {}
    for code in ["us48", "erco", "pjm", "miso", "swpp"]:
        x = []
        for ch in pd.read_csv(os.path.join(EXTRACT_DIR, f"{code}_hours.csv"), comment="#", chunksize=20_000):
            ch = ch[(ch["ts_utc"] >= "2025-10-01") & (ch["ts_utc"] < "2026-10-01")]
            if len(ch):
                x.append(ch)
        x = pd.concat(x).sort_values("ts_utc").reset_index(drop=True)
        x["t"] = pd.to_datetime(x["ts_utc"], utc=True)
        x = x.dropna(subset=["co2_emissions_generated", "net_generation_mwh", "demand_mwh"])
        avg = x["co2_emissions_generated"].sum() * 1000 / x["net_generation_mwh"].sum()
        # Siler-Evans style marginal factor: hour-on-hour change in CO2 against change in generation (and in demand), consecutive hours only
        dx = x.drop(columns=["ts_utc"]).diff()
        ok = dx["t"] == pd.Timedelta(hours=1)
        dco2 = dx.loc[ok, "co2_emissions_generated"] * 1000
        dg = dx.loc[ok, "net_generation_mwh"]
        dd = dx.loc[ok, "demand_mwh"]
        bg = float(np.polyfit(dg, dco2, 1)[0])
        bd = float(np.polyfit(dd, dco2, 1)[0])
        # standard error of the slope (OLS, independent errors assumed; hours follow one another, so a lower bound)
        res_ = dco2 - np.polyval(np.polyfit(dg, dco2, 1), dg)
        se = float(np.sqrt((res_ ** 2).sum() / (len(dg) - 2) / ((dg - dg.mean()) ** 2).sum()))
        # imports' carbon: EIA's CO2 imported over the energy imported; the energy is net interchange (demand less
        # generation, the workbook's own) where positive: a floor on gross imports, so the ratio is a ceiling
        ni = (x["demand_mwh"] - x["net_generation_mwh"]).clip(lower=0)
        imp = x["co2_emissions_imported"].fillna(0) * 1000
        sel = ni > 100
        out[code] = {"hours": int(len(x)), "first": x["ts_utc"].iloc[0], "last": x["ts_utc"].iloc[-1],
                     "average_kg_per_mwh": round(float(avg), 1), "marginal_vs_generation_kg_per_mwh": round(bg, 1), "marginal_se_iid": round(se, 1),
                     "marginal_vs_demand_kg_per_mwh": round(bd, 1), "marginal_over_average": round(bg / avg, 3),
                     "co2_imported_total_kt": round(float(imp.sum() / 1e6), 1),
                     "imported_co2_per_net_import_mwh_ceiling": round(float(imp[sel].sum() / ni[sel].sum()), 1) if sel.any() else None,
                     "hours_with_imported_co2": int((x["co2_emissions_imported"].fillna(0) > 0).sum()),
                     "consumed_identity_max_abs_t": round(float((x["co2_emissions_consumed"] - (x["co2_emissions_generated"] + x["co2_emissions_imported"].fillna(0) - x["co2_emissions_exported"].fillna(0))).abs().max()), 3),
                     "demand_vs_generation_intensity_mean": round(float((x["co2_emissions_consumed"].sum() * 1000 / x["demand_mwh"].sum()) - avg), 1)}
    return out


# ------------------------------------------------------------------ G. how stale "now" is: each table's newest hour against its retrieval
def part_g(snap):
    g = {}
    for name, ent, var in (("eia930_all_demand", "eia930:US48", "demand_mw"), ("eia930_all_generation", "eia930:US48", "net_generation_mw"),
                           ("carbon_intensity_hourly", "eia930:US48", "intensity_generation"), ("eia930_all_interchange", None, None)):
        path = os.path.join(MAIN_OUT, name + ".csv")
        ret = None
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.startswith("#"):
                    break
                if "Retrieved: " in line and ret is None:
                    ret = line.split("Retrieved: ")[1][:16]
        g[name] = {"retrieved": ret}
    g["snapshot"] = {"built": snap["built"], "newest_hour": snap["hours"][-1]}
    return g


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WT, "runs", "c710_grid")
    os.makedirs(out, exist_ok=True)
    res["A_default_view_us48"] = part_a()
    print("A done", flush=True)
    b, snap = part_b()
    res["B_snapshot"] = b
    print("B done", flush=True)
    res["C_netting"] = part_c()
    print("C done", flush=True)
    res["D_seven_share"] = part_share()
    print("D done", flush=True)
    res["E_marginal_imports"] = part_e()
    print("E done", flush=True)
    res["G_staleness"] = part_g(snap)
    with open(os.path.join(out, "grid_audit.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    print(json.dumps(res, indent=1, default=str))


if __name__ == "__main__":
    main()
