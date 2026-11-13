"""Take one group's rows from the reading subagent's hand-over file, check their form, and copy them into rows/.

Energy Research Warehouse (ERW), session 5300. The subagent writes runs/s5300/rows/<group>.json; this script:
- turns an em or en dash in any string into a hyphen (the repository's rule; verify_quotes.py treats dashes as one);
- checks every row's form (the eight fields present, each a value with quoted cites, "not published", "held: <file>"
  or "see row: <rule>"; status one of three; license public or internal);
- writes docs/research/large_load/rows/<group>.json when the form holds (or with --force, to fix by hand after).

    python -I merge_group.py <group> [--force]

Then: verify_quotes.py rows/<group>.json --stamp (every quote against the cached text, the read dates written in).
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FIELDS = ("threshold_mw", "min_demand", "contract_term", "collateral", "exit_fee", "study_timeline",
          "connection_timeline", "queue_size")
STATUSES = ("proposed", "approved", "in effect")
EM, EN = chr(0x2014), chr(0x2013)


def clean(x, in_quote=False):
    if isinstance(x, str):
        if in_quote:
            return x.replace(EM, "-").replace(EN, "-")
        x = x.replace(" " + EM + " ", ", ").replace(" " + EN + " ", " to ")
        return x.replace(EM, ", ").replace(EN, "-")
    if isinstance(x, list):
        return [clean(v, in_quote) for v in x]
    if isinstance(x, dict):
        return {k: clean(v, in_quote or k == "quote") for k, v in x.items()}
    return x


def marker(v: str) -> bool:
    v = (v or "").strip()
    return v == "not published" or v.startswith("held: ") or v.startswith("see row: ")


def problems(row: dict, names: set) -> list[str]:
    out = []
    for k in ("utility", "state", "iso_region", "rule_name", "source_url", "license"):
        if not row.get(k):
            out.append(f"missing {k}")
    if row.get("license") not in ("public", "internal"):
        out.append(f"license {row.get('license')}")
    st = row.get("status") or {}
    if st.get("value") not in STATUSES:
        out.append(f"status {st.get('value')}")
    if not (st.get("cites") or []):
        out.append("status without cites")
    dk = row.get("docket")
    if not isinstance(dk, dict) or not dk.get("value"):
        out.append("docket missing")
    elif not marker(dk["value"]) and not dk.get("cites"):
        out.append("docket value without cites")
    qc = row.get("quoted_clause") or {}
    if not qc.get("quote"):
        out.append("quoted_clause missing")
    fields = row.get("fields") or {}
    for f in FIELDS:
        v = fields.get(f)
        if not isinstance(v, dict) or not (v.get("value") or "").strip():
            out.append(f"{f} missing")
            continue
        val = v["value"].strip()
        if val.startswith("held: "):
            target = val[6:].split()[0]
            if not os.path.exists(os.path.join(ROOT, "warehouse", "sources", target)):
                out.append(f"{f} held file not found: {target}")
        elif val.startswith("see row: "):
            if val[9:] not in names:
                out.append(f"{f} see row not found: {val[9:]}")
        elif val != "not published":
            cites = v.get("cites") or []
            if not cites or not all(c.get("quote") for c in cites):
                out.append(f"{f} value without quoted cites")
            if not all(c.get("page") or c.get("section") for c in cites):
                out.append(f"{f} cite without page or section")
    extra = set(fields) - set(FIELDS)
    if extra:
        out.append(f"unknown fields {sorted(extra)}")
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    group = sys.argv[1]
    force = "--force" in sys.argv
    src = os.path.join(ROOT, "runs", "s5300", "rows", f"{group}.json")
    data = clean(json.load(open(src, encoding="utf-8")))
    rows = data.get("rows") or []
    bad = 0
    for i, r in enumerate(rows):
        # a queue figure a holding company states for several utilities sits on one row of the group (session 5300)
        names = {x.get("rule_name") for x in rows}
        p = problems(r, names)
        if p:
            bad += 1
            print(f"row {i} {r.get('utility', '')[:40]} | {r.get('rule_name', '')[:60]}: " + "; ".join(p))
    print(f"{group}: {len(rows)} rows, {bad} with problems; refused {len(data.get('refused') or [])}; "
          f"none_found {len(data.get('none_found') or [])}")
    if bad and not force:
        return 1
    os.makedirs(os.path.join(HERE, "rows"), exist_ok=True)
    out = os.path.join(HERE, "rows", f"{group}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
