"""Session 10205: two more carbon measures for the Grid audit, from files on disk only.

1. Hour against year factors: EIA's hourly CO2 by fuel over the hour's generation by fuel (eia930_all_generation, the
   same hours): if the ratio is one number for a whole period, the "hourly" intensity is the hour's fuel mix times a
   fixed factor per fuel, and no plant's part-load heat rate or which plant ran enters it.
2. Imports' carbon: EIA's CO2 imported over the energy imported (gross, from the grid's own tie reports in
   eia930_all_interchange), and the US48's imports from Canada and Mexico (EIA's region rows), for the hours both hold.

    C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe runs/c710_grid_audit_f.py OUT_DIR
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c710_grid_audit as g  # noqa: E402

CODES = {"US48": "us48", "ERCO": "erco", "PJM": "pjm", "MISO": "miso", "SWPP": "swpp", "ISNE": "isne", "NYIS": "nyis"}
FUEL = {"co2_emissions_natural_gas": "net_generation_natural_gas_mw", "co2_emissions_coal": "net_generation_coal_mw",
        "co2_emissions_oil": "net_generation_oil_mw"}


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "runs/c710_grid"
    res = {"factors": {}, "imports": {}}
    ents = [f"eia930:{c}" for c in CODES]
    em = g.read_table("eia930_all_emissions", ["entity", "variable", "ts_utc", "value"],
                      lambda c: c["entity"].isin(ents) & (c["ts_utc"] >= "2026-10-20") & c["variable"].isin(list(FUEL) + ["co2_emissions_imported"]))
    gen = g.read_table("eia930_all_generation", ["entity", "variable", "ts_utc", "value"],
                       lambda c: c["entity"].isin(ents) & (c["ts_utc"] >= "2026-10-20") & c["variable"].isin(list(FUEL.values())))
    for c in CODES:
        e = f"eia930:{c}"
        res["factors"][c] = {}
        for co2v, genv in FUEL.items():
            a = em[(em["entity"] == e) & (em["variable"] == co2v)].set_index("ts_utc")["value"]
            b = gen[(gen["entity"] == e) & (gen["variable"] == genv)].set_index("ts_utc")["value"]
            j = pd.concat([a.rename("co2"), b.rename("mw")], axis=1).dropna()
            j = j[j["mw"] > 50]
            if len(j) < 24:
                continue
            f = j["co2"] * 1000 / j["mw"]
            res["factors"][c][genv] = {"hours": int(len(j)), "first": str(j.index.min()), "last": str(j.index.max()),
                                       "kg_per_mwh_median": round(float(f.median()), 2), "p05": round(float(f.quantile(0.05)), 2),
                                       "p95": round(float(f.quantile(0.95)), 2), "distinct_to_0p1": int(f.round(1).nunique())}
    # imports: the extract (to 3 October) and the interchange table (from 13 September) overlap 13 September to 2 October
    x = g.read_table("eia930_all_interchange", ["ts_utc", "value", "ba", "x_to_ba"],
                     lambda c: c["ba"].isin([v for v in CODES.values()]) & (c["ts_utc"] < "2026-10-03"))
    for c, code in CODES.items():
        mine = x[x["ba"] == code]
        if c != "US48":
            mine = mine[~mine["x_to_ba"].str.upper().isin(g.REGIONS)]
        gross = mine.assign(imp=(-mine["value"]).clip(lower=0)).groupby("ts_utc")["imp"].sum()
        ex = []
        for ch in pd.read_csv(os.path.join(g.EXTRACT_DIR, f"{code}_hours.csv"), comment="#", chunksize=20_000):
            ch = ch[(ch["ts_utc"] >= "2026-09-13") & (ch["ts_utc"] < "2026-10-03")]
            if len(ch):
                ex.append(ch)
        ex = pd.concat(ex).set_index("ts_utc")
        j = pd.concat([gross.rename("imp_mwh"), ex["co2_emissions_imported"].rename("co2"),
                       (ex["co2_emissions_generated"] * 1000 / ex["net_generation_mwh"]).rename("own")], axis=1).dropna()
        j = j[j["imp_mwh"] > 0]
        res["imports"][c] = {"hours": int(len(j)), "partners": sorted(mine["x_to_ba"].str.upper().unique().tolist()),
                             "imported_co2_per_imported_mwh": round(float(j["co2"].sum() * 1000 / j["imp_mwh"].sum()), 1),
                             "own_generation_intensity_same_hours": round(float((j["own"] * j["imp_mwh"]).sum() / j["imp_mwh"].sum()), 1),
                             "gross_imports_mean_mw": round(float(j["imp_mwh"].mean()), 1)}
    with open(os.path.join(out_dir, "grid_audit_f.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
