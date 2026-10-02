#!/usr/bin/env python3
"""Session 69: the page fixture for /storage/buildout, cut from the scratch table (real values, nothing made up).

    python tests/fixtures/session69/make_fixture.py [path to storage_buildout_monthly.csv]

Keeps the table's header and the rows of the months the page reads: every December, the newest month and the month
twelve before it. Writes tests/fixtures/session69/storage_buildout_monthly.csv. The site's tests and the local
stand-in for Supabase (site/scripts/buildout-stub.mjs) read it; no page code does.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "runs", "session69", "storage_buildout_monthly", "storage_buildout_monthly.csv")
with open(src, encoding="utf-8") as f:
    lines = f.read().splitlines()
head = [ln for ln in lines if ln.startswith("#")]
cols, rows = lines[len(head)], lines[len(head) + 1:]
ts = cols.split(",").index("ts_utc")
months = sorted({r.split(",")[ts][:7] for r in rows})
newest = months[-1]
before = f"{int(newest[:4]) - 1}{newest[4:]}"
keep = {m for m in months if m.endswith("-12")} | {newest, before}
out = [r for r in rows if r.split(",")[ts][:7] in keep]
note = (f"# Fixture (session 69): {len(out)} of the table's {len(rows)} rows, the months {', '.join(sorted(keep))}; "
        "cut by tests/fixtures/session69/make_fixture.py from the scratch table, values unchanged")
with open(os.path.join(HERE, "storage_buildout_monthly.csv"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(head + [note, cols] + out) + "\n")
print(f"fixture: {len(out)} rows, months {sorted(keep)}")
