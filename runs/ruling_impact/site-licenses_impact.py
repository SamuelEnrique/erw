"""Session 7615 (portable-laptop): the ruling impact of the three lines marked "Changes a figure" under
"Site-wide: licenses and holds" in docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads).

Line 1 (EIA-930's figures held where their key names no grid): reads runs/ruling_impact/cache/held_keys_licenses.json,
written by held_keys.mjs from a local build of wip/7610-fault-rows (main of 17 November) whose Num.tsx carried, for this
read only, each held figure's check key (never committed), and judges each held key under the three choices.
Line 2 (ICE's indices on the price board and the price pages): counts what the warehouse holds of ICE's indices as EIA
republishes them (the live set and Redivis's list of tables), writing no value: the indices are held internal.
Line 3 (the held or paused grids named with the reason and no figure on the data machine's eight tools): counts the cells
of those grids in the tables the eight tools read, writing no value.
No model call. No held value is printed: this repository is public.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from live import q  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
HELD = {"isone", "miso", "nyiso"}
BA = {"CISO": "caiso", "ERCO": "ercot", "PJM": "pjm", "MISO": "miso", "NYIS": "nyiso", "ISNE": "isone", "SWPP": "spp"}

print("== line 1: the held figures of EIA-930 whose key names no grid")
data = json.loads((HERE / "cache" / "held_keys_licenses.json").read_text(encoding="utf-8"))
tot = Counter()
for page, r in data.items():
    c = Counter()
    tables = Counter(h["table"] for h in r["held"])
    for h in r["held"]:
        parts = h["key"].split("|")
        m = next((re.match(r"^eia930:([A-Za-z0-9_]+)$", x) for x in parts if re.match(r"^eia930:", x)), None)
        if not m:
            c["no EIA-930 entity in the key: unchanged by either choice"] += 1
            continue
        ba = m.group(1).upper()
        g = BA.get(ba, "")
        if g in HELD:
            c["EIA-930, a held grid's authority: held under (a), shown under (b)"] += 1
        elif g:
            c[f"EIA-930, a public grid's authority: shown under (a) and (b)"] += 1
            c[f"   of which {g}"] += 1
        else:
            c["EIA-930, no grid (US48 or another authority): shown under (a) and (b)"] += 1
            c[f"   of which {ba}"] += 1
    if not r["held"] and not r["shown"]:
        continue
    print(f"\n{page}: {len(r['held'])} held, {r['shown']} checked figures shown; held by table {dict(tables)}")
    for k, n in sorted(c.items()):
        print(f"  {n:5d}  {k}")
    tot.update({k: v for k, v in c.items() if not k.startswith("   ")})
    tot["held"] += len(r["held"])
    tot["shown"] += r["shown"]
print("\nall pages read:")
for k, n in sorted(tot.items()):
    print(f"  {n:5d}  {k}")
examples = defaultdict(list)
for page, r in data.items():
    for h in r["held"]:
        if len(examples[page]) < 3 and "eia930:" in h["key"]:
            examples[page].append(h["key"])
print("examples of held keys:")
for p, ks in examples.items():
    for k in ks:
        print(f"  {p}: {k}")

print("\n== line 2: ICE's indices as EIA republishes them")
n = q("select count(*) from public.series where table_name = 'eia_ice_electricity_daily'")[0][0]
print(f"live set rows of eia_ice_electricity_daily: {n}")
cov = (ROOT / "warehouse" / "metadata" / "coverage.csv").read_text(encoding="utf-8").splitlines()
head = cov[0].split(",")
for l in cov:
    if l.startswith("eia_ice_electricity_daily,"):
        row = dict(zip(head, l.split(",")))
        print("coverage.csv:", {k: row[k] for k in head if row.get(k)})

print("\n== line 3: the held or paused grids on the data machine's eight tools")
eight = json.loads((HERE / "cache" / "held_keys_eight.json").read_text(encoding="utf-8"))
for page, r in eight.items():
    grids = Counter((re.search(r"(isone|miso|nyiso|pjm)", h["key"]) or [None, "no grid named"])[1] for h in r["held"])
    print(f"{page} (default view): drawn 'license needed' cells {r['text']}; held checked figures {len(r['held'])} {dict(grids) if grids else ''}; checked figures shown {r['shown']}")
print("rows a grid of the tables the eight tools read (live set):")
for t in ["price_board_latest", "price_board_peak_offpeak", "price_board_spreads", "hub_price_comparison", "iso_dam_hub_prices",
          "iso_rtm_hub_prices", "iso_trader_daily", "iso_queue_statistics", "scarcity_hours_by_grid", "grid_stress_days"]:
    rows = q("select split_part(entity, ':', 1), count(*) from public.series where table_name=%s group by 1 order by 1", (t,))
    if rows:
        print(f"{t}: " + "; ".join(f"{g} {n}" for g, n in rows))
