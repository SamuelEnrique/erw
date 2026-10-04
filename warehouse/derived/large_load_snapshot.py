"""Energy Research Warehouse (ERW): the site's copy of ERCOT's large-load status figures (session 106).

  python warehouse/derived/large_load_snapshot.py     # site/data/large_load_status.json, from ercot_large_load_status

The page /datacenters/v2 reads this file. It is the table ercot_large_load_status turned on its side, one entry a
report with the figures that report states in words; it computes nothing but the change between the first and the
last report, and writes no warehouse table. Run after the connector (warehouse/connectors/ercot_large_load_status.py).
"""
import json
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import iso_prices as ip  # noqa: E402

TABLE = "ercot_large_load_status"
SITE_FILE = os.path.join(ROOT, "site", "data", "large_load_status.json")
FIGURES = {"approved_to_energize_mw": "approved", "observed_nonsimultaneous_peak_mw": "nonsimultaneous", "observed_simultaneous_peak_mw": "simultaneous",
           "new_submissions_count": "new_count", "new_submissions_mw": "new_mw"}


def build(out=None):
    path = os.path.join(out or ip.OUT_DIR, TABLE + ".csv")
    d = pd.read_csv(path, skiprows=ip.header_rows(path), dtype=str, keep_default_na=False)
    unknown = set(d["variable"]) - set(FIGURES)
    if unknown:
        raise ValueError(f"{TABLE} holds variables the page does not know: {sorted(unknown)}")
    reports = []
    for day, g in d.groupby(d["ts_utc"].str[:10]):
        r = {"day": day, "document": g["x_document"].iloc[0], "url": g["source_url"].iloc[0], "month_as_written": ""}
        for _, row in g.iterrows():
            r[FIGURES[row["variable"]]] = float(row["value"])
            if row["variable"] == "observed_nonsimultaneous_peak_mw":
                r["month_as_written"] = row["x_month_as_written"]
        reports.append(r)
    reports.sort(key=lambda r: r["day"])
    return {"table": TABLE, "built": ip.utc_iso(pd.Timestamp.now(tz="UTC")), "retrieved": d["retrieved_at"].max(), "rows": int(len(d)),
            "source": d["source"].iloc[0], "reports": reports}


def main():
    f = build()
    with open(SITE_FILE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(f, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    r = f["reports"]
    print(f"large_load_status.json: {len(r)} reports, {r[0]['day']} to {r[-1]['day']}, from {f['rows']} rows of {TABLE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
