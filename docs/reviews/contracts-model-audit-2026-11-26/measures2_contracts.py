"""Session 10226: /contracts, two more claims set against the rows; counts only (the table is internal).

1. A rate filed as a number whose filed description also stands: the page draws the number and its unit and never the
   description. How often does the description make the number something other than the price (an adder to an index,
   a formula's term, one of several prices)?
2. ERCOT's 244 rows of the file: what their product type and descriptions say ("almost all one utility's transmission
   agreements").

    python runs/c10226/measures2_contracts.py
"""
import csv
import re
from collections import Counter

TABLE = r"C:\Users\lossa\Documents\erw\warehouse\output\ferc_eqr_contracts.csv"
POWER = {"ENERGY", "CAPACITY", "TOLLING ENERGY"}
CUT = "2024-01-09"
INDEX = re.compile(r"\b(LMP|INDEX|INDEXED|ADDER|PLUS|ICE|PLATTS|NYMEX|FORMULA|MARGIN|HEAT RATE|GAS DAILY|CPI|ESCALAT\w*)\b|\+|%", re.I)
TRANS = re.compile(r"TRANSMISSION|TRANSM|WHEEL|INTERCONNECT|NETWORK|POINT.TO.POINT|OATT|SERVICE AGREEMENT", re.I)


def rows():
    csv.field_size_limit(1 << 30)
    with open(TABLE, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(line for line in f if not line.startswith("#"))


def numeric(v):
    try:
        x = float(v.strip())
        return x == x
    except ValueError:
        return False


c = Counter()
ercot_type = Counter()
ercot_words = Counter()
for r in rows():
    day = r["event_date"][:10]
    p = r["x_product_name"].strip().upper()
    if r["x_point_of_delivery_balancing_authority"].strip().upper() == "ERCO":
        ercot_type[(p, r["x_product_type_name"].strip().upper())] += 1
        if p == "OTHER":
            blob = " ".join(r[k] for k in ("x_rate_description", "x_ferc_tariff_reference", "x_contract_service_agreement_id", "x_increment_name"))
            ercot_words["transmission words" if TRANS.search(blob) else "no transmission words"] += 1
    if day < CUT or p not in POWER:
        continue
    rate, desc = r["x_rate"].strip(), r["x_rate_description"].strip()
    if not numeric(rate):
        continue
    z = float(rate) == 0
    c["numbers"] += 1
    c["numbers, not 0"] += not z
    if desc:
        c["with a description"] += 1
        c["with a description, not 0"] += not z
        if INDEX.search(desc):
            c["description names an index, LMP, adder, plus, formula, escalation or a percent (not the words market or hub)"] += 1
            c["the same, not 0"] += not z
            if day >= "2026-04-01" and day < "2026-07-01":
                c["the same, signed in 2026 Q2"] += 1
    if day >= "2026-04-01" and day < "2026-07-01":
        c["numbers signed in 2026 Q2"] += 1
        c["numbers signed in 2026 Q2 with a description"] += bool(desc)

print("# Session 10226: /contracts, a number filed with a description; ERCOT's rows. Counts only")
print("## The window's rows of energy, capacity and tolling (executed on or after 2024-01-09) that file a rate as a number")
for k, v in c.items():
    print(f"{k}: {v:,}")
print("## ERCOT's rows of the file (balancing authority ERCO), by product name and product type")
for (p, t), v in ercot_type.most_common():
    print(f"{p} | {t}: {v}")
print("## ERCOT's rows of product OTHER: words of transmission, interconnection or wheeling in the description, tariff, agreement or increment")
for k, v in ercot_words.items():
    print(f"{k}: {v}")
