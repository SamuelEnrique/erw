"""Session 7612 (portable-laptop): the ruling impact of the one line marked "Changes a figure" under
"Site-wide: the Digest and the Roundup" in docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads):
should the Digest's US48 day stay the UTC day, which splits the US evening peak?

The Digest (warehouse/news/brief.py, demand_lines) writes "US48 demand, yesterday: peaked at X MW in the hour starting
... UTC", the peak of the UTC day before the issue, and its change against the same weekday a week (or a year) before.
This script recomputes that line for every day the live set holds whole, under the UTC day (the default) and under a
US day (Eastern, and Central beside it). Reads eia930_all_demand, entity eia930:US48, variable demand_mw, from the live
set, read-only. No model call.
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from live import q, retrieved  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")

r = retrieved("series", "eia930_all_demand")
print(f"eia930_all_demand: latest retrieved {r[0]}, source {r[1]}")
rows = q("select ts_utc, value from public.series where table_name='eia930_all_demand' and entity='eia930:US48' "
         "and variable='demand_mw' order by ts_utc")
s = pd.Series([v for _, v in rows], index=pd.DatetimeIndex([t for t, _ in rows]).tz_convert("UTC"))
print(f"hours held: {len(s)}, {s.index.min()} to {s.index.max()}")


def daily(tz):
    loc = s.tz_convert(tz)
    g = loc.groupby(loc.index.date)
    out = {}
    for d, x in g:
        if len(x) < 23:      # a whole local day (23 or 25 hours on a clock change)
            continue
        i = x.idxmax()
        out[d] = (x.max(), i.tz_convert("UTC"), len(x))
    return out


utc = daily("UTC")
et = daily("America/New_York")
ct = daily("America/Chicago")
days = sorted(set(utc) & set(et) & set(ct))
print(f"days whole under all three clocks: {len(days)} ({days[0]} to {days[-1]})")

late = [d for d in days if utc[d][1].hour == 23]
print(f"days whose UTC-day peak falls in the last hour (23:00 UTC): {len(late)} of {len(days)}")


def compare(name, other):
    moved = [(d, utc[d][0], other[d][0]) for d in days if abs(other[d][0] - utc[d][0]) > 0.5]
    print(f"\n== the UTC day against the {name} day")
    print(f"days whose peak MW changes: {len(moved)} of {len(days)}")
    hours = sum(1 for d in days if other[d][1] != utc[d][1])
    print(f"days whose peak hour changes: {hours} of {len(days)}")
    if moved:
        ch = [(d, b - a, (b - a) / a * 100) for d, a, b in moved]
        big = max(ch, key=lambda t: abs(t[1]))
        print(f"largest change: {big[0]}: {utc[big[0]][0]:,.0f} MW ({utc[big[0]][1]:%H:%M} UTC) to {other[big[0]][0]:,.0f} MW "
              f"({other[big[0]][1]:%Y-%m-%d %H:%M} UTC): {big[1]:+,.0f} MW, {big[2]:+.2f} percent")
        print(f"mean change over the days that move: {sum(c[1] for c in ch) / len(ch):+,.0f} MW, {sum(c[2] for c in ch) / len(ch):+.2f} percent")
        print(f"mean change over all days: {sum(c[1] for c in ch) / len(days):+,.0f} MW")
        for d, dm, dp in sorted(ch, key=lambda t: -abs(t[1]))[:5]:
            print(f"  {d}: {utc[d][0]:,.0f} ({utc[d][1]:%H:%M} UTC) to {other[d][0]:,.0f} ({other[d][1]:%m-%d %H:%M} UTC), {dm:+,.0f} MW, {dp:+.2f} percent")
    # the Digest's change against the same weekday a week before
    wk = []
    for d in days:
        p = d - pd.Timedelta(days=7)
        if p in utc and p in other:
            a = (utc[d][0] - utc[p][0]) / utc[p][0] * 100
            b = (other[d][0] - other[p][0]) / other[p][0] * 100
            wk.append((d, a, b))
    moved_wk = [t for t in wk if round(t[1], 1) != round(t[2], 1)]
    print(f"the week-before change (one decimal, as the Digest writes it): {len(moved_wk)} of {len(wk)} days move")
    if moved_wk:
        big = max(moved_wk, key=lambda t: abs(t[2] - t[1]))
        print(f"largest: {big[0]}: {big[1]:+.1f} percent to {big[2]:+.1f} percent ({big[2] - big[1]:+.1f} points)")
        sign = [t for t in wk if (t[1] > 0) != (t[2] > 0)]
        print(f"days whose change turns sign: {len(sign)}")


compare("Eastern", et)
compare("Central", ct)
