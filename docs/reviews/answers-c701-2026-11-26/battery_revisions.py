"""Window D's data request 20 (the storage audit, finding 2): EIA-930's revisions of the newest battery hours. The data
machine keeps each day's copy of EIA's six-month file (warehouse/raw/eia930_region_hourly/<run>/..._Jul_Dec.csv, 18 to
25 November 2026). For ERCO, ISNE, MISO and SWPP, each hour's "Net Generation (MW) from Battery Storage" as first posted
(the earliest copy that holds it with a value) against the same hour in the first copy taken at least 72 hours later.
US48 is not a row of the six-month file (balancing authorities only), so it is not here. No request; counts only."""
import glob
import os

import pandas as pd

BAS = ["ERCO", "ISNE", "MISO", "SWPP"]
COL = "Net Generation (MW) from Battery Storage"
runs = []
for d in sorted(glob.glob("warehouse/raw/eia930_region_hourly/202611*")):
    f = glob.glob(os.path.join(d, "*EIA930_BALANCE_2026_Jul_Dec.csv"))
    if not f:
        continue
    at = pd.Timestamp(os.path.basename(d), tz="UTC")
    x = pd.read_csv(f[0], usecols=["Balancing Authority", "UTC Time at End of Hour", COL], dtype=str, keep_default_na=False)
    x = x[x["Balancing Authority"].isin(BAS)]
    x["v"] = pd.to_numeric(x[COL].str.replace(",", ""), errors="coerce")
    x["hour"] = pd.to_datetime(x["UTC Time at End of Hour"], format="%m/%d/%Y %I:%M:%S %p", utc=True) - pd.Timedelta(hours=1)
    runs.append((at, x.dropna(subset=["v"]).set_index(["Balancing Authority", "hour"])["v"]))
print("copies:", [str(a)[:16] for a, _ in runs])
rows = []
for ba in BAS:
    first, later = {}, {}
    for at, s in runs:
        if ba not in s.index.get_level_values(0):
            continue
        for h, v in s.loc[ba].items():
            if h not in first and h >= runs[0][0] - pd.Timedelta(days=30):
                first[h] = (at, v)
    for h, (at0, v0) in first.items():
        if at0 == runs[0][0]:
            continue  # held already in the oldest copy: not its first posting
        for at, s in runs:
            if at >= at0 + pd.Timedelta(hours=72) and (ba, h) in s.index:
                later[h] = (v0, float(s.loc[(ba, h)]))
                break
    r = pd.DataFrame([(h, a, b) for h, (a, b) in later.items()], columns=["hour", "first", "later"])
    r["rev"] = r["later"] - r["first"]
    big = r.loc[r["rev"].abs().idxmax()] if len(r) else None
    rows.append(dict(ba=ba, hours_compared=len(r), hours_revised=int((r["rev"].abs() > 0.5).sum()),
                     mean_abs_revision_mw=round(r["rev"].abs().mean(), 1) if len(r) else None,
                     mean_revision_mw=round(r["rev"].mean(), 1) if len(r) else None,
                     mean_abs_revision_pct_of_mean_abs=round(100 * r["rev"].abs().mean() / r["later"].abs().mean(), 1) if len(r) else None,
                     largest_mw=None if big is None else round(big["rev"], 1),
                     largest_at=None if big is None else str(big["hour"]),
                     largest_first_later=None if big is None else (big["first"], big["later"]),
                     first_hour=str(r["hour"].min()) if len(r) else None, last_hour=str(r["hour"].max()) if len(r) else None))
pd.set_option("display.width", 250)
print(pd.DataFrame(rows).to_string(index=False))
