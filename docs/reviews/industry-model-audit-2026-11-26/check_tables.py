"""Session 10224: the page file against the two of its six tables this machine holds (read only, streamed).

    python runs/c10224/check_tables.py <main copy's warehouse/output>

The Monthly Energy Review's industrial series (eia_sector_energy_consumption_monthly) and Form EIA-861M's sales to
industry (eia_retail_sales_monthly, variable retail_sales, sector IND) set beside site/data/industry.json value by
value. The other four tables (eia_mecs_manufacturing, eia_seds_industrial_annual, eia_seds_state_energy,
eia_aeo_industrial) are not on this machine. Standard library only.
"""
import csv
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = sys.argv[1]
F = json.load(open(os.path.join(ROOT, "site", "data", "industry.json"), encoding="utf-8"))
MER = {"TEICBUS": "total", "TNICBUS": "end_use_total", "CLICBUS": "coal", "NNICBUS": "natural_gas", "PAICBUS": "petroleum",
       "REICBUS": "renewables", "ESICBUS": "electricity_retail_sales", "LOICBUS": "electrical_system_losses"}


def rows(name):
    fh = open(os.path.join(OUT, name + ".csv"), encoding="utf-8", newline="")
    lines = (ln for ln in fh if not ln.startswith("#"))
    return csv.DictReader(lines), fh


# the Monthly Energy Review
rd, fh = rows("eia_sector_energy_consumption_monthly")
tab = {}
for r in rd:
    code = r["entity"].split(":")[1]
    if code in MER:
        tab[(MER[code], r["ts_utc"][:7])] = float(r["value"]) if r["value"] not in ("", "nan") else None
fh.close()
M = F["monthly"]
same = diff = only_file = 0
diffs = []
for k, arr in M["by_source"].items():
    for m, v in zip(M["months"], arr):
        t = tab.get((k, m), "absent")
        if t == "absent":
            only_file += v is not None
        elif t is None and v is None or (t is not None and v is not None and abs(round(t, 3) - v) < 0.0005):
            same += 1
        else:
            diff += 1
            diffs.append((k, m, v, t))
newest_tab = max(m for (_, m) in tab)
print(f"Monthly Energy Review: file months {M['months'][0]} to {M['months'][-1]}; the held table to {newest_tab}; equal {same}; differ {diff}; in the file only {only_file}")
for d in diffs[:12]:
    print("  differ (series, month, file, held table):", d)
y = {}
for (k, m), v in tab.items():
    if k == "total" and m.startswith("2025"):
        y[m] = v
print(f"  the held table's 2025 total, twelve months: {sum(y.values()):,.3f} ({len(y)} months)")

# Form EIA-861M, sales to industry
rd, fh = rows("eia_retail_sales_monthly")
sal = {}
for r in rd:
    if r["variable"] == "retail_sales" and r["entity"].endswith(":IND"):
        st = r["entity"].split(":")[2]
        sal[(st, r["ts_utc"][:7])] = float(r["value"]) if r["value"] not in ("", "nan") else None
fh.close()
E = F["electricity_sales_monthly"]
same = diff = only_file = 0
diffs = []
for st, arr in E["states"].items():
    for m, v in zip(E["months"], arr):
        t = sal.get((st, m), "absent")
        if t == "absent":
            only_file += v is not None
        elif t is None and v is None or (t is not None and v is not None and abs(round(t, 1) - v) < 0.05):
            same += 1
        else:
            diff += 1
            diffs.append((st, m, v, t))
newest = max(m for (_, m) in sal)
print(f"Form EIA-861M sales to industry: file months {E['months'][0]} to {E['months'][-1]}, {len(E['states'])} areas; the held table to {newest}; equal {same}; differ {diff}; in the file only {only_file}")
for d in diffs[:12]:
    print("  differ (area, month, file, held table):", d)
areas = sorted(E["states"])
print("  areas in the file:", areas)
sys.exit(0)
