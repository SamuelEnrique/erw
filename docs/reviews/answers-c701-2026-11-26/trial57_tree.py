"""Make a trial folder of hard links to warehouse/output's top-level files (chain 701, request 57). Subfolders are linked
file by file too. Costs no disk space; a writer's rename over a link leaves main's file as it was.

    .venv/Scripts/python.exe runs/c701/trial57_tree.py runs/c701/trial57/before
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
src = os.path.join(ROOT, "warehouse", "output")
dst = os.path.abspath(sys.argv[1])
n = 0
for dirpath, dirs, files in os.walk(src):
    rel = os.path.relpath(dirpath, src)
    if rel.split(os.sep)[0] == "retired":
        continue
    os.makedirs(os.path.join(dst, rel), exist_ok=True)
    for f in files:
        t = os.path.join(dst, rel, f)
        if not os.path.exists(t):
            os.link(os.path.join(dirpath, f), t)
            n += 1
print(f"{n} links made under {dst}")
