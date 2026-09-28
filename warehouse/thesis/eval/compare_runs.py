#!/usr/bin/env python3
"""Compare a Thesis Builder workbook with an earlier one for the same niche (session 27).

Reports, for the new workbook, the Capital rows with a quoted investor (an investors cell other than blank or "not
disclosed", kept under the span rule) and with a quoted date (a date cell kept under the span rule), and every row where
the two runs disagree:
  - Capital: rows of the same company and round (the whole round name, and the date as far as both give one) whose
    amounts differ (their digits);
  - Landscape: companies in both whose stage differs (lower case, parentheses dropped).

    python warehouse/thesis/eval/compare_runs.py OLD.xlsx NEW.xlsx
"""

import re
import sys

from openpyxl import load_workbook


def rows(ws, first):
    out, head = [], None
    for row in ws.iter_rows(values_only=True):
        v = list(row[1:])
        if v and v[0] == first:
            head = v
            continue
        if head and v and str(v[0] or "").startswith("Source(s)"):
            break
        if head and any(x not in (None, "") for x in v):
            out.append({k: ("" if x is None else str(x)) for k, x in zip(head, v)})
    return out


def key(name):
    s = re.sub(r"\(.*?\)", " ", name.lower())
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\b(inc|llc|ltd|corp|corporation|co|plc|lp|energy|power|systems|technologies)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def digits(s):
    m = re.search(r"\d[\d,.]*", s or "")
    return m.group(0).replace(",", "").rstrip(".") if m else ""


def stage(s):
    return re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", (s or "").lower())).strip()


def main(old_path, new_path):
    old, new = load_workbook(old_path), load_workbook(new_path)
    oc, nc = rows(old["Capital"], "Date"), rows(new["Capital"], "Date")
    inv = [r for r in nc if r["Investors"].strip() and r["Investors"].strip().lower() != "not disclosed"]
    dates = [r for r in nc if r["Date"].strip()]
    both = [r for r in inv if r["Date"].strip()]
    print(f"{new_path}: Capital rows {len(nc)}; with a quoted investor {len(inv)}; with a quoted date {len(dates)}; "
          f"with both {len(both)}")
    print(f"  earlier: Capital rows {len(oc)}")
    def kindkey(k):  # the whole round, parentheses kept as words: "Series B (final close)" = "Series B final close"
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", k.lower())).strip()

    for r in nc:
        for o in oc:
            if key(o["Company"]) != key(r["Company"]) or kindkey(o["Kind"]) != kindkey(r["Kind"]):
                continue
            od, nd = o["Date"], r["Date"]
            if od and nd and od[:len(min(od, nd, key=len))] != nd[:len(min(od, nd, key=len))]:
                continue
            a, b = digits(o["Amount"]), digits(r["Amount"])
            if a and b and a != b:
                print(f"  AMOUNT differs: {r['Company']} {r['Kind']} {r['Date'] or o['Date']}: earlier {o['Amount']!r}, now {r['Amount']!r}")
    ol, nl = rows(old["Landscape"], "Company"), rows(new["Landscape"], "Company")
    old_by = {key(o["Company"]): o for o in ol}
    found = 0
    for r in nl:
        o = old_by.get(key(r["Company"]))
        if not o:
            continue
        found += 1
        if stage(o["Stage"]) != stage(r["Stage"]):
            print(f"  STAGE differs: {r['Company']}: earlier {o['Stage']!r}, now {r['Stage']!r}")
    print(f"  Landscape: {len(nl)} companies now, {len(ol)} earlier, {found} in both")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
