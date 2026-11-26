"""Session 10218: an independent restatement of what /prices and /prices/<hub> draw (prices_draw/*.txt, the pages' own
functions at a fixed render time on this machine's tables), from the same rows, written from docs/methods/power_prices.md
and the pages' own words ("Min, mean and max of every interval in the window"; "the intervals held of those the span
from the first row to the last holds at the table's step"; "real time less day-ahead over the hours both hold, a
real-time hour taken only when every interval of the hour is held"). Standard library only; public grids only.

    python restate_prices.py <tables dir> <render ISO> <draw dir>
"""
import collections
import csv
import datetime as dt
import json
import os
import re
import sys

DIR, AT, DRAW = sys.argv[1], sys.argv[2], sys.argv[3]
UTC = dt.timezone.utc
now = dt.datetime.strptime(AT, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
since = (now - dt.timedelta(days=30)).replace(minute=0, second=0)
MK = {"ercot": ("spp_rtm", 15, "spp_dam"), "caiso": ("lmp_rtm_15m_mean", 15, "lmp_dam"), "spp": (None, None, "lmp_dam")}


def rows(table, ent, var, hi):
    out = []
    with open(os.path.join(DIR, table + ".csv"), encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#") or not line.startswith(ent + ","):
                continue
            p = line.split(",", 4)
            if p[0] != ent or p[1] != var:
                continue
            t = dt.datetime.strptime(p[2], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
            if since <= t <= hi:
                out.append((t, float(p[3])))
    return sorted(out)


def price(v):
    return f"{v:,.2f}"


def stats(r, step):
    v = [x for _, x in r]
    lo = min(r, key=lambda x: x[1])  # the first of the lowest (min keeps the first)
    hi = max(r, key=lambda x: x[1])
    due = round((r[-1][0] - r[0][0]).total_seconds() / (step * 60)) + 1
    days = {t.date() for t, _ in r}
    miss = []
    d = r[0][0].date()
    while d <= r[-1][0].date():
        if d not in days:
            miss.append(d.isoformat())
        d += dt.timedelta(days=1)
    return {"n": len(v), "due": due, "min": price(min(v)), "mean": price(sum(v) / len(v)), "max": price(max(v)),
            "first": r[0][0].strftime("%Y-%m-%d %H:%M"), "last": r[-1][0].strftime("%Y-%m-%d %H:%M"), "minAt": lo[0].isoformat(), "maxAt": hi[0].isoformat(), "missing": miss}


tot = ok = 0
bad = []


def check(what, got, want):
    global tot, ok
    tot += 1
    if got == want:
        ok += 1
    else:
        bad.append(f"{what}: drawn {got!r}, restated {want!r}")


def cnt(n, due):
    return f"{n:,}" + (f" of {due:,}" if due != n else "")


for ent in ("ercot:HB_HUBAVG", "ercot:HB_WEST", "caiso:TH_SP15_GEN-APND", "spp:SPPNORTH_HUB"):
    iso = ent.split(":")[0]
    rv, step, dv = MK[iso]
    txt = open(os.path.join(DRAW, re.sub(r"[^\w.-]+", "_", ent) + ".txt"), encoding="utf-8").read()
    da = rows("iso_dam_hub_prices", ent, dv, now + dt.timedelta(days=1))
    s = stats(da, 60)
    m = re.search(r"\] Day-ahead \| iso_dam_hub_prices \| ([\d,]+(?: of [\d,]+)?) \| ([-\d,.]+) \| ([-\d,.]+) \| ([-\d,.]+) \| ([\d: -]+) UTC \| ([\d: -]+) UTC", txt)
    check(f"{ent} day-ahead row", m.groups() if m else None, (cnt(s["n"], s["due"]), s["min"], s["mean"], s["max"], s["first"], s["last"]))
    if rv:
        rt = rows("iso_rtm_hub_prices", ent, rv, now)
        r = stats(rt, step)
        m = re.search(r"\] Real time \| iso_rtm_hub_prices \| ([\d,]+(?: of [\d,]+)?) \| ([-\d,.]+) \| ([-\d,.]+) \| ([-\d,.]+) \| ([\d: -]+) UTC \| ([\d: -]+) UTC", txt)
        check(f"{ent} real-time row", m.groups() if m else None, (cnt(r["n"], r["due"]), r["min"], r["mean"], r["max"], r["first"], r["last"]))
        # real time less day-ahead over the hours both hold
        by = collections.defaultdict(list)
        for t, v in rt:
            by[t.replace(minute=0)].append(v)
        dd = []
        for t, v in da:
            if len(by.get(t, [])) == 60 // step:
                dd.append((t, sum(by[t]) / len(by[t]) - v))
        vals = [x for _, x in dd]
        m = re.search(r"Real time less day-ahead \| the hours both hold \| ([\d,]+) hours \| ([-\d,.]+) \| ([-\d,.]+) \| ([-\d,.]+) \| ([\d: -]+) UTC \| ([\d: -]+) UTC", txt)
        check(f"{ent} real time less day-ahead", m.groups() if m else None,
              (f"{len(vals):,}", price(min(vals)), price(sum(vals) / len(vals)), price(max(vals)), dd[0][0].strftime("%Y-%m-%d %H:%M"), dd[-1][0].strftime("%Y-%m-%d %H:%M")))
        print(f"{ent}: real time {r['n']} of {r['due']}, UTC days with no row {r['missing']}; day-ahead {s['n']} of {s['due']}, days with no row {s['missing']}; "
              f"day-ahead rows after the render time {sum(1 for t, _ in da if t > now)}")

# the first tab: the day-ahead hour holding the render time, and the latest interval made for the stand-in
prices = open(os.path.join(DRAW, "prices.txt"), encoding="utf-8").read()
latest = {r["entity"]: r for r in json.load(open(os.path.join(DRAW, "latest_made.json"), encoding="utf-8"))}
for ent, r in sorted(latest.items()):
    iso = ent.split(":")[0]
    node = ent.split(":", 1)[1]
    line = next((ln for ln in prices.splitlines() if re.match(rf"(\[title: [^\]]*\] )?{re.escape(node)}( main)? \|", ln)), None)
    if line is None:
        check(f"first tab {ent}", None, "a row")
        continue
    cells = [c.strip() for c in line.split("|")]
    check(f"first tab {ent} real time", cells[1], price(float(r["value"])))
    h = now.replace(minute=0, second=0)
    dv = MK[iso][2]
    d = [v for t, v in rows("iso_dam_hub_prices", ent, dv, now + dt.timedelta(days=1)) if t == h]
    check(f"first tab {ent} day-ahead this hour", cells[3], price(d[0]) if d else "(none)")
print(f"figures checked {tot}, equal {ok}")
for b in bad:
    print("  ", b)
