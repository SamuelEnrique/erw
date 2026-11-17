#!/usr/bin/env bash
# Claim a tool in docs/state/ruling_impact_claims.md, commit and push the claim alone.
# usage: bash runs/ruling_impact/claim.sh "/tool" SESSION slug
# exit 3 when the tool is already claimed by any machine.
set -e
cd "$(dirname "$0")/../.."
tool="$1"; session="$2"; slug="$3"
git pull -q --no-rebase origin main
if grep -q "^| ${tool} |" docs/state/ruling_impact_claims.md; then
  echo "already claimed: ${tool}"
  grep "^| ${tool} |" docs/state/ruling_impact_claims.md
  exit 3
fi
echo "| ${tool} | samueloldlaptop | ${session} | claimed | docs/reviews/ruling-impact-${slug}-2026-11-17.md |" >> docs/state/ruling_impact_claims.md
git add docs/state/ruling_impact_claims.md
git commit -q -m "Session ${session}: ${tool} claimed in the ruling impact claims file

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git push -q origin main
echo "claimed ${tool} as session ${session}"
