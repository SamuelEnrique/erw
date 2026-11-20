#!/usr/bin/env python3
"""Cross-check of constraints_binding_hourly against the market monitors' own 2025 figures (chain 601, part C4).

CAISO: Department of Market Monitoring, "2025 Annual Report on Market Issues and Performance" (June 2026), Table 5.3,
"Impact of congestion on day-ahead prices - top 25 primary congestion constraints": each constraint's frequency, the
share of 2025's hours it bound in the day-ahead market. Compared with the hours the warehouse holds it binding (any
contingency), over 8,760.
SPP: Market Monitoring Unit, "2025 Annual State of the Market Report" and its stakeholder presentation: the most
congested flowgates in their order. Compared with the warehouse's 2025 rank by summed shadow price (the monitor ranks by
congestion rent, which weighs flow too, so equal ranks are not expected).

    python replication/congestion/crosscheck.py DMM_TEXT [--tables DIR]
DMM_TEXT is the report's text (pdftotext -layout of
https://www.caiso.com/documents/2025-annual-report-on-market-issues-and-performance.pdf). Writes crosscheck.csv here.
"""
import argparse
import csv
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SPP_ORDER = ["OSAWEBCLESOO", "TMP128_29363", "TMP563_26603", "TMP266_27514"]
CAISO_URL = "https://www.caiso.com/documents/2025-annual-report-on-market-issues-and-performance.pdf"
SPP_URL = "https://www.spp.org/documents/76798/2025_annual_state_of_the_market_report.pdf"


def read(path):
    n = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("#"):
                break
            n += 1
    return pd.read_csv(path, skiprows=n, usecols=["entity", "ts_utc", "value", "market", "x_constraint"], dtype=str, keep_default_na=False)


def dmm_table(text):
    """(constraint, frequency percent) rows of Table 5.3."""
    start = [m.start() for m in re.finditer(r"Table 5\.3\s+Impact of congestion on day-ahead prices", text)][-1]
    block = text[start:start + 6000]
    rows = []
    for line in block.splitlines():
        m = re.match(r"^\s*(\S+)\s+(\d*\.\d+|\d+\.\d+)%", line)
        if m:
            rows.append((m.group(1), float(m.group(2))))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dmm_text")
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    a = ap.parse_args()
    d = read(os.path.join(a.tables, "constraints_binding_hourly.csv"))
    d = d[(d["ts_utc"] >= "2025-01-01T00:00:00Z")]
    out = []
    c = d[d["market"] == "caiso_dam"].copy()
    c = c[(c["ts_utc"] >= "2025-01-01T08:00:00Z") & (c["ts_utc"] < "2026-01-01T08:00:00Z")]
    c["key"] = c["x_constraint"].str.replace(" ", "", regex=False)
    hours = c.groupby("key")["ts_utc"].nunique()
    rank = hours.rank(ascending=False, method="min")
    for name, freq in dmm_table(open(a.dmm_text, encoding="utf-8", errors="replace").read()):
        k = name.replace(" ", "")
        h = int(hours.get(k, 0))
        out.append(dict(operator="CAISO", constraint=name, monitor_figure=f"{freq}% of hours", monitor_source=f"DMM 2025 annual report, Table 5.3 ({CAISO_URL})",
                        warehouse_figure=f"{100 * h / 8760:.1f}% of hours ({h} hours)", difference_points=round(100 * h / 8760 - freq, 1),
                        warehouse_rank_by_hours=int(rank.get(k, 0)) or ""))
    s = d[d["market"] == "spp_dam"].copy()
    s = s[(s["ts_utc"] >= "2025-01-01T06:00:00Z") & (s["ts_utc"] < "2026-01-01T06:00:00Z")]
    s["a"] = s["value"].astype(float).abs()
    cost = s.groupby("x_constraint")["a"].sum().sort_values(ascending=False)
    cr = {k: i + 1 for i, k in enumerate(cost.index)}
    hrs = s.groupby("x_constraint").size()
    for i, k in enumerate(SPP_ORDER):
        out.append(dict(operator="SPP", constraint=k, monitor_figure=f"rank {i + 1} of the most congested flowgates", monitor_source=f"MMU 2025 annual State of the Market report and its stakeholder presentation ({SPP_URL})",
                        warehouse_figure=f"rank {cr.get(k, '')} by summed shadow price ({int(hrs.get(k, 0))} hours bound)", difference_points="",
                        warehouse_rank_by_hours=int(hrs.rank(ascending=False, method='min').get(k, 0)) or ""))
    path = os.path.join(HERE, "crosscheck.csv")
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    caiso = [r for r in out if r["operator"] == "CAISO"]
    near = sum(abs(r["difference_points"]) <= 1.0 for r in caiso)
    print(f"CAISO: {len(caiso)} constraints of Table 5.3; {near} within 1 percentage point of the monitor's frequency")
    for r in out:
        print(f"  {r['operator']} {r['constraint']}: monitor {r['monitor_figure']}; warehouse {r['warehouse_figure']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
