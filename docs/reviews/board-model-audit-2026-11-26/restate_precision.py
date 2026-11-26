# Session 10206: the power rows' daily means at full precision, from the warehouse's own hourly and 15-minute tables on
# this machine (the main copy's warehouse/output, read only: iso_dam_hub_prices, iso_rtm_hub_prices, 26 August to about
# 12 November 2026, under a year), against the board's series files (site/public/board/s) to the fourth decimal. The
# board's hourly files round each hour to the cent, so this is the only way to the digit. MISO rows are skipped unread.
import collections
import csv
import datetime as dt
import json
import os
from zoneinfo import ZoneInfo

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "site")
OUT = r"C:\Users\lossa\Documents\erw\warehouse\output"
TZ = {"ercot": "America/Chicago", "spp": "America/Chicago", "caiso": "America/Los_Angeles"}


def rid(entity, market):
    g, code = entity.split(":", 1)
    return f"{g}-{code.lower().replace('_', '-').replace('.', '-')}-{market}"


def read(name):
    rows = collections.defaultdict(dict)
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8") as f:
        lines = (ln for ln in f if not ln.startswith("#"))
        for r in csv.DictReader(lines):
            g = r["entity"].split(":")[0]
            if g not in TZ or r["value"] == "":
                continue
            rows[r["entity"]][r["ts_utc"]] = float(r["value"])
    return rows


def hours_of(points, per_hour):
    """{utc hour: mean of its intervals} for the hours holding every interval."""
    by = collections.defaultdict(list)
    for t, v in points.items():
        u = dt.datetime.fromisoformat(t.replace("Z", "+00:00"))
        by[u.replace(minute=0, second=0)].append(v)
    return {h: sum(vs) / len(vs) for h, vs in by.items() if len(vs) == per_hour}


def daily(hours, tz):
    z = ZoneInfo(tz)
    by = collections.defaultdict(list)
    for h, v in hours.items():
        by[h.astimezone(z).date()].append(v)
    out = {}
    for d, vs in by.items():
        a = dt.datetime(d.year, d.month, d.day, tzinfo=z)
        n = d + dt.timedelta(days=1)
        b = dt.datetime(n.year, n.month, n.day, tzinfo=z)
        if len(vs) == round((b - a).total_seconds() / 3600):
            out[d] = sum(vs) / len(vs)
    return out


def series(i):
    p = os.path.join(SITE, "public", "board", "s", i + ".json")
    if not os.path.exists(p):
        return None
    f = json.load(open(p, encoding="utf-8"))
    t0 = dt.date.fromisoformat(f["t0"])
    return {t0 + dt.timedelta(days=d): v for d, v in zip(f["d"], f["v"])}


n = bad = 0
worst = (0.0, "")
per = {}
for name, market in (("iso_dam_hub_prices", "da"), ("iso_rtm_hub_prices", "rt")):
    for ent, pts in read(name).items():
        g = ent.split(":")[0]
        steps = collections.Counter(dt.datetime.fromisoformat(t.replace("Z", "+00:00")).minute for t in pts)
        per_hour = 1 if market == "da" else len(steps)
        days = daily(hours_of(pts, per_hour), TZ[g])
        s = series(rid(ent, market))
        if s is None:
            per[rid(ent, market)] = "no series file"
            continue
        k = b = 0
        for d, v in days.items():
            if d in s:
                k += 1
                gap = abs(round(v, 4) - s[d])
                if gap > 0.00005 + 1e-9:
                    b += 1
                if gap > worst[0]:
                    worst = (gap, f"{rid(ent, market)} {d}")
        n += k
        bad += b
        per[rid(ent, market)] = f"{k} days compared, {b} differ at the fourth decimal ({per_hour} intervals an hour)"
for k, v in sorted(per.items()):
    print(f"  {k}: {v}")
print(f"daily means at full precision against the series files: {n} compared, {bad} differ at the fourth decimal; largest gap {worst[0]:.6g} ({worst[1]})")
