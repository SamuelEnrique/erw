"""Session 10226: what /contracts is served, for one load day, by the replication's own copy_rows.py and the loader's
own eqr_summary, with eqr_largest and eqr_terms stubbed (the default view reads neither; the stub saves memory).
Reads the main checkout's warehouse/output (read only); writes runs/c10226/rows_<day>/ in this worktree.

    python runs/c10226/served.py 2026-10-05
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
MAIN_OUT = r"C:\Users\lossa\Documents\erw\warehouse\output"

day = sys.argv[1] if len(sys.argv) > 1 else "2026-10-05"
sys.path.insert(0, os.path.join(ROOT, "warehouse", "supabase"))
import load  # noqa: E402

load.eqr_largest = lambda *a, **k: None
load.eqr_terms = lambda *a, **k: None
sys.path.insert(0, os.path.join(ROOT, "replication", "contracts"))
import copy_rows  # noqa: E402

copy_rows.ROWS = os.path.join(HERE, f"rows_{day}")
sys.exit(copy_rows.main(["copy_rows", "--tables", MAIN_OUT, "--load-day", day]))
