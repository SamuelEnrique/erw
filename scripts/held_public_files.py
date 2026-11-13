#!/usr/bin/env python3
"""The held grids' prices in files the site serves by address: a list for the owner's ruling (chain 245, session 4174).

Energy Research Warehouse (ERW). A grid whose own terms do not allow the ERW (its verdict in
warehouse/metadata/license_verdicts.csv is not "may be public") is held "license needed": the price board's row reads
"licensed" and no new file is built for it (warehouse/derived/board_page.py). But the files built before the hold stay
under site/public/, because the page keeper (warehouse/derived/page_keep.py) keeps a file only the old build has
(its rules 4 and 5). The site's proxy serves any file by address (every extension but .rsc), so those files reach a
visitor who types the address, and they are in the repository's history.

    python scripts/held_public_files.py              the list, and the board row of each file with its status
    python scripts/held_public_files.py --markdown   the same as a table, for docs/reviews/

It deletes nothing and has no mode that does: removing the files is the owner's ruling (the repository's rule against
deleting files), and with it a change to page_keep.py so that a file whose board row reads "licensed" is not kept.
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
GRID_PREFIX = {"ISO-NE": "isone", "MISO": "miso", "NYISO": "nyiso", "PJM": "pjm", "SPP": "spp", "CAISO": "caiso", "ERCOT": "ercot"}


def held_prefixes(root=ROOT):
    with open(os.path.join(root, "warehouse", "metadata", "license_verdicts.csv"), encoding="utf-8", newline="") as f:
        v = {r["key"]: r["verdict"] for r in csv.DictReader(f)}
    return {GRID_PREFIX[g]: g for g in GRID_PREFIX if v.get(g) != "may be public"}


def files(root=ROOT):
    pre = held_prefixes(root)
    out = subprocess.run(["git", "ls-files", "site/public"], cwd=root, capture_output=True, text=True).stdout.split()
    rx = re.compile(r"/(" + "|".join(sorted(pre)) + r")[-_][^/]*$")
    return [f for f in out if rx.search(f)], pre


def board_rows(root=ROOT):
    p = os.path.join(root, "site", "data", "board.json")
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return {r["id"]: r for r in json.load(f).get("rows", [])}


def describe(path, rows, pre):
    name = os.path.basename(path).rsplit(".", 1)[0]
    kind = ("board series (the workbench)" if "/board/s/" in path else "board hourly prices (the workbench)" if "/board/h/" in path
            else "the seller tab's yearly prices" if "/seller/prices/" in path else "other")
    grid = pre.get(re.split(r"[-_]", name)[0], "")
    row = rows.get(name)
    status = row.get("status", "") if row else ("no board row of this id" if "/board/" in path else "not a board file")
    return dict(path=path, bytes=os.path.getsize(os.path.join(ROOT, path)), grid=grid, kind=kind, board_status=status)


def main(argv=None):
    ap = argparse.ArgumentParser(description="The held grids' public files, listed for a ruling (nothing deleted)")
    ap.add_argument("--markdown", action="store_true")
    a = ap.parse_args(argv)
    fs, pre = files()
    rows = board_rows()
    items = [describe(f, rows, pre) for f in fs]
    total = sum(i["bytes"] for i in items)
    if a.markdown:
        print("| File | Bytes | Grid | What it is | Its board row |")
        print("|---|---:|---|---|---|")
        for i in items:
            print(f"| `{i['path']}` | {i['bytes']:,} | {i['grid']} | {i['kind']} | {i['board_status']} |")
    else:
        for i in items:
            print(f"{i['bytes']:>10,}  {i['grid']:<7} {i['board_status']:<26} {i['path']}")
    print(f"\n{len(items)} files, {total:,} bytes, of the held grids {', '.join(sorted(set(pre.values())))}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
