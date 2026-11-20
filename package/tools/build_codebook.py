#!/usr/bin/env python3
"""Write erw/data/codebook.json, the codebook the installed package carries (chain 630, part D).

Energy Research Warehouse (ERW). Inside a clone the package reads warehouse/metadata/variables/ itself; an installed
package reads this copy: the shared names and the metadata file of every table coverage.csv flags public (an internal
table is never named outside the repository's own record). Run it from the repository before a build of the package:

    python package/tools/build_codebook.py            write package/src/erw/data/codebook.json
    python package/tools/build_codebook.py --check    exit 1 when it differs from the repository's files

No request is made.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
VARS = ROOT / "warehouse" / "metadata" / "variables"
OUT = ROOT / "package" / "src" / "erw" / "data" / "codebook.json"


def public():
    with open(ROOT / "warehouse" / "metadata" / "coverage.csv", encoding="utf-8", newline="") as f:
        return {r["table"] for r in csv.DictReader(f) if r.get("license") == "public"}


def build():
    shown = public()
    tables = {}
    for p in sorted(VARS.glob("*.yaml")):
        if p.stem.startswith("_") or p.stem not in shown:
            continue
        tables[p.stem] = yaml.safe_load(p.read_text(encoding="utf-8"))
    shared = yaml.safe_load((VARS / "_shared.yaml").read_text(encoding="utf-8"))["columns"]
    return json.dumps({"shared": shared, "tables": tables}, ensure_ascii=False, sort_keys=False,
                      separators=(",", ":"), default=str) + "\n"


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--check", action="store_true")
    a = p.parse_args(argv)
    text = build()
    if a.check:
        same = OUT.is_file() and OUT.read_text(encoding="utf-8") == text
        print(f"{OUT}: {'agrees with' if same else 'differs from'} warehouse/metadata/variables/")
        return 0 if same else 1
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT} ({len(json.loads(text)['tables'])} public tables, {OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
