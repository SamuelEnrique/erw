# Session 10206: the rows of site/data/board.json kept from an earlier build by warehouse/derived/page_keep.py (the
# row's "held" field), how many days behind the newest value the new build held, by group, and how many of them the page
# marks stale. Counts and dates only; held grids are counted apart and never printed.
import collections
import datetime as dt
import json
import os

SITE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "site")
B = json.load(open(os.path.join(SITE, "data", "board.json"), encoding="utf-8"))
built = dt.date.fromisoformat(B["built"][:10])
HELD = ("nyiso", "isone", "miso", "pjm")
POWER = {"power", "peak", "spark", "da_rt", "battery", "as", "hubspread"}
STALE = {"D": 10, "W": 17, "M": 132, "Q": 135}
kept = [r for r in B["rows"] if r.get("status") == "ok" and "held" in r]
pub = [r for r in kept if not r["id"].startswith(HELD)]
print(f"built {built}; rows with a value {sum(1 for r in B['rows'] if r.get('status') == 'ok')}; kept from an earlier build {len(kept)} ({len(pub)} public)")
why = collections.Counter(r["held"]["why"].split("(")[0].strip() for r in pub)
print("why:", dict(why))
behind = collections.defaultdict(list)
for r in pub:
    last = dt.date.fromisoformat(r["last"]["t"])
    newest = dt.date.fromisoformat(r["held"]["newest"][:10])
    lag = (newest - last).days
    limit = 3 if r["freq"] == "D" and r["group"] in POWER else STALE[r["freq"]]
    age = (built - last).days
    behind[r["group"]].append((lag, age > limit, (built - newest).days > limit, r["id"]))
print("group: kept rows | a newer value held by the new build | marked stale on the page | would not be stale with the new build's newest")
for g, xs in sorted(behind.items()):
    newer = [x for x in xs if x[0] > 0]
    print(f"  {g:12s} {len(xs):4d} | {len(newer):4d} (up to {max((x[0] for x in xs), default=0)} days) | {sum(1 for x in xs if x[1]):4d} | {sum(1 for x in newer if x[1] and not x[2]):4d}")
top = [r for r in pub if r["id"] in ("ercot-hb-hubavg-da", "ercot-hb-hubavg-rt", "caiso-th-sp15-gen-apnd-da", "spp-sppnorth-hub-da", "eia-henry-hub-spot", "ercot-hb-hubavg-spark", "eia-wti-cushing-spot", "eia-brent-spot", "eia-eer-epmru-pf4-y35ny-dpg-spot", "eia-eer-epd2dxl0-pf4-y35ny-dpg-spot", "erw-crack-321-gulf-coast", "fred-dgs10")]
print("the top twelve kept:", [(r["id"], r["last"]["t"], r["held"]["newest"][:10]) for r in top])
old = [r["id"] for r in pub if "moves" in r and "ytd" not in r["moves"]]
print(f"public rows with no YTD move key at all (a row from a build before session 1608): {len(old)}", old[:8])
noavg = [r["id"] for r in pub if r.get("range") and "avg365" not in r]
print(f"public rows with a one-year range and no 12-month mean (built before session 1613): {len(noavg)}", noavg[:8])
wk = {w["hub"]: w for w in B["week"]}
for hub in ("ercot-hb-hubavg", "caiso-th-sp15-gen-apnd", "spp-sppnorth-hub"):
    r = next(x for x in B["rows"] if x["id"] == hub + "-da")
    w = wk.get(hub)
    print(f"{hub}: row's latest day-ahead {r['last']['t']}; the week table's latest day-ahead {w['last_da']['t'] if w and w.get('last_da') else None}")
