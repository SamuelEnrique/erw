"""Match every quote of the large-load research rows against the cached text of its document.

Energy Research Warehouse (ERW), session 5300. Reads rows/*.json (or the files named), finds each cite's document in
runs/s5300/docs/ (the copy fetch_doc.py kept: no request is made), and checks that each part of the quote (parts are
split at " ... ") is in the text, and on the page the cite names when the document is a PDF.

    python -I verify_quotes.py [rows.json ...] [--stamp] [--report out.json]

The match is made on a normalized text: curly quotes and dashes made plain, ligatures opened, soft hyphens dropped,
whitespace collapsed, case ignored. A quote that only matches with every space removed (a column break, a word split
over a line) is reported as "nospace", still a match. A quote found on another page than the one cited is a failure.
--stamp writes each document's date read (from the cache) into the rows: date_read on the row (its source_url), and
date_read on each cite with its own url.
Exit 0 when every cite matches, 1 when any does not, 2 on bad input.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CACHE = os.path.join(ROOT, "runs", "s5300", "docs")
FIELDS = ("threshold_mw", "min_demand", "contract_term", "collateral", "exit_fee", "study_timeline",
          "connection_timeline", "queue_size")
MARKERS = ("not published", "held: ", "see row: ")

TRANS = {
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'", "\u2032": "'",
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u2033": '"',
    "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-", "\u2014": "-", "\u2015": "-", "\u2212": "-",
    "\u00ad": "", "\u00a0": " ", "\ufb01": "fi", "\ufb02": "fl", "\ufb00": "ff", "\ufb03": "ffi", "\ufb04": "ffl",
    "\u2022": " ", "\uf0b7": " ", "\u25cf": " ", "\ufffd": "",
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = "".join(TRANS.get(c, c) for c in s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().lower()


def nospace(s: str) -> str:
    return re.sub(r"[\s\"'\-]", "", s)


def key(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def load_doc(url: str):
    d = os.path.join(CACHE, key(url))
    meta_p = os.path.join(d, "meta.json")
    if not os.path.exists(meta_p):
        return None
    meta = json.load(open(meta_p, encoding="utf-8"))
    pages = {}
    for name in ("text.txt", "layout.txt"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            pages[name] = open(p, encoding="utf-8", errors="replace").read().split("\f")
    return meta, pages


def page_numbers(spec) -> list[int] | None:
    if spec in (None, ""):
        return None
    s = str(spec)
    nums = [int(n) for n in re.findall(r"\d+", s)]
    if not nums:
        return None
    if re.search(r"\d+\s*(-|to|\u2013)\s*\d+", s) and len(nums) >= 2:
        lo, hi = nums[0], nums[1]
        if lo <= hi and hi - lo < 60:
            return list(range(lo, hi + 1))
    return nums


def find(quote: str, meta, pages, page_spec):
    parts = [p for p in re.split(r"\s*(?:\.\.\.|\u2026)\s*", quote) if p.strip(" .,;:")]
    if not parts:
        return "empty", None
    kinds = []
    found_pages = set()
    for part in parts:
        q = norm(part).strip(" .,;:")
        qn = nospace(q)
        hit_kind, hit_pages = None, set()
        for name, pg in pages.items():
            for i, text in enumerate(pg, 1):
                t = norm(text)
                if q and q in t:
                    hit_kind = hit_kind if hit_kind == "exact" else "exact"
                    hit_pages.add(i)
                elif qn and len(qn) >= 12 and qn in nospace(t):
                    hit_kind = hit_kind or "nospace"
                    hit_pages.add(i)
            if not hit_pages:
                # a quote that runs across a page break
                whole = norm(" ".join(pg))
                if q and q in whole:
                    hit_kind = hit_kind or "exact"
                    hit_pages.add(0)
                elif qn and len(qn) >= 12 and qn in nospace(whole):
                    hit_kind = hit_kind or "nospace"
                    hit_pages.add(0)
        if not hit_kind:
            return "missing", part
        kinds.append(hit_kind)
        found_pages |= hit_pages
    kind = "exact" if all(k == "exact" for k in kinds) else "nospace"
    want = page_numbers(page_spec)
    if meta.get("kind") == "pdf" and want and 0 not in found_pages:
        if not (set(want) & found_pages):
            return "wrong_page", f"cited p.{page_spec}, found on p.{','.join(map(str, sorted(found_pages)))}"
    return kind, None


def cites_of(row):
    src = row.get("source_url")
    # a change (changes_*.json) or a law (legislation_*.json) carries its cites at the top
    for c in row.get("cites") or []:
        yield "cite", c, c.get("url") or src
    tm = row.get("threshold_mw")
    if isinstance(tm, dict):
        for c in tm.get("cites") or []:
            yield "threshold_mw", c, c.get("url") or src
    for name in ("requirements",):
        for item in row.get(name) or []:
            for c in item.get("cites") or []:
                yield name, c, c.get("url") or src
    qc = row.get("quoted_clause")
    if isinstance(qc, dict) and qc.get("quote"):
        yield "quoted_clause", qc, qc.get("url") or src
    for name in ("docket", "status"):
        v = row.get(name)
        if isinstance(v, dict):
            for c in v.get("cites") or []:
                yield name, c, c.get("url") or src
    for f in FIELDS:
        v = (row.get("fields") or {}).get(f)
        if isinstance(v, dict):
            for c in v.get("cites") or []:
                yield f, c, c.get("url") or src


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--stamp", action="store_true")
    ap.add_argument("--report")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    files = a.files or sorted(glob.glob(os.path.join(HERE, "rows", "*.json")))
    if not files:
        print("no rows files")
        return 2
    results, bad = [], 0
    for fp in files:
        data = json.load(open(fp, encoding="utf-8"))
        changed = False
        for ri, row in enumerate((data.get("rows") or []) + (data.get("changes") or []) + (data.get("laws") or [])):
            label = f"{os.path.basename(fp)}#{ri} {row.get('utility', '')[:40]} | {row.get('rule_name', '')[:50]}"
            src = row.get("source_url")
            sdoc = load_doc(src) if src else None
            if sdoc and a.stamp:
                if row.get("date_read") != sdoc[0].get("date_read"):
                    row["date_read"] = sdoc[0].get("date_read")
                    changed = True
            elif not sdoc:
                results.append({"row": label, "field": "source_url", "result": "uncached", "url": src})
                bad += 1
            for field, cite, url in cites_of(row):
                doc = load_doc(url)
                if not doc:
                    results.append({"row": label, "field": field, "result": "uncached", "url": url})
                    bad += 1
                    continue
                meta, pages = doc
                if a.stamp and cite.get("url") and cite.get("date_read") != meta.get("date_read"):
                    cite["date_read"] = meta.get("date_read")
                    changed = True
                kind, detail = find(cite.get("quote") or "", meta, pages, cite.get("page"))
                ok = kind in ("exact", "nospace")
                if not ok:
                    bad += 1
                results.append({"row": label, "field": field, "result": kind, "detail": detail, "url": url,
                                "page": cite.get("page"), "quote": (cite.get("quote") or "")[:160]})
        if changed:
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=1, ensure_ascii=False)
                f.write("\n")
    n = len(results)
    for r in results:
        if r["result"] not in ("exact", "nospace"):
            print(f"FAIL {r['result']}: {r['row']} [{r['field']}] {r.get('detail') or ''} :: {r.get('quote', '')} :: {r['url']}")
    counts = {}
    for r in results:
        counts[r["result"]] = counts.get(r["result"], 0) + 1
    print(f"cites checked: {n}; " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    if a.report:
        json.dump(results, open(a.report, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
