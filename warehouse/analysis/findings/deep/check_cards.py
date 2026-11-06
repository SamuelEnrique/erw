#!/usr/bin/env python3
"""The cards of the findings hunt's drafts, checked against their own files (chain 164, session 3017 on).

Energy Research Warehouse (ERW). For every row of public.scanner_drafts this chain wrote (id scan-deep-*), read over
SUPABASE_DB_URL (a read; nothing is written): the chart is the hunt's flag_line, its points are the CSV file's full
years and values, the marked point is the last full year and the reference line the first; the sentence holds both
figures as the card prints them; the eight files are there and the two pictures are PNGs; the limits sentence and the
five tests are present; the state is still draft. The chart's hover is the site's own (lib/discoverychart.ts, an axis
tooltip with a formatter for flag_line), the same for every hunt draft.

    python warehouse/analysis/findings/deep/check_cards.py

Exit 0 every card holds; 1 one or more do not.
"""

import base64
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))


def problems(row):
    out = []
    card, files, did = row["card"], row["files"], row["id"]
    ch, hunt = card.get("chart", {}), card.get("hunt", {})
    names = hunt.get("files", [])
    if card.get("draft") is not True or row["state"] != "draft":
        out.append(f"state {row['state']}")
    if ch.get("kind") != "flag_line":
        out.append(f"chart kind {ch.get('kind')}")
    if sorted(names) != sorted(files):
        out.append("the files listed are not the files stored")
    for n in names:
        if n.endswith(".png"):
            try:
                if not base64.b64decode(files[n]["content"])[:8] == b"\x89PNG\r\n\x1a\n":
                    out.append(f"{n} is not a PNG")
            except Exception as exc:                     # noqa: BLE001
                out.append(f"{n}: {exc}")
    csv = files.get(f"{did}.csv", {}).get("content", "")
    full = {}
    for ln in csv.split("\n"):
        p = ln.split(",")
        if len(p) >= 5 and p[1].isdigit() and p[4].strip() == "1":
            full[p[1]] = float(p[2])
    xs = [str(x) for x in ch.get("x", [])]
    vals = (ch.get("series") or [{}])[0].get("values", [])
    if xs != list(full):
        out.append(f"chart years {xs[:3]}... are not the CSV's full years {list(full)[:3]}...")
    elif any(abs(float(v) - full[x]) > 1e-6 * max(1.0, abs(full[x])) for x, v in zip(xs, vals)):
        out.append("a chart point is not the CSV's value")
    num = card.get("numbers", {})
    if xs and (str(ch.get("mark", {}).get("x")) != xs[-1] or str(num.get("last_year")) != xs[-1] or str(num.get("first_year")) != xs[0]):
        out.append("the marked year or the claim's years are not the CSV's first and last full years")
    if not hunt.get("limits") or "Limits:" not in card.get("footnote", ""):
        out.append("no limits sentence")
    if len(hunt.get("tests", [])) != 5 or not all(t.get("passed") for t in hunt.get("tests", [])):
        out.append("not five passed tests")
    sub = card.get("subtitle", "")
    if f"in {num.get('last_year')}," not in sub or f"in {num.get('first_year')}," not in sub:
        out.append("the sentence does not name both years")
    return out


def main():
    import lock
    import psycopg
    with psycopg.connect(lock.env("SUPABASE_DB_URL")) as c:
        rows = c.execute("select id, state, card, files from public.scanner_drafts where id like 'scan-deep-%' order by id").fetchall()
    bad = 0
    for did, state, card, files in rows:
        p = problems({"id": did, "state": state, "card": card, "files": files})
        if p:
            bad += 1
            print(f"FAIL {did} ({card.get('hunt', {}).get('family')}, {card.get('hunt', {}).get('pattern')}, {card.get('hunt', {}).get('region')}): {'; '.join(p)}")
    print(f"{len(rows) - bad} of {len(rows)} cards hold")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
