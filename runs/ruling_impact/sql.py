"""Session 7611 (portable-laptop): run one read-only SQL statement on the live set and print the rows (exploration only).

    .venv/Scripts/python.exe runs/ruling_impact/sql.py "select ..."
"""
import sys

sys.path.insert(0, __file__.rsplit("\\", 1)[0].rsplit("/", 1)[0])
from live import q  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
for row in q(sys.argv[1]):
    print(" | ".join("" if v is None else str(v) for v in row))
