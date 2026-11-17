"""Session 7614 (portable-laptop): the ruling impact of the one line marked "Changes a figure" under
"Site-wide: the warehouse's sources and publishers' terms" in docs/reviews/rulings-for-samuel-2026-11-17.md
(branch wip/7560-six-reads): should ERCOT's price days of 7 to 9 November be refilled?

The refilled prices are held nowhere (the data machine's note: only through the paths its ruling 2 freezes), so the figure
under the other choice cannot be computed. This script measures what the gap takes out of each ERCOT price table of the
live set, and the figures a reader sees now that stand on a window holding the gap. Read-only. No model call.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from live import q, retrieved  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
CT = "America/Chicago"

print("== the gap, by table (ERCOT entities, Central days 1 to 16 November 2026: rows a day)")
tables = ["iso_dam_hub_prices", "iso_rtm_hub_prices", "ercot_hub_prices_daily", "iso_trader_daily", "price_board_latest",
          "price_board_peak_offpeak", "price_board_spreads", "ercot_rtm_price_adders"]
for t in tables:
    r = retrieved("series", t)
    rows = dict(q("select (ts_utc at time zone %s)::date, count(*) from public.series where table_name=%s and entity like 'ercot:%%' "
                  "and ts_utc >= '2026-11-01 05:00+00' and ts_utc < '2026-11-17 06:00+00' group by 1", (CT, t)))
    days = sorted(rows)
    full = max(rows.values()) if rows else 0
    missing = [f"{d:%m-%d}" for d in sorted(set(days[0] + __import__('datetime').timedelta(days=i) for i in range((days[-1] - days[0]).days + 1)) - set(days))] if days else []
    print(f"{t} (retrieved {r[0]:%Y-%m-%d %H:%M} UTC): {len(days)} days held, {days[0]:%m-%d} to {days[-1]:%m-%d}; days absent {missing or 'none'}")

print("\n== 1 to 15 November (Central days; 1 November has 25 hours, the clock change), ERCOT hub average (HB_HUBAVG)")
H = 15 * 24 + 1
n, avg = q("select count(*), avg(value) from public.series where table_name='iso_dam_hub_prices' and entity='ercot:HB_HUBAVG' "
           "and ts_utc >= '2026-11-01 05:00+00' and ts_utc < '2026-11-16 06:00+00'")[0]
print(f"day-ahead, the hourly table: {n} hours held of {H}: mean {avg:.2f} USD/MWh; {H - n} hours absent ({(H - n) / H * 100:.1f} percent)")
n, avg = q("select count(*), avg(value) from public.series where table_name='iso_rtm_hub_prices' and entity='ercot:HB_HUBAVG' "
           "and ts_utc >= '2026-11-01 05:00+00' and ts_utc < '2026-11-16 06:00+00'")[0]
print(f"real time, the 15-minute table: {n} intervals held of {H * 4}: mean {avg:.2f} USD/MWh; {H * 4 - n} absent ({(H * 4 - n) / (H * 4) * 100:.1f} percent)")

print("\n== the price board's windows (price_board_latest), ERCOT entities")
rows = q("select entity, variable, value, ts_utc from public.series where table_name='price_board_latest' and entity like 'ercot:%' "
         "and variable in ('da_avg_30d','da_days_30d','da_avg_7d','da_days_7d','rt_avg_30d','rt_days_30d','rt_avg_7d','rt_days_7d') order by 1,2")
by = {}
for e, v, val, ts in rows:
    by.setdefault(e, {})[v] = (val, ts)
for e, d in by.items():
    parts = [f"{k} {d[k][0]:g}" for k in sorted(d)]
    print(f"{e} (as of {min(x[1] for x in d.values()):%Y-%m-%d}): " + "; ".join(parts))
