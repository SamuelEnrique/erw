#!/usr/bin/env python3
"""California's EIA-930 hours against CAISO's own: where the one-hour difference comes from (session 82).

Energy Research Warehouse (ERW). Session 80 found that California's average day from EIA-930, before the break of 16
December 2025, sits one hour later than CAISO's own. This reads EIA's CISO workbook as it is (the newest under
warehouse/raw/eia930_emissions/, sheet Published Hourly Data) and CAISO's own supply by fuel (caiso_fuel_supply), and
measures, with no assumption about the cause:

    1. what the workbook itself says about time: its time columns, and the gap between its "UTC time" and its local
       time, before and after the break;
    2. hour by hour, the shift at which EIA's solar best matches CAISO's solar, for each month from June 2025 (the
       ERW's reading of an hour: EIA's "UTC time" less one hour, the hour's start);
    3. the same for wind, and for demand against the sum of CAISO's sources;
    4. the hours around the break itself, side by side.

    python warehouse/analysis/caiso_hour_offset.py      # prints; writes runs/session82/caiso_hour_offset.csv

No request; nothing in warehouse/output.
"""

import glob
import os
import sys
from datetime import timedelta

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
import caiso_join as cj  # noqa: E402

RAW = os.path.join(ROOT, "warehouse", "raw", "eia930_emissions")
OUT = os.path.join(ROOT, "runs", "session82")
KEEP = ["UTC time", "Local date", "Hour", "Local time", "Time zone", "Demand", "Adjusted demand", "Net generation", "Adjusted SUN Gen",
        "Adjusted WND Gen", "Adjusted NG Gen", "Total interchange"]


def workbook(ba="CISO"):
    files = [f for f in glob.glob(os.path.join(RAW, "*", f"*_{ba}.xlsx")) if os.path.getsize(f) > 0]
    if not files:
        raise FileNotFoundError(f"no {ba} workbook under {RAW}")
    return max(files, key=lambda f: (os.path.basename(os.path.dirname(f)), os.path.basename(f)))


def read(path, since="2025-05-25"):
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["Published Hourly Data"]
    rows = ws.iter_rows(values_only=True)
    head = list(next(rows))
    idx = {k: head.index(k) for k in KEEP if k in head}
    t = head.index("UTC time")
    out = []
    for r in rows:
        if r[t] is None or str(r[t])[:10] < since:
            continue
        out.append({k: r[i] for k, i in idx.items()})
    return head, pd.DataFrame(out)


def best_shift(a, b, shifts=(-2, -1, 0, 1, 2)):
    """The shift (hours) of series a at which it correlates best with b: a positive shift means a is late (a's value at
    hour h belongs to hour h - shift). Both indexed by hour start, UTC."""
    res = {}
    for s in shifts:
        x = a.copy()
        x.index = x.index - pd.Timedelta(hours=s)
        j = pd.concat([x, b], axis=1, join="inner").dropna()
        res[s] = float(j.corr().iloc[0, 1]) if len(j) > 48 else np.nan
    return max(res, key=lambda k: -1 if np.isnan(res[k]) else res[k]), res


def main():
    os.makedirs(OUT, exist_ok=True)
    path = workbook()
    head, w = read(path)
    print(f"workbook: {os.path.relpath(path, ROOT)}; {len(head)} columns; time columns: {[h for h in head if h and ('time' in str(h).lower() or 'date' in str(h).lower() or str(h) == 'Hour')]}")
    w["utc_end"] = pd.to_datetime(w["UTC time"], utc=True)
    w["start"] = w["utc_end"] - timedelta(hours=1)          # the ERW's reading: the hour's start
    if "Local time" in w:
        loc = pd.to_datetime(w["Local time"])
        w["utc_less_local_h"] = (w["utc_end"].dt.tz_localize(None) - loc).dt.total_seconds() / 3600
        # what the gap should be if "Local time" is Pacific wall-clock time of the same instant
        true = w["utc_end"].dt.tz_convert("America/Los_Angeles")
        w["pacific_offset_h"] = -true.map(lambda x: x.utcoffset().total_seconds() / 3600)
        g = w.assign(month=w["start"].dt.strftime("%Y-%m")).groupby("month").agg(
            hours=("start", "size"), utc_less_local=("utc_less_local_h", lambda x: sorted(set(x.round(2)))),
            pacific_offset=("pacific_offset_h", lambda x: sorted(set(x.round(2)))))
        print("UTC time less Local time, hours, by month, against Pacific time's own offset:")
        print(g.to_string())
    if "Time zone" in w:
        print("Time zone column:", w["Time zone"].value_counts().to_dict())
    caiso = cj.caiso_hours()
    cidx = pd.to_datetime(caiso.index, utc=True)
    own = {"solar": pd.Series(caiso["solar_mw"].values, index=cidx), "wind": pd.Series(caiso["wind_mw"].values, index=cidx),
           "demand": pd.Series(caiso[cj.ALL].sum(axis=1).values, index=cidx), "gas": pd.Series(caiso["natural_gas_mw"].values, index=cidx)}
    eia = {"solar": "Adjusted SUN Gen", "wind": "Adjusted WND Gen", "demand": "Adjusted demand", "gas": "Adjusted NG Gen"}
    rows = []
    w = w.set_index("start")
    for month, x in w.groupby(w.index.strftime("%Y-%m")):
        r = dict(month=month, hours=len(x))
        for k, col in eia.items():
            if col not in x:
                continue
            a = pd.to_numeric(x[col], errors="coerce")
            s, res = best_shift(a, own[k])
            r[f"{k}_best_shift_h"] = s
            r[f"{k}_corr_at_0"] = round(res[0], 5)
            r[f"{k}_corr_at_1"] = round(res[1], 5)
        rows.append(r)
    d = pd.DataFrame(rows)
    d.to_csv(os.path.join(OUT, "caiso_hour_offset.csv"), index=False)
    pd.set_option("display.width", 250)
    print("the shift at which EIA's hours best match CAISO's own (positive: EIA is late), and the correlation at no shift and at one hour:")
    print(d.to_string(index=False))
    for a, b in ((cj.JOIN[:11] + "00:00:00Z", "2025-12-17T00:00:00Z"),):
        x = w[(w.index >= pd.Timestamp("2025-12-15T12:00:00Z")) & (w.index < pd.Timestamp("2025-12-17T06:00:00Z"))]
        side = pd.DataFrame({"eia_sun": pd.to_numeric(x["Adjusted SUN Gen"], errors="coerce"), "caiso_sun": own["solar"].reindex(x.index).round(0),
                             "eia_local": x.get("Local time"), "eia_hour": x.get("Hour")})
        print("around the break (index: the hour's start as the ERW reads it, UTC):")
        print(side.to_string())
    return 0


if __name__ == "__main__":
    sys.exit(main())
