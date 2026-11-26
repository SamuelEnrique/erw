"""Session 10229 (finding 7): the PG&E default bill is a winter bill; its wholesale price is September 2026's. The share
at the winter months' mean price, and the September price against PG&E's summer bill. From replication/bill/source_rows.csv
and site/data/bill_rules.json."""
import csv
import json
import sys
from decimal import Decimal, ROUND_HALF_UP

rows, rules = sys.argv[1], sys.argv[2]
p = lambda v: str(Decimal(v).quantize(Decimal("0.01"), ROUND_HALF_UP))
lw = {}
with open(rows, encoding="utf-8") as f:
    for r in csv.DictReader(line for line in f if not line.startswith("#")):
        if r["variable"] in ("rt_load_weighted", "rt_hours", "hours_in_month"):
            lw.setdefault((r["entity"], r["ts_utc"][:7]), {})[r["variable"]] = float(r["value"])
ca = json.load(open(rules, encoding="utf-8"))["bills"]["CA"]


def bill(season):
    d = ca["defaults"]
    kwh, ps, days = d["kwh"], d["peak_share"], d["days"]
    base = min(kwh, ca["baseline_quantities"]["code_B"][d["territory"]][0 if season == "summer" else 1] * days)
    s = ca["seasons"][season]
    return kwh * (ps * s["peak"] + (1 - ps) * s["offpeak"]) + base * ca["baseline_credit"]["rate"] + days * ca["base_services"]["tiers"][d["income_tier"]]


win, summ = bill("winter"), bill("summer")
ent = "caiso:TH_NP15_GEN-APND"
sep = lw[(ent, "2026-09")]["rt_load_weighted"]
months = [m for (e, m) in lw if e == ent and "2025-10" <= m <= "2026-05" and "rt_load_weighted" in lw[(e, m)]]
mean = sum(lw[(ent, m)]["rt_load_weighted"] for m in months) / len(months)
whole = [m for m in months if lw[(ent, m)].get("rt_hours") == lw[(ent, m)].get("hours_in_month")]
print("winter bill", p(win), "summer bill", p(summ))
print("September", sep, "wholesale", p(600 * sep / 1000), "share of the winter bill", p(600 * sep / 1000 / win * 100), "of the summer bill", p(600 * sep / 1000 / summ * 100))
print("winter months held", sorted(months), "whole", sorted(whole))
print("their mean", mean, "wholesale", p(600 * mean / 1000), "share of the winter bill", p(600 * mean / 1000 / win * 100))
