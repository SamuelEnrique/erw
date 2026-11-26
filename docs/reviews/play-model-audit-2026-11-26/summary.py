"""Session 10227 (play audit): the lines measures.out does not print (retail with the end condition), and the yearly
highest ERCOT hub average real-time price of the history held here (the cap's year)."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(HERE, "measures.json")))
ex = json.load(open(os.path.join(HERE, "extract.json")))
for d, v in m.items():
    if d == "_rules":
        continue
    print(d, "any power, end free:", round(v["any_power_end_free_check"], 6), "| retail buy:", v.get("retail_buy_any_power") and round(v["retail_buy_any_power"], 6),
          "| retail buy and end >= start:", v.get("retail_buy_end_at_least_start_any_power") and round(v["retail_buy_end_at_least_start_any_power"], 6))
years = {}
for d, (mean, lo, hi, n) in ex["ercot_hist_days"].items():
    y = d[:4]
    years[y] = max(years.get(y, -1e9), hi)
print("highest interval price by year:", {y: round(v, 2) for y, v in sorted(years.items())})
