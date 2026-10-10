#!/usr/bin/env bash
# Energy Research Warehouse (ERW), session 149: the data machine's daily run.
#
# What the GitHub runner cannot do, once a day, on the machine that holds the price histories and the saved workbooks
# (docs/machines.md: a machine whose role is "data" and whose warehouse/output holds the ERCOT price history):
#
#   1. sync: main fast-forwarded, and every table that is behind the Redivis draft brought up to it (scripts/sync.py:
#      a table that is ahead here, or has diverged, is reported and left), so the day's prices from the runner are in;
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
            site/data/curtailment/free_energy.json site/data/curtailment/worth.json)
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
