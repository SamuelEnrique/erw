"""Session 10214 (demand audit): rows of the main copy's eia_retail_sales_monthly (retail_sales, the 24 months to its newest)
and eia_sector_energy_consumption_monthly (the 24 months to its newest), as the live set would serve them to the
consumption view, for draw_consumption.mjs. Standard library; tables streamed.

Usage: python consumption_fixture.py <eia_retail_sales_monthly.csv> <eia_sector_energy_consumption_monthly.csv> <out json>
"""
import csv
import json
import sys


def read(path, keep):
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(line for line in f if not line.startswith("#"))
        head = next(rd)
        ix = {k: i for i, k in enumerate(head)}
        for r in rd:
            row = {k: r[ix[k]] for k in ("entity", "variable", "ts_utc", "unit", "freq")}
            row["value"] = float(r[ix["value"]])
            if keep(row):
                out.append(row)
    return out


def last24(rows):
    months = sorted({r["ts_utc"][:7] for r in rows})[-24:]
    return [r for r in rows if r["ts_utc"][:7] in months]


def main(sales, mer, out):
    s = last24(read(sales, lambda r: r["variable"] == "retail_sales"))
    m = last24(read(mer, lambda r: True))
    key = lambda r: (r["entity"], r["variable"], r["ts_utc"])
    json.dump({"eia_retail_sales_monthly": sorted(s, key=key), "eia_sector_energy_consumption_monthly": sorted(m, key=key)}, open(out, "w", encoding="utf-8"))
    print(f"retail sales rows {len(s)}, MER rows {len(m)}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
