"""Chain 760, five-tools data requests 66 and 67 (the old laptop's equities audit of 28 November, data requests 2 and 3).

67: for each company of seed 11403's sample but SLB, the filing named in docs/reviews/equities-model-audit-2026-11-28/
    sample.txt: its index page, its primary document, and a search of the document's text for each figure the sample
    prints (in whole units, thousands or millions, a loss in brackets too). One line a figure: found, with the words
    around it, or not.
66: for each 10-Q the audit names (six zero-capex filings and VAALCO's two of 2025): the primary document's cash flow
    lines that name capital spending, printed with their figures, for a person to read against the table.
Two or three requests a filing, half a second apart at least, with the owner's declared agent (SEC_USER_AGENT, .env).
Usage: python docs/reviews/answers-c760-2026-11-28/edgar_reads.py sample|capex
"""
import html
import os
import re
import sys
import time

import requests

ROOT = r"C:\Users\Shared\Documents\erw"
ua = next(ln.split("=", 1)[1].strip().strip('"') for ln in open(os.path.join(ROOT, ".env"), encoding="utf-8")
          if ln.startswith("SEC_USER_AGENT="))
S = requests.Session()
S.headers["User-Agent"] = ua
# the company numbers (CIK) as equity_universe holds them; the accessions as the audit names them
CAPEX = {"BSIN": ("0000101594", "0001437749-26-036207"), "EGY": ("0000894627", "0000894627-26-000061"),
         "EONR": ("0001842556", "0001437749-26-038029"), "PROP": ("0001162896", "0001162896-26-000011"),
         "HDRN": ("0002023730", "0001193125-26-453519"), "SPRU": ("0001772720", "0001628280-26-073907"),
         "EGY 2025-06-30": ("0000894627", "0000894627-25-000041"),
         "EGY 2025-09-30": ("0000894627", "0000894627-25-000057")}


# a figure counts as found only beside words of its own line, within the 160 characters before it
WORDS = {"revenue": ("revenue", "sales"), "net_income": ("net income", "net (loss)", "net loss", "net earnings"),
         "capex": ("expenditure", "additions", "purchases of property", "property, plant", "properties", "capital"),
         "debt": ("debt",), "shares_outstanding": ("shares",)}


def get(url):
    time.sleep(0.5)
    r = S.get(url, timeout=120)
    r.raise_for_status()
    return r.text


def index_url(cik, acc):
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{acc}-index.htm"


def primary_text(idx_url):
    page = get(idx_url)
    m = re.search(r'href="(/(?:ix\?doc=/)?Archives/edgar/data/[^"]+\.htm)"[^<]*</a></td>\s*<td[^>]*>\s*10-[QK]', page)
    if not m:
        m = re.search(r'href="(/(?:ix\?doc=/)?Archives/edgar/data/[^"]+\.htm)"', page)
    doc = "https://www.sec.gov" + m.group(1).replace("/ix?doc=", "")
    text = html.unescape(re.sub(r"<[^>]+>", " ", get(doc)))
    return doc, re.sub(r"\s+", " ", text)


def forms(v):
    neg = v < 0
    v = abs(int(v))
    out = [f"{v:,}"]
    for d in (1_000, 1_000_000):
        if v % d == 0:
            out.append(f"{v // d:,}")
        else:
            out.append(f"{v / d:,.1f}")
    return out + ([f"({f})" for f in out] if neg else [])


def sample():
    path = os.path.join(ROOT, "docs", "reviews", "equities-model-audit-2026-11-28", "sample.txt")
    blocks = open(path, encoding="utf-8").read().split("\n\n")[1:]
    found = total = 0
    for b in blocks:
        lines = b.strip().splitlines()
        tk = lines[0].split()[0]
        if tk == "SLB":
            continue
        idx = next((ln.split("filing: ")[1].strip() for ln in lines if "filing:" in ln), None)
        if idx is None:
            continue
        doc, text = primary_text(idx)
        print(f"{tk} {doc}")
        for ln in lines:
            m = re.match(r"\s+(revenue|net_income|capex|debt|shares_outstanding): (-?[\d,]+) (?:USD|at )", ln)
            if not m:
                continue
            var, v = m.group(1), int(m.group(2).replace(",", ""))
            total += 1
            hit = None
            words = WORDS[var]
            for f in forms(v):
                if v == 0:
                    break   # a zero is never searched for: it would match anything
                for mm in re.finditer(r"(?<![\d,.])" + re.escape(f) + r"(?![\d,]|\.\d)", text):
                    before = text[max(0, mm.start() - 160):mm.start()].lower()
                    if any(w in before for w in words):
                        hit = (f, text[max(0, mm.start() - 100):mm.end() + 20])
                        break
                if hit:
                    break
            if hit:
                found += 1
                print(f"  {var} {v:,}: FOUND as '{hit[0]}': ...{hit[1]}...")
            else:
                print(f"  {var} {v:,}: NOT FOUND (forms {forms(v)})")
    print(f"{found} of {total} figures found in the filings")


def capex():
    pat = re.compile(r"(capital expenditures?|purchases? of property|additions? to (?:property|oil and gas|proved|unproved)|"
                     r"(?:development|exploration) (?:capital|expenditures)|payments? (?:for|to acquire) property|"
                     r"investment in (?:oil and gas|property))", re.I)
    for tk, (cik, acc) in CAPEX.items():
        doc, text = primary_text(index_url(cik, acc))
        print(f"{tk} {acc} {doc}")
        low = text.lower()
        seen, shown = set(), 0
        for km in re.finditer(r"investing activities", low):
            part = text[km.start():km.start() + 3000]
            for m in pat.finditer(part):
                snip = part[max(0, m.start() - 40):m.start() + 200]
                key = re.sub(r"\W", "", snip[40:120])
                # a statement line: the words are followed by a figure within 80 characters
                if key in seen or not re.search(r"\(?\s?[\d,]{2,}\s?\)?", part[m.end():m.end() + 80]):
                    continue
                seen.add(key)
                shown += 1
                if shown <= 8:
                    print("  ..." + snip + "...")
        if not shown:
            print("  no capital spending line with a figure found near any 'investing activities'")


def window():
    """The raw text after each 'investing activities' that is followed by figures, for the filings named."""
    for tk in sys.argv[2:]:
        cik, acc = CAPEX[tk]
        doc, text = primary_text(index_url(cik, acc))
        print(f"{tk} {acc} {doc}")
        for km in re.finditer(r"(?i)cash flows? (?:from|used in|provided by)[^.]{0,30}investing activities", text):
            part = text[km.start():km.start() + 700]
            if len(re.findall(r"\d[\d,]{2,}", part[:300])) >= 3:
                print("  ..." + part + "...")


if __name__ == "__main__":
    {"sample": sample, "capex": capex, "window": window}[sys.argv[1]]()
