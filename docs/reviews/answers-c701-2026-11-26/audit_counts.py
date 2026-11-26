"""Window D's data requests 19, 24 and 25 (docs/state/data_requests_five_tools.md): counts from tables held on the data
machine. Counts only; no row is copied. Prints one block a request."""
import sys

import pandas as pd

sys.path.insert(0, "warehouse/connectors")
import iso_prices as ip  # noqa: E402


def t(name):
    p = f"warehouse/output/{name}.csv"
    return pd.read_csv(p, skiprows=ip.header_rows(p), dtype=str, keep_default_na=False)


print("== 19: requests recorded in service, by year of actual_in_service_date (and by status)")
for name in ("miso_interconnection_queue", "nyiso_interconnection_queue"):
    d = t(name)
    y = d["actual_in_service_date"].str[:4]
    print(name, "rows", len(d), "| status counts:", d["status"].value_counts().to_dict())
    for yr in ("2023", "2024", "2025", "2026"):
        print(f"  actual in service {yr}: {(y == yr).sum()}")
    print("  status operational with a date in 2024 or 2025:",
          int(((d["status"].str.lower().str.contains("operat|service|complete")) & y.isin(["2024", "2025"])).sum()),
          "| newest actual_in_service_date:", d.loc[d["actual_in_service_date"] != "", "actual_in_service_date"].max(),
          "| retrieved:", d["retrieved_at"].max())

print("== 24: hifld_transmission_lines")
h = t("hifld_transmission_lines")
km = pd.to_numeric(h["x_length_km"], errors="coerce")
print("lines", len(h), "km", round(km.sum(), 1))
for col in ("x_status", "x_inferred"):
    g = h.assign(km=km).groupby(col).agg(lines=("km", "size"), km=("km", "sum")).round(1)
    print(col); print(g.to_string())
for col in ("x_source_date", "x_val_date"):
    yr = h[col].str[:4].replace("", "blank")
    g = h.assign(km=km, yr=yr).groupby("yr").agg(lines=("km", "size"), km=("km", "sum")).round(1)
    print(col, "by year"); print(g.to_string())

print("== 25: ERCOT operating positions by entry year, two sources")
q = t("iso_queue_statistics")
q = q[(q["x_iso"].str.lower() == "ercot")]
print("iso_queue_statistics variables:", sorted(set(q["variable"]))[:20])
op = q[q["variable"].str.contains("operat", case=False)]
print(op.groupby(["variable", "x_entry_year"])["value"].first().to_string()[:3000])
e = t("ercot_interconnection_queue")
e["entry"] = e["queue_date"].str[:4]
print("ercot_interconnection_queue retrieved", e["retrieved_at"].max(), "| status counts:", e["status"].value_counts().to_dict())
print(e[e["status"].str.lower().str.contains("operat")].groupby("entry").size().to_string())
