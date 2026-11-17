#!/usr/bin/env python3
"""ERW, ruling impact for /contracts (session 7570, 17 November 2026).

For each line of docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads) marked "Changes a figure"
under /contracts, the figure under the default and under the other choice, computed from ferc_eqr_contracts (internal
table, warehouse/output) with the rules of replication/contracts/replicate.py (imported, not copied). No party's name and
no party's own figure is printed: a cell of a ranking is given only as its place and its change in percent.

    .venv/Scripts/python.exe runs/ruling_impact/contracts_impact.py
"""
import importlib.util
import os
import re
import statistics
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
spec = importlib.util.spec_from_file_location("rep", os.path.join(ROOT, "replication", "contracts", "replicate.py"))
rep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rep)

d = rep.tables_dir(None)
rows = [rep.Row(r) for r in rep.rows_of(os.path.join(d, "ferc_eqr_contracts.csv"))]
ceiling = rep.largest_station(os.path.join(d, "eia860m_operating_generators.csv"))
import json
with open(os.path.join(ROOT, "replication", "contracts", "page_figures.json"), encoding="utf-8") as f:
    _pf = json.load(f)
stamp = {"load_day": _pf["meta"]["load_day"] if "meta" in _pf else _pf["load_day"],
         "retrieved": (_pf["meta"] if "meta" in _pf else _pf)["tables_retrieved"]}
import datetime as dt
cutoff = (dt.date.fromisoformat(stamp["load_day"]) - dt.timedelta(days=rep.EVENT_DAYS)).isoformat()
filed_for = sorted({r.filed_for for r in rows})[-1].replace("_", "-")
live = [r for r in rows if r.day >= cutoff]
by_q = defaultdict(list)
for r in live:
    by_q[rep.quarter_of(r.day)].append(r)
listed = sorted((q for q in by_q if q <= filed_for), reverse=True)[:rep.QUARTERS_LISTED]
default_q = listed[0]
print(f"tables: ferc_eqr_contracts, {len(rows):,} rows filed for {filed_for}, retrieved {stamp['retrieved']['ferc_eqr_contracts']}; live window from {cutoff}; "
      f"largest station {ceiling:,.1f} MW; default quarter {default_q}")


def shown_rows(q, slug):
    group = rep.PRODUCT_GROUPS[slug]
    every = sorted(by_q[q], key=lambda r: (r.seller, r.id))
    every.sort(key=lambda r: r.day, reverse=True)
    return [r for r in every if group is None or r.product in group]


def pct(a, b):
    return "n/a" if a == 0 else f"{(b - a) / a * 100:+.1f}%"


# ---- buyer groups, as the page merges names
name_rows = Counter(r.buyer for r in rows)
group, shown_as, _ = rep.buyer_groups(name_rows, near=False)
book = [r for r in rows if r.in_force and r.product in rep.THREE]

# ---- line 1: the "MW filed" column with the megawatts view's ceiling
print("\n== line 1: MW filed, with and without the ceiling of", f"{ceiling:,.1f} MW")
for slug in ("energy", "capacity", "tolling"):
    of = [r for r in book if rep.THREE[r.product] == slug]
    for role in ("buyer", "seller"):
        parties = defaultdict(list)
        for r in of:
            parties[shown_as[group[r.buyer]] if role == "buyer" else r.company].append(r)
        out = []
        for party, rs in parties.items():
            mw = [x for x in (rep.filed_mw(r) for r in rs) if x is not None]
            out.append((party, len({r.contract for r in rs}), len(rs), sum(mw), sum(x for x in mw if x <= ceiling), len(mw), sum(1 for x in mw if x > ceiling)))
        out.sort(key=lambda p: (-p[1], -p[2], str(p[0])))
        moved = [(i, p) for i, p in enumerate(out[:rep.TOP], 1) if p[6]]
        all_before, all_after = sum(p[3] for p in out), sum(p[4] for p in out)
        print(f"{slug} {role}s: column total over every party {all_before:,.1f} -> {all_after:,.1f} MW ({pct(all_before, all_after)}); "
              f"cells of the first 25 that move: {len(moved)}" + "".join(f"; place {i}: {pct(p[3], p[4])} ({p[6]} rows over)" for i, p in moved))

# ---- line 2: the list counted by contract, filer and merged buyer name
print("\n== line 2: the list's counts by agreement and seller name (default) against contract, filer and merged buyer name")
for q in listed[:4]:
    for slug in ("power",):
        s = shown_rows(q, slug)
        a = (len({(r.seller, r.agreement) for r in s}), len({r.seller for r in s if r.seller}), len({r.buyer for r in s if r.buyer}))
        b = (len({r.contract for r in s}), len({r.company for r in s}), len({shown_as[group[r.buyer]] for r in s if r.buyer}))
        print(f"{q} {slug}: agreements {a[0]} -> contracts {b[0]} ({pct(a[0], b[0])}); sellers {a[1]} -> filers {b[1]} ({pct(a[1], b[1])}); "
              f"buyers {a[2]} -> merged buyers {b[2]} ({pct(a[2], b[2])})")

# ---- line 3: a rate filed as 0 counted as a price or not
print("\n== line 3: rows with a price as a number, a 0 counted (default) or not")
tot_n = tot_z = tot_rows = 0
for q in listed:
    for slug in ("energy", "capacity", "tolling"):
        drawn = shown_rows(q, slug)[:rep.SHOWN]
        tot_rows += len(drawn)
        tot_n += sum(1 for r in drawn if r.rate.strip() != "")
        tot_z += sum(1 for r in drawn if rep.is_zero(r.rate))
print(f"listed rows of energy, capacity and tolling, 12 quarters: {tot_rows:,} rows; numbers {tot_n:,} -> {tot_n - tot_z:,} ({pct(tot_n, tot_n - tot_z)}), zeros {tot_z:,}")
for q in listed[:4]:
    for slug in ("power", "energy", "capacity", "tolling"):
        s = shown_rows(q, slug)
        n = sum(1 for r in s if r.rate.strip() != "")
        z = sum(1 for r in s if rep.is_zero(r.rate))
        print(f"headline {q} {slug}: {n} of {len(s)} -> {n - z} of {len(s)} ({pct(n, n - z)})")
headline_n = sum(1 for r in rows if rep.is_number(r.rate))
headline_z = sum(1 for r in rows if rep.is_zero(r.rate))
print(f"terms view, 'rows that file their rate as a number' over the quarter's file: {headline_n:,} -> {headline_n - headline_z:,} ({pct(headline_n, headline_n - headline_z)})")

# ---- line 4: capacity prices converted to USD per kW-month
print("\n== line 4: capacity prices as filed against a second figure in USD per kW-month")
TO_KW_MO = {"$/KW-MO": 1.0, "$/MW-MO": 0.001, "$/KW-DAY": 365.25 / 12, "$/MW-DAY": 365.25 / 12 / 1000, "$/KW-YR": 1 / 12, "$/MW-YR": 1 / 12000}
for q in listed[:4]:
    drawn = shown_rows(q, "capacity")[:rep.SHOWN]
    priced = [r for r in drawn if rep.is_number(r.rate) and not rep.is_zero(r.rate)]
    units = Counter(r.rate_units.strip().upper() for r in priced)
    conv = [float(r.rate) * TO_KW_MO[r.rate_units.strip().upper()] for r in priced if r.rate_units.strip().upper() in TO_KW_MO]
    parts = "; ".join(f"{u or '(no unit)'} {n} rows, median {statistics.median(float(r.rate) for r in priced if r.rate_units.strip().upper() == u):,.2f}"
                      for u, n in units.most_common())
    med = f", median of the converted {statistics.median(conv):,.2f} USD/kW-month (min {min(conv):,.3f}, max {max(conv):,.2f})" if conv else ""
    print(f"{q} capacity, {len(drawn)} rows drawn, {len(priced)} non-zero numbers: {parts}; convertible {len(conv)} -> cells added {len(conv)}{med}")

# ---- line 5: rows whose buyer is a market operator
OPERATOR = re.compile(r"\bPJM\b|MIDCONTINENT INDEPENDENT|\bMISO\b|MIDWEST INDEPENDENT TRANSMISSION|SOUTHWEST POWER POOL|\bSPP\b|ELECTRIC RELIABILITY COUNCIL|\bERCOT\b|"
                      r"CALIFORNIA INDEPENDENT SYSTEM|\bCAISO\b|\bISO NEW ENGLAND|\bISO-NE\b|NEW YORK INDEPENDENT SYSTEM|\bNYISO\b|INDEPENDENT SYSTEM OPERATOR|"
                      r"REGIONAL TRANSMISSION ORG", re.I)
print("\n== line 5: rows whose buyer's name is a market operator's, counted (default) or left out")
lr = op = 0
op_names = Counter()
for q in listed:
    for slug in ("energy", "capacity", "tolling"):
        drawn = shown_rows(q, slug)[:rep.SHOWN]
        lr += len(drawn)
        for r in drawn:
            if OPERATOR.search(r.buyer):
                op += 1
                op_names[rep.name_key(r.buyer)] += 1
print(f"listed rows of energy, capacity and tolling, 12 quarters: {lr:,}; operator buyers {op:,}; rows signed {lr:,} -> {lr - op:,} ({pct(lr, lr - op)})")
print(f"operator names matched (market operators are public bodies, not contract parties of the license): {dict(op_names.most_common(12))}")
for q in listed[:4]:
    for slug in ("power", "energy", "capacity", "tolling"):
        s = shown_rows(q, slug)
        o = sum(1 for r in s if OPERATOR.search(r.buyer))
        print(f"rows signed {q} {slug}: {len(s)} -> {len(s) - o} ({pct(len(s), len(s) - o)})")
