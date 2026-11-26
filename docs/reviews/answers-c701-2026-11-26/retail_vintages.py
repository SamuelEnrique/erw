"""Window D's data request 23 (the demand audit, finding 4): eia_retail_sales_monthly as first published against as held
now. Two earlier vintages rebuilt from the ERW's archive (restore.py --from-bucket --as-of 2026-10-01 and 2026-10-28,
runs/c701/retail/). For each vintage's newest twelve months, each state and sector's 12-month total of sales (the
variable the consumption view ranks) in that vintage against today's table over the same months; and every month the
two vintages share, the largest revisions. Counts only."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402


def t(p):
    d = pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)
    d["v"] = pd.to_numeric(d["value"], errors="coerce")
    return d


now = t("warehouse/output/eia_retail_sales_monthly.csv")
print("variables:", sorted(set(now["variable"]))[:12])
var = "sales_mwh" if "sales_mwh" in set(now["variable"]) else sorted(v for v in set(now["variable"]) if "sales" in v)[0]
print("compared:", var)
key = ["entity", "variable", "ts_utc"]
pd.set_option("display.width", 250)
for tag in ("2026-10-01", "2026-10-28"):
    old = t(f"runs/c701/retail/asof_{tag}.csv")
    o, n = old[old["variable"] == var], now[now["variable"] == var]
    last = o["ts_utc"].max()
    months = sorted(set(o["ts_utc"]))[-12:]
    m = o[o["ts_utc"].isin(months)].merge(n[n["ts_utc"].isin(months)], on=key, suffixes=("_then", "_now"))
    tot = m.groupby("entity")[["v_then", "v_now"]].sum()
    full = m.groupby("entity").size() == 12
    tot = tot[full]
    tot["rev"] = tot["v_now"] - tot["v_then"]
    tot["rev_pct"] = 100 * tot["rev"] / tot["v_then"]
    print(f"== vintage as of {tag}: newest month {last[:7]}, twelve months {months[0][:7]} to {months[-1][:7]}; "
          f"{len(tot)} state-sector totals with all twelve in both")
    print("  totals revised by more than 0.1 percent:", int((tot["rev_pct"].abs() > 0.1).sum()),
          "| by more than 1 percent:", int((tot["rev_pct"].abs() > 1).sum()),
          "| mean absolute revision:", round(tot["rev_pct"].abs().mean(), 3), "percent")
    print(tot.reindex(tot["rev_pct"].abs().sort_values(ascending=False).index).head(10).round(3).to_string())
    mm = o.merge(n, on=key, suffixes=("_then", "_now"))
    mm["rev_pct"] = 100 * (mm["v_now"] - mm["v_then"]) / mm["v_then"]
    mm = mm[mm["v_then"].abs() > 0]
    print("  months shared:", len(mm), "| months revised (any):", int(((mm["v_now"] - mm["v_then"]).abs() > 1e-9).sum()),
          "| largest monthly revisions:")
    print(mm.reindex(mm["rev_pct"].abs().sort_values(ascending=False).index)[["entity", "ts_utc", "v_then", "v_now", "rev_pct"]].head(8).round(3).to_string(index=False))
