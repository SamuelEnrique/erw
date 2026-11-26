"""Window D's data request 40 (the states audit, finding 5): EIA-861M's revenue beside the states page's sales times price.
Twelve months August 2025 to July 2026 (the newest twelve both tables hold). The page's figure: each month's retail sales
(eia_retail_sales_monthly, MWh) times its price (eia_retail_electricity_prices, USD per MWh),
summed. EIA-861M (eia861m_utility_sales_monthly): the sampled utilities' <sector>_revenue summed by state; the table
leaves out EIA's State Adjustment (its estimate for utilities outside the sample), so its sum is a lower bound. Sectors:
residential, commercial, industrial, transportation. Counts only."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402

MONTHS = [f"{y}-{m:02d}" for y, m in [(2025, k) for k in range(8, 13)] + [(2026, k) for k in range(1, 8)]]
SECT = {"RES": "residential", "COM": "commercial", "IND": "industrial", "TRA": "transportation"}


def t(name, cols, filt=None):
    p = f"warehouse/output/{name}.csv"
    parts = []
    for ch in pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, chunksize=400000, usecols=cols):
        ch = ch[ch["ts_utc"].str[:7].isin(MONTHS)]
        parts.append(ch if filt is None else filt(ch))
    return pd.concat(parts)


rs = t("eia_retail_sales_monthly", ["entity", "variable", "ts_utc", "value"], lambda c: c[c["variable"] == "retail_sales"])
pr = t("eia_retail_electricity_prices", ["entity", "ts_utc", "value"])
for f in (rs, pr):
    p = f["entity"].str.split(":")
    f["st"], f["sector"], f["month"] = p.str[2], p.str[3], f["ts_utc"].str[:7]
m = rs.merge(pr, on=["st", "sector", "month"], suffixes=("_s", "_p"))
m = m[m["sector"].isin(SECT)]
m["rev"] = m["value_s"].astype(float) * m["value_p"].astype(float)
page = m.groupby(["st", "sector"]).agg(months=("month", "nunique"), page_usd=("rev", "sum"))
u = t("eia861m_utility_sales_monthly", ["entity", "variable", "ts_utc", "value"],
      lambda c: c[c["variable"].str.endswith(("_revenue", "_sales"))])
u["st"] = u["entity"].str.split(":").str[2]
u["kind"] = u["variable"].str.rsplit("_", n=1).str[1]
u["sector"] = u["variable"].str.rsplit("_", n=1).str[0].map({v: k for k, v in SECT.items()})
us = u[u["kind"] == "sales"].groupby(["st", "sector"])["value"].apply(lambda s: s.astype(float).sum()).rename("m861_mwh")
u = u[u["kind"] == "revenue"]
u = u.dropna(subset=["sector"])
mm = u.groupby(["st", "sector"]).agg(m861_months=("ts_utc", "nunique"), m861_usd=("value", lambda s: s.astype(float).sum()))
sal = m.groupby(["st", "sector"])["value_s"].apply(lambda s: s.astype(float).sum()).rename("page_mwh")
j = page.join(mm, how="inner").join(us).join(sal)
j = j[(j["months"] == 12) & (j["m861_months"] == 12)]
j["gap_pct"] = 100 * (j["m861_usd"] - j["page_usd"]) / j["page_usd"]
j["sales_gap_pct"] = 100 * (j["m861_mwh"] - j["page_mwh"]) / j["page_mwh"]
j["price_861m"] = j["m861_usd"] / j["m861_mwh"]
j["price_page"] = j["page_usd"] / j["page_mwh"]
pd.set_option("display.width", 250)
print("sales: 861M sampled against the page, median", round(j["sales_gap_pct"].median(), 2), "percent; implied price 861M against the page (RES, COM, IND), median ratio", round((j["price_861m"] / j["price_page"])[j.index.get_level_values(1) != "TRA"].median(), 4))
print("state-sectors with all twelve months in both:", len(j))
print("861M sampled revenue against sales x price, percent: median", round(j["gap_pct"].median(), 2), "| mean", round(j["gap_pct"].mean(), 2),
      "| within 1 percent:", int((j["gap_pct"].abs() <= 1).sum()), "| below by more than 5 percent:", int((j["gap_pct"] < -5).sum()),
      "| above by more than 1 percent:", int((j["gap_pct"] > 1).sum()))
for s in ("RES", "COM", "IND"):
    x = j.xs(s, level="sector")
    print(f"{s}: median {x['gap_pct'].median():.2f} percent; all states {x['m861_usd'].sum() / 1e9:.2f} against {x['page_usd'].sum() / 1e9:.2f} billion USD")
print("largest gaps:")
print(j.reindex(j["gap_pct"].abs().sort_values(ascending=False).index).head(12).round(2).to_string())
tx = j.loc["TX"] if "TX" in j.index.get_level_values(0) else None
print("Texas:"); print(tx.round(2).to_string() if tx is not None else "none")
