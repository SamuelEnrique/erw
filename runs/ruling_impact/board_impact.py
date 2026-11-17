#!/usr/bin/env python3
"""ERW, ruling impact for /board (session 7586, 17 November 2026).

The six lines marked "Changes a figure" under the price board in docs/reviews/rulings-for-samuel-2026-11-17.md (branch
wip/7560-six-reads). Read from the page's own file, site/data/board.json (built 2026-11-17T04:59:51Z), and its rules as
docs/methods/price_board.md and site/lib/board.ts state them (the stale ages of closeAge; rangeExtremes for the strip).
No held value is printed: a held row has no value in the file.

    .venv/Scripts/python.exe runs/ruling_impact/board_impact.py
"""
import collections
import datetime as dt
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = json.load(open(os.path.join(ROOT, "site", "data", "board.json"), encoding="utf-8"))
R = B["rows"]
BUILT = dt.date.fromisoformat(B["built"][:10])
print(f"board.json built {B['built']}: {len(R):,} rows; by status {dict(collections.Counter(r['status'] for r in R))}")


def cells(r):
    """The figure cells a row draws when it is ok: latest, its moves, the averages, the range."""
    n = 1 + len(r.get("moves") or {}) + sum(1 for k in ("avg7", "avg30", "lo30", "avg365", "range") if r.get(k) is not None)
    return n


# ---- lines 1 and 3: ICE and the paid sources
print("\n== line 1: ICE's indices printed as EIA republishes them, without a licence")
ice = [r for r in R if "ICE" in (r.get("note") or "")]
print(f"rows whose note names ICE as the source: {len(ice)} ({', '.join(r['id'] for r in ice)}), all 'licensed'; the board holds no value of them, so printing needs the values first. "
      "EIA's own pages carry ICE's daily spot prices with ICE's permission; the ERW's tables of them are held internal: their values are not printed here")

print("\n== line 3: buying access (a PJM membership, an ICE redistribution licence, USD 25,000 to 30,000 a year)")
paid = collections.Counter()
for r in R:
    if r["status"] == "licensed":
        note = r.get("note") or ""
        who = r["tags"].get("grid") if r["tags"].get("grid") in ("PJM", "NYISO", "ISO-NE") else ("ICE" if "ICE" in note else "S&P Global or Platts" if ("S&P" in note or "Platts" in note) else "other")
        paid[who] += 1
print(f"licensed rows by who would have to grant the licence: {dict(paid)}")

# ---- line 2: the held and paused grids
print("\n== line 2: the grids held for a licence or paused (PJM, NYISO, ISO-NE, MISO): named with 'license needed', or shown")
g = collections.Counter((r["tags"].get("grid"), r["status"]) for r in R if r["tags"].get("grid") in ("PJM", "NYISO", "ISO-NE", "MISO"))
print(f"rows of those grids on the board: {dict(g)}; each draws no figure today and would draw its latest, moves, averages and range once a permission is recorded "
      "(the same rows on /prices, /prices/compare and /supply)")
ok_cells = [cells(r) for r in R if r["status"] == "ok" and r["group"] == "power"]
print(f"for scale, an ok power row draws {sum(ok_cells) / len(ok_cells):.1f} figure cells on average: about {round(sum(ok_cells) / len(ok_cells) * sum(g.values())):,} cells for the {sum(g.values())} rows")

# ---- line 4: ERCOT's missing days
print("\n== line 4: ERCOT's missing day-ahead days of 7 to 9 November 2026: refilled or not")
for r in R:
    if r["tags"].get("grid") == "ERCOT" and r["tags"].get("market") == "da" and r.get("avg30") and r["status"] == "ok" and r["tags"].get("scope", "main") == "main":
        print(f"   {r['id']}: 30-day average {r['avg30']['v']:.2f} over {r['avg30']['n']} days; 7-day {r['avg7']['v']:.2f} over {r['avg7']['n']}")
print("the missing days' prices are in no table on this machine either: the refilled averages are not computed. Each average would gain its missing days (28 to 30)")

# ---- line 5: a stale row's averages
print("\n== line 5: on a row marked stale, the 7-day and 30-day averages and the 30-day low to high drawn (default) or blanked")
POWER_GROUPS = {"power", "da_rt", "peak", "hubspread", "as"}
LIMIT = {"D": 10, "W": 17, "M": 132, "Q": 135}
stale = []
for r in R:
    if r["status"] != "ok" or not r.get("last"):
        continue
    age = (BUILT - dt.date.fromisoformat(r["last"]["t"][:10])).days
    lim = 3 if (r["freq"] == "D" and r["group"] in POWER_GROUPS) else LIMIT.get(r["freq"] or "D", 10)
    if age > lim and r.get("avg7") is not None:
        stale.append((r["id"], r["group"], age))
print(f"stale rows that draw a 7-day average (age past closeAge's limit on {BUILT}): {len(stale)}; each would lose 4 cells (7-day, 30-day, 30-day low, 30-day high): {4 * len(stale)} cells")
print("   " + "; ".join(f"{i} ({gp}, {a} days)" for i, gp, a in stale[:20]))

# ---- line 6: the strip's range cells
print("\n== line 6: the strip's highest and lowest in their year's range: every step (default) or daily series only")
BENCH = ["power", "gas", "crude", "products", "metals", "rates", "carbon"]


def extremes(daily_only):
    rows = [r for r in R if r["status"] == "ok" and not r.get("formula") and r["group"] in BENCH and r.get("range") and r["range"].get("pos") is not None
            and r["tags"].get("scope", "main") == "main" and r["tags"].get("kind", "daily") == "daily" and (not daily_only or r["freq"] == "D")]
    rows.sort(key=lambda r: -r["range"]["pos"])
    return rows[0], rows[-1], len(rows)


for label, d in (("default", False), ("daily only", True)):
    top, bot, n = extremes(d)
    print(f"{label}: {n} candidates; highest {top['id']} ({top['freq']}, latest {top['last']['v']} of {top['last']['t']}, position {top['range']['pos']:.3f}); "
          f"lowest {bot['id']} ({bot['freq']}, latest {bot['last']['v']} of {bot['last']['t']}, position {bot['range']['pos']:.3f})")
