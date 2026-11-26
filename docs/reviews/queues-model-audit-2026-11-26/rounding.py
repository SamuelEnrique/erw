"""Session 10213: the three cells where the page's whole MW differs from the exact sum by one: the exact sums, with
Decimal, so float addition is ruled out.

    python rounding.py <lbnl csv>
"""
import csv
import sys
from decimal import Decimal

rows = [r for r in csv.DictReader(ln for ln in open(sys.argv[1], encoding="utf-8", newline="") if not ln.startswith("#"))]


def mw(r):
    try:
        v = Decimal(r["capacity_mw"])
    except Exception:
        return Decimal(0)
    return v if v > 0 else Decimal(0)


def yr(r):
    return int(float(r["q_year"])) if r["q_year"] else None


for label, sel in [("2005 mw_active", lambda r: yr(r) == 2005 and r["q_status"] == "active"),
                   ("2016 mw_entered", lambda r: yr(r) == 2016),
                   ("2022 mw_entered", lambda r: yr(r) == 2022)]:
    s = sum((mw(r) for r in rows if sel(r)), Decimal(0))
    one = s.quantize(Decimal("0.1"), rounding="ROUND_HALF_EVEN")
    print(f"{label}: exact {s}; the builder's round to 0.1 gives {one}; the page rounds that to {int(one + Decimal('0.5'))}; "
          f"the exact sum rounds to {int((s + Decimal('0.5')) // 1)}")
# how many keyed MW cells of the whole file could round twice: sums whose exact hundredths fall at .45 to .49
n = 0
tot = 0
from collections import defaultdict
acc = defaultdict(Decimal)
for r in rows:
    y = yr(r)
    if y is None:
        continue
    st = {"operational": "operating"}.get(r["q_status"], r["q_status"])
    acc[(r["region"], y, "entered")] += mw(r)
    acc[(r["region"], y, st)] += mw(r)
for k, s in acc.items():
    tot += 1
    frac = s - (s // 1)
    if Decimal("0.45") <= frac < Decimal("0.5"):
        n += 1
print(f"region-by-year MW sums (every technology): {tot}; with a fraction from .45 to .49, where rounding twice adds one MW: {n}")
