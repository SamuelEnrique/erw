"""Session 10227 (play audit): each complete Central day's mean of ERCOT's hub average real-time price in the live table
iso_rtm_hub_prices (the main copy's, read only)."""
import os
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")


def local_day(ts):
    return datetime.strptime(ts[:13], "%Y-%m-%dT%H").replace(tzinfo=timezone.utc).astimezone(CT).strftime("%Y-%m-%d")


def need(day):
    a = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=CT)
    b = (a + timedelta(days=1)).replace(tzinfo=CT)
    return int((b.astimezone(timezone.utc) - a.astimezone(timezone.utc)).total_seconds() // 900)


def rtm_day_means(out_dir):
    by = {}
    with open(os.path.join(out_dir, "iso_rtm_hub_prices.csv"), encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("ercot:HB_HUBAVG,spp_rtm,"):
                continue
            e, v, ts, val = ln.split(",", 4)[:4]
            x = by.setdefault(local_day(ts), [0.0, 0])
            x[0] += float(val); x[1] += 1
    return {d: s / n for d, (s, n) in by.items() if n == need(d)}
