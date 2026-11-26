"""Session 10219: one rule of /conditions changed at a time, measured on the page's own files.

argv: worktree, output folder (read only), out JSON.
  A. The ERW's own rule for impossible hours (warehouse/derived/impossible_hours.py, screen) applied to the demand of
     every kept hourly window: the hours it leaves out, and each window's "Highest peak demand" before and after.
  B. The fall-back day (2026-11-01) in the newest window: hours in the local day, and what the repeated hour adds to
     the day's constraint-hours (CAISO, SPP).
  C. The headroom cell of /cost-of-power's All grids tab (grid_peak_vs_capacity and ERCOT's CDR), restated from
     site/data/siting/headroom.json; and the net summer MW EIA lists as retired from January 2026 to the list's month
     in each grid's balancing authority (operating at the end of 2025, absent from the list the capacity is read from).
"""
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import pandas as pd

ROOT, OUTDIR, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import impossible_hours as ih  # noqa: E402

OPS = ["caiso", "ercot", "spp", "miso", "pjm", "nyiso", "isone"]
TZ = {"caiso": "America/Los_Angeles", "ercot": "America/Chicago", "spp": "America/Chicago", "miso": "America/Chicago",
      "pjm": "America/New_York", "nyiso": "America/New_York", "isone": "America/New_York"}


def load(op):
    with open(os.path.join(ROOT, "site", "data", "conditions", op + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def lday(ts, tz):
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(ZoneInfo(tz)).strftime("%Y-%m-%d")


res = {"screen": {}, "dst": {}, "headroom": {}}
for op in OPS:
    f = load(op)
    hc = f["hourly_columns"]
    idm = hc.index("demand")
    per = {}
    for wid, rows in f["hourly"].items():
        ts = [r[0] for r in rows]
        s = pd.Series([r[idm] if r[idm] is not None else float("nan") for r in rows], index=pd.to_datetime(ts, utc=True), dtype=float)
        s = s.asfreq("h")
        kept = ih.screen(s)
        out = ih.left_out(s)
        out = out[out["value"].notna()]
        w = [x for x in f["windows"] if x["id"] == wid][0]
        def peak(series):
            best = None
            for t, v in series.items():
                if pd.isna(v):
                    continue
                d = lday(t.strftime("%Y-%m-%dT%H:%M:%SZ"), TZ[op])
                if not (w["start"] <= d <= w["end"]):
                    continue
                if best is None or v > best[1]:
                    best = (d, v, t.strftime("%Y-%m-%dT%H:%MZ"))
            return best
        before, after = peak(s), peak(kept)
        per[wid] = {"hours": int(s.notna().sum()), "left_out": int(len(out)),
                    "left_out_rows": [[t.strftime("%Y-%m-%dT%H:%MZ"), float(r["value"]), None if pd.isna(r["around"]) else float(r["around"]), r["reason"]] for t, r in out.iterrows()][:6],
                    "highest_before": before, "highest_after": after, "moves": before != after}
    res["screen"][op] = per
    # B: the fall-back day
    rows = f["hourly"].get("recent", [])
    day = [r for r in rows if lday(r[0], TZ[op]) == "2026-11-01"]
    ic = hc.index("cons_n")
    cons = [r[ic] for r in day if r[ic] is not None]
    seen = {}
    rep = None
    for r in day:
        loc = datetime.strptime(r[0], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).astimezone(ZoneInfo(TZ[op])).strftime("%H")
        if loc in seen:
            rep = (loc, r[0], r[ic])
        seen[loc] = r[0]
    res["dst"][op] = {"hours_in_day": len(day), "cons_hours": int(sum(cons)) if cons else None, "repeated_hour": rep}

with open(os.path.join(ROOT, "site", "data", "siting", "headroom.json"), encoding="utf-8") as fh:
    h = json.load(fh)
for g, pc in h.get("peak_capacity", {}).items():
    pct = 100 * pc["capacity_mw"] / pc["peak_mw"] - 100
    res["headroom"][g] = {"file_pct": pc["over_peak_pct"], "restated_pct": round(pct, 2), "shown": f"{round(pct):,}% above peak",
                          "ratio_peak_to_capacity": round(pc["peak_mw"] / pc["capacity_mw"], 2), "list": pc["list"], "year": pc["year"]}
rv = h["reserve"]["grids"]["ercot"]
for k in ("peak", "net", "first_below_zero"):
    x = rv[k]
    res["headroom"]["ercot_cdr_" + k] = {"file_pct": x["pct"], "restated_pct": round(100 * (x["capacity_mw"] - x["firm_peak_mw"]) / x["firm_peak_mw"], 6), "shown": f"{x['pct']:.1f}%"}
# retirements from January 2026 to the list's month, by balancing authority
ba_of = {"caiso": "CISO", "ercot": "ERCO", "spp": "SWPP", "miso": "MISO", "pjm": "PJM", "nyiso": "NYIS", "isone": "ISNE"}
ret = defaultdict(float)
n = defaultdict(int)
with open(os.path.join(OUTDIR, "eia860m_retired_generators_all.csv"), encoding="utf-8", newline="") as fh:
    for r in csv.DictReader(ln for ln in fh if not ln.startswith("#")):
        d = r["retirement_date"] or r["status_date"]
        if "2026-01-01" <= d <= "2026-08-31":
            try:
                ret[r["balancing_authority"]] += float(r["net_summer_mw"] or 0)
                n[r["balancing_authority"]] += 1
            except ValueError:
                pass
res["retired_2026_to_list"] = {g: {"mw": round(ret[b], 1), "units": n[b]} for g, b in ba_of.items()}
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(res, fh, indent=1, default=str)
for op, per in res["screen"].items():
    for wid, v in per.items():
        if v["left_out"] or v["moves"]:
            print("SCREEN", op, wid, "hours", v["hours"], "left out", v["left_out"], "highest", v["highest_before"], "->", v["highest_after"], v["left_out_rows"][:3])
print("DST", res["dst"])
print("HEADROOM", json.dumps(res["headroom"]))
print("RETIRED 2026", res["retired_2026_to_list"])
