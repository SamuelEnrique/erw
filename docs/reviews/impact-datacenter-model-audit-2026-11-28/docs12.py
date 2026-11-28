"""Session 11404: the twelve rows of seed 20261128, each figure against the words the repository holds of its document
(says inside quote, the parsed value, the qualifier, the measure), the picker's figures and whether the row enters the
medians. Also: every row whose quotes state a wage or a spending split the picker does not take."""
import json
import re
import sys

sys.path.insert(0, "warehouse/forecast")
import datacenter_announced as B  # the builder's own parser, to compare with a reading by eye

A = json.load(open("site/data/forecast/datacenter_announced.json", encoding="utf-8"))
IDX = json.load(open("site/data/forecast/deflator.json"))["index"]
rows = {r["id"]: r for r in A["rows"]}
ids = sys.argv[1:]
inmed = {k: set(v["rows"]) for k, v in A["defaults"].items()}
for i in ids:
    r = rows[i]
    print("==", i, "|", r["doc"]["publisher"], r["doc"]["date"], "| to_date", r.get("to_date", False), "| request", r["doc"].get("request"))
    print("   title:", r["doc"]["title"])
    for k in ("mw", "investment", "permanent_jobs", "construction_jobs"):
        f = r.get(k)
        if not f:
            print(f"   {k}: null")
            continue
        inq = f["says"] in f["quote"]
        try:
            parsed = B.parse_says(f["says"])
        except Exception as e:  # noqa: BLE001
            parsed = f"parse error {e}"
        print(f"   {k}: value {f['value']} | says '{f['says']}' in quote {inq} | parsed {parsed} | qualifier '{f.get('qualifier')}' | measure '{f.get('measure', '')}' | year {f.get('year', '')}")
        print(f"      quote: {f['quote']}")
    print("   in medians:", [k for k, s in inmed.items() if i in s])
    print("   flags:", {k: r[k] for k in ("investment_includes_generation", "investment_partial") if r.get(k)}, "| note:", r.get("note", "")[:400])
print()
print("ROWS WHOSE QUOTES STATE A WAGE OR A SPLIT:")
for r in A["rows"]:
    text = " ".join((r.get(k) or {}).get("quote", "") for k in ("mw", "investment", "permanent_jobs", "construction_jobs"))
    if re.search(r"salar|wage|\$\s?[0-9][0-9,]+ (a|per) year|average annual|equipment", text, re.I):
        print(" ", r["id"], "|", text[:300])
