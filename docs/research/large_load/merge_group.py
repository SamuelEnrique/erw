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
STATUSES = ("proposed", "approved", "in effect", "denied", "withdrawn")  # session 5301: a commission may reject a proposal
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


# Hosts whose terms ask written permission, or allow personal use only (README, "The hosts' terms"): a row whose
# values come only from such a host is internal (the owner's ruling 4 of 6 November 2026).
RESTRICTED = {
    "centerpointenergy.com": "CenterPoint's Terms of Use (personal and non-commercial use; robots barred), read 2026-11-13",
    "southerncompany.com": "Southern Company's Terms and Conditions (no reproduction without prior written consent), read 2026-11-13",
    "georgiapower.com": "Southern Company's Terms and Conditions (no reproduction without prior written consent), read 2026-11-13",
    "alabamapower.com": "Southern Company's Terms and Conditions (no reproduction without prior written consent), read 2026-11-13",
    "mississippipower.com": "Southern Company's Terms and Conditions (no reproduction without prior written consent), read 2026-11-13",
    "pge.com": "PG&E's Terms of Use (no use in publications without prior written consent), read 2026-11-13",
    "aps.com": "APS's Terms of Use (personal, noncommercial use; no distribution without written permission), read 2026-11-13",
    "oncor.com": "Oncor's Terms and Conditions (personal, noncommercial, educational use only), read 2026-11-13",
    "srpnet.com": "SRP's Website Terms and Conditions (no reproduction without written permission)",
    "epelectric.com": "El Paso Electric's terms of use (personal, noncommercial use)",
    "aep.com": "AEP's legal notice (personal use only)",
    "aepohio.com": "AEP's legal notice (personal use only)",
    "appalachianpower.com": "AEP's legal notice (personal use only)",
    "indianamichiganpower.com": "AEP's legal notice (personal use only)",
    "psoklahoma.com": "AEP's legal notice (personal use only)",
    "swepco.com": "AEP's legal notice (personal use only)",
    "aeptexas.com": "AEP's legal notice (personal use only)",
    "kentuckypower.com": "AEP's legal notice (personal use only)",
    "in.gov": "IN.gov's statewide terms (written permission)",
    "portlandgeneral.com": "PGE's legal notices (personal or noncommercial use), per the northwest group's reading",
    "rockymountainpower.net": "PacifiCorp's terms (no use unless permitted in writing)",
    "pacificpower.net": "PacifiCorp's terms (no use unless permitted in writing)",
    "basinelectric.com": "Basin Electric's terms (no reproduction without written consent)",
    "chelanpud.org": "Chelan PUD's terms, per the northwest group's reading",
    "northwesternenergy.com": "NorthWestern Energy's terms, per the northwest group's reading",
    "blackhillsenergy.com": "Black Hills Energy's terms, per the northwest group's reading",
    "oppd.com": "OPPD's terms (personal, non-commercial use)",
}


def restricted(url: str):
    import urllib.parse
    host = (urllib.parse.urlsplit(url or "").hostname or "").lower()
    for k, why in RESTRICTED.items():
        if host == k or host.endswith("." + k):
            return why
    return None


def restricted_fields(row: dict) -> dict:
    """The fields whose every cite is a restricted host's document, with the host's terms."""
    src = row.get("source_url", "")
    out = {}
    for f in FIELDS:
        v = (row.get("fields") or {}).get(f) or {}
        cites = v.get("cites") or []
        if cites and not marker(v.get("value", "")):
            whys = [restricted(c.get("url") or src) for c in cites]
            if all(whys):
                out[f] = whys[0]
    return out


def license_audit(row: dict) -> str | None:
    """The reason a public row must be internal (session 5301): its main document is a restricted host's, or every
    valued field rests only on restricted hosts. A row with only some such fields stays public and names them in
    internal_fields, for window A to leave out of a public copy."""
    src = row.get("source_url", "")
    why = restricted(src)
    if why:
        return f"its main document is on a host whose terms ask permission: {why}"
    rf = restricted_fields(row)
    valued = [f for f in FIELDS if not marker(((row.get("fields") or {}).get(f) or {}).get("value", ""))]
    if valued and set(valued) <= set(rf):
        return "every value rests only on hosts whose terms ask permission: " + "; ".join(sorted(set(rf.values())))
    return None


def apply_audit(row: dict) -> str | None:
    """Set license and internal_fields in place; return what changed, for the log."""
    note = None
    why = license_audit(row)
    if why and row.get("license") == "public":
        row["license"] = "internal"
        row["license_basis"] = (row.get("license_basis", "").rstrip() + " Made internal by the license audit: " + why
                                + ".").strip()
        note = "internal: " + why
    rf = restricted_fields(row)
    if row.get("license") == "public" and rf:
        row["internal_fields"] = sorted(rf)
        note = (note or "") + f" internal_fields {sorted(rf)}"
    else:
        row.pop("internal_fields", None)
    return note


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
    for r in rows:
        st = r.get("status") or {}
        date = (st.get("date") or "").strip()
        m = re.match(r"^(\d{4}-\d{2}(?:-\d{2})?)(.*)$", date)
        if date and (not m or m.group(2).strip()):
            # a status date followed by words: the date stays, the words go to the notes as the group wrote them
            st["date"] = m.group(1) if m else ""
            r["notes"] = (r.get("notes", "").rstrip() + f" Status date as the reading group wrote it: '{date}'.").strip()
            print(f"status date normalized: {r.get('utility', '')[:40]} | '{date}' -> '{st['date']}'")
        note = apply_audit(r)
        if note:
            print(f"license audit: {r.get('utility', '')[:50]} | {note}")
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
