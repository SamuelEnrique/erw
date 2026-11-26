"""Session 10231: the two addresses of the ERCOT peak premium set side by side. The ERCOT tab of /prices (where
/explorer/ercot-peak-premium redirects), as it first draws, against /explore/ercot-peak-premium's default view and the
restatement from the 15-minute prices.

    python compare_tabs.py <explorer_tab.json> <peak_opening.json> <hubavg.csv>
"""
import json
import sys
from decimal import Decimal, ROUND_HALF_UP

from restate_peak import load_prices, metrics

tab = json.load(open(sys.argv[1], encoding="utf-8"))
op = json.load(open(sys.argv[2], encoding="utf-8"))
rt = load_prices(sys.argv[3])
m25 = metrics([(l.hour, x) for _, l, x in rt if l.year == 2025])
same = both = 0
mine_eq = 0
for f in tab["figures"]:
    var = f["key"].split("|")[3]
    unit = "count" if var.startswith("n_") else "USD"
    v = m25[var]
    mine = f"{int(round(v)):,}" if unit == "count" else f"{Decimal(repr(round(v, 6))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):,.2f}"
    mine_eq += mine == f["text"]
    if f["key"] in op["keyed"]:
        both += 1
        same += op["keyed"][f["key"]]["text"] == f["text"]
    else:
        print("  on the tab only:", f["key"].split("|", 3)[3], f["text"], "restated", mine)
print(f"the tab's {len(tab['figures'])} figures: {mine_eq} equal the restatement from the prices; {both} are also on /explore's default view, {same} of them with the same text")
print("the tab's words:", tab["text"][:1600])
