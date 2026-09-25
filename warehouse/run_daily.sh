#!/usr/bin/env bash
# Energy Research Warehouse (ERW) daily price refresh.
#
# The exact sequence .github/workflows/daily-prices.yml runs, kept in one
# script so that a local run and the scheduled run cannot drift apart
# (ARCHITECTURE.md, rule 2). The workflow adds only the commit and push.
#
#   bash warehouse/run_daily.sh                 # all ISOs, last 3 operating days
#   DAYS=30 bash warehouse/run_daily.sh
#   PYTHON=.venv/Scripts/python bash warehouse/run_daily.sh
#
# Steps:
#   1. every ISO connector for the last $DAYS complete operating days. Each
#      market is written only if complete, and merges into its existing file:
#      new intervals are appended, intervals already present for the same
#      (entity, variable, ts_utc) are replaced, nothing is duplicated.
#      A failed market is recorded and the run continues with the others.
#   2. erw_validate on every file in warehouse/output. Any blocked file ends
#      the run with exit 1, before coverage is rebuilt or anything committed.
#   3. warehouse/metadata/build_coverage.py regenerates docs/coverage.md and
#      warehouse/metadata/coverage.csv.
#
# Writes runs/daily_status.txt (gitignored): one line per ISO, used by the
# workflow for its commit message.

set -uo pipefail

PYTHON="${PYTHON:-python}"
DAYS="${DAYS:-3}"
ISOS="${ISOS:-ercot caiso nyiso miso spp isone}"

cd "$(dirname "$0")/.."
mkdir -p runs
status=runs/daily_status.txt
: > "$status"

echo "== ERW daily refresh $(date -u +%FT%TZ): ISOs: $ISOS; days: $DAYS"
for iso in $ISOS; do
  out="runs/daily_${iso}.out"
  "$PYTHON" warehouse/connectors/iso_prices.py "$iso" --days "$DAYS" > "$out" 2>&1
  rc=$?
  grep -E "\.csv: rows=|FAILED|run log:" "$out" | grep -vE " - (INFO|DEBUG|WARNING) - "
  failed=$(grep -oE "^${iso} (DAM|RTM) FAILED" "$out" | awk '{print $2}' | sort -u | tr '\n' ' ' | sed 's/ $//')
  if [ "$rc" -eq 0 ]; then
    echo "$iso ok" >> "$status"
  elif [ -n "$failed" ]; then
    echo "$iso failed: $failed" >> "$status"
  else
    echo "$iso failed: connector exit $rc" >> "$status"
    tail -20 "$out"
  fi
done
run_other() {
  # run_other <name> <command...>: a non-ISO connector, recorded like an ISO
  local name="$1"; shift
  local out="runs/daily_${name}.out"
  "$@" > "$out" 2>&1
  local rc=$?
  grep -E "\.csv: rows=|FAILED|run log:" "$out" | grep -vE " - (INFO|DEBUG|WARNING) - "
  if [ "$rc" -eq 0 ]; then
    echo "$name ok" >> "$status"
  else
    failed=$(grep -oE "^${name} [a-z0-9_]+ FAILED" "$out" | awk '{print $2}' | sort -u | tr '\n' ' ' | sed 's/ $//')
    echo "$name failed: ${failed:-connector exit $rc}" >> "$status"
    [ -z "$failed" ] && tail -20 "$out"
  fi
}

# EIA-930 hourly demand and generation (EIA_API_KEY from the environment or .env)
run_other eia930 "$PYTHON" warehouse/connectors/eia930.py --days "$DAYS"

echo "== connector status"
cat "$status"

echo "== validator"
"$PYTHON" warehouse/validate/erw_validate.py warehouse/output/*.csv
vrc=$?
if [ "$vrc" -ne 0 ]; then
  echo "erw_validate exit $vrc: at least one table is blocked; stopping before coverage and commit"
  exit 1
fi

echo "== coverage"
"$PYTHON" warehouse/metadata/build_coverage.py || exit 1

echo "== done"
