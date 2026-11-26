"""Session 10227: the EV game's places whose verdict changes under one rule change (ev_restate.json): the sign of the
net present value, and payback crossing the 8 years kept."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
r = json.load(open(os.path.join(HERE, "ev_restate.json")))
D, R = r["default"], r["rules"]
for rule in ("power_12m_verdict", "gas_52w_verdict", "both_verdict"):
    flips, big = [], []
    for code, v in D.items():
        w = R[code][rule]
        if (v["npv"] > 0) != (w["npv"] > 0):
            flips.append(f"{code} {v['npv']:.0f}->{w['npv']:.0f}")
        big.append((abs(w["npv"] - v["npv"]), code, round(v["npv"]), round(w["npv"]), v["payback"] and round(v["payback"], 1), w["payback"] and round(w["payback"], 1)))
    big.sort(reverse=True)
    pos = sum(1 for c in D if D[c]["npv"] > 0)
    pos2 = sum(1 for c in D if R[c][rule]["npv"] > 0)
    print(f"{rule}: NPV above zero in {pos} of {len(D)} places at the page's rule, {pos2} under this one; sign flips {len(flips)}: {', '.join(flips)}")
    print("   largest moves (abs, code, npv, npv', payback, payback'):", big[:6])
    mean = sum(R[c][rule]["npv"] - D[c]["npv"] for c in D) / len(D)
    print(f"   mean change of the NPV over the places: {mean:.2f}")
dp = [(c, round(D[c]["payback"], 2) if D[c]["payback"] else None, round(R[c]["discounted_payback"], 2) if R[c]["discounted_payback"] else None) for c in ("US", "CA", "TX", "MA", "HI")]
print("payback undiscounted and discounted at 5 percent:", dp)
g = R["US"]
print("US gas newest", g["gas_newest"], "52 weeks mean", round(g["gas_52w"], 4), g["weeks_52w"], "| power newest", g["power_newest"], "12 months mean", round(g["power_12m"], 2), g["months_12m"])
