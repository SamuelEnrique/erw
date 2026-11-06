#!/usr/bin/env python3
"""The periodicals' counts, as a sharp reader counts them (session 1434, chain 149; the measures of session 800's
runs/periodicals/s800/counts.py, which was never committed, written again so they can be run on any issue).

For each Digest or Roundup issue given (a markdown file, or a folder of them), one row:

    adjectives   why lines holding an adjective of the list (massive, unprecedented, significant, major, critical, key,
                 huge; "critical minerals" and "the key to" are the trade's words and are not counted)
    repeated     items whose why line prints a figure the headline already holds
    items        items read (the numbered items, the sector bullets, "AI and power"; a Roundup's numbered items)
    top_sector   the largest number of top items in one sector, and that sector (a Digest's top ten, or "What moved"
                 with "The rest of the top ten")
    google       links whose address is Google News, and all links
    fold_words   words of prose above the fold: a v2 issue's text before "## More" without the source lines, the
                 numbers block's rows and the tables' lines; an issue with no fold, its items' text before the numbers
    no_key       figures with a unit in the opening number and the numbers block that carry no [n] key

    python scripts/periodicals_counts.py docs/digest docs/roundup runs/periodicals_dryrun/s1435/digest/2026-10-26.md
    python scripts/periodicals_counts.py --csv out.csv --md out.md docs/digest

Exit 0 always; it reads, counts and writes the two files when asked. No network.
"""
import argparse
import csv
import os
import re
import sys

ADJ = re.compile(r"\b(massive|unprecedented|significant|significantly|major|critical|critically|key|huge)\b", re.I)
TRADE = re.compile(r"\b(critical minerals?|the key to|key to)\b", re.I)
ITEM = re.compile(r"^\d+\. \*\*(?P<head>.+?)\*\*\s*\((?P<sector>[^)]*)\)\s*$")
BULLET = re.compile(r"^- (?P<head>.+?) \((?P<sector>[^)]*)\): (?P<why>.*)$")
LINK = re.compile(r"\]\((https?://[^)\s]+)\)")
FIG = re.compile(r"(?:(?:USD|US\$|\$|€|£)\s?[\d][\d,.]*\s?(?:billion|million|trillion|bn|mn|b|m|mm|k)?"
                 r"|[\d][\d,.]*\s?(?:billion|million|trillion|bn|mn)?\s?(?:MW|GW|GWh|MWh|TWh|kV|bcf|Bcf|mtpa|tonnes|tons|barrels|bpd|b/d|%|percent)"
                 r"|[\d][\d,.]*\s?(?:USD|EUR)/(?:MWh|bbl|MMBtu))", re.I)
UNIT_FIG = re.compile(r"\d[\d,.]*\s?(?:USD/MWh|USD/bbl|USD/MMBtu|MW|GW|GWh|MWh|%|billion|million)", re.I)
KEY = re.compile(r"\[\d+\]")
HEADS_TOP = ("## Top of the industry", "## What moved", "### The rest of the top ten")


def norm_fig(s):
    s = s.lower().replace(",", "").replace(" ", "")
    s = re.sub(r"(billion|bn|b)$", "b", s)
    s = re.sub(r"(million|mn|mm|m)$", "m", s)
    return s


def sector_of(tag):
    """The sector of an item's tag: "(gas)", "(gas, 3 stories)" or the older "(significance 8, gas)"."""
    parts = [p.strip() for p in tag.split(",")]
    for p in parts:
        if p and not re.match(r"^(significance \d+|\d+ stor(y|ies)|AI \d+)$", p):
            return p
    return parts[0] if parts else ""


def read_items(lines):
    """(head, sector, why, section) for every item of the issue, in order."""
    items, section = [], ""
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("## ") or ln.startswith("### "):
            section = ln.strip("# ").strip()
        m = ITEM.match(ln.strip())
        if m:
            why = ""
            if i + 1 < len(lines):
                nxt = lines[i + 1].strip()
                why = nxt.split("Sources:")[0].strip()
                if re.match(r"Also (?:on this topic|in [a-z][a-z ]*):", why) or why.startswith("What the evidence"):   # 1466
                    why = ""
            items.append((m.group("head"), sector_of(m.group("sector")), why, section))
        else:
            b = BULLET.match(ln.strip())
            if b and section not in ("Weekend",):
                why = re.sub(r"\s*\[[^\]]+\]\(https?://[^)]+\).*$", "", b.group("why")).strip()
                items.append((b.group("head"), sector_of(b.group("sector")), why, section))
        i += 1
    return items


def fold_words(lines):
    text = "\n".join(lines)
    v2 = "\n## More" in text
    stop = "\n## More" if v2 else ("\n## ERW's Numbers Today" if "\n## ERW's Numbers Today" in text else "\n## ERW's Numbers")
    head = text.split(stop)[0] if stop in text else text
    out = []
    in_numbers = False
    for ln in head.split("\n"):
        s = ln.strip()
        if s.startswith("## "):
            in_numbers = s in ("## The numbers", "## The week in five numbers")
            continue
        if not s or s.startswith("<!--") or s.startswith("Tables:") or s.startswith("Sources:") or s.startswith("|"):
            continue
        if in_numbers and s.startswith("- "):
            continue
        if re.match(r"Also (?:on this topic|in [a-z][a-z ]*):", s) or s.startswith("# "):   # session 1466: either label
            continue
        s = re.sub(r"\s*Sources?:.*$", "", s)
        s = re.sub(r"\[([^\]]+)\]\(https?://[^)]+\)", r"\1", s)
        s = re.sub(r"\*\*", "", s)
        out.append(s)
    return len(" ".join(out).split())


def no_key(lines):
    n, section = 0, ""
    for ln in lines:
        s = ln.strip()
        if s.startswith("## "):
            section = s
            continue
        if section not in ("## The opening number", "## The numbers", "## The week in five numbers"):
            continue
        if s.startswith("Tables:") or not s:
            continue
        if UNIT_FIG.search(s) and not KEY.search(s):
            n += 1
    return n


def count(path):
    with open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    items = read_items(lines)
    adjectives = repeated = 0
    for head, sector, why, section in items:
        w = TRADE.sub("", why)
        if ADJ.search(w):
            adjectives += 1
        hf = {norm_fig(x) for x in FIG.findall(head)}
        wf = {norm_fig(x) for x in FIG.findall(why)}
        if hf & wf:
            repeated += 1
    top = [s for (_, s, _, sec) in items if sec in tuple(h.strip("# ") for h in HEADS_TOP)]
    best, best_s = 0, ""
    for s in set(top):
        c = top.count(s)
        if c > best:
            best, best_s = c, s
    links = LINK.findall("\n".join(lines))
    google = sum(1 for u in links if "news.google.com" in u)
    return {"issue": os.path.basename(path).replace(".md", ""), "items": len(items), "adjectives": adjectives,
            "repeated": repeated, "top_sector_n": best, "top_sector": best_s, "google": google, "links": len(links),
            "fold_words": fold_words(lines), "no_key": no_key(lines)}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--csv")
    ap.add_argument("--md")
    a = ap.parse_args(argv)
    files = []
    for p in a.paths:
        if os.path.isdir(p):
            files += sorted(os.path.join(p, f) for f in os.listdir(p) if re.match(r"^\d{4}-(\d\d-\d\d|W\d\d)\.md$", f))
        elif os.path.isfile(p):
            files.append(p)
    rows = [count(f) for f in files]
    cols = ["issue", "items", "adjectives", "repeated", "top_sector_n", "top_sector", "google", "links", "fold_words", "no_key"]
    print("| " + " | ".join(cols) + " |")
    print("|" + "---|" * len(cols))
    for r in rows:
        print("| " + " | ".join(str(r[c]) for c in cols) + " |")
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n")
            for r in rows:
                f.write("| " + " | ".join(str(r[c]) for c in cols) + " |\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
