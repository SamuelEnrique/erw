"""Session 10226: /contracts, one rule at a time, and the claims set against the rows. Counts only: no party's name, no
party's figure, no row is printed (the tables are internal).

Reads ferc_eqr_contracts.csv (the file filed for 2026 Q2) and ferc_eqr_contracts_history.csv (2025 Q3, 2025 Q4, 2026 Q1)
of the main checkout, read only, one row at a time.

    python runs/c10226/measures_contracts.py
"""
import csv
import datetime as dt
import re
from collections import Counter, defaultdict

OUT = r"C:\Users\lossa\Documents\erw\warehouse\output"
POWER = {"ENERGY", "CAPACITY", "TOLLING ENERGY"}
FILES = ["2025_Q3", "2025_Q4", "2026_Q1", "2026_Q2"]
CUT_1005, CUT_1126 = "2024-01-09", "2024-03-01"


def rows(path):
    csv.field_size_limit(1 << 30)
    with open(path, encoding="utf-8", newline="") as f:
        yield from csv.DictReader(line for line in f if not line.startswith("#"))


def qtr(day):
    return f"{day[:4]}_Q{(int(day[5:7]) - 1) // 3 + 1}"


def ymd(s):
    s = (s or "").strip()
    if not re.fullmatch(r"\d{8}", s):
        return None
    try:
        return dt.date(int(s[:4]), int(s[4:6]), int(s[6:]))
    except ValueError:
        return None


def qstart(q):
    return dt.date(int(q[:4]), (int(q[6]) - 1) * 3 + 1, 1)


def numeric(v):
    try:
        x = float(v.strip())
        return x == x
    except ValueError:
        return False


rows_fe = Counter()           # (file, execution quarter, power?) -> rows
keys_fe = defaultdict(set)    # (file, execution quarter) -> contracts (company id | contract id), power products
short_fe = Counter()          # (file, execution quarter) -> power rows whose filed term is under a year
ended_before = defaultdict(set)   # (file, E) -> contracts whose filed termination date is before the newest file's quarter
actual_term = defaultdict(set)    # (file, E) -> contracts with an actual termination date filed
newest = {}
ercot = Counter()
ercot_seller = Counter()
default_rows = []
units_default = Counter()
priced_live = Counter()
by_q_all_live = Counter()
whole_q = Counter()
inforce = Counter()
power_file = Counter()
for path in ("ferc_eqr_contracts_history.csv", "ferc_eqr_contracts.csv"):
    for r in rows(f"{OUT}\\{path}"):
        f = r["x_quarter"]
        day = r["event_date"][:10]
        p = r["x_product_name"].strip().upper()
        is_power = p in POWER
        e = qtr(day)
        if f == "2026_Q2":
            whole_q[e] += 1
            inforce[r["status"]] += 1
            power_file[is_power] += 1
            if r["x_point_of_delivery_balancing_authority"].strip().upper() == "ERCO":
                ercot[p] += 1
                ercot_seller[r["x_company_id"]] += 1
            if day >= CUT_1005:
                by_q_all_live[e] += 1
                rate = r["x_rate"]
                priced_live["nonempty" if rate.strip() else "empty"] += 1
                if rate.strip():
                    priced_live["numeric" if numeric(rate) else "nonempty_not_numeric"] += 1
                    if numeric(rate) and float(rate) == 0:
                        priced_live["zero"] += 1
                if e == "2026_Q2" and is_power:
                    default_rows.append((r["x_seller_company_name"], r["x_contract_service_agreement_id"], p, r["x_company_id"],
                                         r["x_contract_unique_id"], r["x_customer_company_name"], r["x_rate"].strip(), r["x_rate_units"].strip().upper(),
                                         r["x_commencement_date_of_contract_term"], r["x_contract_termination_date"]))
        if "2024_Q1" <= e <= "2026_Q2":
            rows_fe[(f, e, is_power)] += 1
            if is_power:
                k = f"{r['x_company_id']}|{r['x_contract_unique_id']}"
                keys_fe[(f, e)].add(k)
                a, b = ymd(r["x_commencement_date_of_contract_term"]), ymd(r["x_contract_termination_date"])
                if a and b and b >= a and (b - a).days / 365.25 < 1:
                    short_fe[(f, e)] += 1
                if b and b < qstart("2026_Q2"):
                    ended_before[(f, e)].add(k)
                if ymd(r["x_actual_termination_date"]):
                    actual_term[(f, e)].add(k)

print("# Session 10226: /contracts, one rule at a time; counts only")
print("\n## 1. The quarters signed, as each quarter's own file filed them and as the newest file (2026 Q2) holds them: energy, capacity and tolling")
print("execution quarter | rows in its own file | rows in the next file | rows in 2026 Q2's file (the page) | the page over its own file | contracts: own file, 2026 Q2, kept | short terms (under a year): own file, 2026 Q2")
for e in ["2025_Q3", "2025_Q4", "2026_Q1", "2026_Q2"]:
    own = rows_fe[(e, e, True)]
    nxt_f = FILES[FILES.index(e) + 1] if e != "2026_Q2" else None
    nxt = rows_fe[(nxt_f, e, True)] if nxt_f else None
    page = rows_fe[("2026_Q2", e, True)]
    ko, kp = keys_fe[(e, e)], keys_fe[("2026_Q2", e)]
    print(f"{e} | {own:,} | {nxt if nxt is None else f'{nxt:,}'} | {page:,} | {page / own:.3f} | {len(ko):,}, {len(kp):,}, {len(ko & kp):,} | {short_fe[(e, e)]:,}, {short_fe[('2026_Q2', e)]:,}")
print("every product, rows: " + "; ".join(f"{e} own file {rows_fe[(e, e, True)] + rows_fe[(e, e, False)]:,}, 2026 Q2's {rows_fe[('2026_Q2', e, True)] + rows_fe[('2026_Q2', e, False)]:,}" for e in ["2025_Q3", "2025_Q4", "2026_Q1"]))

print("\n## 2. Why a contract of an older quarter is missing from 2026 Q2's file (energy, capacity and tolling)")
for e in ["2025_Q3", "2025_Q4", "2026_Q1"]:
    ko, kp = keys_fe[(e, e)], keys_fe[("2026_Q2", e)]
    gone = ko - kp
    ended = gone & ended_before[(e, e)]
    act = gone & actual_term[(e, e)]
    print(f"{e}: {len(gone):,} of {len(ko):,} contracts in its own file are not in 2026 Q2's; of them {len(ended):,} file a termination date before 1 April 2026, "
          f"{len(act):,} an actual termination date; {len(gone - ended - act):,} neither")

print("\n## 3. Filed late: contracts executed in a quarter that first appear in the next quarter's file (energy, capacity and tolling)")
for e, nxt in [("2025_Q3", "2025_Q4"), ("2025_Q4", "2026_Q1"), ("2026_Q1", "2026_Q2")]:
    ko, kn = keys_fe[(e, e)], keys_fe[(nxt, e)]
    late = kn - ko
    print(f"{e}: {len(ko):,} contracts in its own file; {len(late):,} more first filed for {nxt} (+{len(late) / len(ko) * 100:.1f} percent); rows in {nxt}'s file {rows_fe[(nxt, e, True)]:,} against {rows_fe[(e, e, True)]:,}")

print("\n## 4. The window (1,000 days) against the whole file, rows by quarter of execution, every product")
for e in sorted(by_q_all_live):
    if e <= "2026_Q2":
        print(f"{e}: window {by_q_all_live[e]:,}, whole file {whole_q[e]:,}")
print(f"rows of 2026 Q2's file executed before {CUT_1005}: {sum(n for q, n in whole_q.items() if q < '2024_Q1') + whole_q['2024_Q1'] - by_q_all_live['2024_Q1']:,} of {sum(whole_q.values()):,}")
print(f"largest quarter in the window (every product): {max(v for q, v in by_q_all_live.items() if q <= '2026_Q2'):,} rows (the read's limit 5,000)")

print("\n## 5. A price as a number: the rows of the window")
print(f"x_rate not empty {priced_live['nonempty']:,}; of them reading as a number {priced_live['numeric']:,}, not a number {priced_live['nonempty_not_numeric']:,}; the number 0 {priced_live['zero']:,}; empty {priced_live['empty']:,}")

print("\n## 6. The default view (2026 Q2 signed, energy, capacity and tolling): rows, agreements, contracts, products")
n = len(default_rows)
g_agr = Counter((r[0], r[1]) for r in default_rows)
g_agr_p = Counter((r[0], r[1], r[2]) for r in default_rows)
g_con = Counter((r[3], r[4]) for r in default_rows)
g_con_p = Counter((r[3], r[4], r[2]) for r in default_rows)
print(f"rows {n}; agreements (seller name | agreement id) {len(g_agr)}; contracts (company id | contract id) {len(g_con)}")
print(f"agreement and product: {len(g_agr_p)} pairs; {sum(1 for v in g_agr_p.values() if v > 1)} hold more than one row, {sum(v for v in g_agr_p.values() if v > 1)} rows in them, largest {max(g_agr_p.values())}")
print(f"contract and product: {len(g_con_p)} pairs; {sum(1 for v in g_con_p.values() if v > 1)} hold more than one row, {sum(v for v in g_con_p.values() if v > 1)} rows in them, largest {max(g_con_p.values())}")
print(f"sellers by name {len({r[0] for r in default_rows if r[0]})}, by company id {len({r[3] for r in default_rows if r[3]})}; "
      f"buyers by name {len({r[5] for r in default_rows if r[5]})}, by name in capitals and trimmed {len({r[5].strip().upper() for r in default_rows if r[5].strip()})}")
for r in default_rows:
    if r[6] and numeric(r[6]):
        units_default[(r[2], r[7] or "(none)")] += 1
print("numbers by product and unit: " + "; ".join(f"{p} {u} {c}" for (p, u), c in sorted(units_default.items())))
mstrip = Counter()
for r in default_rows:
    a, b = ymd(r[8]), ymd(r[9])
    if a and b and a.day == 1:
        nxt = (a.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
        if b == nxt - dt.timedelta(days=1):
            mstrip["to the month's last day"] += 1
        elif b == nxt:
            mstrip["to the next month's first day"] += 1
print("strips of one calendar month from its first day: " + "; ".join(f"{k} {v}" for k, v in mstrip.items()))

print("\n## 7. ERCOT in 2026 Q2's whole file")
tot = sum(ercot.values())
top = max(ercot_seller.values()) if ercot_seller else 0
print(f"rows {tot}; by product: " + "; ".join(f"{p} {c}" for p, c in ercot.most_common()) + f"; filers {len(ercot_seller)}, the largest filer's rows {top} ({top / tot * 100:.1f} percent)")

print("\n## 8. The decisions' figures")
whole = sum(whole_q.values())
print(f"energy, capacity and tolling: {power_file[True]:,} of {whole:,} rows of the file ({power_file[True] / whole * 100:.1f} percent); "
      f"of the rows signed in 2026 Q2 (the window): {n} of {by_q_all_live['2026_Q2']:,} ({n / by_q_all_live['2026_Q2'] * 100:.1f} percent)")
print(f"in force {inforce['in_force']:,}, terminated {inforce['terminated']:,}, whole file {whole:,}")
