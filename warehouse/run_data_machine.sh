#!/usr/bin/env bash
# Energy Research Warehouse (ERW), session 149: the data machine's daily run.
#
# What the GitHub runner cannot do, once a day, on the machine that holds the price histories and the saved workbooks
# (docs/machines.md: a machine whose role is "data" and whose warehouse/output holds the ERCOT price history):
#
#   1. sync: main fast-forwarded, and every table that is behind the Redivis draft brought up to it (scripts/sync.py:
#      a table that is ahead here, or has diverged, is reported and left), so the day's prices from the runner are in;
#   1c. (session 206, the owner's ruling of 12 October 2026) the publishers that refuse GitHub's runner, asked from here
#      once a day: CARB's auction summary (carb_auction_allowance_prices), CARB's LCFS credit prices
#      (carb_lcfs_credit_prices) and Oregon's docket lists (policy_monitor_refresh.py --only orpuc, into the two
#      large-load rule tables). On the runner each is a known gap recorded as skipped (warehouse/metadata/known_gaps.csv).
#      A table that moved gets its stores, as the node prices do;
#   1b. ERCOT's node prices (ercot_rtm_node_prices; session 204, the owner's ruling of 12 October 2026): the real-time
#      Settlement Point Prices at the storage resources' points, the hubs and the Load Zones, NP6-905-CD, through
#      warehouse/scheduled.py. ERCOT's list keeps seven days and no more, so a day not pulled within the week is not
#      held at all. The list is asked each day, and a file only when this machine has not saved it (96 a day). The
#      ceiling is 500,000 rows a UTC day, counted as each file is saved; the request that could pass it is not made.
#      The table is internal: no page reads it and it is in no live set. A soft step, before ERCOT's load zones and
#      never fatal to them. When the table moved: its stores (warehouse/table_stores.py: the validator and the
#      coverage row, each a gate for this table's stores only, then the archive and the Redivis draft);
#   2. ERCOT's load zone prices (ercot_zone_prices_history): the daily refresh the owner approved on 7 October 2026.
#      ERCOT's two lists are asked each day; a workbook only when the list names a document this machine does not
#      hold (ERCOT posts the current year again on Sundays). A row counts once against the ceiling of 3,000,000; the
#      count is in the step's log on every run, and the request that would pass the ceiling is refused before it is
#      made (warehouse/connectors/ercot_zone_prices.py --refresh). When rows were added: the validator (a gate), the
#      table's coverage row, the archive and the Redivis draft;
#   3. the page files that are rebuilt whole from the price histories, each under warehouse/health.py (a failure is
#      tried once more, recorded in erw_health and in the status file, and never stops the run):
#        datacenter_page      site/data/datacenter/              /cost-of-power          (session 138)
#        capture_price        site/data/seller/capture.json      /cost-of-power/seller   (session 145)
#        curtailment_shares   site/data/curtailment/shares.json  /curtailment            (session 144)
#        free_energy          site/data/curtailment/free_energy.json
#        curtailment_worth    site/data/curtailment/worth.json
#      and, where node is installed, each file's own test (a file whose test fails is put back as it was);
#      then (session 190) the replication CSV of /cost-of-power's default case, written again from the datacenter
#      files as they now stand (warehouse/derived/datacenter_hourly_export.py: it reads those files and no table, and
#      leaves the CSV as it was when no hour of the default case moved or when its own check fails);
#   3b. (session 204, the owner's rulings of 12 October 2026) the battery page's downloads, the generator page's
#      builders and its hourly CSV, each through warehouse/scheduled.py as a soft step:
#        battery_dispatch_export  site/public/battery/erw_2026_battery_dispatch.csv   /cost-of-power/battery (session 178)
#        battery_scenario_steps   site/data/battery_scenario_steps.json                                      (session 179)
#        merchant_revenue         site/data/merchant_snapshot.json, merchant_revenue_monthly  /cost-of-power/seller (session 51)
#        merchant_hubs            site/data/seller/hubs/                                                     (session 183)
#        seller_hybrid            site/data/seller/hybrid.json, site/public/seller/prices/                   (session 162)
#        generator_hourly_export  site/public/seller/erw_2026_generator_hourly.csv                           (session 183)
#      A battery file whose hours, months and model are as held is left as it is. merchant_revenue_monthly gets its
#      stores when it moved. Then each group's own tests, as the files above have theirs: a group one of whose steps
#      or tests failed is put back whole as the last commit has it (the snapshot, the hub files and the CSV are one
#      group: the CSV is checked against the snapshot, and the hub files against it), recorded, and the run goes on.
#      SWITCHED OFF, with GENERATOR=1 to run them: merchant_revenue, merchant_hubs and generator_hourly_export, until
#      the six tests that hold the CSV to its export of 7 October 2026 are changed (the note above the steps says which);
#   4. the commit: the page files and the metadata the refresh changed, committed to main and pushed, as a data task
#      is (docs/machines.md: "Data tasks do not use branches: they commit to main under the data lock").
#
# NOT here: site/data/curtailment/ercot.json. The runner builds it every day from the table it restores and refreshes
# (warehouse/run_daily.sh, session 144), and that table is newer there than on a data machine until the sync.
#
# IT REFUSES TO RUN ON THE GITHUB RUNNER. The runner holds no price history: a builder that rewrites its file from the
# tables on the machine would thin the file there. How it knows where it is, in this order: GITHUB_ACTIONS is "true"
# (GitHub sets it in every workflow job); the machine's role is not "data" (warehouse/lock.py role, .erw/machine.json);
# or one of the three price histories is not in warehouse/output. Any of the three: one line, nothing built, exit 0.
#
#   python warehouse/lock.py run --task "data machine daily" --wait 60 -- bash warehouse/run_data_machine.sh
#   bash warehouse/run_data_machine.sh --check      # say where this is and what would run; build, ask and write nothing
#
# The data lock is needed for the load zone table, the stores and the commit, so the whole run goes under
# warehouse/lock.py run, after the runner's daily run has released it (that run starts at 14:00 UTC and holds the lock
# until about 16:00). It is started by a person or by the machine's own scheduler (docs/machines.md, "The data
# machine's daily run"); nothing in the repository starts it, and no workflow calls it.
#
# COMMIT=0 builds and commits nothing. PUSH=0 commits and does not push. The commit is made only on the branch main,
# and only of the paths named below.
set -uo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
if [ -z "${PYTHON:-}" ]; then
  if [ -x "$ROOT/.venv/Scripts/python.exe" ]; then PYTHON="$ROOT/.venv/Scripts/python.exe"
  elif [ -x "$ROOT/.venv/bin/python" ]; then PYTHON="$ROOT/.venv/bin/python"
  else PYTHON=python; fi
fi
export PYTHON
CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1
HISTORIES="ercot_all_hub_prices_history ercot_zone_prices_history iso_zone_prices_history"
ZONES=ercot_zone_prices_history
PAGE_PATHS=(site/data/datacenter site/data/seller/capture.json site/data/curtailment/shares.json
            site/data/curtailment/free_energy.json site/data/curtailment/worth.json
            site/public/datacenter/erw_2026_datacenter_hourly.csv
            site/public/battery/erw_2026_battery_dispatch.csv site/data/battery_scenario_steps.json
            site/data/merchant_snapshot.json site/data/seller/hubs site/public/seller/erw_2026_generator_hourly.csv
            site/data/seller/hybrid.json site/public/seller/prices)
# session 204: the generator export's dated record of the capture file's build (docs/methods/figures/<day>/, session
# 199), committed with the CSV whose header names it, and only when the generator's group was not put back
RECORD_PATH=docs/methods/figures
META_PATHS=(warehouse/metadata/coverage.csv docs/coverage.md warehouse/metadata/sources.csv
            warehouse/metadata/archive_manifest.csv warehouse/metadata/redivis_uploads.csv)

# ---- where is this: the three refusals ------------------------------------------------------------------------------
if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
  echo "run_data_machine REFUSED: this is the GitHub runner (GITHUB_ACTIONS is true). It holds no price history and would thin the page files; nothing is built here."
  exit 0
fi
# lock.py role prints the machine's setting as JSON: {"name": "...", "role": "data"}
role="$("$PYTHON" warehouse/lock.py role 2>/dev/null | tr -d '\r' | sed -n -E 's/.*"role": *"([a-z]+)".*/\1/p')"
if [ "$role" != "data" ]; then
  echo "run_data_machine REFUSED: this machine's role is '${role:-not set}', not data (python warehouse/lock.py role); nothing is built here."
  exit 0
fi
missing=""
for t in $HISTORIES; do
  [ -f "warehouse/output/$t.csv" ] || missing="$missing $t"
done
if [ -n "$missing" ]; then
  echo "run_data_machine REFUSED: this machine does not hold the price histories:$missing (warehouse/output); nothing is built here."
  exit 0
fi
if [ "$CHECK" = "1" ]; then
  echo "run_data_machine: a data machine with the three price histories. It would run, in this order:"
  echo "  sync (scripts/sync.py); ERCOT's load zones (ercot_zone_prices.py --refresh) and, when rows were added, the validator, coverage, the archive and the Redivis draft;"
  echo "  datacenter_page, capture_price, curtailment_shares, free_energy, curtailment_worth, each under warehouse/health.py;"
  echo "  (session 204) first of all after the sync, ERCOT's node prices (scheduled.py ercot_rtm_node_prices, 500,000 rows a day at most) and its stores when it moved;"
  echo "  (session 206) then the runner's known gaps: carbon_auctions.py --table carb, carb_lcfs.py, policy_monitor_refresh.py --only orpuc, each table's stores when it moved;"
  echo "  (session 244) then ERCOT's reserve price adders: ercot_rt_adders.py (the list, and a year's workbook when ERCOT posted it again), its stores when the table moved;"
  echo "  (session 247) then the tables no other schedule refreshes (bash warehouse/run_data_machine_tables.sh --list): six steps a day, three once a month, their stores, and the live-set load of the tables only this machine builds;"
  echo "  (session 204) after the page files: battery_dispatch_export, battery_scenario_steps and seller_hybrid, each through scheduled.py, then each group's tests;"
  echo "  (session 204) switched off, GENERATOR=${GENERATOR:-0} (1 runs them): merchant_revenue (and its table's stores), merchant_hubs, generator_hourly_export;"
  echo "  then a commit to main of: ${PAGE_PATHS[*]} ${META_PATHS[*]}"
  echo "  branch here: $(git rev-parse --abbrev-ref HEAD); COMMIT=${COMMIT:-1} PUSH=${PUSH:-1}"
  exit 0
fi

mkdir -p runs
status="runs/data_machine_status.txt"
: > "$status"
day="$(date -u +%F)"
echo "== the data machine's daily run, $day (UTC), $(date -u +%H:%M) on $(hostname)"
. warehouse/soft_step.sh   # soft_step <name> <command...>: under warehouse/health.py, tried once more, recorded, never stops the run

# ---- 1. the day's tables ----------------------------------------------------------------------------------------------
echo "== sync: main, and the tables behind the Redivis draft"
soft_step dm_sync "$PYTHON" scripts/sync.py
# Session 204 (sessions 198 and 200 found it): the sync brings the day's storage awards and daily offers, and leaves the
# two monthly tables as they were (a table rewritten whole has no more rows and no newer month for the sync to see), so
# the daily and the monthly offers stood a day apart. Both monthly tables are added up again here from the tables just
# synced, the awards first (the offers builder checks each month against them and refuses where they disagree). No
# request; the stores hold the runner's. Two steps, each started as every other step here is: a `bash -c` under
# warehouse/health.py would be looked for by Windows itself, which can find another bash than the one running this.
soft_step dm_storage_awards_rollup "$PYTHON" warehouse/derived/ercot_storage_dam_awards.py
soft_step dm_storage_offers_rollup "$PYTHON" warehouse/derived/ercot_storage_dam_offers.py

# ---- 1b. ERCOT's node prices (session 204) ----------------------------------------------------------------------------
# A table's stores when a step moved it (warehouse/table_stores.py: the validator and the coverage row, each a gate for
# that table's stores only, then the archive and the Redivis draft). Nothing here stops the run.
sha_of() { sha256sum "warehouse/output/$1.csv" 2>/dev/null | cut -d' ' -f1; }
table_stores() {  # table_stores <step> <table> <its sha256 before the step that writes it>
  local name="$1" table="$2" was="$3"
  if [ "$(sha_of "$table")" = "$was" ]; then
    echo "$table: as it was; its stores are left as they are"
    echo "$name skipped: no change in $table" >> "$status"
  else
    echo "== $table moved: the validator and its coverage row (gates for its stores), the archive and the Redivis draft"
    soft_step "$name" "$PYTHON" warehouse/table_stores.py "$table"
    grep -E " exit=[0-9]+ " "runs/daily_${name}.out"
  fi
}
NODES=ercot_rtm_node_prices
echo "== ERCOT's node prices: the list's seven days, each file not yet saved (the count against the ceiling is in runs/daily_dm_ercot_node_prices.out)"
was="$(sha_of "$NODES")"
soft_step dm_ercot_node_prices "$PYTHON" warehouse/scheduled.py "$NODES"
grep -E "rows counted against the ceiling|STOPPED before" runs/daily_dm_ercot_node_prices.out
table_stores dm_node_stores "$NODES" "$was"

# ---- 1c. the publishers that refuse GitHub's runner (session 206, the owner's ruling of 12 October 2026) --------------
# CARB's auction summary and its LCFS credit prices (ww2.arb.ca.gov answers the runner HTTP 202 with no body since
# 27 September 2026) and Oregon's docket host (apps.puc.state.or.us, which did not answer the runner on 11 and 12
# October): known gaps on the runner (warehouse/metadata/known_gaps.csv), where each is recorded as skipped. This
# machine asks each once a day, and a table that moved gets its stores (table_stores, above). Each a soft step. Oregon
# goes through the policy monitor's refresh (--only orpuc: its other regulators are the runner's), whose rows go into
# the two large-load rule tables; the refresh needs the data lock, which this whole run holds.
echo "== the known gaps of the runner: CARB's auction prices, CARB's LCFS credit prices, Oregon's dockets"
CARB=carb_auction_allowance_prices
LCFS=carb_lcfs_credit_prices
RULES=large_load_rules
RULES_HELD=large_load_rules_internal
was="$(sha_of "$CARB")"
soft_step dm_carb_auction "$PYTHON" warehouse/connectors/carbon_auctions.py --table carb
table_stores dm_carb_auction_stores "$CARB" "$was"
was="$(sha_of "$LCFS")"
soft_step dm_carb_lcfs "$PYTHON" warehouse/connectors/carb_lcfs.py
table_stores dm_carb_lcfs_stores "$LCFS" "$was"
was_rules="$(sha_of "$RULES")"
was_held="$(sha_of "$RULES_HELD")"
soft_step dm_orpuc_dockets "$PYTHON" warehouse/connectors/policy_monitor_refresh.py --only orpuc
grep -E "SKIPPED for|FAILED for|new rows" runs/daily_dm_orpuc_dockets.out
table_stores dm_orpuc_rules_stores "$RULES" "$was_rules"
table_stores dm_orpuc_held_stores "$RULES_HELD" "$was_held"

# ---- 1d. ERCOT's real-time reserve price adders (session 244) -----------------------------------------------------------
# ERCOT posts the current year's workbook again every week (NP6-792-ER). The connector asks for the list once a day and
# for a workbook only when the list names one whose rows the table does not hold: most days one request and no change.
# The yearly workbooks are on this machine (warehouse/raw/ercot_rt_adders), which is why the step is here and not on
# the runner. A table that moved gets its stores. The live set is loaded by a person or a session (python
# warehouse/supabase/load.py --only '^ercot_rtm_price_adders$'), as for every table only this machine builds.
ADDERS=ercot_rtm_price_adders
echo "== ERCOT's reserve price adders: the list, and a year's workbook when ERCOT posted it again"
was="$(sha_of "$ADDERS")"
soft_step dm_ercot_rt_adders "$PYTHON" warehouse/connectors/ercot_rt_adders.py
table_stores dm_rt_adders_stores "$ADDERS" "$was"

# ---- 1e. the public tables no other schedule refreshed (session 247) ---------------------------------------------------
# Session 218 listed, for each stale public table, the line its schedule needs; the owner's chain prompt of 12 October
# 2026 asked for them. They are one file, sourced here so that its steps use this run's soft_step, table_stores, status
# file and data lock: six steps a day (EIA's daily total interchange, CAISO's and ERCOT's wind and solar forecasts, the
# NRC's reactor status, CAISO's notices, CAISO's evenings), three once a month (CAISO's curtailment reports not yet
# saved, who owns the batteries, the shoulder hours), each table's stores when it moved, and the live-set load of the
# tables only this machine builds. bash warehouse/run_data_machine_tables.sh --list names every step and its command.
. warehouse/run_data_machine_tables.sh

# ---- 2. ERCOT's load zones --------------------------------------------------------------------------------------------
echo "== ERCOT's load zone prices: the daily refresh (the count against the ceiling is in runs/daily_dm_ercot_zone_prices.out)"
before="$(sha256sum "warehouse/output/$ZONES.csv" | cut -d' ' -f1)"
soft_step dm_ercot_zone_prices "$PYTHON" warehouse/connectors/ercot_zone_prices.py --refresh
grep -E "counted against the ceiling|STOPPED before|not asked again|: saved " runs/daily_dm_ercot_zone_prices.out
after="$(sha256sum "warehouse/output/$ZONES.csv" | cut -d' ' -f1)"
if grep -q "(this run [0-9]*: 0 new, 0 replaced" runs/daily_dm_ercot_zone_prices.out || [ "$before" = "$after" ]; then
  echo "$ZONES: no new row today; the stores are left as they are"
  echo "dm_zone_stores skipped: no new row in $ZONES" >> "$status"
else
  echo "== $ZONES gained rows: the validator (a gate), then its coverage row, the archive and the Redivis draft"
  "$PYTHON" warehouse/validate/erw_validate.py "warehouse/output/$ZONES.csv" > runs/data_machine_validate.out 2>&1
  rc=$?
  echo "validator exit=$rc (runs/data_machine_validate.out)"
  if [ "$rc" -ne 0 ]; then
    echo "dm_zone_stores failed: the validator exited $rc on $ZONES; coverage, the archive and the Redivis draft were not run" >> "$status"
    "$PYTHON" warehouse/health.py record --step "dm_zone_validate" --status failed --reason "erw_validate.py exit $rc on $ZONES"
  else
    "$PYTHON" warehouse/metadata/build_coverage.py --only "^${ZONES}\$" > runs/data_machine_coverage.out 2>&1
    rc=$?
    echo "coverage exit=$rc (runs/data_machine_coverage.out)"
    if [ "$rc" -ne 0 ]; then
      echo "dm_zone_stores failed: build_coverage.py exited $rc; the archive and the Redivis draft were not run" >> "$status"
      "$PYTHON" warehouse/health.py record --step "dm_zone_coverage" --status failed --reason "build_coverage.py exit $rc"
    else
      soft_step dm_zone_archive "$PYTHON" warehouse/archive/archive.py write --tables "^${ZONES}\$"
      soft_step dm_zone_redivis "$PYTHON" warehouse/redivis/upload.py --tables "$ZONES"
    fi
  fi
fi

# ---- 3. the page files ------------------------------------------------------------------------------------------------
echo "== the page files (each rebuilt from the tables here; a failed builder leaves its file as it was)"
soft_step dm_datacenter_page "$PYTHON" warehouse/derived/datacenter_page.py
soft_step dm_capture_price "$PYTHON" warehouse/derived/capture_price.py --cache-dir runs/capture_cache
soft_step dm_curtailment_shares "$PYTHON" warehouse/derived/curtailment_shares.py
soft_step dm_free_energy "$PYTHON" warehouse/derived/free_energy.py
soft_step dm_curtailment_worth "$PYTHON" warehouse/derived/curtailment_worth.py
# Session 181, the scanner: after the sync this machine holds the day's tables and the full histories, so the daily
# scan runs here (about four minutes; it reads tables and writes none). The run is kept under runs/scanner/<date>/ and
# its drafts are added to the internal review list (public.scanner_drafts); a draft raised before is never raised
# twice. No model call. A soft step: a failure is recorded in erw_health and never stops this run.
soft_step dm_scanner "$PYTHON" warehouse/analysis/findings/findings_scanner.py --daily

# a file whose builder failed, or whose own test fails, is put back as the last commit has it: never a half-built file
put_back() {  # put_back <step> <path...>
  local name="$1"; shift
  if grep -q "^${name} failed" "$status"; then
    echo "$name failed: $* put back as committed"
    git checkout -- "$@" 2>/dev/null || true
  fi
}
put_back dm_datacenter_page site/data/datacenter
put_back dm_capture_price site/data/seller/capture.json
put_back dm_curtailment_shares site/data/curtailment/shares.json
put_back dm_free_energy site/data/curtailment/free_energy.json
put_back dm_curtailment_worth site/data/curtailment/worth.json
if command -v node >/dev/null 2>&1 && [ -d site/node_modules ]; then
  page_test() {  # page_test <name> <script> <path...>
    local name="$1" script="$2"; shift 2
    [ -f "site/scripts/$script" ] || return 0
    (cd site && node "scripts/$script") > "runs/data_machine_${name}.out" 2>&1
    local rc=$?
    echo "$script exit=$rc (runs/data_machine_${name}.out)"
    if [ "$rc" -ne 0 ]; then
      echo "$name failed: site/scripts/$script exited $rc; $* put back as committed" >> "$status"
      "$PYTHON" warehouse/health.py record --step "$name" --status failed --reason "site/scripts/$script exit $rc"
      git checkout -- "$@" 2>/dev/null || true
    else
      echo "$name ok" >> "$status"
    fi
  }
  page_test dm_test_capture test-capture.mjs site/data/seller/capture.json
  page_test dm_test_freeenergy test-freeenergy.mjs site/data/curtailment/shares.json site/data/curtailment/free_energy.json site/data/curtailment/worth.json
  page_test dm_test_datacenter test-datacenter-rule.mjs site/data/datacenter
else
  echo "node or site/node_modules is not here: the files' own tests were not run" | tee -a "$status"
fi
# Session 190: the hours of /cost-of-power's default case as the page's files now hold them, for the page's download
# and its do-file (tests/test_session190_replication.py holds the CSV to those files). After the files are final:
# a datacenter file put back above is the one exported. It reads no table and writes nothing but the CSV.
soft_step dm_datacenter_export "$PYTHON" warehouse/derived/datacenter_hourly_export.py

# ---- 3b. the battery page's downloads, the generator page's builders and its hourly CSV (session 204) -----------------
# Each through warehouse/scheduled.py (it skips with the reason where an input is not here), each a soft step. After
# the page files above: the generator's builders read the capture file as it now stands (put back above if its builder
# or its test failed). The seller's model writes a table as well as the snapshot, so it gets its stores when it moved.
echo "== the battery page's downloads (a file whose hours and months are as held is left as it is)"
soft_step dm_battery_dispatch_export "$PYTHON" warehouse/scheduled.py battery_dispatch_export
soft_step dm_battery_scenario_steps "$PYTHON" warehouse/scheduled.py battery_scenario_steps
echo "== the generator page's builders and its hourly CSV"
# SWITCHED OFF UNTIL SIX TESTS ARE CHANGED: GENERATOR=1 runs the three steps of the snapshot's group. The snapshot, the
# table merchant_revenue_monthly, the hub files and the CSV move together or not at all (the CSV is checked against the
# snapshot, the hub files and the table against it). On 12 October 2026 six tests that a landing must pass still held
# the CSV to its export of 7 October: four of tests/test_session183_replication.py (72,384 rows, the last hour
# 2026-10-03T04:00:00Z, the last local day 2026-10-02, 72 blank hours) and two of tests/test_session199.py (the capture
# build its header names, and the list of dated records, which a daily export lengthens by one a day). A re-export
# fails them, so the group below would put the files back every day, after the table had already moved and could not
# be put back (the archive keeps no return to an earlier value). Session 204 ran the three once, saw this, and left
# them here for a session that may change those tests (archive/sessions/SESSION_204_REPORT.md). The hybrid's hours are
# not of that group and run every day.
MERCHANT=merchant_revenue_monthly
GENERATOR_OK=0
if [ "${GENERATOR:-0}" = "1" ]; then
  was="$(sha_of "$MERCHANT")"
  soft_step dm_merchant_revenue "$PYTHON" warehouse/scheduled.py merchant_revenue
  table_stores dm_merchant_stores "$MERCHANT" "$was"
  if grep -q "^dm_merchant_revenue ok" "$status"; then
    soft_step dm_merchant_hubs "$PYTHON" warehouse/scheduled.py merchant_hubs
    soft_step dm_generator_hourly_export "$PYTHON" warehouse/scheduled.py generator_hourly_export
  else
    # the hub files are checked against the snapshot and the CSV is written from it: without today's snapshot neither is built
    echo "dm_merchant_hubs skipped: dm_merchant_revenue did not finish" >> "$status"
    echo "dm_generator_hourly_export skipped: dm_merchant_revenue did not finish" >> "$status"
  fi
else
  echo "the snapshot, the hub files and the hourly CSV: switched off (GENERATOR=1 runs them; six tests still hold the CSV to its export of 7 October 2026)"
  for s in dm_merchant_revenue dm_merchant_hubs dm_generator_hourly_export; do
    echo "$s skipped: switched off until the tests that hold the CSV to its export of 7 October 2026 are changed (GENERATOR=1)" >> "$status"
  done
fi
soft_step dm_seller_hybrid "$PYTHON" warehouse/scheduled.py seller_hybrid

# Each group's own tests, on the files as they now stand and the tables on this machine. A group one of whose steps
# did not finish, or one of whose tests fails, is put back whole as the last commit has it: main never gets a file
# its own tests refuse, or half of a group. (The table merchant_revenue_monthly is not in git and stays as written.)
group() {  # group <name> <steps, spaced> <test modules, spaced> -- <path...>
  local name="$1" steps="$2" tests="$3"; shift 4
  local s rc=0 why=""
  for s in $steps; do
    grep -q "^$s ok" "$status" || { why="$s did not finish"; break; }
  done
  if [ -z "$why" ]; then
    "$PYTHON" -m unittest $tests > "runs/data_machine_${name}.out" 2>&1
    rc=$?
    echo "$name: unittest $tests exit=$rc (runs/data_machine_${name}.out)"
    [ "$rc" -ne 0 ] && why="its tests exited $rc ($tests)"
  fi
  if [ -n "$why" ]; then
    echo "$name failed: $why; $* put back as committed" >> "$status"
    "$PYTHON" warehouse/health.py record --step "$name" --status failed --reason "$why; the group was put back as committed"
    git checkout -- "$@" 2>/dev/null || true
    return 1
  fi
  echo "$name ok" >> "$status"
}
group dm_test_battery_dispatch "dm_battery_dispatch_export" "tests.test_session178" -- site/public/battery/erw_2026_battery_dispatch.csv
group dm_test_battery_steps "dm_battery_scenario_steps" "tests.test_session179" -- site/data/battery_scenario_steps.json
if [ "${GENERATOR:-0}" = "1" ]; then
  GENERATOR_OK=1
  group dm_test_generator "dm_merchant_revenue dm_merchant_hubs dm_generator_hourly_export" \
    "tests.test_session51 tests.test_session183 tests.test_session183_replication tests.test_session186 tests.test_session199" -- \
    site/data/merchant_snapshot.json site/data/seller/hubs site/public/seller/erw_2026_generator_hourly.csv || GENERATOR_OK=0
fi
group dm_test_hybrid "dm_seller_hybrid" "tests.test_session162" -- site/data/seller/hybrid.json site/public/seller/prices

# ---- 4. the commit ----------------------------------------------------------------------------------------------------
echo "== status"
cat "$status"
if [ "${COMMIT:-1}" = "0" ]; then
  echo "COMMIT=0: nothing committed"
  exit 0
fi
branch="$(git rev-parse --abbrev-ref HEAD)"
if [ "$branch" != "main" ]; then
  echo "this checkout is on $branch, not main: the files are built and left uncommitted" | tee -a "$status"
  "$PYTHON" warehouse/health.py record --step "dm_commit" --status skipped --reason "the checkout is on $branch, not main"
  exit 0
fi
for p in "${PAGE_PATHS[@]}" "${META_PATHS[@]}"; do
  [ -e "$p" ] && git add -- "$p"
done
# session 204: the generator export's record of the day, with the CSV that names it
[ "${GENERATOR_OK:-0}" = "1" ] && [ -e "$RECORD_PATH" ] && git add -- "$RECORD_PATH"
if git diff --cached --quiet; then
  echo "nothing changed today: no commit"
  "$PYTHON" warehouse/health.py record --step "dm_commit" --status skipped --reason "no page file changed"
  exit 0
fi
ok="$(awk '$2=="ok"{print $1}' "$status" | tr '\n' ' ' | sed 's/ $//')"
bad="$(grep -E ' failed' "$status" | cut -d: -f1 | tr '\n' ' ' | sed 's/ $//')"
git commit --quiet -m "Page files $day (the data machine's daily run): ok: ${ok:-none}${bad:+; failed: $bad}"
rc=$?
echo "commit exit=$rc"
if [ "$rc" -ne 0 ]; then
  "$PYTHON" warehouse/health.py record --step "dm_commit" --status failed --reason "git commit exit $rc"
  exit 0
fi
if [ "${PUSH:-1}" = "0" ]; then
  echo "PUSH=0: committed, not pushed"
  exit 0
fi
git pull --rebase --quiet origin main
rc=$?
echo "pull exit=$rc"
if [ "$rc" -ne 0 ]; then
  git rebase --abort 2>/dev/null || true
  "$PYTHON" warehouse/health.py record --step "dm_commit" --status failed --reason "git pull --rebase exit $rc: committed here, not pushed"
  echo "main moved in a way the commit could not follow: committed here, not pushed"
  exit 0
fi
git push --quiet origin main
rc=$?
echo "push exit=$rc"
if [ "$rc" -ne 0 ]; then
  "$PYTHON" warehouse/health.py record --step "dm_commit" --status failed --reason "git push exit $rc"
else
  "$PYTHON" warehouse/health.py record --step "dm_commit" --status ok --reason "page files $day pushed to main"
fi
exit 0
