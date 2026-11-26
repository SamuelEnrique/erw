"""Window D's data request 45 (the supply audit, finding 4): eia_basin_production_monthly's monthly values as first
written against as held now, 2025 and 2026, from three archive vintages (restore.py --from-bucket --as-of 2026-10-01,
2026-10-20, 2026-11-05: runs/c701/basin/). For each vintage, every region-variable-month of 2025 and 2026 it shares with
today's table: how far the value moved, in percent; and the newest months of each vintage separately. Counts only."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402


def t(p):
    d = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
    d["v"] = pd.to_numeric(d["value"], errors="coerce")
    return d[d["ts_utc"].str[:4].isin(["2025", "2026"])]


now = t("warehouse/output/eia_basin_production_monthly.csv")
key = ["entity", "variable", "ts_utc"]
print("today: newest month", now["ts_utc"].max()[:7], "| variables", sorted(set(now["variable"]))[:6])
for tag in ("2026-10-01", "2026-10-20", "2026-11-05"):
    old = t(f"runs/c701/basin/asof_{tag}.csv")
    if old.empty:
        print(f"== as of {tag}: the table was not yet in the archive (no rows)")
        continue
    m = old.merge(now, on=key, suffixes=("_then", "_now"))
    m = m[m["v_then"].abs() > 0]
    m["pct"] = 100 * (m["v_now"] - m["v_then"]) / m["v_then"]
    newest = old["ts_utc"].max()
    last3 = sorted(set(old["ts_utc"]))[-3:]
    n3 = m[m["ts_utc"].isin(last3)]
    print(f"== as of {tag}: newest month {newest[:7]}; shared values {len(m)}; moved at all {int((m['pct'].abs() > 1e-9).sum())}; "
          f"more than 1 percent {int((m['pct'].abs() > 1).sum())}; largest {m['pct'].abs().max():.2f} percent")
    print(f"   its three newest months ({last3[0][:7]} to {last3[-1][:7]}): {len(n3)} values, mean absolute move {n3['pct'].abs().mean():.2f} percent, "
          f"largest {n3['pct'].abs().max():.2f}")
    print(m.reindex(m["pct"].abs().sort_values(ascending=False).index)[["entity", "variable", "ts_utc", "v_then", "v_now", "pct"]].head(6).round(3).to_string(index=False))
