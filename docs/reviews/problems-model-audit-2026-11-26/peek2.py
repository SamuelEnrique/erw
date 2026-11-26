"""Session 10229: the figures behind three of the sets' sentences, and the season of the bill questions' wholesale month."""
import csv
import json
import sys
from pathlib import Path

D, COP = Path(sys.argv[1]), Path(sys.argv[2])
el = json.loads((D / "regions/events/elliott_2022.json").read_text(encoding="utf-8"))
dem = el["regions"]["TEN"]["demand_mw"]
tn = max(range(len(dem)), key=lambda k: (dem[k] if isinstance(dem[k], (int, float)) else -1, -k))
print("Elliott TEN peak position", tn)
for src in ("natural_gas", "coal", "nuclear", "hydro", "wind", "solar", "other"):
    g = el["regions"]["TEN"]["gen"].get(src)
    b = el["regions"]["TEN"]["baseline"]["gen"].get(src)
    if g is not None:
        print(f"  {src}: at the peak {g[tn]}, baseline that hour {b[tn] if b else None}; the window's highest {max(x for x in g if isinstance(x, (int, float)))}")
ind = json.loads((D / "industry.json").read_text(encoding="utf-8"))["industries"]
tots = [(c, ind["industries"][c]["by_region"]["us"]["total"]) for c in ind["ranked_3_digit"]]
s = sum(v for _, v in tots if isinstance(v, (int, float)))
print("MECS 2022: 21 industries' sum", s, "first four", tots[:4], "share", sum(v for _, v in tots[:4]) / s)

rows = {}
with COP.open(encoding="utf-8") as fh:
    for r in csv.DictReader(line for line in fh if not line.startswith("#")):
        rows.setdefault((r["entity"], r["ts_utc"][:7]), {})[r["variable"]] = float(r["value"])
for ent, tot in (("caiso:TH_NP15_GEN-APND", 229.629900), ("ercot:HB_HUBAVG", 95.2732), ("caiso:TH_SP15_GEN-APND", 224.76)):
    months = sorted(m for (e, m) in rows if e == ent)
    print(ent, "months held", months[0], "to", months[-1])
    win = []
    for m in months:
        v = rows[(ent, m)]
        full = v.get("rt_hours") == v.get("hours_in_month")
        if m >= "2025-10" and "rt_load_weighted" in v:
            print(f"  {m} lw {v['rt_load_weighted']:.4f} full {full} -> wholesale {600 * v['rt_load_weighted'] / 1000:.2f} share {600 * v['rt_load_weighted'] / 1000 / tot * 100:.2f}")
            if "2025-10" <= m <= "2026-05" and full:
                win.append(v["rt_load_weighted"])
    if win:
        mean = sum(win) / len(win)
        print(f"  winter months 2025-10 to 2026-05 held whole: {len(win)}, mean lw {mean:.4f} -> wholesale {600 * mean / 1000:.2f}, share {600 * mean / 1000 / tot * 100:.2f}")
