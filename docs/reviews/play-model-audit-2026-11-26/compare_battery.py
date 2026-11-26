"""Session 10227 (play audit): restate.py's independent figures against the site's own (site_side.json), every level,
mode and play: score, the server's four-place score, kWh bought and sold, their average prices, the end and its reason.

    python compare_battery.py      (writes compare_battery.out's lines to stdout)
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
mine = json.load(open(os.path.join(HERE, "restate.json")))
site = json.load(open(os.path.join(HERE, "site_side.json")))
worst, n, bad = 0.0, 0, []
for key, m in mine.items():
    date, mode = key.split("|")
    for smode in ([mode, "easy"] if mode == "normal" else [mode]):
        s = site[f"{date}|{smode}"]
        d = abs(m["dp"] - s["optimum"])
        worst = max(worst, d); n += 1
        if round(m["dp"], 4) != s["server_optimal"]:
            bad.append(f"{key} {smode} optimum {m['dp']} against {s['server_optimal']}")
        for play, r in m["plays"].items():
            t = s["plays"][play]
            for a, b in (("score", "score"), ("bought", "bought"), ("sold", "sold"), ("buy_avg", "buy_avg"), ("sell_avg", "sell_avg"), ("soc_end", "soc_end")):
                x, y = r[a], t[b]
                if x is None or y is None:
                    if x is not y:
                        bad.append(f"{key} {smode} {play} {a}: {x} against {y}")
                    continue
                worst = max(worst, abs(x - y)); n += 1
            if round(r["score"], 4) != t["server"]:
                bad.append(f"{key} {smode} {play} server score {round(r['score'], 4)} against {t['server']}")
            if (r["end"], r["why"]) != (t["end"], t["why"]):
                bad.append(f"{key} {smode} {play} end {r['end']} {r['why']} against {t['end']} {t['why']}")
        # the site's own best plan scored by the restatement equals the restatement's optimum
        sb = s["plays"]["site_best"]["score"]
        worst = max(worst, abs(sb - m["dp"])); n += 1
print(f"figures compared {n}; largest difference {worst:.3e}; disagreements {len(bad)}")
for x in bad:
    print("  ", x)
print()
print("level, mode: optimum (three actions) | any power | naive | bad | sell first | idle  (USD, one battery)")
for key, m in mine.items():
    p = m["plays"]
    print(f"{m['slug']:>16} {key}: {m['dp']:.4f} | {m['mip_any_power']:.4f} | {p['naive']['score']:.4f} {p['naive']['why'] or ''} | "
          f"{p['bad']['score']:.4f} {p['bad']['why'] or ''} | {p['sell_first']['score']:.4f} | {p['idle']['score']:.4f}"
          f" | best bought {p['best']['bought']:.4f} kWh at {p['best']['buy_avg'] if p['best']['buy_avg'] is None else round(p['best']['buy_avg'], 2)},"
          f" sold {p['best']['sold']:.4f} at {round(p['best']['sell_avg'], 2)}")
