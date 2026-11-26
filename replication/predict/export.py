"""ERW forecast (predict): the inputs and the expected result of predict_demand.do, for one place and one target day.

Session 10600, chain 730. Writes two files to --out (default runs/predict_replication):
  <place>_days.csv          one row a local day: day, dow (0 Monday to 6 Sunday), hol, bridge, doy, v0 to v23 (the
                            day's demand by local hour, MW, the repeated autumn hour the mean of its two; empty where
                            not held), from the public table eia930_ba_demand_hourly as warehouse/predict/data.py reads it
  <place>_<day>_python.csv  hour, forecast: the regression's forecast for the target day by warehouse/predict/demand.py

    python replication/predict/export.py --place region-tex --day 2026-11-20 [--h 2]

The target day must be held (a day of the backtest), so that the do-file's forecast can be set beside the Python one.
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(ROOT, "warehouse", "predict"))
import predict_data as data  # noqa: E402
import predict_demand as demand  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--place", required=True)
    ap.add_argument("--day", required=True)
    ap.add_argument("--h", type=int, default=2)
    ap.add_argument("--out", default=os.path.join(ROOT, "runs", "predict_replication"))
    a = ap.parse_args(argv)
    os.makedirs(a.out, exist_ok=True)
    ref, _ = data.reference()
    tz = data.place_tz(a.place, ref)
    res = demand.place_forecasts(data.demand_panel()[a.place], tz, h=a.h)
    M = res["M"]
    hol, bri = demand.calendar(M.index)
    days = pd.DataFrame({"day": M.index.strftime("%Y-%m-%d"), "dow": M.index.dayofweek, "hol": hol.astype(int), "bridge": bri.astype(int),
                         "doy": M.index.dayofyear})
    for k in range(24):
        days[f"v{k}"] = M[k].to_numpy()
    p = os.path.join(a.out, f"{a.place}_days.csv")
    days.to_csv(p, index=False, float_format="%.4f")
    i = int(np.flatnonzero(M.index == pd.Timestamp(a.day))[0])
    q = os.path.join(a.out, f"{a.place}_{a.day}_python.csv")
    pd.DataFrame({"hour": range(24), "forecast": res["P"]["regression"][i]}).to_csv(q, index=False, float_format="%.6f")
    print(p)
    print(q)


if __name__ == "__main__":
    main()
