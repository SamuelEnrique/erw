#!/usr/bin/env bash
# Mark a tool done, commit its impact file and script, push.
# usage: bash runs/ruling_impact/done.sh "/tool" SESSION slug
set -e
cd "$(dirname "$0")/../.."
tool="$1"; session="$2"; slug="$3"
sed -i "s#^| ${tool} | samueloldlaptop | ${session} | claimed |#| ${tool} | samueloldlaptop | ${session} | done |#" docs/state/ruling_impact_claims.md
git add docs/state/ruling_impact_claims.md "docs/reviews/ruling-impact-${slug}-2026-11-17.md"
git add -f runs/ruling_impact/${slug}_impact.py runs/ruling_impact/${slug}_impact.out
git commit -q -m "Session ${session}: ruling impact of ${tool}

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git pull -q --no-rebase origin main
git push -q origin main
echo "done ${tool}"
grep "^| ${tool} |" docs/state/ruling_impact_claims.md
