"""Session 10220: rows of the page's ranked lists drawn with the same label (an element whose files before 2022 name no
contingency is one key, and from 2021 the same element with contingency BASE is another, and the page drops "BASE").
Read only.
usage: s6_labels.py"""
import json
import os
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
F = json.load(open(os.path.join(ROOT, "site", "data", "conditions", "congestion.json"), encoding="utf-8"))


def label(c):
    return f"{c['name']} (contingency {c['contingency']})" if c["contingency"] and c["contingency"] != "BASE" else c["name"]


for op, O in F["constraints"].items():
    for yr, t in O["top"].items():
        for lst in ("by_hours", "by_cost"):
            labs = Counter(label(O["constraints"][k]) for k in t[lst])
            twice = {l: n for l, n in labs.items() if n > 1}
            if twice:
                rows = [(i + 1, k, (O["constraints"][k]["hours"] if yr == "all" else O["constraints"][k]["by_year"][yr]["hours"]),
                         (O["constraints"][k]["cost"] if yr == "all" else O["constraints"][k]["by_year"][yr]["cost"]))
                        for i, k in enumerate(t[lst]) if label(O["constraints"][k]) in twice]
                print(f"{op} {yr} {lst}: the same label on two rows: {rows}")
# the three SPP elements with two keys: hours by key and year
O = F["constraints"]["spp"]
for n in ("TEXAS_CO_TXPS_TXCO_PHSHFT_PS", "SPSNMTIES", "Ozrk_B-xfmr_A"):
    for k in (f"spp:{n}", f"spp:{n}|BASE"):
        c = O["constraints"][k]
        print(k, "hours", c["hours"], "cost", c["cost"], {y: v["hours"] for y, v in c["by_year"].items()})
# the hours of 2021 under each key, by month: does the switch happen inside a month?
for n in ("TEXAS_CO_TXPS_TXCO_PHSHFT_PS",):
    for k in (f"spp:{n}", f"spp:{n}|BASE"):
        print(k, [m[:2] for m in O["constraints"][k]["monthly"] if m[0].startswith("2021") or m[0].startswith("2022-01")])
