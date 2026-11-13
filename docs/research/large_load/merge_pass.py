"""Take one group of the second pass (changes) or the third (laws) from its hand-over file, check the form, copy it in.

Energy Research Warehouse (ERW), session 5302. The subagent writes runs/s5300/changes/<group>.json or
runs/s5300/legislation/<group>.json; this script turns em and en dashes into hyphens (as merge_group.py does), checks
each entry's form against the README, applies the license audit of merge_group.py to a change, and writes
docs/research/large_load/changes/<group>.json or legislation/<group>.json.

    python -I merge_pass.py changes <group> [--force]
    python -I merge_pass.py legislation <group> [--force]

Then: verify_quotes.py <that file> --stamp.
"""

from __future__ import annotations

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
from merge_group import clean, restricted  # noqa: E402

CHANGES = ("filed", "approved", "in effect", "amended", "denied", "withdrawn", "suspended", "hearing set",
           "order issued", "other")
LAW_STATUSES = ("introduced", "passed one chamber", "passed", "enacted", "in effect", "vetoed", "died")
DATE = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")


def cites_ok(cites) -> list[str]:
    out = []
    if not cites:
        out.append("no cites")
    for c in cites or []:
        if not c.get("quote"):
            out.append("a cite without a quote")
        if not (c.get("page") or c.get("section")):
            out.append("a cite without a page or section")
    return out


def normalize_date(entry: dict, key: str) -> None:
    d = (entry.get(key) or "").strip()
    if not d or d == "not published":
        entry[key] = ""
        return
    m = re.match(r"^(\d{4}-\d{2}(?:-\d{2})?)(.*)$", d)
    if not m or m.group(2).strip():
        entry[key] = m.group(1) if m else ""
        entry["notes"] = (entry.get("notes", "").rstrip() + f" {key} as the reading group wrote it: '{d}'.").strip()


def change_problems(c: dict) -> list[str]:
    out = []
    for k in ("utility", "rule_name", "affects", "change", "source_url", "what", "license"):
        if not c.get(k):
            out.append(f"missing {k}")
    if c.get("change") not in CHANGES:
        out.append(f"change {c.get('change')}")
    if c.get("date") and not DATE.match(c["date"]):
        out.append(f"date {c.get('date')}")
    if c.get("license") not in ("public", "internal"):
        out.append(f"license {c.get('license')}")
    aff = c.get("affects", "")
    if aff.startswith(("large_load_tariffs/", "large_load_connection_rules/")):
        if not os.path.exists(os.path.join(ROOT, "warehouse", "sources", aff.split()[0])):
            out.append(f"affects a registry file not found: {aff}")
    return out + cites_ok(c.get("cites"))


def law_problems(law: dict) -> list[str]:
    out = []
    for k in ("state", "bill", "title", "status", "source_url", "license"):
        if not law.get(k):
            out.append(f"missing {k}")
    if law.get("status") not in LAW_STATUSES:
        out.append(f"status {law.get('status')}")
    for k in ("status_date", "effective_date"):
        if law.get(k) and not DATE.match(law[k]):
            out.append(f"{k} {law.get(k)}")
    out += cites_ok(law.get("cites"))
    tm = law.get("threshold_mw") or {}
    if not tm.get("value"):
        out.append("threshold_mw missing")
    elif tm["value"] != "not published":
        out += ["threshold_mw: " + p for p in cites_ok(tm.get("cites"))]
    for q in law.get("requirements") or []:
        if not (q.get("topic") and q.get("value")):
            out.append("a requirement without topic or value")
        out += ["requirement: " + p for p in cites_ok(q.get("cites"))]
    return out


def main() -> int:
    if len(sys.argv) < 3 or sys.argv[1] not in ("changes", "legislation"):
        print(__doc__)
        return 2
    kind, group = sys.argv[1], sys.argv[2]
    force = "--force" in sys.argv
    src = os.path.join(ROOT, "runs", "s5300", kind, f"{group}.json")
    data = clean(json.load(open(src, encoding="utf-8")))
    items = data.get("changes" if kind == "changes" else "laws") or []
    bad = 0
    for i, e in enumerate(items):
        if kind == "changes":
            normalize_date(e, "date")
            if e.get("license") == "public" and restricted(e.get("source_url", "")):
                e["license"] = "internal"
                e["license_basis"] = (e.get("license_basis", "") + " Made internal by the license audit: "
                                      + restricted(e["source_url"]) + ".").strip()
            p = change_problems(e)
        else:
            normalize_date(e, "status_date")
            normalize_date(e, "effective_date")
            p = law_problems(e)
        if p:
            bad += 1
            label = e.get("utility") or f"{e.get('state')} {e.get('bill')}"
            print(f"{i} {label[:50]}: " + "; ".join(p))
    print(f"{kind}/{group}: {len(items)} entries, {bad} with problems")
    if bad and not force:
        return 1
    os.makedirs(os.path.join(HERE, kind), exist_ok=True)
    out = os.path.join(HERE, kind, f"{group}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print("wrote", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
