"""Copy the tables the forty do-files read into docs/findings/_top40/tables, without the ERW's '#' header lines.

Energy Research Warehouse (ERW), session 8905 (chain 590, 19 November 2026). The do-files read a table's CSV with the
variable names on the first line, as Redivis's download gives it. The ERW's own files (warehouse/output on the data
machine, and the site's Download CSV) open with provenance lines that begin with '#'. This copies each table the
sheet needs from a folder you name, drops those leading lines, and leaves every other line as it is. It streams the
file, so a large hourly table needs little memory. Nothing is changed in the source folder.

Usage, from the repository's root:
    python docs/findings/_top40/strip_hash_lines.py C:/path/to/warehouse/output          (the forty's tables)
    python docs/findings/_top40/strip_hash_lines.py C:/path/to/warehouse/output --ten    (tonight's ten only)
    python docs/findings/_top40/strip_hash_lines.py --list                                 (print the tables, copy nothing)
"""
import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_runners import TOP10, findings  # noqa: E402


def needed(ten=False):
    rows = [r for r in findings() if (r["n"] in TOP10 or not ten)]
    out = {}
    for r in rows:
        for t in r["tables"]:
            out.setdefault(t, []).append(r["n"])
    return out


def strip_copy(src, dst):
    """Copy src to dst, dropping the lines before the header that begin with '#'. Returns the lines dropped."""
    dropped = 0
    with open(src, "r", encoding="utf-8", newline="") as fin, open(dst, "w", encoding="utf-8", newline="") as fout:
        head = True
        for line in fin:
            if head and line.startswith("#"):
                dropped += 1
                continue
            head = False
            fout.write(line)
    return dropped


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("source", nargs="?", help="the folder that holds the ERW's CSVs (warehouse/output)")
    ap.add_argument("--ten", action="store_true", help="only the tables of tonight's ten")
    ap.add_argument("--list", action="store_true", help="print the tables and the findings that read them; copy nothing")
    ap.add_argument("--dest", default=str(HERE / "tables"), help="where the copies go (default: docs/findings/_top40/tables)")
    a = ap.parse_args(argv)
    tables = needed(a.ten)
    if a.list or not a.source:
        for t, ns in sorted(tables.items()):
            print("%s  (findings %s)" % (t, ", ".join(str(n) for n in ns)))
        return 0
    src, dst = Path(a.source), Path(a.dest)
    dst.mkdir(parents=True, exist_ok=True)
    missing = 0
    for t in sorted(tables):
        if not (src / t).exists():
            print("missing: %s (findings %s)" % (t, ", ".join(str(n) for n in tables[t])))
            missing += 1
            continue
        n = strip_copy(src / t, dst / t)
        print("copied: %s (%d header lines dropped)" % (t, n))
    print("%d of %d tables copied to %s" % (len(tables) - missing, len(tables), dst))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
