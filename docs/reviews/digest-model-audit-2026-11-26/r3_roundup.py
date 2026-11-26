"""Session 10235, the Roundup audit: the warehouse-table figures of the three newest Roundups (W43, W44, W45) re-done
from the main checkout's CSVs, by code that imports nothing of the ERW.

  the main hubs' weekly day-ahead means over the ISO's local week (Monday 00:00 to the next Monday 00:00, every hour
  held, half-up to the cent), the week before, the change;
  the fuel table (the close on each printed day, the change and percent);
  the week's highest real-time price (the value at its node and interval; the highest of the grids' rows retrieved
  before the issue was written; the highest of the grids' rows held now);
  US48's peak hour of the week and the count of hours it rests on;
  the opening number and the five numbers where they repeat a table's figure.

Run: python r3_roundup.py <output dir> <docs/roundup dir> > r3_roundup.out
"""
import csv
import os
import re
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

OUT, RD = sys.argv[1], sys.argv[2]
WEEKS = {"2026-W43": (date(2026, 10, 19), "2026-10-25T23:20"), "2026-W44": (date(2026, 10, 26), "2026-11-01T23:28"),
         "2026-W45": (date(2026, 11, 2), "2026-11-08T23:26")}
TZ = {"ERCOT": ZoneInfo("America/Chicago"), "SPP": ZoneInfo("America/Chicago"), "CAISO": ZoneInfo("America/Los_Angeles"),
      "NYISO": ZoneInfo("America/New_York"), "ISO-NE": ZoneInfo("America/New_York"), "MISO": timezone(timedelta(hours=-5))}
FUEL = {"Henry Hub natural gas": "eia:henry_hub", "WTI Cushing crude": "eia:wti_cushing", "Brent crude": "eia:brent"}


def rows(name):
    with open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="") as f:
        yield from csv.DictReader(ln for ln in f if not ln.startswith("#"))


def ts(s):
    return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def mean2(vals):
    d = [Decimal(repr(float(v))) for v in vals]
    return (sum(d) / len(d)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


dam = defaultdict(dict)
for r in rows("iso_dam_hub_prices"):
    dam[(r["entity"].split(":")[0].upper(), r["node"])][ts(r["ts_utc"])] = float(r["value"])
for iso, name in (("NYISO", "nyiso_dam_zone_prices"), ("ISO-NE", "isone_dam_zone_prices")):
    for r in rows(name):
        dam[(iso, r["node"])][ts(r["ts_utc"])] = float(r["value"])
rt = []
for name in ("iso_rtm_hub_prices", "nyiso_rtm_zone_prices", "isone_rtm_zone_prices", "isone_rtm_zone_prices_hourly"):
    for r in rows(name):
        g = {"ercot": "ERCOT", "caiso": "CAISO", "spp": "SPP", "miso": "MISO", "nyiso": "NYISO", "isone": "ISO-NE"}[r["entity"].split(":")[0]]
        rt.append((g, r["node"], ts(r["ts_utc"]), float(r["value"]), r["retrieved_at"]))
fuel = defaultdict(dict)
for r in rows("eia_fuel_spot_prices"):
    fuel[r["entity"]][r["ts_utc"][:10]] = float(r["value"])
demand = {}
for r in rows("eia930_all_demand"):
    if r["entity"] == "eia930:US48" and r["variable"] == "demand_mw":
        demand[ts(r["ts_utc"])] = (float(r["value"]), r["retrieved_at"])

res = []


def check(week, what, printed, redone):
    res.append((week, what, str(printed), str(redone), str(printed) == str(redone)))


def week_mean(iso, node, monday):
    tz = TZ[iso]
    st = datetime(monday.year, monday.month, monday.day, tzinfo=tz).astimezone(timezone.utc)
    nm = monday + timedelta(days=7)
    en = datetime(nm.year, nm.month, nm.day, tzinfo=tz).astimezone(timezone.utc)
    exp = int((en - st).total_seconds() // 3600)
    vals = [v for t, v in dam.get((iso, node), {}).items() if st <= t < en]
    return (mean2(vals) if len(vals) == exp else f"{len(vals)} of {exp} hours"), st, en


for week, (monday, written) in WEEKS.items():
    md = open(os.path.join(RD, week + ".md"), encoding="utf-8").read()
    for l in md.split("\n"):
        c = [x.strip() for x in l.split("|")[1:-1]] if l.startswith("| ") else []
        if len(c) >= 5 and c[0] in TZ and c[0] != "MISO" and c[1]:
            this, _, _ = week_mean(c[0], c[1], monday)
            before, _, _ = week_mean(c[0], c[1], monday - timedelta(days=7))
            if re.fullmatch(r"-?[\d,]+\.\d{2}", c[2]):
                check(week, f"week mean {c[0]} {c[1]}", c[2], this)
            else:
                m = re.search(r"\((\d+) of (\d+) hours\)", c[2])
                if m:
                    check(week, f"week mean {c[0]} {c[1]} hours held (now; at writing fewer may have been)", f"{m.group(1)} of {m.group(2)} hours", this)
            if re.fullmatch(r"-?[\d,]+\.\d{2}", c[3]):
                check(week, f"week before mean {c[0]} {c[1]}", c[3], before)
            if re.fullmatch(r"[+-][\d.]+", c[4]) and not isinstance(this, str) and not isinstance(before, str):
                check(week, f"week change {c[0]} {c[1]}", c[4], f"{float(this - before):+.2f}")
        if len(c) >= 5 and c[0] in FUEL:
            m1 = re.fullmatch(r"([\d.,]+) \S+ on (\d{4}-\d{2}-\d{2})", c[1])
            m0 = re.fullmatch(r"([\d.,]+) on (\d{4}-\d{2}-\d{2})", c[2])
            mc = re.fullmatch(r"([+-][\d.]+) \(([+-][\d.]+)%\)", c[3])
            s = fuel[FUEL[c[0]]]
            if m1:
                check(week, f"fuel {c[0]} {m1.group(2)}", m1.group(1), f"{s.get(m1.group(2)):.2f}" if m1.group(2) in s else None)
            if m0:
                check(week, f"fuel {c[0]} {m0.group(2)} (a week before)", m0.group(1), f"{s.get(m0.group(2)):.2f}" if m0.group(2) in s else None)
            if m1 and m0 and mc and m1.group(2) in s and m0.group(2) in s:
                a, b = s[m1.group(2)], s[m0.group(2)]
                check(week, f"fuel {c[0]} change", mc.group(1), f"{a - b:+.2f}")
                check(week, f"fuel {c[0]} percent", mc.group(2), f"{100 * (a - b) / b:+.1f}")
                # the close a week before: the newest close at or before seven days before the newest
                cut = (date.fromisoformat(m1.group(2)) - timedelta(days=7)).isoformat()
                prior = sorted(k for k in s if k <= cut)
                check(week, f"fuel {c[0]} the close a week before is the newest on or before {cut}", m0.group(2), prior[-1] if prior else None)
        m = re.match(r"\*\*Highest real-time price of the week:\*\* (-?[\d,]+\.\d{2}) USD/MWh at (.+?) \(([A-Z-]+)\), interval starting (\S+) (\S+) local \((\S+) (\S+) UTC\)", l)
        if m:
            v, node, iso, ld, lt, ud, ut = m.groups()
            t = datetime.fromisoformat(f"{ud}T{ut}:00+00:00")
            hit = [x for x in rt if x[0] == iso and x[1] == node and x[2] == t]
            check(week, f"rt week high {iso} {node} at {ud} {ut}Z", v.replace(",", ""), f"{max(h[3] for h in hit):.2f}" if hit else "row not in this copy")
            held = {"NYISO", "ISO-NE", "MISO"}   # every one of the three weeks is after 21 October 2026
            best_now = best_then = best_open = None
            for x in rt:
                tz = TZ[x[0]]
                st = datetime(monday.year, monday.month, monday.day, tzinfo=tz).astimezone(timezone.utc)
                if not (st <= x[2] < st + timedelta(days=7)):
                    continue
                if best_now is None or x[3] > best_now[3]:
                    best_now = x
                if x[4][:16] <= written and (best_then is None or x[3] > best_then[3]):
                    best_then = x
                if x[0] not in held and x[4][:16] <= written and (best_open is None or x[3] > best_open[3]):
                    best_open = x
            fmt = lambda x: f"{x[3]:.2f} {x[1]} {x[0]} {x[2]:%Y-%m-%d %H:%M}Z" if x else None   # noqa: E731
            check(week, "rt the week's highest among rows retrieved before the issue (every grid)", f"{v} {node} {iso}", fmt(best_then))
            check(week, "rt the week's highest among rows retrieved before the issue (grids not held)", f"{v} {node} {iso}", fmt(best_open))
            check(week, "rt the week's highest held now (every grid in this copy)", f"{v} {node} {iso}", fmt(best_now))
        m = re.match(r"\*\*US48 peak demand of the week:\*\* ([\d,]+) MW in the hour starting (\S+) (\S+) UTC.*from (\d+) hours of the week to (\S+) (\S+) UTC", l)
        if m:
            v, d, t, n, ed, et = m.groups()
            st = datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)
            wk = {k: x for k, x in demand.items() if st <= k < st + timedelta(days=7)}
            then = {k: x for k, x in wk.items() if x[1][:16] <= written}
            top = max(wk.items(), key=lambda kv: kv[1][0]) if wk else None
            topt = max(then.items(), key=lambda kv: kv[1][0]) if then else None
            check(week, "US48 week peak among rows retrieved before the issue", f"{v.replace(',', '')} at {d} {t}",
                  f"{topt[1][0]:.0f} at {topt[0]:%Y-%m-%d %H:%M}" if topt else None)
            check(week, "US48 week peak held now", f"{v.replace(',', '')} at {d} {t}", f"{top[1][0]:.0f} at {top[0]:%Y-%m-%d %H:%M}" if top else None)
            check(week, "US48 hours of the week held now (the issue's count, then)", n, len(wk))
    # the five numbers and the opening repeat a table's figure: the same string must stand in the numbers section
    for l in md.split("\n"):
        m = re.match(r"- \*\*US48 peak demand:\*\* ([\d,]+) MW in the hour starting (\S+ \S+) UTC", l)
        if m:
            check(week, "five numbers: US48 peak says how many hours it rests on", "no count of hours in the line", "the numbers section: " + (re.search(r"from \d+ hours of the week", md).group(0) if re.search(r"from \d+ hours of the week", md) else "none"))

bad = [r for r in res if not r[4]]
print(f"figures re-done: {len(res)}; equal: {len(res) - len(bad)}; differ: {len(bad)}")
for r in res:
    print(f"  {'ok ' if r[4] else 'BAD'} {r[0]} | {r[1]} | printed {r[2]} | re-done {r[3]}")
