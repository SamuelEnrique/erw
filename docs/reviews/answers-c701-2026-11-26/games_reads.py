"""Window D's data request 51 (the games audit, findings 1 and 7), parts (a) and (b), from the data machine's tables.
(a) CAISO SP15 day-ahead (iso_dam_hub_prices, caiso:TH_SP15_GEN-APND, lmp_dam) on the Pacific days 2026-04-27 and
2026-07-24: hours held, mean, lowest and highest hour. (b) site/data/ev_prices.json's gasoline per state (its week) against
eia_regional_retail_fuel_prices: the same week's value, and the 52-week mean to that week. Counts only."""
import json
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402


def t(name, cols):
    p = f"warehouse/output/{name}.csv"
    return pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, usecols=cols)


print("== (a)")
h = t("price_congestion_hourly", ["entity", "variable", "ts_utc", "value", "market"])  # the rolling iso_dam_hub_prices starts 2026-08-26; this table matched it hour for hour (request 29)
h = h[(h["entity"] == "caiso:TH_SP15_GEN-APND") & (h["variable"] == "lmp_dam")].copy()
h["day"] = pd.to_datetime(h["ts_utc"], utc=True).dt.tz_convert("America/Los_Angeles").dt.date.astype(str)
print("held from", h["ts_utc"].min(), "to", h["ts_utc"].max())
for d in ("2026-04-27", "2026-07-24"):
    x = h[h["day"] == d]["value"].astype(float)
    print(d, "hours", len(x), "| mean", round(x.mean(), 2) if len(x) else None, "| low", x.min() if len(x) else None, "| high", x.max() if len(x) else None)

print("== (b)")
ev = json.load(open("site/data/ev_prices.json", encoding="utf-8"))
f = t("eia_regional_retail_fuel_prices", ["entity", "variable", "ts_utc", "value"])
f["v"] = pd.to_numeric(f["value"], errors="coerce")
print("fuel table to", f["ts_utc"].max()[:10], "| variables", sorted(set(f["variable"]))[:6])
st = ev["states"]
print("an EV state entry:", json.dumps(st[0])[:500])
print("us:", json.dumps(ev["us"])[:300])
rows = []
for s in [dict(code="US", name="US", **ev["us"])] + st:
    g = s["gas"]
    x = f[f["entity"] == g["entity"]].sort_values("ts_utc")
    wk = x[x["ts_utc"].str[:10] == g["ts"]]
    to = x[x["ts_utc"].str[:10] <= g["ts"]].tail(52)
    rows.append(dict(code=s["code"], file=g["value"], table_same_week=float(wk["v"].iloc[0]) if len(wk) else None,
                     mean_52w=round(to["v"].mean(), 3), weeks=len(to), newest=x["ts_utc"].max()[:10]))
r = pd.DataFrame(rows)
r["equal"] = (r["file"] - r["table_same_week"]).abs() < 1e-9
r["mean_vs_week_pct"] = (100 * (r["mean_52w"] / r["file"] - 1)).round(2)
print("cells", len(r), "| equal to the table's same week:", int(r["equal"].sum()), "| 52 weeks held for:", int((r["weeks"] == 52).sum()))
print(r.sort_values("mean_vs_week_pct").head(5).to_string(index=False))
print(r.sort_values("mean_vs_week_pct").tail(5).to_string(index=False))
print("US:", r[r["code"] == "US"].to_string(index=False))
