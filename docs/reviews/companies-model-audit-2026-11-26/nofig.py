"""Whether a words branch moved a figure: every keyed figure (data-n, data-raw and the number drawn) and every table cell
of each drawing under runs/c10228/draw/<prefix>_<page>.html set against main's (main_<page>.html). Prints the count
compared and every difference. Session 10228.
    python nofig.py <prefix>"""
import html
import os
import re
import sys

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "draw")
pre = sys.argv[1]
n, diff = 0, []
for page in ("index", "index_policy", "fpl", "google", "ceg", "tab"):
    a_p, b_p = os.path.join(HERE, f"main_{page}.html"), os.path.join(HERE, f"{pre}_{page}.html")
    if not (os.path.exists(a_p) and os.path.exists(b_p)):
        continue
    a, b = open(a_p, encoding="utf-8").read(), open(b_p, encoding="utf-8").read()
    ka = re.findall(r'data-n="([^"]+)" data-raw="([^"]*)"[^>]*>([^<]*)<', a)
    kb = re.findall(r'data-n="([^"]+)" data-raw="([^"]*)"[^>]*>([^<]*)<', b)
    ca = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", a, re.S)]
    cb = [html.unescape(re.sub(r"<[^>]+>", "", x)).strip() for x in re.findall(r"<td[^>]*>(.*?)</td>", b, re.S)]
    n += len(ka) + len(ca)
    if ka != kb:
        diff.append((page, "keyed", len(ka), len(kb)))
    if ca != cb:
        diff.append((page, "cells", len(ca), len(cb), next((i for i, (x, y) in enumerate(zip(ca, cb)) if x != y), None)))
print(f"{pre}: {n:,} keyed figures and cells compared with main; {len(diff)} differences")
for d in diff:
    print("DIFF", d)
sys.exit(1 if diff else 0)
