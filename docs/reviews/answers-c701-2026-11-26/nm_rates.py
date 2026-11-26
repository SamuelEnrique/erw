"""Data request 11 of docs/state/data_requests_five_tools.md, New Mexico: each TRD rate table's oil (O), horizontal-well
oil (H) and gas (G) rates by period: severance, school, conservation (the same in every district) and the district's
ad valorem production rate (its range across districts). Usage: nm_rates.py FILE..."""
import io
import sys
from collections import defaultdict

import openpyxl

out = defaultdict(lambda: dict(sev=set(), school=set(), cons=set(), ad=[], n=0))
for path in sys.argv[1:]:
    wb = openpyxl.load_workbook(io.BytesIO(open(path, "rb").read()), read_only=True, data_only=True)
    for ws in wb.worksheets:
        head = None
        for row in ws.iter_rows(values_only=True):
            v = list(row[:12])
            if v and v[0] == "COUNTY":
                head = v
                continue
            if head is None or not v or v[0] in (None, "") or v[6] not in ("O", "H", "G"):
                continue
            frm, to = v[4], v[5]
            key = (frm.strftime("%Y-%m-%d") if hasattr(frm, "strftime") else str(frm), to.strftime("%Y-%m-%d") if hasattr(to, "strftime") else str(to), v[6])
            o = out[key]
            o["sev"].add(round(float(v[7]), 6))
            o["school"].add(round(float(v[8]), 6))
            o["cons"].add(round(float(v[9]), 6))
            o["ad"].append(float(v[10]))
            o["n"] += 1
print("from | to | kind | severance | school | conservation | ad valorem (lowest to highest district) | districts")
for (frm, to, kind), o in sorted(out.items()):
    print(f"{frm} | {to} | {kind} | {sorted(o['sev'])} | {sorted(o['school'])} | {sorted(o['cons'])} | {min(o['ad']):.6f} to {max(o['ad']):.6f} | {o['n']}")
