#!/usr/bin/env python3
"""Score a filled deal-extraction evaluation file (eval_sample.csv, or a spot check).

Energy Research Warehouse (ERW), session 15, Task 4.

    python warehouse/deals/eval/score.py warehouse/deals/eval/eval_sample.csv

Reads the <field>_ok columns (1 correct, 0 wrong, blank not marked) and prints, per
field, how many rows were marked and the precision: correct / marked. Fields are
scored separately for rows where the extractor filled the field and rows where it
left it empty (an empty field marked 1 means the stories indeed do not state it).
Nothing is imputed: an unmarked row is not counted.
"""

import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from sample import FIELDS  # noqa: E402

VALUE_COL = {"is_deal": None, "dedup": None}


def main(path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    rows = []
    for f in FIELDS:
        col = f"{f}_ok"
        if col not in df.columns:
            continue
        marked = df[df[col].isin(["0", "1"])]
        val = VALUE_COL.get(f, f)
        for label, part in (("all", marked),
                            ("filled", marked[marked[val] != ""] if val else marked.iloc[0:0]),
                            ("empty", marked[marked[val] == ""] if val else marked.iloc[0:0])):
            if label != "all" and not val:
                continue
            n = len(part)
            ok = int((part[col] == "1").sum())
            rows.append({"field": f, "rows": label, "marked": n, "correct": ok,
                         "precision": f"{ok / n:.2f}" if n else ""})
    out = pd.DataFrame(rows)
    print(f"{os.path.basename(path)}: {len(df)} deals")
    print(out.to_string(index=False))
    allm = sum(r["marked"] for r in rows if r["rows"] == "all")
    allc = sum(r["correct"] for r in rows if r["rows"] == "all")
    if allm:
        print(f"all fields: {allc} of {allm} marked field values correct ({allc / allm:.2f})")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
