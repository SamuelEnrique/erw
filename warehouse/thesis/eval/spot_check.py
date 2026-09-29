#!/usr/bin/env python3
"""Spot check of Thesis Builder workbooks (session 25): company and capital rows against their sources.

For each sampled row, every source it names is fetched now (as a reader would) and its text searched for the row's
claims: the company name, the amount (its digits), the stage or round word, the date's year, and the first named
investor or founder. The script prints what it found; the verdict per row is a person's, written in
archive/sessions/SESSION_25_REPORT.md. It never changes the builder.

    python warehouse/thesis/eval/spot_check.py docs/thesis/a.xlsx:5 docs/thesis/b.xlsx:5 --capital a.xlsx:5 b.xlsx:5
"""

import argparse
import html
import random
import re
import sys

import requests
from openpyxl import load_workbook

UA = {"User-Agent": "Mozilla/5.0 (ERW research; https://github.com/SamuelEnrique/erw)"}


def table(ws, first_col):
    rows, head = [], None
    for row in ws.iter_rows(values_only=True):
        vals = list(row[1:])
        if vals and vals[0] == first_col:
            head = vals
            continue
        if head and vals and vals[0] and not str(vals[0]).startswith(("Source(s)", "(")):
            rows.append(dict(zip(head, vals)))
        elif head and (not vals or not vals[0]):
            head = None
    return rows


def sources(wb):
    return {r["Id"]: r["URL"] for r in table(wb["Sources"], "Id")}


_cache = {}


def text(url):
    if url in _cache:
        return _cache[url]
    try:
        r = requests.get(url, headers=UA, timeout=25)
        t = r.text if r.status_code == 200 else f"HTTP {r.status_code}"
    except Exception as exc:
        t = f"fetch failed: {type(exc).__name__}"
    t = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", t)))
    _cache[url] = re.sub(r"\s+", " ", t)
    return _cache[url]


def found(needle, hay):
    return bool(needle) and needle.lower() in hay.lower()


def amount_digits(s):
    m = re.search(r"\d[\d,.]*", s or "")
    return m.group(0).rstrip(".,") if m else ""


def state_cited(path):
    """The passages the search API returned for each source (the run's saved state), by source id: the evidence when a
    publisher refuses a plain fetch (HTTP 403)."""
    import glob
    import json
    import os
    slug = os.path.splitext(os.path.basename(path))[0]
    files = sorted(glob.glob(os.path.join("warehouse", "output", "thesis_state", f"{slug}_*.json")))
    if not files:
        return {}
    st = json.load(open(files[-1], encoding="utf-8"))
    return {s["id"]: " ".join(s["cited"] + [s["title"]]) for s in st["sources"].values()}


def check(row, ids, srcs, claims, cited):
    out = {}
    pages = [(i, srcs.get(i, "")) for i in ids]
    for name, needle in claims.items():
        hits = [i for i, u in pages if u and found(needle, text(u))]
        hits += [f"{i} (cited passage)" for i, u in pages if i in cited and found(needle, cited[i]) and i not in hits]
        out[name] = (needle, hits)
    return out, [(i, u, text(u)[:60]) for i, u in pages if u and (text(u).startswith(("HTTP", "fetch")))]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("company", nargs="*", help="workbook:n company rows")
    ap.add_argument("--capital", nargs="*", default=[], help="workbook:n capital rows")
    ap.add_argument("--seed", type=int, default=25)
    a = ap.parse_args(argv)
    rnd = random.Random(a.seed)
    for spec, kind in [(s, "company") for s in a.company] + [(s, "capital") for s in a.capital]:
        path, n = spec.rsplit(":", 1)
        wb = load_workbook(path)
        srcs = sources(wb)
        cited = state_cited(path)
        rows = table(wb["Landscape"], "Company") if kind == "company" else table(wb["Capital"], "Date")
        rows = [r for r in rows if r.get("Sources") and "licensed" not in str(r.get("Sources"))]
        for r in rnd.sample(rows, min(int(n), len(rows))):
            ids = [x.strip() for x in str(r["Sources"]).split(",")]
            if kind == "company":
                claims = {"name": str(r["Company"]).split(" (")[0], "raised": amount_digits(str(r["Raised"])),
                          "stage": re.sub(r"\s*\(.*", "", str(r["Stage"])).split(";")[0].strip(),
                          "founder": re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", str(r["Founders"]))[0:1][0]
                          if re.findall(r"[A-Z][a-z]+ [A-Z][a-z]+", str(r["Founders"])) else ""}
                label = f"{path} | {r['Company']} | stage {r['Stage']} | raised {str(r['Raised'])[:80]}"
            else:
                m = re.search(r"(?:led by |co-led by )?([A-Z][A-Za-z&.]*(?: [A-Z][A-Za-z&.]*)*)", str(r["Investors"]))
                inv = [m.group(1)] if m else []
                claims = {"company": str(r["Company"]).split(" (")[0], "amount": amount_digits(str(r["Amount"])),
                          "year": str(r["Date"])[:4], "investor": inv[0] if inv and r["Investors"] != "not disclosed" else ""}
                label = f"{path} | {r['Date']} | {r['Company']} | {r['Kind']} | {r['Amount']} {r['Currency']} | {str(r['Investors'])[:60]}"
            res, bad = check(r, ids, srcs, claims, cited)
            print(f"{kind.upper()}: {label}")
            for k, (needle, hits) in res.items():
                print(f"   {k}: {needle!r} found in {hits if hits else 'no fetched source'}")
            for i, u, why in bad:
                print(f"   source {i} not readable now: {u} ({why})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
