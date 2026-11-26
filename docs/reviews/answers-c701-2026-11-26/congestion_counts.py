"""Window D's data requests 28, 29 and 30 (the congestion audit, findings 2, 4, 5 and 6). Counts from the data machine's
tables; nothing is published. 28: by operator and year, the constraint-hours at a ceiling shadow price (absolute value:
SPP 1,500.00 or more, CAISO 1,000.00 or more), the share of the year's top-25 sum (keys ranked by summed absolute shadow
price, as the page ranks them) those hours carry; and elements (the name alone) against keys (name and contingency):
key-hours against the element's distinct hours. 29: SP15 day-ahead, 22 to 31 October 2026, the two tables hour by hour.
30: SPP, March against April 2026, a day at a time: distinct constraints, constraint-hours, both hubs' congestion part."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402


def t(name, cols=None):
    p = f"warehouse/output/{name}.csv"
    return pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False, usecols=cols)


pd.set_option("display.width", 250)
c = t("constraints_binding_hourly", ["entity", "ts_utc", "value", "market", "x_constraint", "x_contingency"])
c["op"] = c["market"].str.split("_").str[0]
c["abs"] = c["value"].astype(float).abs()
c["yr"] = c["ts_utc"].str[:4]
CEIL = {"spp": 1500.0, "caiso": 1000.0}
print("== 28")
rows = []
for (op, yr), g in c.groupby(["op", "yr"]):
    ceil = CEIL.get(op)
    at = g["abs"] >= ceil - 1e-9
    top = g.groupby("entity")["abs"].sum().nlargest(25).index
    gt = g[g["entity"].isin(top)]
    kh = len(g)
    eh = g.drop_duplicates(["x_constraint", "ts_utc"]).shape[0]
    dbl = g.groupby("x_constraint").apply(lambda x: len(x) > x["ts_utc"].nunique(), include_groups=False)
    rows.append(dict(op=op, yr=yr, constraint_hours=kh, at_ceiling=int(at.sum()), top25_sum=round(gt["abs"].sum(), 1),
                     top25_ceiling_share_pct=round(100 * gt.loc[gt["abs"] >= ceil - 1e-9, "abs"].sum() / gt["abs"].sum(), 2),
                     top25_with_a_ceiling_hour=int(gt[gt["abs"] >= ceil - 1e-9]["entity"].nunique()),
                     keys=g["entity"].nunique(), elements=g["x_constraint"].nunique(), element_hours=eh,
                     key_hours_over_element_hours=kh - eh, elements_with_two_keys_in_an_hour=int(dbl.sum())))
print(pd.DataFrame(rows).to_string(index=False))

print("== 29")
pc = t("price_congestion_hourly", ["entity", "variable", "ts_utc", "value", "market"])
a = pc[(pc["variable"] == "lmp_dam") & pc["entity"].str.contains("TH_SP15_GEN-APND")]
a = a[(a["ts_utc"] >= "2026-10-22T07:00:00Z") & (a["ts_utc"] < "2026-11-01T07:00:00Z")].set_index("ts_utc")["value"].astype(float)
h = t("iso_dam_hub_prices", ["entity", "ts_utc", "value", "market"])
b = h[(h["market"] == "caiso_dam") & h["entity"].str.contains("TH_SP15_GEN-APND")]
b = b[(b["ts_utc"] >= "2026-10-22T07:00:00Z") & (b["ts_utc"] < "2026-11-01T07:00:00Z")].set_index("ts_utc")["value"].astype(float)
j = pd.concat([a.rename("price_congestion"), b.rename("iso_dam_hub")], axis=1)
j["diff"] = (j["price_congestion"] - j["iso_dam_hub"]).round(5)
print("hours:", len(j), "| both held:", int(j.dropna().shape[0]), "| only price_congestion:", int(j["iso_dam_hub"].isna().sum()),
      "| only iso_dam_hub:", int(j["price_congestion"].isna().sum()), "| hours differing by more than 0.005:", int((j["diff"].abs() > 0.005).sum()))
print(j[j["diff"].abs() > 0.005].head(30).to_string())
print("means over the hours both hold:", round(j.dropna()["price_congestion"].mean(), 4), round(j.dropna()["iso_dam_hub"].mean(), 4))

print("== 30")
s = c[(c["op"] == "spp") & (c["ts_utc"] >= "2026-03-01T06:00:00Z") & (c["ts_utc"] < "2026-05-01T05:00:00Z")].copy()
s["day"] = pd.to_datetime(s["ts_utc"], utc=True).dt.tz_convert("America/Chicago").dt.date
per = s.groupby("day").agg(constraints=("entity", "nunique"), constraint_hours=("entity", "size"))
cg = pc[(pc["variable"] == "congestion_dam") & pc["entity"].str.startswith("spp:")].copy()
cg["t"] = pd.to_datetime(cg["ts_utc"], utc=True)
cg = cg[(cg["t"] >= pd.Timestamp("2026-03-01T06:00:00Z")) & (cg["t"] < pd.Timestamp("2026-05-01T05:00:00Z"))]
cg["day"] = cg["t"].dt.tz_convert("America/Chicago").dt.date
cg["v"] = cg["value"].astype(float)
hub = cg.pivot_table(index="day", columns="entity", values="v", aggfunc="mean").round(3)
out = per.join(hub)
print(out.to_string())
for lo, hi, name in (("2026-03-01", "2026-04-01", "March"), ("2026-04-01", "2026-05-01", "April")):
    m = out[(out.index >= pd.Timestamp(lo).date()) & (out.index < pd.Timestamp(hi).date())]
    print(name, "mean a day:", m.mean().round(3).to_dict())
