"""Session 10225: Uri's comparisons with the baseline are by calendar day (2019 and 2020); the page's "largest shortfall
against the 2019 and 2020 average for the same day" restated, and the same with the weekday rule of the other events
(the same weekday 364 and 728 days earlier), where the table holds both days.

    python uri_weekday.py <event_window_daily.csv>
"""
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import restate as R  # noqa: E402

rows = R.read(sys.argv[1])
for var in ("net_generation_mwh", "demand_mwh"):
    v = {r["d"]: r["v"] for r in R.sel(rows, "uri_2021", "eia930:ERCO", var)}
    cal, wk = {}, {}
    for d in sorted(x for x in v if x.startswith("2021")):
        b = [v.get(f"{y}{d[4:]}") for y in ("2019", "2020")]
        if None not in b:
            cal[d] = v[d] - sum(b) / 2
        t = dt.date.fromisoformat(d)
        w = [v.get((t - dt.timedelta(days=o)).isoformat()) for o in (364, 728)]
        if None not in w:
            wk[d] = v[d] - sum(w) / 2
    lo_c = min(cal, key=cal.get)
    both = [d for d in cal if d in wk]
    lo_w = min(wk, key=wk.get)
    print(var, "calendar: lowest", lo_c, dt.date.fromisoformat(lo_c).strftime("%A"), round(cal[lo_c], 2), "| weekday rule: lowest", lo_w, round(wk[lo_w], 2),
          "| on", lo_c, "the weekday rule gives", round(wk.get(lo_c, float("nan")), 2), "| days held by both rules", len(both))
    if var == "demand_mwh":
        pos_c = [d for d in cal if "2021-02-09" <= d <= "2021-02-20" and cal[d] > 0]
        pos_w = [d for d in wk if "2021-02-09" <= d <= "2021-02-20" and wk[d] > 0]
        print("  demand above the baseline on 9 to 20 February: calendar", len(pos_c), "of 12; weekday rule", len(pos_w), "of", len([d for d in wk if "2021-02-09" <= d <= "2021-02-20"]))
