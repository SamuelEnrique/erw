"""Session 10205: the carbon formula restated to the digit on hours EIA did not revise, and what imports' CO2 is worth.

1. September 2026, the Lower 48 and the seven grids: the 4 October extract's CO2 and denominators against
   carbon_intensity_hourly (built from the 5 November extract) and eia930_all_emissions (the same 5 November vintage).
   Where the extract's CO2 equals the table's to the tonne's last digit, the denominator is the only input that could
   have moved; an hour whose intensity then differs is a denominator EIA revised.
2. Over October 2025 to September 2026 (the extract): EIA's imported CO2 over demand, kg per MWh used: how far the "of
   demand" intensity would fall if every import carried no CO2 (a bound), per grid.

    C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe runs/c710_grid_audit_h.py OUT_DIR
"""
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c710_grid_audit as g  # noqa: E402

CODES = ["us48", "erco", "pjm", "miso", "swpp", "isne", "nyis"]


def extract(code, lo, hi):
    out = []
    for ch in pd.read_csv(os.path.join(g.EXTRACT_DIR, f"{code}_hours.csv"), comment="#", chunksize=20_000):
        ch = ch[(ch["ts_utc"] >= lo) & (ch["ts_utc"] < hi)]
        if len(ch):
            out.append(ch)
    return pd.concat(out)


def main():
    out_dir = sys.argv[1]
    res = {"restated": {}, "imports_bound": {}}
    ents = [f"eia930:{c.upper()}" for c in CODES]
    ci = g.read_table("carbon_intensity_hourly", ["entity", "variable", "ts_utc", "value"],
                      lambda c: c["entity"].isin(ents) & (c["ts_utc"] >= "2026-09-01") & (c["ts_utc"] < "2026-10-01"))
    em = g.read_table("eia930_all_emissions", ["entity", "variable", "ts_utc", "value"],
                      lambda c: c["entity"].isin(ents) & (c["ts_utc"] >= "2026-09-01") & (c["ts_utc"] < "2026-10-01")
                      & c["variable"].isin(["co2_emissions_generated", "co2_emissions_consumed"]))
    for code in CODES:
        e = f"eia930:{code.upper()}"
        x = extract(code, "2026-09-01", "2026-10-01").set_index("ts_utc")
        row = {}
        for var, co2, den in (("intensity_generation", "co2_emissions_generated", "net_generation_mwh"),
                              ("intensity_demand", "co2_emissions_consumed", "demand_mwh")):
            t = ci[(ci["entity"] == e) & (ci["variable"] == var)].set_index("ts_utc")["value"]
            m = em[(em["entity"] == e) & (em["variable"] == co2)].set_index("ts_utc")["value"]
            j = pd.concat([t.rename("table"), m.rename("co2_table"), x[co2].rename("co2_x"), x[den].rename("den_x")], axis=1).dropna()
            j = j[j["den_x"] > 0]
            same = j[(j["co2_table"] - j["co2_x"]).abs() < 1e-9]
            r = (same["co2_x"] * 1000 / same["den_x"]).round(4)
            row[var] = {"hours": int(len(j)), "co2_unrevised_hours": int(len(same)),
                        "equal_to_4dp_of_those": int(((r - same["table"]).abs() < 0.00005).sum()),
                        "max_abs_diff_of_those": round(float((r - same["table"]).abs().max()), 4) if len(same) else None}
        res["restated"][code] = row
        y = extract(code, "2025-10-01", "2026-10-01").dropna(subset=["co2_emissions_imported", "demand_mwh", "co2_emissions_consumed"])
        y = y[y["demand_mwh"] > 0]
        res["imports_bound"][code] = {"hours": int(len(y)),
                                      "of_demand_kg_per_mwh": round(float(y["co2_emissions_consumed"].sum() * 1000 / y["demand_mwh"].sum()), 1),
                                      "imported_co2_per_mwh_demand": round(float(y["co2_emissions_imported"].sum() * 1000 / y["demand_mwh"].sum()), 1),
                                      "imported_share_of_consumed_pct": round(float(y["co2_emissions_imported"].sum() / y["co2_emissions_consumed"].sum() * 100), 1)}
    with open(os.path.join(out_dir, "grid_audit_h.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
