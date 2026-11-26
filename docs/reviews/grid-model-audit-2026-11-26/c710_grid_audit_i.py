"""Session 10205: each tie of the seven grids, its two sides' reports compared (eia930_all_interchange, the hours the
table holds), and the newest hour of carbon intensity per grid (the hour the "now, ranked" table shows for each).

    C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe runs/c710_grid_audit_i.py OUT_DIR
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
    res = {"ties": [], "carbon_newest": {}}
    x = g.read_table("eia930_all_interchange", ["ts_utc", "value", "ba", "x_to_ba"], lambda c: c["value"].notna())
    x["a"], x["b"] = x["ba"].str.upper(), x["x_to_ba"].str.upper()
    x = x[~x["a"].isin(g.REGIONS) & ~x["b"].isin(g.REGIONS)]
    x = x[x["a"].isin(g.ISO) | x["b"].isin(g.ISO)].copy()
    x["first"] = np.where(x["a"] < x["b"], x["a"], x["b"])
    x["second"] = np.where(x["a"] < x["b"], x["b"], x["a"])
    x["flow"] = np.where(x["a"] < x["b"], x["value"], -x["value"])
    x["side"] = np.where(x["a"] < x["b"], "rf", "rs")
    p = x.pivot_table(index=["first", "second", "ts_utc"], columns="side", values="flow", aggfunc="first").reset_index()
    for (a, b), t in p.groupby(["first", "second"]):
        both = t.dropna(subset=["rf", "rs"]) if "rs" in t and "rf" in t else t.iloc[0:0]
        gap = (both["rf"] - both["rs"]) if len(both) else pd.Series(dtype=float)
        res["ties"].append({"tie": f"{a}-{b}", "hours_first": int(t["rf"].notna().sum()) if "rf" in t else 0,
                            "hours_second": int(t["rs"].notna().sum()) if "rs" in t else 0, "hours_both": int(len(both)),
                            "mean_first_mw": round(float(t["rf"].mean()), 1) if "rf" in t and t["rf"].notna().any() else None,
                            "mean_second_mw": round(float(t["rs"].mean()), 1) if "rs" in t and t["rs"].notna().any() else None,
                            "mean_abs_gap_mw": round(float(gap.abs().mean()), 1) if len(gap) else None,
                            "sign_disagrees_hours": int(((both["rf"] * both["rs"]) < 0).sum()) if len(both) else 0})
    res["ties"].sort(key=lambda r: -(r["mean_abs_gap_mw"] or 0))
    ci = g.read_table("carbon_intensity_hourly", ["entity", "variable", "ts_utc"],
                      lambda c: (c["variable"] == "intensity_generation") & (c["ts_utc"] >= "2026-10-15"))
    res["carbon_newest"] = ci.groupby("entity")["ts_utc"].max().to_dict()
    with open(os.path.join(out_dir, "grid_audit_i.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    for r in res["ties"][:25]:
        print(r)
    print(res["carbon_newest"])


if __name__ == "__main__":
    main()
