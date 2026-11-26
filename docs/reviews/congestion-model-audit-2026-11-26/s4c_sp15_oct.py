"""Session 10220: SP15's day-ahead LMP of October 2026, iso_dam_hub_prices against iso_hub_prices_history, hour by hour,
and the daily means of iso_dam_hub_prices (the page's October mean is 46.75; iso_dam_hub_prices gives 46.78 on the same
744 hours). Read only.
usage: s4c_sp15_oct.py <main copy warehouse/output dir>"""
import csv
import os
import sys
from collections import defaultdict

OUT = sys.argv[1]
E = "caiso:TH_SP15_GEN-APND"


def read(name):
    h = defaultdict(list)
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("#"):
                cols = next(csv.reader([line]))
                break
        ie, iv, it, ix, ir = (cols.index(c) for c in ("entity", "variable", "ts_utc", "value", "retrieved_at"))
        for row in csv.reader(fh):
            if row[ie] == E and row[iv] == "lmp_dam" and "2026-10-01T07" <= row[it] < "2026-11-01T07":
                h[row[it]].append((float(row[ix]), row[ir]))
    return h


a = read("iso_dam_hub_prices.csv")
b = read("iso_hub_prices_history.csv")
dup = {t: v for t, v in a.items() if len(v) > 1}
print("iso_dam_hub_prices October hours", len(a), "with more than one row", len(dup), list(dup.items())[:3])
common = sorted(set(a) & set(b))
diff = [(t, a[t], b[t]) for t in common if abs(a[t][0][0] - b[t][0][0]) > 0.005]
print("hours in both", len(common), "differing", len(diff))
for d in diff[:20]:
    print("  ", d)
days = defaultdict(list)
for t, v in a.items():
    days[t[:10]].append(v[0][0])
print("days of iso_dam_hub_prices with their hour counts:", {d: len(v) for d, v in sorted(days.items()) if len(v) != 24})
