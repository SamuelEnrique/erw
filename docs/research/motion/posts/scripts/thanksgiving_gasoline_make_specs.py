"""B3, session 9900: write the two gasoline specs (versions A and B) from thanksgiving_week_fuel.csv. The display is
EIA's three-decimal price rounded half up to cents (JavaScript's toFixed would print 3.805 as 3.80)."""
import csv
import json
import sys
from decimal import ROUND_HALF_UP, ROUND_UP, Decimal

rows_in = [r for r in csv.DictReader(open(sys.argv[1])) if 2020 <= int(r["year"]) <= 2026]
outdir = sys.argv[2]
rows = [{"label": r["year"], "value": float(r["gasoline_regular"]),
         "display": "$" + str(Decimal(r["gasoline_regular"]).quantize(Decimal("0.01"), ROUND_HALF_UP))} for r in rows_in]
top = max(Decimal(r["gasoline_regular"]) for r in rows_in)
mx = float((top * Decimal("1.1")).quantize(Decimal("0.01"), ROUND_UP))
source = ("Source: EIA, Weekly Retail Gasoline and Diesel Prices. US regular gasoline, all formulations, USD a gallon, "
          "nominal, on the Monday of Thanksgiving week, 2020-2025. 2026 is 16 November, the newest week EIA had "
          "published on 24 November.")
for ver, title in (("a", "Gasoline on Thanksgiving week, 2020-2026"), ("b", "Everything is on sale this Friday. Gasoline isn't.")):
    spec = {"id": f"thanksgiving_gasoline_{ver}", "type": "post", "width": 1080, "height": 1080, "frames": 450,
            "decimals": 2, "max": mx, "title": title, "source": source, "rows": rows,
            "_numbers_from": "eia_retail_fuel_prices (retrieved 20261120T150214Z), eia:EMM_EPMR_PTE_NUS_DPG; EIA API v2 "
                             "read 2026-11-24T10:32:45Z, newest week 2026-11-16"}
    json.dump(spec, open(f"{outdir}/thanksgiving_gasoline_{ver}.json", "w"), indent=1)
print("max", mx)
for r in rows:
    print(r)
