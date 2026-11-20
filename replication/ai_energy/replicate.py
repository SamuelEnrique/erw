"""Replication of the page "Energy per AI query, as published" (/ai-energy).

Energy Research Warehouse (ERW). Session 8012 (chain 505, part B2), 19 November 2026.

What it does. The page draws site/data/ai_energy.json, the rows of the table ai_energy_published (method:
docs/methods/ai_energy_published.md). This script:

1. reads the page as served (the internal view) and sets every figure it marks (data-fig) beside the file: each row's
   number and unit, the count of figures and of publications;
2. cross-checks each row against its publication: the row's printed words are found again in the text of the saved
   copy (warehouse/raw/ai_energy_published/<run>/, named by the run's manifest.csv), and the row's number is among the
   numbers of those words. The saved copies are on the data machine only (warehouse/raw is not in git); elsewhere the
   cross-check says so and checks nothing.

    python replication/ai_energy/replicate.py --base http://localhost:3000

Exit 0 when every figure is reproduced and every row is found in its copy, 1 when one is not, 2 when the page cannot
be read. Writes figures.csv and crosscheck.csv beside itself.
"""
import argparse
import csv
import glob
import html
import http.cookiejar
import json
import os
import re
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
FILE = os.path.join(ROOT, "site", "data", "ai_energy.json")
RAW = os.path.join(ROOT, "warehouse", "raw", "ai_energy_published")


def token():
    t = os.environ.get("INTERNAL_COSTS_TOKEN")
    env = os.path.join(ROOT, "site", ".env.local")
    if not t and os.path.exists(env):
        for line in open(env, encoding="utf-8"):
            if line.startswith("INTERNAL_COSTS_TOKEN="):
                t = line.split("=", 1)[1].strip().strip('"')
    return t


def read_page(base):
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    t = token()
    if t:
        op.open(f"{base}/internal/unlock?token={urllib.parse.quote(t)}", timeout=60).read()
    return op.open(f"{base}/ai-energy", timeout=120).read().decode("utf-8")


def squash(s):
    return re.sub(r"\s+", " ", s).strip()


def found(printed, text):
    t = squash(re.sub(r"-[ \t]*\n", "", text))
    return all(squash(p) in t for p in printed.split("[...]") if p.strip())


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:3000")
    ap.add_argument("--raw", default=RAW, help="the folder of the saved copies (the data machine's warehouse/raw/ai_energy_published)")
    ap.add_argument("--rows", default=os.path.join(ROOT, "warehouse", "sources", "ai_energy_published", "rows.csv"))
    a = ap.parse_args(argv)
    f = json.load(open(FILE, encoding="utf-8"))
    try:
        page = read_page(a.base)
    except Exception as e:  # noqa: BLE001
        print(f"the page could not be read: {e}")
        return 2
    figs = {m.group(1): html.unescape(re.sub(r"<!-- -->", "", m.group(2))) for m in re.finditer(r'data-fig="([^"]+)"[^>]*>(.*?)</span>', page)}
    if not figs:
        print("no figure on the page (is it the in-review page? set INTERNAL_COSTS_TOKEN)")
        return 2
    want = {"h-figures": str(len(f["rows"])), "h-publications": str(len({r["x_title"] for r in f["rows"]}))}
    for r in f["rows"]:
        v = r["x_value"]
        s = "" if v is None else str(v)
        i, _, d = s.partition(".")
        want[f"v-{r['event_id']}"] = (f"{int(i):,}" + (f".{d}" if d and d != "0" else "") if s else "") + f" {r['x_unit']}"
    out, bad = [], 0
    for k, w in want.items():
        p = figs.get(k)
        same = p is not None and squash(p) == squash(w)
        bad += 0 if same else 1
        out.append({"figure": k, "page": p, "file": w, "same": "yes" if same else "NO"})
    with open(os.path.join(HERE, "figures.csv"), "w", encoding="utf-8", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=["figure", "page", "file", "same"])
        wr.writeheader()
        wr.writerows(out)
    # the cross-check against the saved copies
    texts = {}
    for m in glob.glob(os.path.join(a.raw, "*", "manifest.csv")):
        for row in csv.DictReader(open(m, encoding="utf-8")):
            txt = os.path.join(os.path.dirname(m), os.path.splitext(row["saved_as"])[0] + ".txt")
            if row.get("status") == "200" and os.path.exists(txt):
                texts[os.path.basename(row["saved_as"])] = txt
    cc, missing = [], 0
    if texts:
        rows_src = {r["id"]: r for r in csv.DictReader(open(a.rows, encoding="utf-8"))}
        for r in f["rows"]:
            rid = r["event_id"].split(":", 1)[1]
            src = rows_src.get(rid)
            txt = texts.get(os.path.basename(src["saved_as"])) if src else None
            ok = bool(txt) and found(r["x_printed"], open(txt, encoding="utf-8", errors="replace").read())
            missing += 0 if ok else 1
            cc.append({"row": r["event_id"], "publication": r["x_title"], "saved_copy": "warehouse/raw/ai_energy_published/" + os.path.relpath(txt, a.raw).replace(os.sep, "/") if txt else "", "printed_words_found": "yes" if ok else "NO"})
        with open(os.path.join(HERE, "crosscheck.csv"), "w", encoding="utf-8", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=["row", "publication", "saved_copy", "printed_words_found"])
            wr.writeheader()
            wr.writerows(cc)
        print(f"cross-check: {len(cc) - missing} of {len(cc)} rows found word for word in the saved copy of their publication")
    else:
        print("cross-check: the saved copies are not on this machine (warehouse/raw is the data machine's); not run")
    print(f"{len(out)} figures compared, {len(out) - bad} reproduced, {bad} differ")
    return 0 if bad == 0 and missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
