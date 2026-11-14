"""Apply the license audit to the rows already merged (docs/research/large_load/rows/*.json), in place.

Energy Research Warehouse (ERW), session 5301. The same rule merge_group.py applies to a new group: a row is internal
when its main document, or every value, rests only on a host whose terms ask permission (README, "The hosts' terms");
a public row names in internal_fields the fields that rest only on such hosts. Makes no request.

    python -I license_audit.py
"""

import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from merge_group import apply_audit  # noqa: E402


def main() -> int:
    for fp in sorted(glob.glob(os.path.join(HERE, "rows", "*.json"))):
        data = json.load(open(fp, encoding="utf-8"))
        changed = False
        for i, r in enumerate(data.get("rows") or [], 1):
            before = (r.get("license"), tuple(r.get("internal_fields") or []))
            note = apply_audit(r)
            if (r.get("license"), tuple(r.get("internal_fields") or [])) != before:
                changed = True
                print(f"{data.get('group')}-{i:02d}: {note}")
        if changed:
            with open(fp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=1, ensure_ascii=False)
                f.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
