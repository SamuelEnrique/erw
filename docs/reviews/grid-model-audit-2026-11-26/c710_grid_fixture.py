"""Session 10205: rows from the main copy's tables (read only) for drawing the Grid tool's Now, Exchange and Clean blocks
to HTML without a build or a database: the newest days of each table the blocks read, for the Lower 48, PJM and the
seven grids. Writes OUT_DIR/fixture.json, {table: [rows]}.

    C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe runs/c710_grid_fixture.py OUT_DIR
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c710_grid_audit as g  # noqa: E402

ENTS = [f"eia930:{c}" for c in g.ISO + ["US48"]]


def newest(df, days):
    if not len(df):
        return df
    cut = (__import__("pandas").Timestamp(df["ts_utc"].max()) - __import__("pandas").Timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    return df[df["ts_utc"] >= cut]


def main():
    out = {}
    cols = ["entity", "variable", "ts_utc", "value"]
    d = g.read_table("eia930_all_demand", cols, lambda c: c["entity"].isin(ENTS) & (c["variable"] == "demand_mw") & (c["ts_utc"] >= "2026-10-25"))
    out["eia930_all_demand"] = newest(d, 9).to_dict("records")
    gn = g.read_table("eia930_all_generation", cols, lambda c: c["entity"].isin(["eia930:US48", "eia930:PJM"]) & (c["ts_utc"] >= "2026-11-01"))
    out["eia930_all_generation"] = gn.to_dict("records")
    ci = g.read_table("carbon_intensity_hourly", cols, lambda c: c["entity"].isin(ENTS) & (c["ts_utc"] >= "2026-10-29"))
    out["carbon_intensity_hourly"] = ci.to_dict("records")
    cm = g.read_table("carbon_intensity_monthly", cols, lambda c: c["entity"].isin(ENTS) & (c["variable"] == "intensity_generation"))
    out["carbon_intensity_monthly"] = cm.to_dict("records")
    with open(os.path.join(sys.argv[1], "fixture.json"), "w", encoding="utf-8") as f:
        json.dump(out, f)
    print({k: len(v) for k, v in out.items()})


if __name__ == "__main__":
    main()
