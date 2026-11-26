"""Window D's data request 34 (the conditions audit, finding 1): for seven grids' demand in eia930_ba_demand_hourly
since July 2018, the hours impossible_hours.screen leaves out (by its reasons, left_out), and each local day whose peak
moves when they are left out. The screen is applied to each grid's whole series in time order, one row an hour, as the
demand builders apply it. Counts only.

Also row 32 (the conditions audit, finding 9): constraints_binding_hourly over its last twelve months held, rows per
hour against distinct x_constraint per hour, and the same for daily sums."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
sys.path.insert(0, "warehouse/derived")
import impossible_hours as ih  # noqa: E402
import iso_prices as ip  # noqa: E402

GRIDS = {"ERCO": "America/Chicago", "CISO": "America/Los_Angeles", "PJM": "America/New_York", "MISO": "America/Chicago",
         "NYIS": "America/New_York", "ISNE": "America/New_York", "SWPP": "America/Chicago"}
pd.set_option("display.width", 250)
p = "warehouse/output/eia930_ba_demand_hourly.csv"
parts = []
for ch in pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, chunksize=500000,
                      usecols=["entity", "variable", "ts_utc", "value"]):
    ch = ch[ch["variable"] == "demand_mw"]
    ch = ch[ch["entity"].isin([f"eia930:{g}" for g in GRIDS])]
    parts.append(ch)
d = pd.concat(parts)
print("== 34")
rows, moved = [], []
for g, tz in GRIDS.items():
    x = d[d["entity"] == f"eia930:{g}"].copy()
    x["t"] = pd.to_datetime(x["ts_utc"], utc=True)
    x = x[x["t"] >= pd.Timestamp("2018-07-01T00:00:00Z")].sort_values("t")
    full = pd.date_range(x["t"].min(), x["t"].max(), freq="h")
    s = x.set_index("t")["value"].astype(float).reindex(full)
    out = ih.left_out(s)
    kept = ih.screen(s)
    held = s.dropna()
    lo = out[out["value"].notna()]
    day = pd.Series(s.index.tz_convert(tz).date, index=s.index)
    raw_peak = s.groupby(day).max()
    kept_peak = kept.groupby(day).max()
    mv = (raw_peak - kept_peak).abs() > 1e-9
    r = dict(grid=g, hours_held=len(held), left_out=len(lo), **{f"left_{k}": int((lo["reason"] == k).sum()) for k in ih.REASONS[1:]},
             days=int(raw_peak.notna().sum()), days_peak_moves=int(mv.sum()))
    rows.append(r)
    top = pd.DataFrame({"raw_peak": raw_peak, "screened_peak": kept_peak})[mv]
    top["drop"] = top["raw_peak"] - top["screened_peak"]
    for dd, rr in top.nlargest(3, "drop").iterrows():
        moved.append(dict(grid=g, day=str(dd), raw_peak=rr["raw_peak"], screened_peak=rr["screened_peak"]))
print(pd.DataFrame(rows).to_string(index=False))
print("the three days a grid whose peak moves most:")
print(pd.DataFrame(moved).to_string(index=False))

print("== 32")
c = pd.read_csv("warehouse/output/constraints_binding_hourly.csv", skiprows=ip.header_rows("warehouse/output/constraints_binding_hourly.csv"),
                dtype=str, keep_default_na=False, usecols=["entity", "ts_utc", "market", "x_constraint"])
c["t"] = pd.to_datetime(c["ts_utc"], utc=True)
for m, tz in (("caiso_dam", "America/Los_Angeles"), ("spp_dam", "America/Chicago")):
    x = c[c["market"] == m]
    end = x["t"].max()
    x = x[x["t"] > end - pd.Timedelta(days=365)]
    per_h = x.groupby("t").agg(rows=("entity", "size"), distinct=("x_constraint", "nunique"))
    x = x.assign(day=x["t"].dt.tz_convert(tz).dt.date)
    per_d = x.groupby("day").agg(rows=("entity", "size"), distinct_constraint_hours=("x_constraint", lambda s: 0))
    dd = x.drop_duplicates(["x_constraint", "t"]).groupby("day").size()
    per_d["distinct_constraint_hours"] = dd
    print(m, "from", x["t"].min(), "to", end, "| hours with a row", len(per_h),
          "| rows", int(per_h["rows"].sum()), "| distinct name-hours", int(per_h["distinct"].sum()),
          "| hours where rows exceed distinct names", int((per_h["rows"] > per_h["distinct"]).sum()),
          "| largest excess in an hour", int((per_h["rows"] - per_h["distinct"]).max()),
          "| days where the daily sum differs", int((per_d["rows"] != per_d["distinct_constraint_hours"]).sum()), "of", len(per_d),
          "| mean rows a day", round(per_d["rows"].mean(), 1), "against", round(per_d["distinct_constraint_hours"].mean(), 1))
