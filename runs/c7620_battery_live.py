"""Session 7620: read the live set's battery_stack_monthly rows (public table) for the alternative of the battery
window, read only. Prints, per hub, duration and strategy, the months held and the year to September 2026 and to the
newest month. Writes the CAISO and ERCOT 4-hour perfect foresight rows to a JSON fixture for the test on the branch.

    .venv/Scripts/python.exe runs/c7620_battery_live.py <fixture path>
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "ruling_impact"))
from live import q  # noqa: E402

rows = q("select entity, variable, ts_utc::text, value from series where table_name = 'battery_stack_monthly' "
         "and (variable like 'foresight_4h_%%' or variable like 'dayahead_2h_%%' or variable like 'foresight_8h_%%') "
         "order by entity, variable, ts_utc")
print(len(rows), "rows")
by = {}
for e, v, t, val in rows:
    by.setdefault(e, []).append({"variable": v, "ts_utc": t[:10], "value": float(val) if val is not None else None})
for e, rs in by.items():
    for pre in ("foresight_4h_", "foresight_8h_", "dayahead_2h_"):
        tot = {r["ts_utc"][:7]: r["value"] for r in rs if r["variable"] == pre + "revenue_total_usd_per_mw"}
        held = {r["ts_utc"][:7]: r["value"] for r in rs if r["variable"] == pre + "days_held"}
        dim = {r["ts_utc"][:7]: r["value"] for r in rs if r["variable"] == pre + "days_in_month"}
        ms = sorted(tot)
        if not ms:
            continue
        a = [m for m in ms if "2025-10" <= m <= "2026-09"]
        b = ms[-12:]
        print(e, pre, "newest", ms[-1], "days", held.get(ms[-1]), "of", dim.get(ms[-1]),
              "| Oct25-Sep26", round(sum(tot[m] for m in a) / 1000, 2), len(a),
              "| to newest", b[0], b[-1], round(sum(tot[m] for m in b) / 1000, 2))
if len(sys.argv) > 1:
    keep = {e: [r for r in rs if r["variable"].startswith("foresight_4h_") and r["ts_utc"] >= "2023-08"] for e, rs in by.items()
            if e in ("caiso:TH_SP15_GEN-APND", "ercot:HB_HUBAVG")}
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        json.dump(keep, f, indent=0)
    print("fixture", sys.argv[1])
