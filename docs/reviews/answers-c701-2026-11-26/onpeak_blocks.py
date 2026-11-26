"""Window D's data request 18 (the trader view audit, finding 5): for NYISO's and ISO-NE's zones, the last twelve whole
local months held, day-ahead: the on-peak and off-peak means under two blocks, hours ending 7 to 22 (the trader view's,
hours starting 06:00 to 21:00) and hours ending 8 to 23 (starting 07:00 to 22:00), weekdays that are not NERC
holidays (trader_view.nerc_holidays), and the differences. Only whole days (every hour held). Counts and means only;
the two grids are held, so nothing here is published."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
sys.path.insert(0, "warehouse/derived")
import iso_prices as ip  # noqa: E402
from trader_view import nerc_holidays  # noqa: E402

TZ = "America/New_York"
SETS = [("nyiso", "iso_zone_prices_history", "nyiso_dam", "2025-11-01", "2026-11-01"),
        ("isone", "isone_zone_prices_history", "isone_dam", "2025-10-01", "2026-10-01")]
rows = []
for grid, table, market, a, b in SETS:
    p = f"warehouse/output/{table}.csv"
    parts = []
    for ch in pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, chunksize=500000,
                          usecols=["entity", "ts_utc", "value", "market"]):
        parts.append(ch[ch["market"] == market])
    d = pd.concat(parts)
    d["t"] = pd.to_datetime(d["ts_utc"], utc=True).dt.tz_convert(TZ)
    d = d[(d["t"] >= pd.Timestamp(a, tz=TZ)) & (d["t"] < pd.Timestamp(b, tz=TZ))]
    d["v"] = d["value"].astype(float)
    d["day"] = d["t"].dt.date
    d["h"] = d["t"].dt.hour
    n = d.groupby(["entity", "day"])["t"].transform("nunique")
    want = d["day"].map(lambda x: int((pd.Timestamp(x, tz=TZ) + pd.DateOffset(days=1) - pd.Timestamp(x, tz=TZ)) / pd.Timedelta(hours=1)))
    d = d[n == want]
    hol = set().union(*[nerc_holidays(y) for y in (2025, 2026)])
    work = d["day"].map(lambda x: x.weekday() < 5 and x not in hol)
    for ent, g in d.groupby("entity"):
        w = work.loc[g.index]
        r = dict(grid=grid, zone=ent.split(":", 1)[1], days=g["day"].nunique(), first=str(g["day"].min()), last=str(g["day"].max()))
        for name, lo, hi in (("he7_22", 6, 21), ("he8_23", 7, 22)):
            on = g[w & g["h"].between(lo, hi)]["v"]
            off = g[~(w & g["h"].between(lo, hi))]["v"]
            r[f"{name}_on"], r[f"{name}_off"], r[f"{name}_hours_on"] = round(on.mean(), 4), round(off.mean(), 4), len(on)
        r["on_diff_usd"] = round(r["he8_23_on"] - r["he7_22_on"], 4)
        r["on_diff_pct"] = round(100 * r["on_diff_usd"] / r["he7_22_on"], 3)
        r["off_diff_usd"] = round(r["he8_23_off"] - r["he7_22_off"], 4)
        r["off_diff_pct"] = round(100 * r["off_diff_usd"] / r["he7_22_off"], 3)
        rows.append(r)
out = pd.DataFrame(rows)
pd.set_option("display.width", 250)
print(out.to_string(index=False))
out.to_csv("runs/c701/onpeak_blocks.csv", index=False)
