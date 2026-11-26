"""Session 10205: the MISO-SPP tie's two reports, day by day (eia930_all_interchange), in MISO's direction.

    C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe runs/c710_grid_audit_k.py OUT_DIR
"""
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import c710_grid_audit as g  # noqa: E402


def main():
    out_dir = sys.argv[1]
    x = g.read_table("eia930_all_interchange", ["ts_utc", "value", "ba", "x_to_ba"],
                     lambda c: ((c["ba"] == "miso") & (c["x_to_ba"] == "swpp")) | ((c["ba"] == "swpp") & (c["x_to_ba"] == "miso")))
    x["miso_dir"] = x["value"].where(x["ba"] == "miso", -x["value"])
    p = x.pivot_table(index="ts_utc", columns="ba", values="miso_dir", aggfunc="first")
    p["day"] = p.index.str[:10]
    d = p.groupby("day").agg(miso=("miso", "mean"), swpp=("swpp", "mean"), n_miso=("miso", "count"), n_swpp=("swpp", "count"))
    d.round(1).to_csv(os.path.join(out_dir, "miso_swpp_by_day.csv"))
    print(d.round(1).to_string())


if __name__ == "__main__":
    main()
