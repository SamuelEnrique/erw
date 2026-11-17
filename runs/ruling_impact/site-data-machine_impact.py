"""Session 7613 (portable-laptop): the ruling impact of the two lines marked "Changes a figure" under
"Site-wide: the data machine and its tables" in docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads).

Line A: datacenter_mw in generator_pipeline_by_grid reads 0 everywhere: drop it, or fill it by joining the tracker by plant ID?
Line B: may EIA's six-month file fill the 2025 interchange gap (2,779 days) though it matches the API on 96.3 percent of days?

Reads generator_pipeline_by_grid and eia930_daily_total_interchange from Redivis (datapages.erw:b9wm, the draft), cached under
runs/ruling_impact/cache/; the tracker tables' columns from warehouse/output (read only); the site's source for readers of
each table. No model call.
"""
import re
import subprocess
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from redivis_read import table  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def readers(name):
    """Files of the site and the chat that name a table or column (git grep, tracked files only)."""
    out = subprocess.run(["git", "grep", "-l", name, "--", "site/app", "site/lib", "site/components", "warehouse/chat", "site/data"],
                         cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    return [l for l in out.stdout.splitlines() if l]


print("== line A: datacenter_mw in generator_pipeline_by_grid")
p, where = table("generator_pipeline_by_grid")
p["v"] = pd.to_numeric(p["value"], errors="coerce")
print(f"{where}: {len(p)} rows; vintages {sorted(p['vintage'].unique())}; retrieved {p['retrieved_at'].max()}")
dc = p[p["variable"] == "datacenter_mw"]
pl = p[p["variable"] == "planned_mw"]
print(f"datacenter_mw rows: {len(dc)}; non-zero: {(dc['v'] != 0).sum()}; sum {dc['v'].sum():,.3f} MW")
for vin, g in pl.groupby("vintage"):
    print(f"  planned_mw, snapshot {vin}: {len(g)} cells, {g['v'].sum():,.1f} MW; datacenter_mw {dc[dc['vintage'] == vin]['v'].sum():,.3f} MW")
print("readers of 'datacenter_mw' on the site and in the chat:", readers("datacenter_mw") or "none")
print("readers of 'generator_pipeline_by_grid':", readers("generator_pipeline_by_grid") or "none")
for f in ["datacenter_facilities", "datacenter_projects", "datacenter_operator_sites", "datacenter_queue_positions"]:
    cols = []
    for line in open(ROOT / "warehouse" / "output" / f"{f}.csv", encoding="utf-8"):
        if not line.startswith("#"):
            cols = line.strip().split(",")
            break
    plant = [c for c in cols if re.search(r"plant|eia_?id|generator", c, re.I)]
    print(f"tracker table {f}: {len(cols)} columns; a plant or generator id column: {plant or 'none'}")

print("\n== line B: the 2025 interchange gap filled from EIA's six-month file")
t, where = table("eia930_daily_total_interchange")
t["v"] = pd.to_numeric(t["value"], errors="coerce")
t["day"] = pd.to_datetime(t["ts_utc"], utc=True)
print(f"{where}: {len(t)} rows; {t['day'].min()} to {t['day'].max()}; variables {sorted(t['variable'].unique())}")
srcs = t.groupby("source").size()
print("rows by source:", dict(srcs))
six = t["source"].str.contains("six|BALANCE|bulk|6mo|six_month", case=False, regex=True) | t["source_url"].str.contains("BALANCE", case=False)
print(f"rows from the six-month file: {six.sum()}")
f = t[six]
print(f"  by month: {dict(f.groupby(f['day'].dt.strftime('%Y-%m')).size())}")
y = t[(t["day"] >= "2025-01-01") & (t["day"] < "2026-01-01")]
nd = y[y["day"] >= "2025-11-01"]
print(f"2025: {len(y)} BA days; November and December: {len(nd)}, of which from the six-month file {six[nd.index].sum()}")
rows = []
for e, g in y.groupby("entity"):
    a = g["v"].sum()
    b = g.loc[~six[g.index], "v"].sum()
    nfill = six[g.index].sum()
    if nfill:
        rows.append((e, nfill, a, b))
rows.sort(key=lambda r: -abs(r[2] - r[3]))
print(f"balancing authorities with a filled day in 2025: {len(rows)}")
print("largest moves of a BA's 2025 net total interchange (MWh): with the fill, without it, change")
for e, n, a, b in rows[:8]:
    ch = a - b
    print(f"  {e}: {n} days filled; {a:,.0f} with, {b:,.0f} without: {ch:+,.0f} MWh ({(ch / b * 100) if b else float('nan'):+.1f} percent)")
nov = nd[nd["day"] < "2025-12-01"]
dec = nd[nd["day"] >= "2025-12-01"]
for name, g in (("November 2025", nov), ("December 2025", dec)):
    ents = g["entity"].nunique()
    with_fill = g.groupby("entity").size()
    print(f"{name}: {len(g)} BA days held with the fill ({ents} BAs); {(~six[g.index]).sum()} without it; "
          f"BAs whose month is whole with the fill: {(with_fill >= (30 if name.startswith('Nov') else 31)).sum()}")
print("readers of 'eia930_daily_total_interchange':", readers("eia930_daily_total_interchange") or "none")
print("the method's measure of the file against the API (docs/methods/grid_network.md, session 3941): 6,811 of 7,074 BA days "
      f"equal to the MWh, July to October 2025: {6811 / 7074 * 100:.1f} percent")
