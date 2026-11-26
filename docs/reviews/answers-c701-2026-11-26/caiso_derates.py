"""Window D's data request 33 (the conditions audit, finding 10): CAISO's curtailed and non-operational generator
reports for 14 to 18 November 2026, as warehouse/connectors/grid_outages.py reads them (its caiso_frame, and its
weighting of each curtailment by the part of the hour it covers, each resource capped at its Pmax), with each hour's MW
split by the report's NATURE OF WORK: the derates the row names (ambient, transmission induced, fuel) against the rest.
Reads the workbooks the connector saved (warehouse/raw/grid_outages, newest copy of each day); no request."""
import csv
import glob
import os
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import grid_outages as go  # noqa: E402

DAYS = ["20261114", "20261115", "20261116", "20261117", "20261118"]
found = {}
for man in sorted(glob.glob("warehouse/raw/grid_outages/*/manifest.csv")):
    for r in csv.DictReader(open(man, encoding="utf-8")):
        for d in DAYS:
            if r["url"].endswith(f"report-{d}.xlsx") and r["status"] == "200":
                found[d] = os.path.join(os.path.dirname(man), r["file"])
print({d: f.split("/")[-2] for d, f in found.items()})
DERATE = ("AMBIENT", "TRANSMISSION")  # CAISO's fuel code is AMBIENT_DUE_TO_FUEL_INSUFFICIENCY
natures = {}
rows = []
for d in DAYS:
    day = pd.Timestamp(d)
    x = go.caiso_frame(open(found[d], "rb").read(), day)
    x = x[x["OUTAGE MRID"].notna()]
    nat = x["NATURE OF WORK"].astype(str).str.strip().str.upper() if "NATURE OF WORK" in x.columns else pd.Series("", index=x.index)
    for k, v in nat.value_counts().items():
        natures[k] = natures.get(k, 0) + int(v)
    tz = go.gc.CAISO_TZ
    b = (day + pd.Timedelta(days=1)).tz_localize(tz)
    st = pd.to_datetime(x["CURTAILMENT START DATE TIME"]).dt.tz_localize(tz, ambiguous=True, nonexistent="shift_forward")
    en = pd.to_datetime(x["CURTAILMENT END DATE TIME"]).dt.tz_localize(tz, ambiguous=True, nonexistent="shift_forward").fillna(b)
    mw = pd.to_numeric(x["CURTAILMENT MW"], errors="coerce").fillna(0.0)
    res = x["RESOURCE ID"].astype(str).str.strip() if "RESOURCE ID" in x.columns else x["OUTAGE MRID"].astype(str)
    pmax = pd.to_numeric(x["RESOURCE PMAX MW"], errors="coerce") if "RESOURCE PMAX MW" in x.columns else pd.Series(float("nan"), index=x.index)
    once = ~pd.DataFrame({"m": x["OUTAGE MRID"].astype(str), "s": st, "e": en, "w": mw}).duplicated()
    derate = nat.apply(lambda s: s.startswith(DERATE))
    for h in go.gc.day_hours(day, tz):
        h0 = h.tz_convert(tz)
        h1 = h0 + pd.Timedelta(hours=1)
        lo = st.where(st > h0, h0)
        hi = en.where(en < h1, h1)
        w = mw * ((hi - lo).dt.total_seconds() / 3600.0).clip(lower=0) * once
        tot = w.groupby(res).transform("sum")
        cap = pmax.groupby(res).transform("max")
        w = w * (cap / tot).where((tot > cap) & (cap > 0), 1.0).fillna(1.0)
        r = dict(hour_utc=h.isoformat(), local_day=d, total=round(float(w.sum()), 1), derate=round(float(w[derate].sum()), 1),
                 outage=round(float(w[~derate].sum()), 1))
        r["ambient"] = round(float(w[nat.isin(["AMBIENT_DUE_TO_TEMP", "AMBIENT_NOT_DUE_TO_TEMP"])].sum()), 1)
        r["transmission"] = round(float(w[nat == "TRANSMISSION_INDUCED"].sum()), 1)
        r["fuel"] = round(float(w[nat == "AMBIENT_DUE_TO_FUEL_INSUFFICIENCY"].sum()), 1)
        rows.append(r)
out = pd.DataFrame(rows)
out.to_csv("runs/c701/caiso_derates.csv", index=False)
print("natures of work (rows, five days):", dict(sorted(natures.items(), key=lambda kv: -kv[1])))
g = out.groupby("local_day")[["total", "outage", "derate", "ambient", "transmission", "fuel"]].mean().round(1)
print("mean MW over each day's hours:"); print(g.to_string())
print("five days:", out[["total", "outage", "derate", "ambient", "transmission", "fuel"]].mean().round(1).to_dict(),
      "| derate share of the total", round(100 * out["derate"].sum() / out["total"].sum(), 1), "percent")
