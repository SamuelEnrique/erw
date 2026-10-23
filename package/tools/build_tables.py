#!/usr/bin/env python3
"""Write erw/data/tables.csv, the license and live-window record the installed package carries (session 1001).

Energy Research Warehouse (ERW), docs/methods/packages.md. Inside a clone the package reads the repository's own
files; an installed package reads this copy. Run it from the repository before a build of the package:

    python package/tools/build_tables.py            write package/src/erw/data/tables.csv
    python package/tools/build_tables.py --check    exit 1 when the shipped copy differs from the repository's record

No request is made.
"""

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))

from erw import licenses  # noqa: E402


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true")
    a = p.parse_args(argv)
    root = HERE.parents[1]
    fresh = licenses.build(root)
    path = licenses.shipped_path()
    if a.check:
        old = {r["table"]: r for r in licenses._csv(path)}
        new = {r["table"]: {k: r.get(k, "") for k in licenses.FIELDS} for r in fresh}
        diff = sorted(t for t in set(old) | set(new) if old.get(t) != new.get(t))
        print(f"{path}: {len(old)} rows shipped, {len(new)} in the record, {len(diff)} differ"
              + (f": {', '.join(diff[:20])}" if diff else ""))
        return 1 if diff else 0
    licenses.write(path, fresh)
    counts = {v: sum(1 for r in fresh if r["verdict"] == v) for v in licenses.VERDICTS}
    print(f"wrote {path}: {len(fresh)} tables ({', '.join(f'{v} {n}' for v, n in counts.items())})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
