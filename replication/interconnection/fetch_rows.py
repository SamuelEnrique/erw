#!/usr/bin/env python3
"""ERW, the interconnection queue explorer: the tables the replication reads, copied into rows/ (session 7509).

    python replication/interconnection/fetch_rows.py --from <a folder of ERW tables, such as warehouse/output>

Copies iso_queue_statistics.csv (what the page reads) and each <iso>_interconnection_queue.csv found there (what part B
recomputes the statistics from) into this folder's rows/, unchanged, header and all. rows/ is not in git:
iso_queue_statistics, nyiso_interconnection_queue, miso_interconnection_queue and isone_interconnection_queue are held
("license needed" since 21 October 2026, site/data/license_status.json), and no row of a held table is committed. The
three public queue tables (CAISO, ERCOT, SPP) are also on the site's data page and in the Redivis dataset. Nothing is
requested of any grid operator here: the files are copied from a folder on this machine. Standard library only.
"""
import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TABLES = ["iso_queue_statistics"] + [f"{q}_interconnection_queue" for q in ("caiso", "ercot", "nyiso", "miso", "spp", "isone")]


def main(argv=None):
    ap = argparse.ArgumentParser(description="Copy the tables the interconnection replication reads into rows/")
    ap.add_argument("--from", dest="src", default=os.path.join(ROOT, "warehouse", "output"))
    a = ap.parse_args(argv)
    dst = os.path.join(HERE, "rows")
    os.makedirs(dst, exist_ok=True)
    n = 0
    for t in TABLES:
        p = os.path.join(a.src, f"{t}.csv")
        if not os.path.exists(p):
            print(f"not in {a.src}: {t}.csv")
            continue
        shutil.copyfile(p, os.path.join(dst, f"{t}.csv"))
        n += 1
        print(f"copied {t}.csv ({os.path.getsize(p):,} bytes)")
    if not os.path.exists(os.path.join(dst, "iso_queue_statistics.csv")):
        print("iso_queue_statistics.csv is needed and was not found")
        return 2
    print(f"{n} of {len(TABLES)} tables in {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
