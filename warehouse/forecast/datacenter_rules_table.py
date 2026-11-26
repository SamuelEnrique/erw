"""Chain 740, session 10821: a markdown table of every state in site/data/forecast/datacenter_rules.json (sales tax
exemption, property, electricity), for docs/methods/forecast.md 13.3. Usage: rules_table.py RULES_JSON > out.md"""
import json
import sys

r = json.load(open(sys.argv[1], encoding="utf-8"))
rows = []
for code, s in sorted(r["states"].items(), key=lambda kv: kv[1]["name"]):
    ex = s.get("sales_exemption")
    if not ex:
        sale = "none read"
    elif ex.get("discretionary"):
        sale = "words only"
    else:
        bits = []
        if ex.get("min_investment_usd"):
            bits.append("USD %s million" % format(ex["min_investment_usd"] / 1e6, ",.0f"))
        if ex.get("min_jobs"):
            bits.append("%d jobs" % ex["min_jobs"])
        if ex.get("min_mw"):
            bits.append("%d MW" % ex["min_mw"])
        if ex.get("last_year"):
            bits.append("through %d" % ex["last_year"])
        if ex.get("term_years"):
            bits.append("%d years" % ex["term_years"])
        if ex.get("rate_part") == "state":
            bits.append("state rate")
        bits.append("+".join(ex.get("covers", [])) or "nothing")
        sale = "; ".join(bits)
    p = s.get("property")
    prop = "none read" if not p else "building %s, equipment %s" % (
        format(p["building_ratio"] * 100, ".4g") + "%", format(p["equipment_ratio"] * 100, ".4g") + "%")
    el = s.get("electricity")
    elec = "none read" if not el else ("%d monthly blocks" % len(el["blocks"])) + (" or an elective schedule" if el.get("elective") else "")
    rows.append("| %s | %s | %s | %s |" % (s["name"], sale, prop, elec))
print("| State | Sales tax exemption as applied | Property: assessed share of cost | Electricity tax |")
print("|---|---|---|---|")
print("\n".join(rows))
