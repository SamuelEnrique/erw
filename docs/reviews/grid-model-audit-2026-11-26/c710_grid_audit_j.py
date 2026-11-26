"""Session 10205: each of the seven grids' net export hour by hour under two rules, over the hours eia930_all_interchange
holds: the page's pair rule (each tie read from the authority whose code sorts first, else the other's turned) and
"own first" (each tie read from the grid's own report, else the neighbour's turned). Every hour with a report on every
tie the grid has in the window. Also the same at the snapshot's rule over the region view's rule (the mean of the two
where both reported).

    C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe runs/c710_grid_audit_j.py OUT_DIR
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c710_grid_audit as g  # noqa: E402


def main():
    out_dir = sys.argv[1]
    x = g.read_table("eia930_all_interchange", ["ts_utc", "value", "ba", "x_to_ba"], lambda c: c["value"].notna())
    x["a"], x["b"] = x["ba"].str.upper(), x["x_to_ba"].str.upper()
    x = x[~x["a"].isin(g.REGIONS) & ~x["b"].isin(g.REGIONS)]
    # session 10205: reports no tie can carry (above 20,000 MW either way): counted, and which the page's rule would read
    big = x[x["value"].abs() > 20000].copy()
    big["read_by_page_rule"] = big["a"] < big["b"]
    res = {"_reports_over_20000_mw": {"n": int(len(big)), "read_by_page_rule": int(big["read_by_page_rule"].sum()),
                                      "by_reporter": big.groupby(["a", "b"]).size().rename("n").reset_index().to_dict("records")}}
    screened = "--screen" in sys.argv
    if screened:
        x = x[x["value"].abs() <= 20000]
    for iso in g.ISO:
        m = x[(x["a"] == iso) | (x["b"] == iso)].copy()
        m["other"] = np.where(m["a"] == iso, m["b"], m["a"])
        m["exp"] = np.where(m["a"] == iso, m["value"], -m["value"])   # export from the grid's side
        m["own"] = m["a"] == iso
        p = m.pivot_table(index=["other", "ts_utc"], columns="own", values="exp", aggfunc="first")
        p.columns = ["nbr" if not k else "own" for k in p.columns]
        p = p.reset_index()
        if "nbr" not in p:
            p["nbr"] = np.nan
        p["first_is_grid"] = iso < p["other"]
        p["page"] = np.where(p["first_is_grid"], p["own"].where(p["own"].notna(), p["nbr"]), p["nbr"].where(p["nbr"].notna(), p["own"]))
        p["ownfirst"] = p["own"].where(p["own"].notna(), p["nbr"])
        p["mean2"] = p[["own", "nbr"]].mean(axis=1)
        n_ties = p["other"].nunique()
        h = p.groupby("ts_utc").agg(page=("page", "sum"), ownfirst=("ownfirst", "sum"), mean2=("mean2", "sum"), n=("other", "nunique"))
        h = h[h["n"] == n_ties]
        d = h["page"] - h["ownfirst"]
        res[iso] = {"ties": int(n_ties), "hours": int(len(h)),
                    "page_rule_mean_net_export_mw": round(float(h["page"].mean()), 1),
                    "own_first_mean_net_export_mw": round(float(h["ownfirst"].mean()), 1),
                    "mean_of_two_mean_net_export_mw": round(float(h["mean2"].mean()), 1),
                    "page_minus_own_first_mean_abs_mw": round(float(d.abs().mean()), 1), "page_minus_own_first_median_abs_mw": round(float(d.abs().median()), 1), "page_minus_own_first_mean_mw": round(float(d.mean()), 1),
                    "page_minus_own_first_max_abs_mw": round(float(d.abs().max()), 1),
                    "sign_differs_hours": int(((h["page"] * h["ownfirst"]) < 0).sum()),
                    "page_minus_mean2_mean_abs_mw": round(float((h["page"] - h["mean2"]).abs().mean()), 1), "page_minus_mean2_median_abs_mw": round(float((h["page"] - h["mean2"]).abs().median()), 1)}
    with open(os.path.join(out_dir, "grid_audit_j_screened.json" if screened else "grid_audit_j.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
