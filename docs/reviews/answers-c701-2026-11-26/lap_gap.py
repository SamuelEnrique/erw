"""Chain 701, data request five_tools 7 (window D's datacenter audit, finding 8): CAISO's default load aggregation
points against the matching trading hub, day-ahead, November 2025 to October 2026, a flat load (every hour weighs the
same). Read from price_congestion_hourly (CAISO OASIS PRC_LMP, DAM), variable lmp_dam, hours where both are held.
Prints the means and writes runs/c701/lap_gap_dam.csv. Months are Pacific clock months (CAISO's operating day)."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

P = "warehouse/output/price_congestion_hourly.csv"
PAIRS = {"DLAP_PGAE-APND": "TH_NP15_GEN-APND", "DLAP_SCE-APND": "TH_SP15_GEN-APND", "DLAP_SDGE-APND": "TH_SP15_GEN-APND"}
want = set(PAIRS) | set(PAIRS.values())
parts = []
for ch in pd.read_csv(P, skiprows=ip.header_rows(P), dtype=str, keep_default_na=False, chunksize=500000,
                      usecols=["entity", "variable", "ts_utc", "value", "market", "node"]):
    ch = ch[(ch["variable"] == "lmp_dam") & ch["node"].isin(want)]
    if len(ch):
        parts.append(ch)
d = pd.concat(parts)
d["t"] = pd.to_datetime(d["ts_utc"], utc=True)
d["local"] = d["t"].dt.tz_convert("America/Los_Angeles")
d = d[(d["local"] >= "2025-11-01") & (d["local"] < "2026-11-01")]
d["v"] = d["value"].astype(float)
w = d.pivot_table(index="t", columns="node", values="v", aggfunc="first")
rows = []
for lap, hub in PAIRS.items():
    both = w[[lap, hub]].dropna()
    rows.append(dict(lap=lap, hub=hub, market="day-ahead", hours=len(both), lap_mean=round(both[lap].mean(), 4),
                     hub_mean=round(both[hub].mean(), 4), gap_usd_mwh=round((both[lap] - both[hub]).mean(), 4),
                     first=both.index.min().isoformat(), last=both.index.max().isoformat()))
out = pd.DataFrame(rows)
print(out.to_string(index=False))
out.to_csv("runs/c701/lap_gap_dam.csv", index=False)
