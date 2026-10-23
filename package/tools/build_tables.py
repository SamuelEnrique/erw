#!/usr/bin/env python3
"""Write erw/data/tables.csv, the license and live-window record the installed package carries (session 1001).

Energy Research Warehouse (ERW), docs/methods/packages.md. Inside a clone the package reads the repository's own
files; an installed package reads this copy. Run it from the repository before a build of the package:

    python package/tools/build_tables.py            write package/src/erw/data/tables.csv, and site/data/table_verdicts.json
    python package/tools/build_tables.py --check    exit 1 when either differs from the repository's record

Session 1008: the site's copy, site/data/table_verdicts.json ({table: [verdict, words]}), from which /data writes each
table's three one-line calls, or the refusal of a table that is not public. Session 1009: site/data/table_citations.json
({table: the citation's words before "Via ..."}, the package's own cite), which the download route writes in its header.

No request is made.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from erw import licenses  # noqa: E402


def citation_heads(root, names):
    """{table: the citation's words before "Via the Energy Research Warehouse (ERW), table"}, by the package's own cite
    on the clone's record (no request)."""
    import erw
    erw.set_backend(str(root / "warehouse" / "output"))
    via = " Via the Energy Research Warehouse (ERW), table "
    return {t: erw.cite(t).split(via)[0] for t in sorted(names)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true")
    a = p.parse_args(argv)
    root = HERE.parents[1]
    fresh = licenses.build(root)
    path = licenses.shipped_path()
    site = root / "site" / "data" / "table_verdicts.json"
    verdicts = json.dumps({r["table"]: [r["verdict"], r["words"]] for r in sorted(fresh, key=lambda r: r["table"])},
                          indent=1, ensure_ascii=False) + "\n"
    cites_path = root / "site" / "data" / "table_citations.json"
    cites = json.dumps(citation_heads(root, [r["table"] for r in fresh]), indent=1, ensure_ascii=False) + "\n"
    if a.check:
        old = {r["table"]: r for r in licenses._csv(path)}
        new = {r["table"]: {k: r.get(k, "") for k in licenses.FIELDS} for r in fresh}
        diff = sorted(t for t in set(old) | set(new) if old.get(t) != new.get(t))
        site_ok = site.is_file() and site.read_text(encoding="utf-8") == verdicts
        site_ok = site_ok and cites_path.is_file() and cites_path.read_text(encoding="utf-8") == cites
        print(f"{path}: {len(old)} rows shipped, {len(new)} in the record, {len(diff)} differ"
              + (f": {', '.join(diff[:20])}" if diff else "") + f"; the site's two files {'agree' if site_ok else 'differ'}")
        return 1 if diff or not site_ok else 0
    licenses.write(path, fresh)
    site.write_text(verdicts, encoding="utf-8", newline="\n")
    cites_path.write_text(cites, encoding="utf-8", newline="\n")
    counts = {v: sum(1 for r in fresh if r["verdict"] == v) for v in licenses.VERDICTS}
    print(f"wrote {path}: {len(fresh)} tables ({', '.join(f'{v} {n}' for v, n in counts.items())})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
