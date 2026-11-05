#!/bin/bash
# session 2403 (chain 088): screenshots of the chain's eleven pages at 1280 by 900 and 390 by 844 from a local build of
# wip/2400-policy-games served on the port given, under docs/brand/review-<N>/. node scripts/shot.mjs <url> <out.png> [w] [h]
BASE=${1:-http://localhost:32404}
OUT=${2:-/c/Users/samen/Documents/erw/docs/brand/review-2404}
mkdir -p "$OUT"
cd /c/Users/samen/Documents/erw-823/site || exit 2
shot() { node scripts/shot.mjs "$BASE$1" "$OUT/$2_$3.png" $3 $4 "$5" || echo "shot failed: $1 at $3"; }
for v in "1280 900" "390 844"; do
  set -- $v
  W=$1; H=$2
  shot "/policy" policy $W $H "[data-policy-shown]"
  shot "/policy?view=week" policy-week $W $H "[data-week-foot]"
  shot "/policy?view=week&agency=vascc" policy-week-vascc $W $H "[data-week-foot]"
  shot "/play/battery" play-battery $W $H ""
  shot "/play/battery?mode=hard" play-battery-hard $W $H ""
  shot "/play/ev" play-ev $W $H "[data-ev-step]"
  shot "/learn/bill" learn-bill $W $H ""
  shot "/learn/problems/know-your-grid" problems-know-your-grid $W $H ""
  shot "/learn/problems/prices-and-your-bill" problems-prices-and-your-bill $W $H ""
  shot "/learn/problems/when-the-grid-broke" problems-when-the-grid-broke $W $H ""
  shot "/learn/problems/storage-and-taxes" problems-storage-and-taxes $W $H ""
  shot "/learn/problems/networks-and-money" problems-networks-and-money $W $H ""
done
echo SHOTS_DONE
