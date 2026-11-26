"""Session 10229: look at the page files the problem sets read, for the claims the questions make (standard library)."""
import json
import sys
from pathlib import Path

D = Path(sys.argv[1])  # site/data
j = lambda p: json.loads((D / p).read_text(encoding="utf-8"))

t = j("regions/trade/ten.json")
print("ten.json built", t["built"], "months", t["months"][0], "to", t["months"][-1], "n", len(t["months"]))
for c, v in sorted(t["neighbors"].items()):
    print(" ", c, "fields", sorted(v.keys()))
    print("   month0 hours_own", v["hours_own"][0], "hours_their", v.get("hours_their", [None])[0], "hours_both", v.get("hours_both", [None])[0], "of", t["hours_in_month"][0])
    shares = [(h / t["hours_in_month"][k] if isinstance(h, (int, float)) else None, t["months"][k]) for k, h in enumerate(v["hours_own"])]
    low = sorted([s for s in shares if s[0] is not None])[:4]
    print("   lowest shares", [(round(a, 4), m) for a, m in low])
mx = j("regions/trade_matrix.json")
print("matrix keys", list(mx.keys())[:10])
pairs = [p for p in mx["region_pairs"] if p["a"] == "MIDA" and p["b"] == "TEN"]
for p in sorted(pairs, key=lambda p: p["year"]):
    print("  MIDA-TEN", p["year"], p["a_report_mwh"], p["b_report_mwh"], p["gap_mwh"], p["months_held"], p["months_in_year"], p["hours_a"], p["hours_b"])
pairs = [p for p in mx["region_pairs"] if p["a"] == "MIDW" and p["b"] == "TEN"]
for p in sorted(pairs, key=lambda p: p["year"]):
    print("  MIDW-TEN", p["year"], p["a_report_mwh"], p["b_report_mwh"], p["months_held"], p["months_in_year"])

m = j("resources/manifest.json")
for l in m["layers"]:
    if l["id"] in ("solar_ghi", "solar_dni", "wind_speed_100m", "wind_capacity_factor"):
        print(l["id"], "legend", l.get("legend"), "stats", l.get("stats"), "source_stats", l.get("source_stats"), "unit", l.get("unit"))
        for x in l.get("other_extents", []) or []:
            print("    extent", x.get("extent"), "legend", x.get("legend"), "stats", x.get("stats"), "source_stats", x.get("source_stats"))
        print("    keys", sorted(l.keys()))

for code in ("tva", "erco", "ciso"):
    a = j(f"regions/authority/{code}.json")
    print(code, "burns.months", a["burns"]["months"], "co2", a["burns"]["co2"], "size", a["size"], "trades.year", a["trades"]["year"], "owns.vintage", a["owns"]["vintage"])

for ev in ("elliott_2022", "uri_2021"):
    e = j(f"regions/events/{ev}.json")
    print(ev, e["start"], e["end"], e["baseline"], e["hours"], "pairs ending TEN", [k for k in e["pairs"] if k.endswith("-TEN")], "pairs with TEN", [k for k in e["pairs"] if "TEN" in k])
