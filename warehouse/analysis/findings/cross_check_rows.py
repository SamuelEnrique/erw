#!/usr/bin/env python3
"""ERW Research: the cross-check rows of docs/methods/automated_analysis_findings.md that name a card's figure by its
key, written again from the cards as the daily recompute leaves them (session 3779, chain 212).

site/scripts/check-cross-checks.mjs (test 538) holds each such row to its card: our figure is the card's, and the gap is
ours less the published figure. The data machine's recompute (card_statistics.py --recompute) rewrites the cards each
day; when a card's figure moved, the row no longer matched and the run put the whole refresh back (9 and 10 November:
queue_divorce read 22,348 requests and 3,591 GW, not 21,758 and 3,509, since session 3009's read_table stopped losing
the Queued Up rows that hold a # in a field). This script writes our figure and the gap of those rows, and the one
sentence of Finding 3 that quotes the reproduction, from the cards. The published figures (the thesis's), the sources
and the reasons are left as they are: a published figure is never computed here.

    python warehouse/analysis/findings/cross_check_rows.py [--check]

--check writes nothing and exits 1 when the note would change. Standard library only. No request, no model.
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
NOTE = os.path.join(ROOT, "docs", "methods", "automated_analysis_findings.md")
CARDS = os.path.join(ROOT, "site", "data", "findings")


def card(card_id):
    with open(os.path.join(CARDS, f"{card_id}.json"), encoding="utf-8") as f:
        return json.load(f)["numbers"]


def num(s):
    return float(s.replace(",", "").lstrip("+"))


def signed(v, d):
    """A gap as the note writes it: 0.00 when nil at the digits shown, else with its sign."""
    r = round(v, d)
    if r == 0:
        return f"{0:.{d}f}"
    return f"{r:+,.{d}f}" if d else f"{int(r):+,}"


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def row_line(cs):
    return "| " + " | ".join(cs) + " |"


def usd_row(cs, ours):
    """A row whose our figure and published figure are each 'USD x per MWh', the gap in cell 3 to the cent."""
    theirs = num(re.search(r"USD ([\d.,]+) per MWh", cs[1]).group(1))
    cs[0] = re.sub(r"USD [\d.,]+ per MWh", f"USD {ours:,.2f} per MWh", cs[0], count=1)
    cs[3] = signed(ours - theirs, 2)
    return cs


def queue_row(cs, pct, gw):
    m = re.search(r"([\d.]+) percent of ([\d,]+) GW", cs[1])
    tpct, tgw = num(m.group(1)), num(m.group(2))
    cs[0] = re.sub(r"[\d.]+ percent of [\d,]+ GW", f"{pct:.1f} percent of {round(gw):,} GW", cs[0], count=1)
    cs[3] = re.sub(r"[+-]?[\d.]+ points", f"{signed(pct - tpct, 1)} points", cs[3], count=1)
    cs[3] = re.sub(r"[+-]?[\d,]+ GW", f"{signed(gw - tgw, 0)} GW", cs[3], count=1)
    return cs


def rebuilt(text):
    b = card("batteries_lunch_grids")
    q = card("queue_divorce")
    rules = [
        ("the median real-time price", lambda cs: usd_row(cs, b["ercot_median_last"])),
        ("the 99.9th percentile", lambda cs: usd_row(cs, b["ercot_p999_last"])),
        ("Requests withdrawn, 2000 to 2020", lambda cs: queue_row(cs, q["withdrawn_pct"], q["requested_gw"])),
    ]
    lines = text.split("\n")
    at = next((i for i, l in enumerate(lines) if re.match(r"#+ .*Cross-checks", l)), None)
    if at is None:
        raise ValueError("the note has no section Cross-checks")
    done = set()
    for i in range(at, len(lines)):
        if not lines[i].startswith("|"):
            continue
        cs = cells(lines[i])
        for find, fix in rules:
            if find in done or len(cs) < 5 or find not in cs[0]:
                continue
            lines[i] = row_line(fix(cs))
            done.add(find)
            break
    missing = [f for f, _ in rules if f not in done]
    if missing:
        raise ValueError(f"no cross-check row found for: {', '.join(missing)}")
    out = "\n".join(lines)
    out = re.sub(r"(is reproduced as )\d+ percent of [\d,]+ GW", lambda m: f"{m.group(1)}{round(q['withdrawn_pct'])} percent of {round(q['requested_gw']):,} GW", out, count=1)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 when the note would change")
    args = ap.parse_args(argv)
    with open(NOTE, encoding="utf-8", newline="") as f:
        have = f.read()
    crlf = "\r\n" in have
    try:
        want = rebuilt(have.replace("\r\n", "\n"))
    except (OSError, ValueError, KeyError, AttributeError) as exc:
        print(f"cross_check_rows: {exc}")
        return 2
    if crlf:
        want = want.replace("\n", "\r\n")
    same = want == have
    if args.check:
        print("cross_check_rows: " + ("the rows are the cards'" if same else "the note's rows would change"))
        return 0 if same else 1
    if not same:
        with open(NOTE, "w", encoding="utf-8", newline="") as f:
            f.write(want)
    print("cross_check_rows: " + ("unchanged" if same else "the rows written from the cards"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
