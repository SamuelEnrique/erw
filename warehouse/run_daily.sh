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
#   Session 28: after coverage, the archive step (warehouse/archive/archive.py write) appends every
#   table's new or changed rows to warehouse/archive/<table>/<YYYY-MM>.csv and the private Supabase
#   storage bucket erw-archive, before anything rewrites a shared store. If it fails, the Redivis
#   upload is skipped, so the draft is never rewritten while the rows are not recoverable elsewhere.
#   Session 28: uploads are routed by license (public tables to energy_research_warehouse, internal
#   ones to the private energy_research_warehouse_internal), and upload.py --check-license, after the
#   upload, fails the run if any internal table is in the public dataset.
#   Session 28: MODEL_STEPS=0 skips the seven steps that call the Claude API (scoring, extraction, reads, the
#   fun fact and the digest) and SEND_EMAIL=0 skips the email, each recorded as skipped: for a local run of the
#   sequence that must spend nothing and send nothing. CI never sets them.
#   Session 29: 54 tables became 6 consolidated tables (docs/migrations/2026-09-29-consolidation.md). After the restore,
#   warehouse/consolidate.py split writes their members for the connectors; after the last connector, build writes the
#   consolidated tables back and moves the members to warehouse/output/members/. Either failing stops the run.
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
# Session 26: the site's chat spec must be regenerated after every change to package/llms.txt (ARCHITECTURE.md);
# a stale spec fails the run before anything is pulled
"$PYTHON" warehouse/chat/check_spec.py || { echo "stopping: regenerate site/lib/chat/spec.json first"; exit 1; }
if [ "${RESTORE_FROM_REDIVIS:-0}" = "1" ]; then
  echo "== restore rolling-window tables from the Redivis draft (session 10)"
  "$PYTHON" warehouse/redivis/upload.py --restore || {
    echo "restore from Redivis failed: stopping, so a partial window is never uploaded over a full one"
    exit 1
  }
fi
# Session 29: the consolidated tables (warehouse/metadata/table_migrations.csv) hold what used to be 54 tables. The
# connectors still read and write those members, so they are written back out of the consolidated tables first,
# and consolidated again after the last connector (below). A failed split stops the run: a connector must never
# merge its window into a member that lost its history.
echo "== split the consolidated tables into their members (session 29)"
"$PYTHON" warehouse/consolidate.py split || { echo "stopping: consolidate.py split failed"; exit 1; }
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
model_step() {
  # session 28: model_step <name> <command...>: a step that calls the Claude API. With MODEL_STEPS=0 (a local test
  # run that must spend nothing) it is skipped and recorded as skipped; CI never sets it
  if [ "${MODEL_STEPS:-1}" = "0" ]; then
    echo "$1 skipped: MODEL_STEPS=0 (no model calls in this run)" >> "$status"
    echo "$1: skipped, MODEL_STEPS=0"
  else
    run_other "$@"
  fi
}
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
# Session 31: EIA-930 battery storage (fuel type BAT), merged into its history like EIA-930 demand; its daily cycle
# runs after CAISO's own battery series below (session 34) (docs/methods/storage.md)
run_other eia930_storage "$PYTHON" warehouse/connectors/eia930_storage.py --days "$DAYS"
# Session 32: EIA-930 CO2 estimates from EIA's per-BA workbooks (the newest workbook per BA; the last $DAYS days merged
# on (entity, variable, ts_utc); the raw copy kept), then carbon intensity (docs/methods/emissions.md)
run_other eia930_emissions "$PYTHON" warehouse/connectors/eia930_emissions.py --days "$DAYS"
run_other carbon_intensity "$PYTHON" warehouse/derived/carbon_intensity.py
# Session 49 (session 42's A2): EIA-930 interchange, every BA pair EIA reports, merged into its history like the other
# EIA-930 tables (the last $DAYS days pulled again), then the grid network's tables and the /network snapshot
# site/data/grid_network.json (docs/methods/grid_network.md)
run_other eia930_interchange "$PYTHON" warehouse/connectors/eia930_interchange.py --days "$DAYS"
run_other grid_network "$PYTHON" warehouse/derived/grid_network.py

# Session 24: NWS weather at one airport per ISO load center: hourly observations (the API serves about 7 days;
# the table grows by merging) and the 7-day hourly forecast, for /grid's temperature overlay and degree days
run_other weather_nws "$PYTHON" warehouse/connectors/weather_nws.py

# EIA daily fuel spot prices, full history each run (small)
run_other eia_fuels "$PYTHON" warehouse/connectors/eia_fuels.py
# Session 19: the trader view (tool 24), from the ISO price tables above and Henry Hub
# (docs/methods/trader_view.md); SPP has no real-time table, PJM no price table
run_other trader_view "$PYTHON" warehouse/derived/trader_view.py

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
# Session 23: CAISO battery storage output (Today's Outlook, 5-minute), the last 30 days, for the Automated
# Analysis template storage_evening_peak (EIA-930 carries no battery series)
run_other caiso_outlook "$PYTHON" warehouse/connectors/caiso_outlook.py
# Session 31: the daily cycle of battery storage from eia930_all_storage; session 34: with CAISO's rows from
# caiso_battery_storage (above), so it runs after both (docs/methods/storage.md)
run_other storage_daily_cycle "$PYTHON" warehouse/derived/storage_daily_cycle.py

# Session 8 entities. EIA-860M generator inventory: runs every day, writes only when EIA's
# newest published monthly vintage differs from the one in the tables (a monthly cadence).
run_other eia860 "$PYTHON" warehouse/connectors/eia860.py
# ISO interconnection queues: weekly, on Mondays (UTC), or any day with QUEUES=1
if [ "$(date -u +%u)" = "1" ] || [ "${QUEUES:-0}" = "1" ]; then
  run_other iso_queues "$PYTHON" warehouse/connectors/iso_queues.py
  # Session 17: ERCOT large-load requests. ERCOT publishes no request-level list (the status report
  # aggregates, Protocol 3.2.7); this watches its Large Load Integration page and fails loudly until one appears
  run_other ercot_large_load "$PYTHON" warehouse/connectors/ercot_large_load.py
  # Session 22: the datacenter operators' own site lists (nine connectors), weekly with the queues
  run_other datacenter_operators "$PYTHON" warehouse/datacenters/operators/run.py
else
  echo "iso_queues: weekly (Mondays UTC); skipped today, QUEUES=1 to force"
fi
# Session 16: the project map table (tool 3), derived from the EIA-860M inventories and the six
# queues, geocoded with the Census county gazetteer (docs/methods/energy_projects.md). In CI the
# queues exist only on the days they are pulled; other days it skips with a warning.
run_other energy_projects "$PYTHON" warehouse/derived/energy_projects.py
# Session 31: the battery units of the EIA-860M tables (storage_capacity); skips when the runner has no EIA-860M tables
run_other storage_capacity "$PYTHON" warehouse/derived/storage_capacity.py

# News (session 6): ingest the feeds, then score new stories with the Claude API
# (ANTHROPIC_API_KEY). The digest is written after validation and coverage, below.
run_other news_ingest "$PYTHON" warehouse/news/ingest.py
model_step news_score "$PYTHON" warehouse/news/score.py
# Session 30 (B4): the Haiku shadow scorer scores the same stories into news_scores_shadow (internal), only while
# SHADOW_MODEL is set (the workflow sets it; unsetting it is the kill switch) and before the expiry date in
# warehouse/config/shadow.yaml; otherwise it prints SKIPPED and spends nothing
model_step news_score_shadow "$PYTHON" warehouse/news/shadow.py score
run_other news_index "$PYTHON" warehouse/news/index.py   # public companion table (session 7)
# Session 24: policy actions (tool 12): the Federal Register, NRC, DOE, PUCT and CPUC, linked to the scored news,
# then scored with the news rubric and read for impact (warehouse/policy/)
run_other policy_sources "$PYTHON" warehouse/connectors/policy_sources.py
model_step policy_score "$PYTHON" warehouse/policy/score.py
model_step policy_reads "$PYTHON" warehouse/policy/reads.py
# Session 15: deals from the newly scored stories (warehouse/deals/extract.py, tool 6)
model_step deals "$PYTHON" warehouse/deals/extract.py
# Session 27: every party of energy_deals is a row of energy_companies (tool 10), merged with the Thesis Builder's rows
run_other companies_from_deals "$PYTHON" warehouse/companies/seed_from_deals.py
# Session 16: datacenter facilities from the newly scored datacenter_power stories (tool 4)
model_step datacenters "$PYTHON" warehouse/datacenters/extract.py
# Session 22: the tracker's one table: the news facilities, the operator sites and the queue rows that
# name a datacenter or large load, deduplicated by operator plus location (docs/methods/datacenter_facilities.md)
run_other datacenter_facilities "$PYTHON" warehouse/derived/datacenter_facilities.py

# Session 29: the members back into their consolidated tables; the members move to warehouse/output/members/, where
# nothing below looks. A failed build stops the run before the validator: the old names must never be uploaded again.
echo "== build the consolidated tables from their members (session 29)"
if "$PYTHON" warehouse/consolidate.py build > runs/daily_consolidate.out 2>&1; then
  grep -E "^built|left as it is|consolidate build" runs/daily_consolidate.out
  echo "consolidate ok" >> "$status"
else
  cat runs/daily_consolidate.out
  echo "consolidate failed: $(grep -m1 FAILED runs/daily_consolidate.out)" >> "$status"
  "$PYTHON" warehouse/metadata/run_status.py record
  echo "stopping: consolidate.py build failed (runs/daily_consolidate.out)"
  exit 1
fi
# Session 49: the main hubs' price history (iso_hub_prices_history, from 2025-09-01, restored from the draft) takes the
# consolidated live tables' rows of its hubs, so it keeps growing past their rolling window. Never in Supabase.
run_other hub_history "$PYTHON" warehouse/connectors/hub_history.py append
# Session 30 (Part A): price board v2, four derived tables from the consolidated price tables, the EIA fuels and the
# carbon auctions (docs/methods/price_board.md). On the runner, the rows built from the ERCOT history (never restored)
# and from CARB (a known gap there) are carried from the last run's tables, restored from the draft, and said so
run_other price_board "$PYTHON" warehouse/derived/price_board.py

echo "== connector status"
cat "$status"
"$PYTHON" warehouse/metadata/run_status.py record || exit 1

echo "== validator"
# session 36A: the reports are kept as JSON (runs/validate_reports.json) for coverage to reuse, and summarized here:
# every file's verdict, and each error and warning in full
: > runs/validate_reports.json.started  # the validator's start: coverage reuses a report only for files older than this
"$PYTHON" warehouse/validate/erw_validate.py --json warehouse/output/*.csv > runs/validate_reports.json
vrc=$?
"$PYTHON" -c "
import json
for r in json.load(open('runs/validate_reports.json', encoding='utf-8')):
    print(r['file'], r['verdict'].upper(), r.get('detail', ''))
    for e in r.get('errors', []): print('  ERROR [' + e['check'] + '] ' + e['detail'])
    for w in r.get('warnings', []): print('  warn  [' + w['check'] + '] ' + w['detail'])
" || echo "validator reports unreadable (runs/validate_reports.json)"
if [ "$vrc" -ne 0 ]; then
  echo "erw_validate exit $vrc: at least one table is blocked; stopping before coverage and commit"
  exit 1
fi

echo "== coverage"
"$PYTHON" warehouse/metadata/build_coverage.py --reports runs/validate_reports.json || exit 1

echo "== archive (session 28): new or changed rows to warehouse/archive and the bucket erw-archive"
if [ "${DRY_STORES:-0}" = "1" ]; then
  run_other archive "$PYTHON" warehouse/archive/archive.py write --no-bucket
else
  run_other archive "$PYTHON" warehouse/archive/archive.py write
fi

echo "== Supabase live set (session 10; warehouse/supabase/live_set.yaml)"
if [ "${DRY_STORES:-0}" = "1" ]; then
  run_other supabase_load "$PYTHON" warehouse/supabase/load.py --dry-run
else
  run_other supabase_load "$PYTHON" warehouse/supabase/load.py
fi

echo "== Energy Digest (docs/digest/), Monday to Friday"
# Session 23: the digest is written Monday to Friday only (UTC). On Saturday and Sunday brief.py and
# email_digest.py --auto print "SKIPPED: no weekend issue" and write nothing; the weekend's stories open
# Sunday's Energy Roundup (.github/workflows/roundup.yml, Sundays 23:00 UTC), which also sends it.
# Session 23: the fun fact engine adds one verified fact to warehouse/news/facts/bank.csv and writes the day's
# item (warehouse/news/facts/items/<date>.json); brief.py re-verifies it and prints it as the digest's last section
model_step news_funfact "$PYTHON" warehouse/news/funfact.py
model_step news_brief "$PYTHON" warehouse/news/brief.py
# Session 19: the digest by email (tool 25). Rendered to docs/digest/email/ always; sent through
# Resend only when RESEND_API_KEY and DIGEST_RECIPIENTS are set
if [ "${SEND_EMAIL:-1}" = "0" ]; then
  # session 28: a local test run sends no email to anyone; CI never sets it
  echo "news_email skipped: SEND_EMAIL=0 (nothing sent)" >> "$status"
  echo "news_email: skipped, SEND_EMAIL=0"
else
  run_other news_email "$PYTHON" warehouse/news/email_digest.py --auto
fi
# Session 30 (B4): the shadow Digest from the shadow scores, to the shadow recipient only, subject "SHADOW HAIKU"
# (weekdays, until the expiry in warehouse/config/shadow.yaml, while SHADOW_MODEL is set); SEND_EMAIL=0 writes it only
model_step news_digest_shadow "$PYTHON" warehouse/news/shadow.py digest $([ "${SEND_EMAIL:-1}" = "0" ] && echo --no-send)
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
elif ! grep -q "^archive ok" "$status"; then
  # session 28: the upload deletes and recreates draft tables; not while this run's rows are unarchived
  echo "redivis_upload failed: skipped because the archive step failed" >> "$status"
  echo "redivis_upload: skipped, the archive step failed (runs/daily_archive.out)"
else
  run_other redivis_upload "$PYTHON" warehouse/redivis/upload.py --changed
fi
if [ "${DRY_STORES:-0}" != "1" ]; then
  # session 28 (review item 3): no table licensed internal may be in the public dataset; if one is, the run fails
  echo "== Redivis: license check (internal tables only in energy_research_warehouse_internal)"
  "$PYTHON" warehouse/redivis/upload.py --check-license || {
    echo "redivis_license failed: an internal table is in the public dataset" >> "$status"
    echo "stopping: an internal table is in the public Redivis dataset (upload.py --check-license --fix moves it)"
    exit 1
  }
fi

echo "== done"
