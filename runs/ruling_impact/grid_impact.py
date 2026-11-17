"""Session 7616 (portable-laptop): the ruling impact of the two lines marked "Changes a figure" under /grid in
docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads). Both are the Mix tab's lead
(site/components/grid/NowView.tsx): demand at the latest hour of eia930_all_demand, the exchange at the latest hour of the
network's hourly snapshot, carbon at the latest hour of carbon_intensity_hourly.

Line 1: all three figures at the newest hour all three hold, instead of each at its own newest hour.
Line 2: the lead's demand from the hourly snapshot (as the Network tab), instead of the daily-loaded table.

Reads the live set (read-only) and the snapshot fetched by grid_snapshot.py. No model call. MW are printed for the public
grids only; for ISO-NE, MISO and NYISO (held grids' own authorities) the hours and the change in percent only.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from live import q, retrieved  # noqa: E402
import grid_snapshot  # noqa: E402,F401  (fetches the snapshot afresh)

sys.stdout.reconfigure(encoding="utf-8")
snap = json.loads((HERE / "cache" / "grid_network_snapshot.json").read_text(encoding="utf-8"))
GRIDS = [("ERCOT", "ERCO"), ("CAISO", "CISO"), ("PJM", "PJM"), ("SPP", "SWPP"), ("MISO", "MISO"), ("NYISO", "NYIS"), ("ISO-NE", "ISNE"), ("Lower 48", "US48")]
HELD = {"MISO", "NYIS", "ISNE"}
for t in ("eia930_all_demand", "carbon_intensity_hourly"):
    r = retrieved("series", t)
    print(f"{t}: latest retrieved {r[0]}, source {r[1]}")
print(f"snapshot built {snap['built']}; exchange hours {snap['hours'][0]} to {snap['hours'][-1]}")
hours = [datetime.fromisoformat(h.replace("Z", "+00:00")) for h in snap["hours"]]
nodes = {n["id"]: n for n in snap["nodes"]}


def net(ba, i):
    """Net flow at hour i: the sum of mw on links from ba (a == ba) less links into ba; positive = out (export)."""
    s = 0.0
    for l in snap["links"]:
        v = l["mw"][i]
        if v is None:
            continue
        if l["a"] == ba:
            s += v
        elif l["b"] == ba:
            s -= v
    return s


def mw(ba, x):
    return "held grid: not written" if ba in HELD else f"{x:,.0f} MW"


def pct(a, b):
    return f"{(b - a) / a * 100:+.2f} percent" if a else "n/a"


print("\nERCOT's exchange at the snapshot's newest hour, to fix the sign: net out", round(net("ERCO", len(hours) - 1), 1), "MW (the page read 145 MW in on 16 November)")
for name, ba in GRIDS:
    ent = f"eia930:{ba}"
    d = q("select ts_utc, value from public.series where table_name='eia930_all_demand' and entity=%s and variable='demand_mw' order by ts_utc desc limit 1", (ent,))
    c = q("select ts_utc, value from public.series where table_name='carbon_intensity_hourly' and entity=%s order by ts_utc desc limit 1", (ent,))
    print(f"\n== {name} ({ent})")
    if not d:
        print("no demand in the live set")
        continue
    dts, dv = d[0]
    cts = c[0][0] if c else None
    xi = len(hours) - 1 if ba in nodes else None
    xts = hours[xi] if xi is not None else None
    print(f"default: demand {mw(ba, dv)} at {dts:%Y-%m-%d %H:%M} UTC; exchange at {xts:%Y-%m-%d %H:%M} UTC" if xts else f"default: demand {mw(ba, dv)} at {dts:%Y-%m-%d %H:%M} UTC; no exchange (not a node)", end="")
    print(f"; carbon at {cts:%Y-%m-%d %H:%M} UTC" if cts else "; no carbon")
    # line 1: the newest hour all three hold
    common = min(t for t in (dts, xts, cts) if t is not None)
    d1 = q("select value from public.series where table_name='eia930_all_demand' and entity=%s and variable='demand_mw' and ts_utc=%s", (ent, common))
    if d1:
        print(f"line 1: the common hour {common:%Y-%m-%d %H:%M} UTC: demand {mw(ba, d1[0][0])} ({(dts - common).total_seconds() / 3600:.0f} hours older): {pct(dv, d1[0][0])}"
              + ("" if ba in HELD else f", {d1[0][0] - dv:+,.0f} MW"))
    if xts and common in hours:
        j = hours.index(common)
        a, b = net(ba, xi), net(ba, j)
        print(f"line 1: the exchange from {xts:%m-%d %H:%M} to {common:%m-%d %H:%M} UTC: net out {('held grid: not written' if ba in HELD else f'{a:,.0f} to {b:,.0f} MW ({b - a:+,.0f} MW)')}")
    elif xts:
        print(f"line 1: the common hour is before the snapshot's window ({hours[0]:%m-%d %H:%M} UTC): the exchange there is not in the snapshot")
    # line 2: the snapshot's demand
    n = nodes.get(ba)
    if n and n.get("demand_mw") is not None:
        sts = datetime.fromisoformat(n["demand_ts"].replace("Z", "+00:00"))
        print(f"line 2: the snapshot's demand {mw(ba, n['demand_mw'])} at {sts:%Y-%m-%d %H:%M} UTC, {(sts - dts).total_seconds() / 3600:.0f} hours newer than the table's: "
              f"{pct(dv, n['demand_mw'])}" + ("" if ba in HELD else f", {n['demand_mw'] - dv:+,.0f} MW"))
    else:
        print("line 2: the snapshot holds no demand for it")
print(f"\nread at {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC")
