# Session 10215: a copy of a figures or measures file for the review's folder with nothing that names a row of the held
# table: every key or field naming a party, a buyer, a deal's id or a priced deal is dropped; counts and sums stay.
#   python runs/c10215/sanitize.py <in.json> <out.json>
import json
import re
import sys

DROP_KEY = re.compile(r"\|party\||chart_party\||\|buyer\||ai_top_|chart_price\||^deals\|ai_(deals|mw|usd|with_mw|with_usd)\|buyer")
DROP_FIELD = {"id", "ids", "kept", "words"}


def clean(o):
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items() if k not in DROP_FIELD and not DROP_KEY.search(k)}
    if isinstance(o, list):
        return [clean(v) for v in o]
    return o


d = json.load(open(sys.argv[1], encoding="utf-8"))
json.dump(clean(d), open(sys.argv[2], "w", encoding="utf-8"), indent=1, sort_keys=True)
print("written", sys.argv[2])
