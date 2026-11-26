"""Session 10235, the Digest audit: every warehouse-table figure of the ten newest Digests re-done from the main
checkout's CSVs, by code that imports nothing of the ERW (no brief.py, no site code).

What is re-done, per issue (operating day = issue date - 1):
  the main hubs' day-ahead means (24 local hours, half-up to the cent), the day before, the change and the percent;
  the mover lines (value, day, change, percent, value before, day before);
  the highest real-time price (the value at its node and interval, and whether it is the highest of the tables read);
  EIA's fuel closes (the close on its day, the close before);
  US48 demand's peak hour (the UTC day) and the week or year before, and the percent.
Then every number left in the numbers sections that none of these explains is printed for a reading by hand.

Run: python r1_tables.py <output dir of CSVs> <docs/digest dir> > r1_tables.out
"""
import csv
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

OUT, DIG = sys.argv[1], sys.argv[2]
ISSUES = ["2026-10-09", "2026-10-12", "2026-10-13", "2026-10-14", "2026-10-20", "2026-10-21", "2026-10-22",
          "2026-10-23", "2026-11-06", "2026-11-12"]
TZ = {"ERCOT": ZoneInfo("America/Chicago"), "SPP": ZoneInfo("America/Chicago"), "CAISO": ZoneInfo("America/Los_Angeles"),
      "NYISO": ZoneInfo("America/New_York"), "ISO-NE": ZoneInfo("America/New_York"), "MISO": timezone(timedelta(hours=-5))}
PREFIX = {"ERCOT": "ercot", "SPP": "spp", "CAISO": "caiso", "NYISO": "nyiso", "ISO-NE": "isone", "MISO": "miso"}
DAM_FILE = {"NYISO": "nyiso_dam_zone_prices", "ISO-NE": "isone_dam_zone_prices"}
FUEL = {"Henry Hub natural gas": "eia:henry_hub", "WTI Cushing crude": "eia:wti_cushing", "Brent crude": "eia:brent"}


def rows(name, keep=None):
    path = os.path.join(OUT, name + ".csv")
    with open(path, encoding="utf-8", newline="") as f:
        lines = (ln for ln in f if not ln.startswith("#"))
        for r in csv.DictReader(lines):
            if keep is None or keep(r):
                yield r


def ts(s):
    return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def mean2(vals):
    d = [Decimal(repr(float(v))) for v in vals]
    return (sum(d) / len(d)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---- load
dam = defaultdict(dict)        # (iso, node) -> {ts: value}
for r in rows("iso_dam_hub_prices"):
    iso = r["entity"].split(":")[0].upper()
    dam[(iso, r["node"])][ts(r["ts_utc"])] = float(r["value"])
for iso, name in DAM_FILE.items():
    for r in rows(name):
        dam[(iso, r["node"])][ts(r["ts_utc"])] = float(r["value"])
RT_FILES = {"iso_rtm_hub_prices": None, "nyiso_rtm_zone_prices": "NYISO", "isone_rtm_zone_prices": "ISO-NE",
            "isone_rtm_zone_prices_hourly": "ISO-NE"}
rt = []                        # (iso, node, variable, ts, value, table)
for name, iso0 in RT_FILES.items():
    for r in rows(name):
        iso = iso0 or {"ercot": "ERCOT", "caiso": "CAISO", "spp": "SPP", "miso": "MISO"}[r["entity"].split(":")[0]]
        rt.append((iso, r["node"], r["variable"], ts(r["ts_utc"]), float(r["value"]), name))
fuel = defaultdict(dict)
for r in rows("eia_fuel_spot_prices"):
    fuel[r["entity"]][r["ts_utc"][:10]] = float(r["value"])
demand = {}
for r in rows("eia930_all_demand", lambda r: r["entity"] == "eia930:US48" and r["variable"] == "demand_mw"):
    demand[ts(r["ts_utc"])] = float(r["value"])


def dam_day(iso, node, day):
    tz = TZ[iso]
    start = datetime(day.year, day.month, day.day, tzinfo=tz).astimezone(timezone.utc)
    nd = day + timedelta(days=1)
    end = datetime(nd.year, nd.month, nd.day, tzinfo=tz).astimezone(timezone.utc)
    s = dam.get((iso, node), {})
    vals = [v for t, v in s.items() if start <= t < end]
    exp = int((end - start).total_seconds() // 3600)
    return (mean2(vals) if len(vals) == exp else None), len(vals), exp


def pct(new, old):
    return Decimal(repr(round(100 * (float(new) - float(old)) / float(old), 2))) if float(old) > 0 and float(new) >= 0 else None


def fmt_pct1(p):
    return f"{abs(float(p)):.1f}"


results = []   # (issue, what, printed, redone, equal)
unexplained = []


def check(issue, what, printed, redone):
    eq = (str(printed) == str(redone))
    results.append((issue, what, str(printed), str(redone), eq))


def peak(day0):
    vals = [(v, t) for t, v in demand.items() if day0 <= t < day0 + timedelta(days=1)]
    return max(vals) if vals else None


for issue in ISSUES:
    md = open(os.path.join(DIG, issue + ".md"), encoding="utf-8").read()
    lines = md.split("\n")
    d_issue = date.fromisoformat(issue)
    day = d_issue - timedelta(days=1)
    explained_lines = set()
    # -- the day-ahead table
    for i, l in enumerate(lines):
        c = [x.strip() for x in l.split("|")[1:-1]] if l.startswith("| ") else []
        if len(c) >= 5 and c[0] in TZ and re.fullmatch(r"\d{4}-\d{2}-\d{2}", c[2]):
            iso, node, od = c[0], c[1], date.fromisoformat(c[2])
            m1, n1, x1 = dam_day(iso, node, od)
            if re.fullmatch(r"-?[\d,]+\.\d{2}", c[3]):
                check(issue, f"dam {iso} {node} {od}", c[3].replace(",", ""), m1 if m1 is not None else f"{n1} of {x1} hours")
            if len(c) >= 7 and re.fullmatch(r"-?[\d,]+\.\d{2}", c[5]):
                m0, n0, x0 = dam_day(iso, node, od - timedelta(days=1))
                check(issue, f"dam {iso} {node} {od - timedelta(days=1)} (day before)", c[5].replace(",", ""), m0 if m0 is not None else f"{n0} of {x0} hours")
                mc = re.fullmatch(r"([+-][\d.]+) \(([+-][\d.]+)%\)", c[6])
                if mc and m1 is not None and m0 is not None:
                    ch = m1 - m0
                    check(issue, f"dam {iso} {node} change", mc.group(1), f"{float(ch):+.2f}")
                    p = pct(m1, m0)
                    check(issue, f"dam {iso} {node} percent", mc.group(2), f"{float(p):+.1f}" if p is not None else None)
            explained_lines.add(i)
    # -- mover lines (and the v2 market price row, the same form)
    for i, l in enumerate(lines):
        m = re.search(r"(?:^- |\*\* )(?:\*\*[^*]+\*\* )?([A-Za-z][^:]*?): (-?[\d,]+\.\d{2}) (\S+) on (\d{4}-\d{2}-\d{2}), (up|down) ([\d,.]+) \S+ \(([\d.]+)%\) from (-?[\d,]+\.\d{2}) \S+ on (\d{4}-\d{2}-\d{2})", l)
        if not m:
            continue
        label, v, unit, d1, updown, ch, pc, pv, d0 = m.groups()
        hub = re.fullmatch(r"(ERCOT|CAISO|NYISO|MISO|SPP|ISO-NE) (\S+) day-ahead", label)
        if label.startswith("**"):
            label = re.sub(r"^\*\*[^*]+\*\* ", "", label)
        if label in FUEL:
            s = fuel[FUEL[label]]
            rv1, rv0 = s.get(d1), s.get(d0)
            check(issue, f"mover {label} {d1}", v, f"{rv1:.2f}" if rv1 is not None else None)
            check(issue, f"mover {label} {d0} (before)", pv, f"{rv0:.2f}" if rv0 is not None else None)
            prior = sorted(k for k in s if k < d1)
            check(issue, f"mover {label} the close before {d1} is {d0}", d0, prior[-1] if prior else None)
            if rv1 is not None and rv0 is not None:
                check(issue, f"mover {label} change", ch, f"{abs(rv1 - rv0):.2f}")
                check(issue, f"mover {label} percent", pc, fmt_pct1(pct(rv1, rv0)))
                check(issue, f"mover {label} direction", updown, "up" if rv1 >= rv0 else "down")
        elif hub:
            iso, node = hub.groups()
            m1, _, _ = dam_day(iso, node, date.fromisoformat(d1))
            m0, _, _ = dam_day(iso, node, date.fromisoformat(d0))
            check(issue, f"mover {label} {d1}", v, m1)
            check(issue, f"mover {label} {d0} (before)", pv, m0)
            if m1 is not None and m0 is not None:
                check(issue, f"mover {label} change", ch, f"{abs(float(m1 - m0)):.2f}")
                check(issue, f"mover {label} percent", pc, fmt_pct1(pct(m1, m0)))
                check(issue, f"mover {label} direction", updown, "up" if m1 >= m0 else "down")
        explained_lines.add(i)
    # -- the real-time line
    held = {"NYISO", "ISO-NE", "MISO"} if d_issue >= date(2026, 10, 21) else set()
    for i, l in enumerate(lines):
        m = re.match(r"\*\*Highest real-time price[^*]*:\*\* (-?[\d,]+\.\d{2}) USD/MWh at (.+?) \(([A-Z-]+)\), .*?starting (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) (?:local|[A-Z][a-z]+)(?: \((?:(\d{4}-\d{2}-\d{2}) )?(\d{2}:\d{2}) UTC\))?", l)
        if not m:
            continue
        v, node, iso, ld, lt, ud, ut = m.groups()
        ud = ud or ld
        t_utc = datetime.fromisoformat(f"{ud}T{ut}:00+00:00") if ut else None
        local = datetime.fromisoformat(f"{ld}T{lt}:00").replace(tzinfo=TZ[iso]).astimezone(timezone.utc)
        check(issue, f"rt {iso} {node} local {ld} {lt} is UTC {ud} {ut}", t_utc.isoformat() if t_utc else None, local.isoformat())
        hits = [x for x in rt if x[0] == iso and x[1] == node and x[3] == local]
        check(issue, f"rt {iso} {node} value at {local:%Y-%m-%d %H:%M}Z", v.replace(",", ""), f"{max(h[4] for h in hits):.2f}" if hits else None)
        # the highest of the day over every grid read: each grid's own local operating day
        best = None
        for iso2 in ["ERCOT", "CAISO", "SPP", "MISO", "NYISO", "ISO-NE"]:
            if iso2 in held:
                continue
            tz = TZ[iso2]
            st = datetime(day.year, day.month, day.day, tzinfo=tz).astimezone(timezone.utc)
            en = st + timedelta(days=1)
            for x in rt:
                if x[0] == iso2 and st <= x[3] < en and (best is None or x[4] > best[4]):
                    best = x
        check(issue, "rt the highest of the day over the grids read", f"{v.replace(',', '')} {node} {iso}",
              f"{best[4]:.2f} {best[1]} {best[0]}" if best else None)
        explained_lines.add(i)
    # -- fuel close lines
    for i, l in enumerate(lines):
        m = re.match(r"- (Henry Hub natural gas|WTI Cushing crude|Brent crude): (-?[\d,]+\.\d{2}) (\S+) on (\d{4}-\d{2}-\d{2})\b(.*)$", l)
        if not m or i in explained_lines:
            continue
        label, v, unit, d1, rest = m.groups()
        rv = fuel[FUEL[label]].get(d1)
        check(issue, f"fuel {label} {d1}", v, f"{rv:.2f}" if rv is not None else None)
        a = re.search(r"\((\d+) days? before this issue\)", rest)
        if a:
            check(issue, f"fuel {label} age in days", a.group(1), str((d_issue - date.fromisoformat(d1)).days))
        explained_lines.add(i)
    # -- US48 demand
    for i, l in enumerate(lines):
        if "US48 demand peaked at" not in l and not l.startswith("**US48 demand"):
            continue
        ps = re.findall(r"peaked at ([\d,]+) MW in the hour starting (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) UTC", l)
        for k, (v, d, t) in enumerate(ps):
            d0 = datetime.fromisoformat(f"{d}T00:00:00+00:00")
            pk = peak(d0)
            check(issue, f"demand peak {d}", f"{v.replace(',', '')} at {t}", f"{pk[0]:.0f} at {pk[1]:%H:%M}" if pk else None)
        if ps:
            want = day.isoformat()
            check(issue, "demand peak is of the UTC day before the issue", ps[0][1], want)
        mp = re.search(r"so ([+-][\d.]+)% on the (week|year)", l)
        if mp and len(ps) >= 2:
            a, b = peak(datetime.fromisoformat(f"{ps[0][1]}T00:00:00+00:00")), peak(datetime.fromisoformat(f"{ps[1][1]}T00:00:00+00:00"))
            if a and b:
                check(issue, f"demand percent on the {mp.group(2)}", mp.group(1), f"{100 * (a[0] / b[0] - 1):+.1f}")
        explained_lines.add(i)

# ---- report
bad = [r for r in results if not r[4]]
print(f"figures re-done: {len(results)}; equal: {len(results) - len(bad)}; differ: {len(bad)}")
by = defaultdict(lambda: [0, 0])
for r in results:
    by[r[0]][0] += 1
    by[r[0]][1] += r[4]
for k in ISSUES:
    print(f"  {k}: {by[k][0]} re-done, {by[k][1]} equal")
print("\nDIFFER (printed | re-done):")
for r in bad:
    print(f"  {r[0]} | {r[1]} | printed {r[2]} | re-done {r[3]}")
print("\nALL:")
for r in results:
    print(f"  {'ok ' if r[4] else 'BAD'} {r[0]} | {r[1]} | {r[2]} | {r[3]}")
