#!/bin/sh
# Session 10206: draws /cost-of-power on each words branch of the datacenter audit (detached in this worktree), then
# compares it with origin/main's drawing. Returns the worktree to wip/audit-board-doc at the end.
cd /c/Users/lossa/Documents/erw-c710-b || exit 2
PY=/c/Users/lossa/Documents/erw/.venv/Scripts/python.exe
for n in 1 2 3 5 6; do
  git checkout -q --detach origin/wip/audit-datacenter-$n || exit 3
  echo "##### branch wip/audit-datacenter-$n at $(git rev-parse --short HEAD)"
  (cd site && node --import ./scripts/tsx-register.mjs ../runs/c10206/draw_dc.mjs ../runs/c10206/tables ../runs/c10206/draw/b$n > ../runs/c10206/draw_b$n.out 2>&1; echo "draw exit=$?")
  ERW_SPEND_CAP_USD=0 $PY runs/c10206/compare_draw.py runs/c10206/draw/main runs/c10206/draw/b$n
done
git checkout -q wip/audit-board-doc
git status --short | head -5
