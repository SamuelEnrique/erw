"""Audit of /equities, session 11403: does a held price reach a file the page or the board reads, or a download?

Checks every file under site/data/equities/ and any equities file under site/public/: a company's or index's or
segment's daily rows, last value, moves and market value; the board rows; the list's last close, moves and market value;
the energy prices of a held grid (PJM, NYISO, ISO-NE held by their terms; MISO paused). Prints counts, never a value of
a held series. No request, no write."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "site", "data", "equities")
found = []

idx = json.load(open(os.path.join(D, "index.json"), encoding="utf-8"))
for c in idx["companies"]:
    for k in ("last_close", "moves", "market_value", "first", "last"):
        v = c.get(k)
        if v and (not isinstance(v, dict) or any(v.values())):
            found.append(f"index.json {c['ticker']} {k}")
    if c["price_status"] != "license needed":
        found.append(f"index.json {c['ticker']} price_status {c['price_status']}")
if idx["indices"] or idx["segment_series"] or idx["last_day"]:
    found.append("index.json carries an index, a segment line or a last trading day")

n_files = n_rows = 0
for f in sorted(os.listdir(os.path.join(D, "series"))):
    s = json.load(open(os.path.join(D, "series", f), encoding="utf-8"))
    n_files += 1
    for r in s.get("daily") or []:
        if any(x is not None for x in r[1:]):
            found.append(f"series/{f} a daily row with a value")
        n_rows += 1
    for k in ("last", "last_value_weight"):
        if s.get(k):
            found.append(f"series/{f} {k}")
    for k in ("moves", "moves_value_weight"):
        if any((s.get(k) or {}).values()):
            found.append(f"series/{f} {k}")

b = json.load(open(os.path.join(D, "board.json"), encoding="utf-8"))
for r in b["rows"]:
    if r["status"] != "not_held" or r.get("last") or r.get("moves") or r.get("spark") or r.get("file"):
        found.append(f"board.json {r['id']} {r['status']}")
weights = sorted({r["tags"]["weighting"] for r in b["rows"]})

p = json.load(open(os.path.join(D, "energy_prices.json"), encoding="utf-8"))
held = [s["id"] for s in p["series"] if s["status"] != "shown"]
for s in p["series"]:
    if s["status"] != "shown" and (p["daily"].get(s["id"]) or s["last_value"] or any(s["moves"].values())):
        found.append(f"energy_prices.json {s['id']} ({s['status']}) carries a value")
    if s["status"] == "shown" and any(g in (s["entity"] or "") for g in ("pjm", "nyiso", "isone", "miso")):
        found.append(f"energy_prices.json {s['id']} is a held grid's and shown")

pub = []
for dp, dn, fn in os.walk(os.path.join(ROOT, "site", "public")):
    pub += [os.path.join(dp, x) for x in fn if "equit" in x.lower() or "equit" in dp.lower()]

print(f"list: {len(idx['companies'])} companies; series files {n_files} with {n_rows} daily rows (all must be empty)")
print(f"board rows {len(b['rows'])}, weightings named {weights}, statuses {sorted({r['status'] for r in b['rows']})}")
print(f"energy prices: {len(p['series'])} series, held {held}; shown {[s['id'] for s in p['series'] if s['status'] == 'shown']}")
print(f"equities files under site/public: {pub}")
print(f"held values found: {len(found)}")
for x in found:
    print("  " + x)
