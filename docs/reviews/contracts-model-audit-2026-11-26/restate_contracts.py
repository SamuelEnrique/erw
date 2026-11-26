"""Session 10226: every figure the default view of /contracts prints, restated from the raw table and set against the page
as drawn by its own code (runs/c10226/default_<day>.html, from draw_contracts.mjs).

Written from docs/methods/contracts.md, section 3, and the page's words, not from site/lib/contracts.ts or load.py: the
restatement reads ferc_eqr_contracts.csv of the main checkout (read only) with the standard library, applies the live
set's window itself, and prints counts only (no party's name, no party's figure, no row: the table is internal).

    python runs/c10226/restate_contracts.py 2026-10-05 runs/c10226/default_1005.html
"""
import csv
import datetime as dt
import html as H
import math
import re
import sys

TABLE = r"C:\Users\lossa\Documents\erw\warehouse\output\ferc_eqr_contracts.csv"
POWER = {"ENERGY", "CAPACITY", "TOLLING ENERGY"}
TODAY = dt.date.today().isoformat()

load_day, page_file = sys.argv[1], sys.argv[2]
cutoff = (dt.date.fromisoformat(load_day) - dt.timedelta(days=1000)).isoformat()


def rows():
    csv.field_size_limit(1 << 30)
    with open(TABLE, encoding="utf-8", newline="") as f:
        lines = (line for line in f if not line.startswith("#"))
        yield from csv.DictReader(lines)


def qtr(day):
    return f"{day[:4]}-Q{(int(day[5:7]) - 1) // 3 + 1}"


def ba_name(v):
    s = (v or "").strip().upper()
    return "not stated" if s in ("", "NOT STATED") else s


def js_date(s):
    """YYYYMMDD as the page's engine reads YYYY-MM-DD: a day 1 to 31 runs past its month's end; anything else no date."""
    s = (s or "").strip()
    if not re.fullmatch(r"\d{8}", s):
        return None
    y, m, d = int(s[:4]), int(s[4:6]), int(s[6:])
    if not (1 <= m <= 12 and 1 <= d <= 31) or y < 1:
        return None
    return dt.date(y, m, 1) + dt.timedelta(days=d - 1)


def term(r):
    a, b = js_date(r["x_commencement_date_of_contract_term"]), js_date(r["x_contract_termination_date"])
    if a is None or b is None or b < a:
        return None, None
    y = (b - a).days / 365.25
    days = None if float(f"{y:.1f}") >= 1 else int(math.floor(y * 365.25 + 0.5)) + 1
    return y, days


def is_zero(rate):
    t = rate.strip()
    if t == "":
        return False
    try:
        return float(t) == 0
    except ValueError:
        return False


live, whole = [], 0
for r in rows():
    whole += 1
    if r["event_date"][:10] >= cutoff:
        live.append({k: r[k] for k in ("event_id", "event_date", "x_rate", "x_rate_units", "x_product_name", "x_seller_company_name",
                                        "x_customer_company_name", "x_contract_affiliate", "x_contract_service_agreement_id",
                                        "x_point_of_delivery_balancing_authority", "x_quarter", "x_commencement_date_of_contract_term",
                                        "x_contract_termination_date")})

mine = {}
mine["limits|rows_held"] = len(live)
mine["limits|unpriced"] = sum(1 for r in live if r["x_rate"].strip() == "")
days = sorted(r["event_date"][:10] for r in live)
first, last = days[0], days[-1]
filed = max(q for q in {r["x_quarter"] for r in live} if re.fullmatch(r"\d{4}_Q[1-4]", q)).replace("_", "-")
byq = {}
for r in live:
    byq[qtr(r["event_date"][:10])] = byq.get(qtr(r["event_date"][:10]), 0) + 1
listed = sorted((q for q in byq if q <= filed), reverse=True)
later = sorted((q for q in byq if q > filed), reverse=True)
for q in listed[:12]:
    mine[f"panel|quarter_rows|{q}"] = byq[q]
mine["panel|later_rows"] = sum(byq[q] for q in later)
quarter = listed[0]
qrows = [r for r in live if qtr(r["event_date"][:10]) == quarter]
qrows.sort(key=lambda r: r["event_id"])
qrows.sort(key=lambda r: r["x_seller_company_name"])
qrows.sort(key=lambda r: r["event_date"][:10], reverse=True)
power = [r for r in qrows if r["x_product_name"].strip().upper() in POWER]
mine["sentence|rows"] = len(power)
mine["sentence|agreements"] = len({(r["x_seller_company_name"], r["x_contract_service_agreement_id"]) for r in power})
mine["sentence|sellers"] = len({r["x_seller_company_name"] for r in power if r["x_seller_company_name"]})
mine["sentence|buyers"] = len({r["x_customer_company_name"] for r in power if r["x_customer_company_name"]})
mine["sentence|priced"] = sum(1 for r in power if r["x_rate"].strip())
mine["headline|unpriced"] = mine["sentence|rows"] - mine["sentence|priced"]
mine["headline|zero"] = sum(1 for r in power if is_zero(r["x_rate"]))
mine["headline|affiliate"] = sum(1 for r in power if r["x_contract_affiliate"].strip().upper() == "Y")
bas = {}
for r in power:
    bas[ba_name(r["x_point_of_delivery_balancing_authority"])] = bas.get(ba_name(r["x_point_of_delivery_balancing_authority"]), 0) + 1
ba_list = sorted(bas.items(), key=lambda kv: (-kv[1], kv[0].lower(), kv[0]))[:14]
ties = sum(1 for i in range(1, len(ba_list)) if ba_list[i][1] == ba_list[i - 1][1])
for i, (b, n) in enumerate(ba_list, 1):
    mine[f"panel|ba_rows|{i}"] = n
mine["cannot_see|ercot_rows"] = sum(1 for r in live if ba_name(r["x_point_of_delivery_balancing_authority"]) == "ERCO")
table = []
for r in power[:400]:
    y, d = term(r)
    rate = r["x_rate"].strip()
    table.append((r["event_date"][:10], "as filed" if r["event_date"][:10] > TODAY else "",
                  "" if y is None else f"{y:.1f}", "" if d is None else str(d),
                  "no unit" if rate and not r["x_rate_units"].strip() else ""))
mine["table|rows_drawn"] = len(table)
mine["table|terms_in_years"] = sum(1 for t in table if t[2])
mine["table|terms_in_days"] = sum(1 for t in table if t[3])
mine["table|no_unit_marks"] = sum(1 for t in table if t[4])
mine["table|as_filed_marks"] = sum(1 for t in table if t[1])

# the page as drawn
page = open(page_file, encoding="utf-8").read()


def text(s):
    s = re.sub(r"<!-- -->", "", s)
    return re.sub(r"\s+", " ", H.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def num(s):
    return int(s.replace(",", "")) if s is not None else None


T = text(page)
drawn = {}
drawn["limits|rows_held"] = num(re.search(r"Of the ([\d,]+) rows held", T).group(1))
drawn["limits|unpriced"] = num(re.search(r'data-n="unpriced">([\d,]+)<', page).group(1))
for m in re.finditer(r'href="/contracts\?q=(\d{4}-Q[1-4])&amp;product=power"[^>]*>[^<]*</a>\s*(?:<!-- -->)?\s*<span[^>]*>([\d,]+)(?:<!-- -->)? rows</span>', page):
    drawn[f"panel|quarter_rows|{m.group(1)}"] = num(m.group(2))
drawn["panel|later_rows"] = num(re.search(r'data-later="(\d+)"', page).group(1))
s = re.search(r'<p[^>]*data-summary="1"[^>]*>([\s\S]*?)</p>', page).group(1)
for m in re.finditer(r'data-n="([^"]+)">([^<]*)<', s):
    drawn[f"sentence|{m.group(1)}"] = num(m.group(2))
drawn["headline|unpriced"] = num(re.search(r"The other ([\d,]+) gives? words", T).group(1))
z = re.search(r'data-zero="(\d+)"', page)
drawn["headline|zero"] = num(z.group(1)) if z else 0
drawn["headline|affiliate"] = num(re.search(r"Between affiliates ([\d,]+)", T).group(1))
nav = re.search(r'<nav aria-label="Delivered in"[\s\S]*?</nav>', page).group(0)
ba_drawn = [(H.unescape(m.group(1)), num(m.group(2))) for m in re.finditer(r'<a [^>]*>([^<]+)</a>\s*(?:<!-- -->)?\s*<span[^>]*>([\d,]+)</span>', nav)]
for i, (b, n) in enumerate(ba_drawn, 1):
    drawn[f"panel|ba_rows|{i}"] = n
drawn["cannot_see|ercot_rows"] = num(re.search(r"([\d,]+) of the ([\d,]+) rows held here name ERCOT", T).group(1))
body = re.search(r"<tbody>([\s\S]*?)</tbody>", page).group(1)
trs = re.findall(r"<tr\b[\s\S]*?</tr>", body)
dtable = []
for tr in trs:
    cells = [text(c) for c in re.findall(r"<t[dh]\b[\s\S]*?</t[dh]>", tr)]
    ty = re.search(r"\(\s*(\d+\.\d) years\s*(?::\s*([\d,]+) days?)?\s*\)", cells[4])
    dtable.append((cells[0][:10], "as filed" if "as filed" in cells[0] else "", ty.group(1) if ty else "",
                   (ty.group(2) or "").replace(",", "") if ty else "", "no unit" if "(no unit filed)" in cells[6] else ""))
drawn["table|rows_drawn"] = len(dtable)
drawn["table|terms_in_years"] = sum(1 for t in dtable if t[2])
drawn["table|terms_in_days"] = sum(1 for t in dtable if t[3])
drawn["table|no_unit_marks"] = sum(1 for t in dtable if t[4])
drawn["table|as_filed_marks"] = sum(1 for t in dtable if t[1])

words = {
    "panel|filed_for": (re.search(r"Filed for ([^.]+)\.", T).group(1), filed.replace("-", " ")),
    "panel|first_last": (re.search(r"executed from (\S+) to (\S+?)(?: as filed)?\.", T).group(0),
                         f"executed from {first} to {last}{' as filed' if last > TODAY else ''}."),
    "panel|later_last": (re.search(r"the latest in (\d{4} Q[1-4])", T).group(1), later[0].replace("-", " ") if later else ""),
    "held_here|since": (re.search(r'data-held-here="1">The rows the first view lists: the contracts signed since (\S+?),', page).group(1), first),
    "panel|oldest_held_from": ((re.search(r'data-held-from="[^"]+">Held\s+from (?:<!-- -->)?(\d{4}-\d{2}-\d{2})', page) or [None, ""])[1],
                               first if listed[:12] and dt.date.fromisoformat(first) > dt.date(int(listed[:12][-1][:4]), (int(listed[:12][-1][6]) - 1) * 3 + 1, 1) else ""),
    "default|quarter": (re.search(r'aria-current="true"[^>]*>(\d{4} Q[1-4])<', page).group(1), quarter.replace("-", " ")),
    "panel|ba_names": (" ".join(b for b, _ in ba_drawn), " ".join(b for b, _ in ba_list)),
    "panel|quarters_listed": (" ".join(k.split("|")[2] for k in drawn if k.startswith("panel|quarter_rows|")), " ".join(listed[:12])),
}

print(f"# Session 10226: /contracts, the default view, restated from the raw table against the page drawn by its own code")
print(f"# load day {load_day}: the live set holds the rows executed on or after {cutoff}; today {TODAY}; the quarter's file {whole:,} rows, the window {len(live):,}")
print(f"# the default: {quarter}, energy, capacity and tolling, every balancing authority; ties in the authorities' list: {ties}")
agree = 0
keys = sorted(set(mine) | set(drawn))
for k in keys:
    a, b = mine.get(k), drawn.get(k)
    ok = a == b
    agree += ok
    print(f"{'same' if ok else 'DIFF'}  {k}: restated {a}, drawn {b}")
wagree = 0
for k, (b, a) in words.items():
    ok = a == b
    wagree += ok
    print(f"{'same' if ok else 'DIFF'}  {k}: restated {a!r}, drawn {b!r}")
rows_same = sum(1 for a, b in zip(table, dtable) if a == b)
print(f"table, row by row (date, as filed, years, days, no unit): {rows_same} of {len(table)} the same (drawn {len(dtable)})")
for i, (a, b) in enumerate(zip(table, dtable)):
    if a != b:
        print(f"  row {i + 1}: restated {a}, drawn {b}")
cells = 5 * len(table)
print(f"FIGURES: {agree} of {len(keys)} the same; WORDS: {wagree} of {len(words)} the same; TABLE CELLS: {5 * rows_same} of {cells}")
