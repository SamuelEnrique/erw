#!/usr/bin/env python3
"""ERW, the severance tool: the cross-check against published figures (session 7502, chain 304).

Two things are set beside what their publishers say, and nothing is adjusted to match:

1. The rates of the rules file (site/data/severance_rules.json) for Texas, beside the Texas Comptroller's pages as they
   read today: the oil, gas and condensate rates, the two regulatory fees, and every certified price of the
   low-producing credits, period by period.
2. A year of Texas collections: the tool's base rule (4.6 percent of value for oil, 7.5 percent for gas) on the state's
   published production and a published price, beside what the Comptroller says it collected. Oil is taxed the month
   after it is produced (the report is due the 25th of the next month), so a fiscal year of collections (September to
   August) stands against production from August to July; gas is due the 20th of the second month, so against
   production from July to June.

    python replication/severance/crosscheck.py --published DIR [--tables DIR] [--fetch] [--write FILE]

    --published DIR  the publishers' files (named below). --fetch downloads them there first, one request each, with
                     the User-Agent "ERW research project, github.com/SamuelEnrique/erw" (the robots file and the terms
                     of each host were read on 16 November 2026: docs/methods/severance.md, "The cross-check").
    --tables DIR     the folder that holds eia_fuel_spot_prices.csv (the tool's default prices, for the second line of
                     each year). Default: warehouse/output of this copy.

Needs openpyxl for the Comptroller's workbook. Exit 0 when every file is read; 2 when one is missing.
"""
import argparse
import csv
import html
import json
import os
import re
import sys
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
UA = "ERW research project, github.com/SamuelEnrique/erw"
FILES = {
    "tx_oil.html": "https://comptroller.texas.gov/taxes/crude-oil/",
    "tx_gas.html": "https://comptroller.texas.gov/taxes/natural-gas/",
    "tx_lp_oil.html": "https://comptroller.texas.gov/taxes/crude-oil/low-producing-leases.php",
    "tx_lp_gas.html": "https://comptroller.texas.gov/taxes/natural-gas/low-producing-wells.php",
    "all-funds-historical.xlsx": "https://comptroller.texas.gov/transparency/revenue/watch/all-funds/data/all-funds-historical.xlsx",
    "eia_tx_crude.html": "https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=MCRFPTX1&f=M",
    "eia_tx_fpp.html": "https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=F003048__3&f=M",
    "eia_tx_gas.html": "https://www.eia.gov/dnav/ng/hist/n9050tx2m.htm",
}
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def text_of(path):
    """A fetched page as lines of text: comments, scripts and styles dropped (a row inside an HTML comment is not
    published), tags removed."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    raw = re.sub(r"(?is)<!--.*?-->", " ", raw)
    raw = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)<(br|/p|/tr|/li|/h\d|/div|/td|/th)\b[^>]*>", "\n", raw)
    lines = [re.sub(r"[ \t\xa0]+", " ", l).strip() for l in html.unescape(re.sub(r"(?s)<[^>]+>", " ", raw)).split("\n")]
    return [l for l in lines if l]


def certified(path):
    """The Comptroller's certified prices as published: {YYYY-MM: (price, eligibility)}."""
    lines, out = text_of(path), {}
    for i, l in enumerate(lines[:-2]):
        m = re.fullmatch(r"(%s) (20\d\d)" % "|".join(MONTHS), l)
        p = re.fullmatch(r"\$?(\d+\.\d+)/(bbl|Mcf)", lines[i + 1])
        if m and p:
            out["%s-%02d" % (m.group(2), MONTHS.index(m.group(1)) + 1)] = (float(p.group(1)), lines[i + 2])
    return out


def eia_months(path):
    """An EIA history page (one row a year, twelve months): {YYYY-MM: value}, and its title."""
    raw = open(path, encoding="utf-8", errors="replace").read()
    title = html.unescape(re.search(r"(?s)<title>(.*?)</title>", raw).group(1)).strip()
    released = re.search(r"Release Date:\s*([0-9/]+)", re.sub(r"<[^>]+>", " ", raw))
    out = {}
    for tr in re.findall(r"(?is)<tr[^>]*>(.*?)</tr>", raw):
        cells = [re.sub(r"<[^>]+>", "", c).replace("&nbsp;", "").strip() for c in re.findall(r"(?is)<t[dh][^>]*>(.*?)</t[dh]>", tr)]
        if cells and re.fullmatch(r"(19|20)\d\d", cells[0]) and len(cells) >= 13:
            for k, c in enumerate(cells[1:13]):
                if c:
                    out["%s-%02d" % (cells[0], k + 1)] = float(c.replace(",", ""))
    return out, title, released.group(1) if released else ""


def collections(path, year):
    """The Comptroller's all funds tax collections of a fiscal year, USD: the year's total of each production tax."""
    import openpyxl
    ws = openpyxl.load_workbook(path, read_only=True, data_only=True)["FY %d" % year]
    out = {}
    for row in ws.iter_rows(values_only=True):
        if row and row[0] and re.fullmatch(r"(Oil|Natural Gas) Production Tax", str(row[0]).strip()):
            out[str(row[0]).strip()] = float(row[13]) * 1000      # the workbook is in thousands of dollars
    return out


def shift(month, k):
    n = int(month[:4]) * 12 + int(month[5:7]) - 1 + k
    return "%04d-%02d" % (n // 12, n % 12 + 1)


def spot_means(tables, entity):
    by = {}
    with open(os.path.join(tables, "eia_fuel_spot_prices.csv"), encoding="utf-8", newline="") as f:
        rows = csv.reader(line for line in f if not line.startswith("#"))
        head = next(rows)
        e, t, v = head.index("entity"), head.index("ts_utc"), head.index("value")
        for r in rows:
            if r[e] == entity:
                by.setdefault(r[t][:7], []).append(float(r[v]))
    return {m: sum(xs) / len(xs) for m, xs in by.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--published", required=True)
    ap.add_argument("--tables", default=os.path.join(ROOT, "warehouse", "output"))
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--write")
    a = ap.parse_args()
    if a.fetch:
        os.makedirs(a.published, exist_ok=True)
        for name, url in FILES.items():
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r, open(os.path.join(a.published, name), "wb") as f:
                f.write(r.read())
            time.sleep(1)
    missing = [n for n in FILES if not os.path.exists(os.path.join(a.published, n))]
    if missing:
        print("not in %s: %s (run with --fetch)" % (a.published, ", ".join(missing)))
        return 2
    pub = lambda n: os.path.join(a.published, n)
    rules = json.load(open(os.path.join(ROOT, "site", "data", "severance_rules.json"), encoding="utf-8"))
    tx = rules["states"]["TX"]["products"]
    rows = []      # what, ours, theirs, publisher and document, difference, why

    # 1. the rates and the certified prices
    oil_page, gas_page = " ".join(text_of(pub("tx_oil.html"))), " ".join(text_of(pub("tx_gas.html")))
    for what, ours, page, pattern, doc in (
        ("Texas oil rate, percent of market value", tx["oil"]["base"][0]["rate"] * 100, oil_page, r"Oil production tax: ([\d.]+) percent", "Crude Oil Production Tax"),
        ("Texas oil clean-up fee, USD per barrel", tx["oil"]["fees"][0]["per_unit"], oil_page, r"Oil Field Clean-Up Fee of \$([\d.]+)", "Crude Oil Production Tax"),
        ("Texas enhanced recovery rate, percent", next(o for o in tx["oil"]["options"] if o["id"] == "tx_eor")["rate"] * 100, oil_page, r"\(EOR\): ([\d.]+) percent", "Crude Oil Production Tax"),
        ("Texas gas rate, percent of market value", tx["gas"]["base"][0]["rate"] * 100, gas_page, r"Gas: ([\d.]+) percent", "Natural Gas Production Tax"),
        ("Texas condensate rate, percent of market value", tx["condensate"]["base"][0]["rate"] * 100, gas_page, r"Condensate Production Tax: ([\d.]+) percent", "Natural Gas Production Tax"),
        ("Texas gas regulatory fee, USD per Mcf", tx["gas"]["fees"][0]["per_unit"], gas_page, r"Fee on Natural Gas of \$([\d.]+)", "Natural Gas Production Tax"),
    ):
        m = re.search(pattern, page)
        theirs = float(m.group(1)) if m else None
        rows.append((what, round(ours, 6), theirs, "Texas Comptroller, %s (page as read today)" % doc, None if theirs is None else round(ours - theirs, 6),
                     "the page's sentence was not found" if theirs is None else ""))
    for rule, product, name in (("tx_lp_oil", "oil", "tx_lp_oil.html"), ("tx_lp_gas", "gas", "tx_lp_gas.html")):
        ours = {p["period"]: p["price"] for p in next(o for o in tx[product]["options"] if o["id"] == rule)["certified"]["prices"]}
        theirs = certified(pub(name))
        same = sorted(m for m in ours if m in theirs and abs(ours[m] - theirs[m][0]) < 1e-9)
        differ = sorted(m for m in ours if m in theirs and abs(ours[m] - theirs[m][0]) >= 1e-9)
        newer = sorted(m for m in theirs if m not in ours and m > max(ours))
        rows.append(("Texas certified %s prices, periods the same as published" % product, len(ours), len(same),
                     "Texas Comptroller, low-producing %s page" % ("oil leases" if product == "oil" else "gas wells"), len(ours) - len(same),
                     ("differ: %s" % ", ".join(differ)) if differ else ""))
        rows.append(("Texas certified %s price, latest period held" % product, max(ours), max(theirs), "the same page", None,
                     "" if not newer else "published since the rules file was read on 30 September 2026: %s"
                     % "; ".join("%s USD %.2f (%s)" % (m, theirs[m][0], theirs[m][1]) for m in newer)))

    # 2. a fiscal year of collections
    crude, crude_title, crude_rel = eia_months(pub("eia_tx_crude.html"))        # thousand barrels
    fpp, fpp_title, fpp_rel = eia_months(pub("eia_tx_fpp.html"))                # USD per barrel
    gasp, gas_title, gas_rel = eia_months(pub("eia_tx_gas.html"))               # million cubic feet
    wti = spot_means(a.tables, "eia:wti_cushing") if os.path.exists(os.path.join(a.tables, "eia_fuel_spot_prices.csv")) else {}
    hh = spot_means(a.tables, "eia:henry_hub") if wti else {}
    for fy in (2025, 2026):
        got = collections(pub("all-funds-historical.xlsx"), fy)
        doc = "Texas Comptroller, Historical All Funds (Excluding Trusts) Revenue, fiscal %d" % fy
        oil_months = [shift("%d-08" % (fy - 1), k) for k in range(12)]           # August to July
        gas_months = [shift("%d-07" % (fy - 1), k) for k in range(12)]           # July to June
        for label, prices in (("Texas first purchase price (EIA)", fpp), ("WTI Cushing monthly mean, the tool's default", wti)):
            if all(m in crude and m in prices for m in oil_months):
                ours = sum(crude[m] * 1000 * prices[m] * 0.046 for m in oil_months)
                rows.append(("Texas oil production tax, fiscal %d: 4.6 percent of EIA's production at the %s, USD" % (fy, label), round(ours), round(got["Oil Production Tax"]), doc,
                             round(ours - got["Oil Production Tax"]),
                             "ours is %.0f percent above. What would lower collections, none of it measured here: EIA's crude oil holds lease condensate, which Texas taxes "
                             "under the gas tax; oil from enhanced recovery pays 2.3 percent; an exempt owner's royalty pays nothing; and collections are cash received, "
                             "with refunds and late reports"
                             % ((ours / got["Oil Production Tax"] - 1) * 100)))
        if hh and all(m in gasp and m in hh for m in gas_months):
            ours = sum(gasp[m] * 1000 * hh[m] * 0.075 for m in gas_months)       # MMcf to Mcf; one Mcf priced as one MMBtu
            rows.append(("Texas natural gas production tax, fiscal %d: 7.5 percent of EIA's marketed production at the Henry Hub monthly mean, USD" % fy, round(ours),
                         round(got["Natural Gas Production Tax"]), doc, round(ours - got["Natural Gas Production Tax"]),
                         "ours is %.0f percent %s. What moves it, none of it measured here: Henry Hub is not the price at a Texas well; high-cost gas pays a reduced rate and "
                         "low-producing wells earned a 100 percent credit in every period the Comptroller certified; marketing costs are deducted; and the Comptroller's "
                         "figure also holds the condensate tax"
                         % (abs(ours / got["Natural Gas Production Tax"] - 1) * 100, "above" if ours > got["Natural Gas Production Tax"] else "below")))
    print("EIA: %s (released %s); %s (released %s); %s (released %s)" % (crude_title, crude_rel, fpp_title, fpp_rel, gas_title, gas_rel))
    for what, ours, theirs, doc, diff, why in rows:
        print("%s | ours %s | theirs %s | %s | difference %s | %s" % (what, ours, theirs, doc, diff, why))
    if a.write:
        with open(a.write, "w", encoding="utf-8", newline="\n") as f:
            json.dump({"note": "The severance tool's cross-check (session 7502): ours beside the publisher's figure, nothing adjusted.",
                       "eia": {"crude": [crude_title, crude_rel], "first_purchase_price": [fpp_title, fpp_rel], "gas": [gas_title, gas_rel]},
                       "rows": [{"what": w, "ours": o, "theirs": t, "document": d, "difference": x, "why": y} for w, o, t, d, x, y in rows]}, f, indent=1)
            f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
