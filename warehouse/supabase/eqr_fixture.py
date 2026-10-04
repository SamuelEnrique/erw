#!/usr/bin/env python3
"""The summary of ferc_eqr_contracts as the loader would store it, written to a file and to nothing else (session 99).

Energy Research Warehouse (ERW). For checking /contracts on a built site without touching the database: the rows the
live set would hold (live_set.yaml's rule for the table), summarized by load.eqr_summary, with the largest buyers and
sellers where warehouse/derived/eqr_buyers.py has been run. The file holds internal figures: give it a path outside
git (runs/ is not in git). No database is read or written.

    python warehouse/supabase/eqr_fixture.py runs/session99/summary.json
"""

import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import load  # noqa: E402


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print(__doc__)
        return 2
    out = os.path.abspath(argv[0])
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    inside = os.path.relpath(out, root).replace("\\", "/")
    if not inside.startswith(("runs/", "..")):
        print(f"refused: {inside} is inside the repository and not under runs/: the summary is internal and must stay out of git")
        return 2
    df = load.filtered(load.EQR, None, pd.Timestamp.now(tz="UTC"))[0]
    summary = load.eqr_summary(df)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f)
    print(f"the summary of {summary['rows']:,} rows written to {inside}; largest buyers and sellers: {'yes' if 'largest' in summary else 'no (run warehouse/derived/eqr_buyers.py)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
