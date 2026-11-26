"""Session 10214 (demand audit): 2025's growth of average demand and of the peak on another base year, from a restatement
run with --base (restate.py writes the growth under the 2019 names whatever the base). Standard library.

Usage: python print_base.py <restated json> <base year>
"""
import json
import sys

NAMES = {"ERCO": "ERCOT", "CISO": "CAISO", "PJM": "PJM", "MISO": "MISO", "SWPP": "SPP", "NYIS": "NYISO", "ISNE": "ISO-NE", "US48": "Lower 48"}
R = json.load(open(sys.argv[1], encoding="utf-8"))["areas"]
for ba, r in R.items():
    y = r["years"]
    base = y.get(sys.argv[2], {})
    print(f"{NAMES[ba]}: {sys.argv[2]} {'whole' if 'avg_demand_mw' in base else 'not whole'} ({base.get('hours_used')} of {base.get('hours_in_year')} hours); "
          f"2025 average on {sys.argv[2]} {y['2025'].get('avg_demand_growth_since_2019_pct')}, peak {y['2025'].get('peak_demand_growth_since_2019_pct')}")
