#!/usr/bin/env bash
# Energy Research Warehouse (ERW) daily refresh: ISO prices, EIA-930, EIA fuels.
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
#   1. every connector (ISO prices, EIA-930 demand and generation, EIA fuel
#      prices), then news ingest and scoring, for the last $DAYS complete
#      operating days (news: the last 2 days of stories). Each
#      market is written only if complete, and merges into its existing file:
#      new intervals are appended, intervals already present for the same
#      (entity, variable, ts_utc) are replaced, nothing is duplicated.
#      A failed market is recorded and the run continues with the others.
#   2. erw_validate on every file in warehouse/output. Any blocked file ends
#      the run with exit 1, before coverage is rebuilt or anything committed.
#   3. warehouse/metadata/build_coverage.py regenerates docs/coverage.md and
#      warehouse/metadata/coverage.csv; then warehouse/news/brief.py writes the
#      Energy Digest to docs/digest/<date>.md and docs/digest/latest.md.
#   Also, from the session 5 rulings: each connector's per-table status is
#   appended to the tracked warehouse/metadata/run_status.csv (before the
#   validator, so a failing day is still on record); markets that failed the
#   last 3 runs are listed in runs/failure_streaks.txt for the workflow to open
#   an issue; raw files older than 14 days are pruned (manifests kept).
#   Session 10: (0) with RESTORE_FROM_REDIVIS=1 (the workflow sets it), the
#   rolling-window tables missing locally are first restored from the Redivis
#   draft, so a fresh CI checkout merges into the full tables; a failed restore
#   stops the run. (4) After the validator and coverage, the Supabase live set is
#   loaded (warehouse/supabase/load.py). (5) Last, the tables this run changed
#   are uploaded to the Redivis draft (warehouse/redivis/upload.py --changed);
#   nothing is ever released.
#   Session 14: DRY_STORES=1 runs the same sequence but writes to no shared store:
#   the Supabase load runs with --dry-run and the Redivis upload lists what it
#   would upload. For testing the workflow logic in a fresh clone; CI never sets it.
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
rm -f runs/status/*.json runs/failure_streaks.txt  # this run's status only

echo "== ERW daily refresh $(date -u +%FT%TZ): ISOs: $ISOS; days: $DAYS"
if [ "${RESTORE_FROM_REDIVIS:-0}" = "1" ]; then
  echo "== restore rolling-window tables from the Redivis draft (session 10)"
  "$PYTHON" warehouse/redivis/upload.py --restore || {
    echo "restore from Redivis failed: stopping, so a partial window is never uploaded over a full one"
    exit 1
  }
fi
for iso in $ISOS; do
  out="runs/daily_${iso}.out"
  "$PYTHON" warehouse/connectors/iso_prices.py "$iso" --days "$DAYS" > "$out" 2>&1
  rc=$?
  grep -E "\.csv: rows=|FAILED|run log:" "$out" | grep -vE " - (INFO|DEBUG|WARNING) - "
  failed=$(grep -oE "^${iso} (DAM|RTM|RTM_HOURLY) FAILED" "$out" | awk '{print $2}' | sort -u | tr '\n' ' ' | sed 's/ $//')
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
  grep -E "\.csv: rows=|FAILED|SKIPPED|run log:" "$out" | grep -vE " - (INFO|DEBUG|WARNING) - "
  if [ "$rc" -eq 0 ] && grep -q "^${name} SKIPPED" "$out"; then
    # session 10 ruling 3: a derived script without its inputs in CI skips with a warning
    echo "$name skipped: $(grep -m1 "^${name} SKIPPED" "$out" | sed "s/^${name} SKIPPED: //")" >> "$status"
  elif [ "$rc" -eq 0 ]; then
    echo "$name ok" >> "$status"
  else
    failed=$(grep -oE "^${name} [a-z0-9_]+ FAILED" "$out" | awk '{print $2}' | sort -u | tr '\n' ' ' | sed 's/ $//')
    echo "$name failed: ${failed:-connector exit $rc}" >> "$status"
    [ -z "$failed" ] && tail -20 "$out"
  fi
}

# Derived (session 9): ERCOT peak premium metrics from the ERCOT real-time history and live
# tables, right after the ERCOT connector (docs/methods/ercot_peak_premium.md). It needs the
# yearly history tables, which are not in git (warehouse/output/README.md). In CI they are
# absent, so it skips with a warning (session 10 ruling 3); locally, missing inputs fail loudly.
run_other ercot_peak_premium "$PYTHON" warehouse/derived/ercot_peak_premium.py

# EIA-930 hourly demand and generation (EIA_API_KEY from the environment or .env)
run_other eia930 "$PYTHON" warehouse/connectors/eia930.py --days "$DAYS"

# EIA daily fuel spot prices, full history each run (small)
run_other eia_fuels "$PYTHON" warehouse/connectors/eia_fuels.py

# EIA refined products, retail fuels, weekly trade and stocks, LNG exports by terminal
# (session 7), full history each run
run_other eia_series "$PYTHON" warehouse/connectors/eia_series.py
# Session 18: the energy mix explorer (tool 21): EIA-923 generation by state (eia_series, above)
# grouped by fuel (docs/methods/generation_mix.md)
run_other generation_mix "$PYTHON" warehouse/derived/generation_mix.py

# Session 7 price board: PJM RPM capacity prices (internal), CARB and RGGI carbon
# auctions (internal), FRED series without a key (public domain daily; IMF monthly internal)
run_other capacity_prices "$PYTHON" warehouse/connectors/capacity_prices.py
run_other carbon_auctions "$PYTHON" warehouse/connectors/carbon_auctions.py
run_other fred_series "$PYTHON" warehouse/connectors/fred_series.py
# IMF PortWatch daily chokepoint transits (session 8; internal until terms are confirmed)
run_other portwatch "$PYTHON" warehouse/connectors/portwatch.py
# Session 18: the curtailment tracker (tool 22): CAISO and SPP curtailment, ERCOT output below HSL,
# the latest days (the history is restored from Redivis first), then the monthly sums
# (docs/methods/curtailment.md)
run_other curtailment "$PYTHON" warehouse/connectors/curtailment.py
run_other iso_curtailment_monthly "$PYTHON" warehouse/derived/iso_curtailment_monthly.py

# Session 8 entities. EIA-860M generator inventory: runs every day, writes only when EIA's
# newest published monthly vintage differs from the one in the tables (a monthly cadence).
run_other eia860 "$PYTHON" warehouse/connectors/eia860.py
# ISO interconnection queues: weekly, on Mondays (UTC), or any day with QUEUES=1
if [ "$(date -u +%u)" = "1" ] || [ "${QUEUES:-0}" = "1" ]; then
  run_other iso_queues "$PYTHON" warehouse/connectors/iso_queues.py
  # Session 17: ERCOT large-load requests. ERCOT publishes no request-level list (the status report
  # aggregates, Protocol 3.2.7); this watches its Large Load Integration page and fails loudly until one appears
  run_other ercot_large_load "$PYTHON" warehouse/connectors/ercot_large_load.py
else
  echo "iso_queues: weekly (Mondays UTC); skipped today, QUEUES=1 to force"
fi
# Session 16: the project map table (tool 3), derived from the EIA-860M inventories and the six
# queues, geocoded with the Census county gazetteer (docs/methods/energy_projects.md). In CI the
# queues exist only on the days they are pulled; other days it skips with a warning.
run_other energy_projects "$PYTHON" warehouse/derived/energy_projects.py

# News (session 6): ingest the feeds, then score new stories with the Claude API
# (ANTHROPIC_API_KEY). The digest is written after validation and coverage, below.
run_other news_ingest "$PYTHON" warehouse/news/ingest.py
run_other news_score "$PYTHON" warehouse/news/score.py
run_other news_index "$PYTHON" warehouse/news/index.py   # public companion table (session 7)
# Session 15: deals from the newly scored stories (warehouse/deals/extract.py, tool 6)
run_other deals "$PYTHON" warehouse/deals/extract.py
# Session 16: datacenter facilities from the newly scored datacenter_power stories (tool 4)
run_other datacenters "$PYTHON" warehouse/datacenters/extract.py

echo "== connector status"
cat "$status"
"$PYTHON" warehouse/metadata/run_status.py record || exit 1

echo "== validator"
"$PYTHON" warehouse/validate/erw_validate.py warehouse/output/*.csv
vrc=$?
if [ "$vrc" -ne 0 ]; then
  echo "erw_validate exit $vrc: at least one table is blocked; stopping before coverage and commit"
  exit 1
fi

echo "== coverage"
"$PYTHON" warehouse/metadata/build_coverage.py || exit 1

echo "== Supabase live set (session 10; warehouse/supabase/live_set.yaml)"
if [ "${DRY_STORES:-0}" = "1" ]; then
  run_other supabase_load "$PYTHON" warehouse/supabase/load.py --dry-run
else
  run_other supabase_load "$PYTHON" warehouse/supabase/load.py
fi

echo "== Energy Digest (docs/digest/)"
run_other news_brief "$PYTHON" warehouse/news/brief.py
"$PYTHON" warehouse/metadata/run_status.py record || exit 1

echo "== STATUS.md (session 14): tables, last runs, open gaps"
run_other build_status "$PYTHON" warehouse/metadata/build_status.py

echo "== failure streaks (3 runs in a row)"
"$PYTHON" warehouse/metadata/run_status.py streaks --n 3 || exit 1

echo "== prune raw files older than 14 days (manifests kept)"
"$PYTHON" warehouse/prune_raw.py --days 14 || exit 1

echo "== Redivis: upload the tables this run changed, to the draft only (session 10)"
if [ "${DRY_STORES:-0}" = "1" ]; then
  run_other redivis_upload "$PYTHON" warehouse/redivis/upload.py --changed --dry-run
else
  run_other redivis_upload "$PYTHON" warehouse/redivis/upload.py --changed
fi

echo "== done"
