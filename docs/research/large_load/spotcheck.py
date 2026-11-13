"""Print one row in five of a group, each value beside the words around its quote in the copy read, for a person's check.

Energy Research Warehouse (ERW), session 5300. The quote check (verify_quotes.py) proves the words are in the
document; this shows the value next to the words in their place, so that a reader can judge whether the value is
what the words say (a threshold that is really a minimum bill, a range written as one figure, a proposal read as in
effect). Rows 1, 6, 11 and so on of each group are shown (the first, then every fifth). Makes no request.

    python -I spotcheck.py rows/<group>.json [--every 5] [--start 0]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from verify_quotes import FIELDS, load_doc, norm  # noqa: E402


def around(quote: str, pages: dict, width: int = 300) -> str:
    part = re.split(r"\s*(?:\.\.\.|\u2026)\s*", quote)[0]
    q = norm(part)[:80]
    for name in ("text.txt", "layout.txt"):
        for i, text in enumerate(pages.get(name) or [], 1):
            t = norm(text)
            k = t.find(q)
            if k >= 0:
                return f"[p.{i}] ..." + t[max(0, k - width): k + len(norm(quote)) + width] + "..."
    return "[not found in the copy]"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--every", type=int, default=5)
    ap.add_argument("--start", type=int, default=0)
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    data = json.load(open(a.file, encoding="utf-8"))
    group = data.get("group")
    for i, r in enumerate(data.get("rows") or []):
        if (i - a.start) % a.every:
            continue
        src = r.get("source_url")
        print("=" * 100)
        print(f"{group}-{i + 1:02d} | {r.get('utility')} | {r.get('rule_name')}")
        st = r.get("status") or {}
        items = [("status", {"value": f"{st.get('value')} {st.get('date')}", "cites": st.get("cites")})]
        items += [("docket", r.get("docket") or {})]
        items += [(f, (r.get("fields") or {}).get(f) or {}) for f in FIELDS]
        for name, v in items:
            val = v.get("value")
            if not v.get("cites"):
                print(f"-- {name}: {val}")
                continue
            print(f"-- {name}: {val}")
            for c in v["cites"]:
                url = c.get("url") or src
                doc = load_doc(url)
                print(f"   cite p.{c.get('page')} {c.get('section') or ''}: \"{c.get('quote')}\"")
                print("   in place: " + (around(c.get("quote") or "", doc[1]) if doc else "[uncached]"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
