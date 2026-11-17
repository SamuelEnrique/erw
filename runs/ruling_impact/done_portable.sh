#!/usr/bin/env bash
# Session 7611 on (portable-laptop): mark a tool done, commit its impact file and script, push.
# usage: bash runs/ruling_impact/done_portable.sh "/tool" SESSION slug
set -e
cd "$(dirname "$0")/../.."
tool="$1"; session="$2"; slug="$3"
git pull -q --no-rebase --no-edit origin main
python_bin=".venv/Scripts/python.exe"
"$python_bin" runs/ruling_impact/mark_done.py "$tool" "$session"
git add docs/state/ruling_impact_claims.md "docs/reviews/ruling-impact-${slug}-2026-11-17.md"
git add -f runs/ruling_impact/${slug}_impact.py runs/ruling_impact/${slug}_impact.out
git commit -q -m "Session ${session}: ruling impact of ${tool}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git pull -q --no-rebase --no-edit origin main
git push -q origin main
echo "done ${tool}"
grep -F "| ${tool} |" docs/state/ruling_impact_claims.md
