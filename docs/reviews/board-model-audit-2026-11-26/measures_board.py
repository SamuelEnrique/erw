# Session 10206: one rule of the board changed at a time, measured on the page's own files (site/public/board/h and s).
#  1. battery spread: the day's highest hour less its lowest in either order (the board) against the best ordered spread
#     (charge in an hour before the hour it discharges), against 85 percent round-trip efficiency, and two hours a side;
#  2. spark spread: all 24 hours (the board) against the on-peak hours; 7.0 against EIA's fleet heat rate (heat_ref);
#  3. the 30-day mean with the days held against a mean that waits for 30 days.
# Main hubs of the public grids only; the last 365 complete local days the hourly file holds.
import collections
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import restate_board as R  # noqa: E402  (its days_of and on_peak: the rules written again from the note)

HUBS = ["ercot-hb-hubavg", "ercot-hb-west", "caiso-th-sp15-gen-apnd", "spp-sppnorth-hub"]
print("1. Battery spread, day-ahead, the last 365 complete days of each hub's hourly file")
for hub in HUBS:
    h = R.hourly(hub)
    days = R.days_of(h, "da")
    keep = sorted(days)[-365:]
    board = ordered = eff = two = 0.0
    rev = 0
    for d in keep:
        p = [v for *_, v in days[d]]
        hi, lo = max(p), min(p)
        board += hi - lo
        best, low = -1e18, p[0]
        for v in p[1:]:
            best = max(best, v - low)
            low = min(low, v)
        ordered += max(best, 0.0)
        if p.index(lo) > p.index(hi):
            rev += 1
        best85, low = 0.0, p[0]
        for v in p[1:]:
            best85 = max(best85, v - low / 0.85)
            low = min(low, v)
        eff += best85
        s = sorted(p)
        two += (s[-1] + s[-2]) / 2 - (s[0] + s[1]) / 2
    n = len(keep)
    print(f"  {hub}: {n} days {keep[0]} to {keep[-1]}; board's mean {board / n:.2f}; ordered {ordered / n:.2f} ({100 * (ordered / board - 1):+.1f}%);"
          f" ordered at 85% round trip {eff / n:.2f} ({100 * (eff / board - 1):+.1f}%); two hours a side, either order {two / n:.2f}; days the lowest hour came after the highest {rev} ({100 * rev / n:.0f}%)")

print("2. Spark spread, ERCOT Hub average, against the board's own row")
B = R.B
row = R.ROWS["ercot-hb-hubavg-spark"]
hh = dict(R.series("eia-henry-hub-spot"))
h = R.hourly("ercot-hb-hubavg")
days = R.days_of(h, "da")
last = R.day(row["last"]["t"])
win = [d for d in sorted(days) if last - dt.timedelta(days=30) < d <= last]
ref = row.get("heat_ref", {}).get("v")
alls, peaks, refs = [], [], []
for d in win:
    gd = next((d - dt.timedelta(days=k) for k in range(5) if d - dt.timedelta(days=k) in hh), None)
    if gd is None:
        continue
    p = [v for *_, v in days[d]]
    pk = [v for _, loc, v in days[d] if R.on_peak(loc, "ercot")]
    alls.append(sum(p) / len(p) - 7.0 * hh[gd])
    if pk:
        peaks.append(sum(pk) / len(pk) - 7.0 * hh[gd])
    if ref:
        refs.append(sum(p) / len(p) - ref * hh[gd])
print(f"  the 30 days to {last}: the board's rule (all hours, 7.0) {sum(alls) / len(alls):.2f} over {len(alls)} days (the row's 30-day avg {row['avg30']['v']:.2f} over {row['avg30']['n']});"
      f" on-peak hours, weekdays only {sum(peaks) / len(peaks):.2f} over {len(peaks)} days; EIA's fleet heat rate {ref} {sum(refs) / len(refs):.2f}")
print(f"  the latest day, {last}: board {row['last']['v']:.2f}; at {ref}: {row['inputs']['hub'] - ref * row['inputs']['gas']:.2f}")

print("3. The 30-day mean over the days held (the board) against a mean that needs all 30 days")
short = [(r["id"], r["avg30"]["n"]) for r in R.OK if r.get("avg30") and r["avg30"]["n"] < 30 and r["group"] in R_POWER] if (R_POWER := {"power", "peak", "spark", "da_rt", "battery", "as", "hubspread"}) else []
by = collections.Counter(n for _, n in short)
print(f"  power-group rows whose 30-day avg is of fewer than 30 days: {len(short)} of {sum(1 for r in R.OK if r.get('avg30') and r['group'] in R_POWER)}; by count of days {dict(sorted(by.items()))}")
print("  the header says \"30-day avg\"; the count is on hover only")
