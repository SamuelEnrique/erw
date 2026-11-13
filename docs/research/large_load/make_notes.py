"""Write one short notes file a utility from the checked rows (docs/research/large_load/notes/<slug>.md).

Energy Research Warehouse (ERW), session 5300. For each utility in rows/*.json (and each one a group found no rule
for), the note lists its rows (rule, status, source, what is not published), the row's own notes, and the documents
refused or blocked that the group tagged with that utility. A note already written by hand is kept: only the part
between the two generated markers is replaced.

    python -I make_notes.py
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIELDS = ("threshold_mw", "min_demand", "contract_term", "collateral", "exit_fee", "study_timeline",
          "connection_timeline", "queue_size")
START, END = "<!-- generated: start -->", "<!-- generated: end -->"


def slug(s: str) -> str:
    s = re.sub(r"\(.*?\)", " ", s or "")
    s = re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")
    return s[:60] or "unknown"


def slug_for(name: str, given: str = "") -> str:
    """The notes file's slug: the row's own notes_slug, else notes_slugs.json's entry for the name, else the name's."""
    if given:
        return given
    try:
        table = json.load(open(os.path.join(HERE, "notes_slugs.json"), encoding="utf-8"))
    except FileNotFoundError:
        table = {}
    return table.get(name) or slug(name)


def main() -> int:
    notes = {}
    for fp in sorted(glob.glob(os.path.join(HERE, "rows", "*.json"))):
        data = json.load(open(fp, encoding="utf-8"))
        group = data.get("group") or os.path.basename(fp)[:-5]
        for i, r in enumerate(data.get("rows") or [], 1):
            s = slug_for(r.get("utility", ""), r.get("notes_slug") or "")
            n = notes.setdefault(s, {"utility": r.get("utility"), "state": set(), "group": group, "rows": [],
                                     "none": [], "refused": []})
            n["state"].add(r.get("state", ""))
            n["rows"].append((f"{group}-{i:02d}", r))
        for nf in data.get("none_found") or []:
            s = slug_for(nf.get("utility", ""), nf.get("notes_slug") or "")
            n = notes.setdefault(s, {"utility": nf.get("utility"), "state": set(), "group": group, "rows": [],
                                     "none": [], "refused": []})
            n["none"].append(nf)
        for rf in data.get("refused") or []:
            u = rf.get("utility")
            if u:
                s = slug_for(u, rf.get("notes_slug") or "")
                if s in notes:
                    notes[s]["refused"].append(rf)
    os.makedirs(os.path.join(HERE, "notes"), exist_ok=True)
    for s, n in sorted(notes.items()):
        lines = [START, "", f"Group `{n['group']}`. Rows in `utilities_<date>.csv`:", ""]
        for rid, r in n["rows"]:
            st = r.get("status") or {}
            lines.append(f"- **{rid}**: {r.get('rule_name')}. Status: {st.get('value')} ({st.get('date') or 'date not published'}). "
                         f"License: {r.get('license')}. Source: {r.get('source_url')}")
            missing = [f for f in FIELDS if ((r.get('fields') or {}).get(f) or {}).get('value') == 'not published']
            held = [f for f in FIELDS if str(((r.get('fields') or {}).get(f) or {}).get('value', '')).startswith('held: ')]
            if missing:
                lines.append(f"  - Not published in the documents read: {', '.join(missing)}.")
            if held:
                lines.append(f"  - Held already by window A, not repeated: {', '.join(held)}.")
            if r.get("erw_overlap") and r.get("erw_overlap") != "none":
                lines.append(f"  - Overlap with window A's registries: {r['erw_overlap']}")
            if r.get("notes"):
                lines.append(f"  - Notes: {r['notes']}")
        if not n["rows"]:
            lines.append("- None.")
        for nf in n["none"]:
            lines.append(f"- No large-load rule found. Searched: {nf.get('searched', 'not stated')}")
        if n["refused"]:
            lines += ["", "Refused or blocked (not read, not retried another way):", ""]
            for rf in n["refused"]:
                lines.append(f"- {rf.get('url')}: {rf.get('reason')}")
        lines += ["", END]
        block = "\n".join(lines)
        path = os.path.join(HERE, "notes", f"{s}.md")
        if os.path.exists(path):
            old = open(path, encoding="utf-8").read()
            if START in old and END in old:
                new = old.split(START)[0] + block + old.split(END, 1)[1]
            else:
                new = old.rstrip() + "\n\n" + block + "\n"
        else:
            states = ", ".join(sorted(x for x in n["state"] if x))
            head = (f"# {n['utility']}{' (' + states + ')' if states else ''}: large-load rules\n\n"
                    f"Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). "
                    f"Method: `../README.md`.\n\n")
            new = head + block + "\n"
        open(path, "w", encoding="utf-8", newline="\n").write(new)
    print(f"notes written: {len(notes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
