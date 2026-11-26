"""Chain 730 part F, the cross-check: ERCOT's own monthly MAPE of its day-ahead (RUC) load forecast, read off ERCOT's
chart "MTLF Monthly MAPE" (www.ercot.com/files/assets/2026/11/05/load-backcast.png, fetched 26 November 2026; the
values are read from the image to about 0.05 point and are approximate), beside the backtest's monthly MAPE of the
operator's forecast as filed on Form EIA-930 for ba-erco (site/data/predict/scores.json, cut month)."""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
site = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "site", "data", "predict")
READ = {"2024-10": 1.55, "2024-11": 2.05, "2024-12": 1.82, "2025-01": 2.89, "2025-02": 2.72, "2025-03": 1.97, "2025-04": 2.06,
        "2025-05": 2.72, "2025-06": 2.42, "2025-07": 2.25, "2025-08": 2.13, "2025-09": 1.78, "2025-10": 1.72, "2025-11": 2.17,
        "2025-12": 2.21, "2026-01": 2.70, "2026-02": 1.50, "2026-03": 1.77, "2026-04": 1.60, "2026-05": 2.48, "2026-06": 1.85,
        "2026-07": 1.49, "2026-08": 1.46, "2026-09": 1.33, "2026-10": 1.51}
s = json.load(open(os.path.join(site, "scores.json"), encoding="utf-8"))
c = s["rows_columns"]
rows = {r[4]: dict(zip(c, r)) for r in s["rows"] if r[0] == "ba-erco" and r[1] == "demand" and r[2] == "operator" and r[3] == "month"}
erw = {r[4]: dict(zip(c, r)) for r in s["rows"] if r[0] == "ba-erco" and r[1] == "demand" and r[2] == "erw" and r[3] == "month"}
out = []
print("| Month | ERCOT's chart, day-ahead RUC MAPE % (read off the image) | Operator's forecast as filed on EIA-930, MAPE % (backtest) | ERW forecast, MAPE % | Hours |")
print("|---|---:|---:|---:|---:|")
for m, v in READ.items():
    r = rows.get(m)
    e = erw.get(m)
    out.append([m, v, r["mape"] if r else None, e["mape"] if e else None, r["hours"] if r else None])
    print(f"| {m} | {v:.2f} | {r['mape']:.2f} | {e['mape']:.2f} | {r['hours']} |" if r else f"| {m} | {v:.2f} | | | |")
with open(os.path.join(HERE, "crosscheck_ercot.csv"), "w", encoding="utf-8", newline="\n") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["month", "ercot_chart_mape_pct", "eia930_operator_mape_pct", "erw_mape_pct", "hours"])
    w.writerows(out)
both = [(v, r) for _, v, r, _, _ in out if r is not None]
print("\nmean of the chart's months", round(sum(v for v, _ in both) / len(both), 2), "; mean of the EIA-930 months", round(sum(r for _, r in both) / len(both), 2), "; months", len(both))
