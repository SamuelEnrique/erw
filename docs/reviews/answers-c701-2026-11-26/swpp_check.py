"""Data request 16 of docs/state/data_requests_five_tools.md (the curtailment audit, finding 7): EIA-930's SWPP wind and
solar by month, 2025 and 2026, beside SWPW's (SPP's western area) own, from eia930_ba_supply_hourly as held here. If
SWPW's output stopped being reported apart from April 2026 while SWPP's rose by about as much, SWPP took it in."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

p = "warehouse/output/eia930_ba_supply_hourly.csv"
parts = []
for ch in pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, chunksize=1_000_000,
                      usecols=["entity", "variable", "ts_utc", "value"]):
    ch = ch[ch["entity"].str.contains("SWPP|SWPW", regex=True) & (ch["variable"] == "net_generation_mw")
            & (ch["ts_utc"] >= "2025-01-01")]
    if len(ch):
        parts.append(ch)
d = pd.concat(parts)
d["month"] = d["ts_utc"].str[:7]
d["v"] = pd.to_numeric(d["value"], errors="coerce")
g = d.groupby(["entity", "variable", "month"]).agg(mwh=("v", "sum"), hours=("v", "size")).reset_index()
print(sorted(set(d["entity"])), sorted(set(d["variable"])))
piv = g.pivot_table(index="month", columns=["entity", "variable"], values="mwh", aggfunc="sum").round(0)
print(piv.to_string())
