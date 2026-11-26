"""Session 10219 (chain 710, part D): /conditions restated from its own page files, standard library only.

Reads site/data/conditions/<op>.json and index.json of the worktree given as argv[1]. None of the site's code and none
of the builder's code: the page's rules are restated from page.tsx and lib/conditions.ts as words.

  1. The default view (ERCOT, the newest window) and each operator's opening view: window, hours drawn, the glance
     figures (largest day of each column, earliest day on a tie, the adder kept only above zero), the alerts heading's
     count and the rows the table draws (the first 40), the status table.
  2. Every daily row restated from the hourly rows where a kept window holds every hour of the local day.
  3. The alerts column of the daily rows against the alerts list.
Writes JSON to argv[2].
"""
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = sys.argv[1]
OUT = sys.argv[2]
D = os.path.join(ROOT, "site", "data", "conditions")
OPS = ["caiso", "ercot", "spp", "miso", "pjm", "nyiso", "isone"]
TZ = {"caiso": "America/Los_Angeles", "ercot": "America/Chicago", "spp": "America/Chicago", "miso": "America/Chicago",
      "pjm": "America/New_York", "nyiso": "America/New_York", "isone": "America/New_York"}
STRIPS = ["demand", "out", "constraints", "scarcity", "alerts", "reserves"]
GLANCE = [("demand_peak", "Highest peak demand"), ("out_max", "Most megawatts out of service in an hour"),
          ("cons_hours", "Most constraint-hours in a day"), ("adder_hours", "Most hours with the adder above zero in a day")]


def load(name):
    with open(os.path.join(D, name + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def local_day(ts, tz):
    t = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    return t.astimezone(ZoneInfo(tz)).strftime("%Y-%m-%d")


def window(f, event=None):
    for w in f["windows"]:
        if event and w["id"] == event and w["id"] != "recent":
            return w["start"], w["end"], w["title"], w["id"] if w["id"] in f["hourly"] else None
    w = [x for x in f["windows"] if x["id"] == "recent"][0]
    return w["start"], w["end"], w["title"], "recent" if "recent" in f["hourly"] else None


def view(f, event=None):
    s, e, title, hk = window(f, event)
    dc = f["daily_columns"]
    daily = [r for r in f["daily"] if s <= r[0] <= e]
    hourly = f["hourly"].get(hk, []) if hk else []
    glance = []
    for c, words in GLANCE:
        j = dc.index(c)
        best = None
        for r in daily:
            if r[j] is None:
                continue
            if best is None or r[j] > best[j]:
                best = r
        if best is None or (c == "adder_hours" and best[j] <= 0):
            continue
        glance.append({"c": c, "words": words, "value": best[j], "shown": f"{round(best[j]):,}", "day": best[0]})
    alerts = [a for a in f["alerts"] if s <= a[0] <= e] if f["strips"]["alerts"]["status"] == "shown" else None
    return {"start": s, "end": e, "title": title, "days": len(daily), "hours_drawn": len(hourly),
            "glance": glance, "alerts_heading": None if alerts is None else len(alerts),
            "alerts_rows_drawn": None if alerts is None else min(40, len(alerts)),
            "alerts_left_out": None if alerts is None else max(0, len(alerts) - 40),
            "last_alert_drawn": None if not alerts else alerts[min(40, len(alerts)) - 1][0],
            "last_alert_in_window": None if not alerts else alerts[-1][0]}


def restate_daily(f, tz):
    """Each daily row against its hours, for local days whose every hour a kept window holds."""
    hc = f["hourly_columns"]
    dc = f["daily_columns"]
    hours = {}
    for rows in f["hourly"].values():
        for r in rows:
            hours[r[0]] = r
    by_day = defaultdict(list)
    for ts, r in hours.items():
        by_day[local_day(ts, tz)].append(r)
    daily = {r[0]: r for r in f["daily"]}
    checked = 0
    bad = []
    n_hours = Counter()
    for day, rows in by_day.items():
        d0 = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=ZoneInfo(tz))
        d1 = (d0 + timedelta(days=1)).replace(tzinfo=ZoneInfo(tz))
        want = int((d1.astimezone(timezone.utc) - d0.astimezone(timezone.utc)).total_seconds() // 3600)
        n_hours[len(rows) - want] += 1
        if len(rows) != want or day not in daily:
            continue
        def col(c):
            i = hc.index(c)
            return [r[i] for r in rows if r[i] is not None]
        def r1(v):
            return None if v is None else round(v + 0.0, 1)
        dem, fc, out, cn, cm, ad = col("demand"), col("forecast"), col("out_total"), col("cons_n"), col("cons_max"), col("adder")
        mine = {
            "demand_peak": r1(max(dem)) if dem else None,
            "demand_min": r1(min(dem)) if dem else None,
            "forecast_peak": r1(max(fc)) if fc else None,
            "out_mean": r1(sum(out) / len(out)) if out else None,
            "out_max": r1(max(out)) if out else None,
            "cons_hours": int(sum(cn)) if cn else None,
            "cons_max": r1(max(cm)) if cm else None,
            "adder_hours": sum(1 for v in ad if v > 0) if ad else None,
            "adder_max": r1(max(ad)) if ad else None,
        }
        row = daily[day]
        for c, v in mine.items():
            got = row[dc.index(c)]
            checked += 1
            if not (got == v or (got is not None and v is not None and abs(got - v) <= 0.051)):
                bad.append({"day": day, "col": c, "file": got, "restated": v})
    return checked, bad, dict(n_hours)


def alerts_by_day(f):
    dc = f["daily_columns"]
    j = dc.index("alerts")
    cnt = Counter(a[0] for a in f["alerts"])
    bad = [r[0] for r in f["daily"] if r[j] is not None and r[j] != cnt.get(r[0], 0)]
    return {"days": sum(1 for r in f["daily"] if r[j] is not None), "mismatch": bad[:10], "n_mismatch": len(bad),
            "alerts_on_days_not_in_daily": sum(v for k, v in cnt.items() if k not in {r[0] for r in f["daily"]})}


def main():
    idx = load("index")
    files = {op: load(op) for op in OPS}
    res = {"built": idx["built"], "recent_days": idx["recent_days"], "events": [e["id"] for e in idx["events"]]}
    res["default"] = view(files["ercot"])
    res["opening"] = {op: view(files[op]) for op in OPS}
    res["events_view"] = {op: {e["id"]: view(files[op], e["id"]) for e in idx["events"]} for op in OPS}
    res["status_table"] = {o["op"]: [files[o["op"]]["strips"][k]["status"] for k in STRIPS] for o in idx["operators"]}
    res["index_matches_files"] = all(o["strips"] == {k: v["status"] for k, v in files[o["op"]]["strips"].items()} for o in idx["operators"])
    res["daily_restated"] = {}
    for op in OPS:
        checked, bad, nh = restate_daily(files[op], TZ[op])
        res["daily_restated"][op] = {"figures_checked": checked, "differ": len(bad), "first_differ": bad[:8], "hours_vs_local_day": nh}
    res["alerts_by_day"] = {op: alerts_by_day(files[op]) for op in ("caiso", "ercot")}
    # The recent window: its days and the hours its last day holds.
    rec = {}
    for op in OPS:
        f = files[op]
        s, e, _, hk = window(f)
        rows = f["hourly"].get("recent", [])
        hc = f["hourly_columns"]
        last_day = [r for r in rows if local_day(r[0], TZ[op]) == e]
        dem_i, fc_i = hc.index("demand"), hc.index("forecast")
        held_days = sorted({local_day(r[0], TZ[op]) for r in rows if r[dem_i] is not None})
        rec[op] = {"start": s, "end": e, "days_in_window": (datetime.strptime(e, "%Y-%m-%d") - datetime.strptime(s, "%Y-%m-%d")).days + 1,
                   "hours_rows": len(rows), "first_hour": rows[0][0] if rows else None, "last_hour": rows[-1][0] if rows else None,
                   "last_day_rows": len(last_day), "last_day_demand_hours": sum(1 for r in last_day if r[dem_i] is not None),
                   "last_day_forecast_hours": sum(1 for r in last_day if r[fc_i] is not None),
                   "last_demand_hour": max((r[0] for r in rows if r[dem_i] is not None), default=None),
                   "last_forecast_hour": max((r[0] for r in rows if r[fc_i] is not None), default=None),
                   "first_demand_day": held_days[0] if held_days else None}
    res["recent"] = rec
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=1)
    d = res["default"]
    print("built", res["built"])
    print("DEFAULT (ERCOT):", d["title"], d["start"], "to", d["end"], "days", d["days"], "hours drawn", d["hours_drawn"])
    for g in d["glance"]:
        print("  ", g["words"], g["shown"], "on", g["day"])
    print("   alerts heading", d["alerts_heading"], "rows drawn", d["alerts_rows_drawn"])
    for op in OPS:
        v = res["opening"][op]
        print("OPEN", op, v["start"], v["end"], "hours", v["hours_drawn"], [(g["c"], g["shown"], g["day"]) for g in v["glance"]], "alerts", v["alerts_heading"])
    for op in OPS:
        for ev, v in res["events_view"][op].items():
            if v["alerts_left_out"]:
                print("CUT", op, ev, v["alerts_heading"], "drawn", v["alerts_rows_drawn"], "last drawn", v["last_alert_drawn"], "last in window", v["last_alert_in_window"])
    for op, v in res["daily_restated"].items():
        print("DAILY", op, v["figures_checked"], "differ", v["differ"], v["hours_vs_local_day"], v["first_differ"][:3])
    print("ALERTS_BY_DAY", res["alerts_by_day"])
    for op, v in rec.items():
        print("RECENT", op, v)
    print("status", res["status_table"], "index matches", res["index_matches_files"])


if __name__ == "__main__":
    main()
