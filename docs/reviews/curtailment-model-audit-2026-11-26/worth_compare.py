"""Session 10210: worth.json's CAISO months against worth_check.py's restatement from the tables, hub by hub and market
by market, and the audit's measures (hours counted as curtailed, the flat load at thresholds, the battery rule on
intervals against hours). Prints a table and writes worth_compare.json."""
import json
import sys

W = json.load(open(sys.argv[1], encoding="utf-8"))["grids"]["caiso"]
out = {"months": {}, "years": {}}
for path in sys.argv[2:]:
    C = json.load(open(path, encoding="utf-8"))
    for m, rec in C["months"].items():
        row = {}
        for hub in ("TH_SP15_GEN-APND", "TH_NP15_GEN-APND"):
            for mk in ("rt", "da"):
                mine = rec.get(f"caiso:{hub}|{mk}")
                page = W["hubs"][hub][mk]["months"].get(m)
                if not mine or "missing" in mine or not page:
                    row[f"{hub}|{mk}"] = {"page": bool(page), "restated": None if not mine else mine.get("missing", "held")}
                    continue
                d = {
                    "value_usd": (page["value_usd"], round(mine["value_usd"], 0)),
                    "usd_per_mwh": (page["usd_per_mwh_curtailed"], round(mine["usd_per_mwh"], 2)),
                    "mwh": (page["curtailed_mwh_priced"], round(mine["curtailed_mwh_priced"], 1)),
                    "hours_priced": (page["hours_priced"], mine["hours_priced"]),
                    "hours_curtailed": (page["hours_curtailed_priced"], mine["hours_curtailed_priced"]),
                    "neg": (page["share_mwh_negative_pct"], round(mine["neg_pct"], 2)),
                    "flat": (page["price_curtailed_hours_mean"], round(mine["price_curtailed"], 2)),
                    "all": (page["price_all_hours_mean"], round(mine["price_all"], 2)),
                }
                row[f"{hub}|{mk}"] = {"agree": all(abs(a - b) <= (1.0 if k == "value_usd" else 0.011 if k in ("usd_per_mwh", "neg", "flat", "all") else 0.11) for k, (a, b) in d.items()), "pairs": d,
                                      "measures": {k: mine[k] for k in mine if k.startswith(("hours_ge", "price_ge", "mwh_in"))}}
        bp = W["battery"]["months"].get(m, {})
        row["battery"] = {D: {"page": bp.get("absorb_mwh_per_mw", {}).get(D), "intervals": round(rec[f"absorb{D}_intervals"], 2), "hourly": round(rec[f"absorb{D}_hourly"], 2)} for D in ("2", "4", "8")}
        out["months"][m] = row
agree = sum(1 for r in out["months"].values() for k, v in r.items() if k != "battery" and v.get("agree"))
cells = sum(1 for r in out["months"].values() for k, v in r.items() if k != "battery" and "agree" in v)
print(f"{agree} of {cells} hub-market-months agree with worth.json (value to USD 1, per MWh and shares to 0.01, MWh to 0.1, hours exactly)")
for m, r in sorted(out["months"].items()):
    s = r.get("TH_SP15_GEN-APND|rt", {})
    if "pairs" in s:
        p, ms = s["pairs"], s["measures"]
        bad = [k for k, (a, b) in p.items() if abs(a - b) > (1.0 if k == "value_usd" else 0.011 if k in ("usd_per_mwh", "neg", "flat", "all") else 0.11)]
        print(f"{m} SP15 rt agree={s['agree']} {bad} | hours curtailed {p['hours_curtailed'][1]} of {p['hours_priced'][1]}; >=1 MWh {ms['hours_ge1']}, >=10 {ms['hours_ge10']}, >=100 {ms['hours_ge100']}; "
              f"flat {p['flat'][1]} | >=100 MWh {ms['price_ge100'] and round(ms['price_ge100'], 2)} | all {p['all'][1]} | per MWh {p['usd_per_mwh'][1]} | MWh in hours under 100: {round(ms['mwh_in_hours_under100'])} of {p['mwh'][1]}")
    else:
        print(m, "SP15 rt", s)
    print("   battery per MW", r["battery"])
json.dump(out, open("worth_compare.json", "w", encoding="utf-8"), indent=1)
