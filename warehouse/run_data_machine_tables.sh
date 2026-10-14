#!/usr/bin/env bash
# Energy Research Warehouse (ERW), session 247: the public tables no schedule refreshed, on the data machine's daily run.
#
# Session 218 found 33 public tables behind their cadence and listed, for each, the line its schedule needs. The owner's
# chain prompt of 12 October 2026 asked for those lines. This is them, in one block of warehouse/run_data_machine.sh
# (it sources this file after ERCOT's reserve price adders), on the machine that holds every input: EIA-930's
# workbooks, the saved reports, the price histories. Each step is a soft step (warehouse/soft_step.sh: under
# warehouse/health.py, tried once more, recorded in erw_health as dm_<name>, never stops the run), and a table a step
# moved gets its stores (warehouse/table_stores.py: the validator and the coverage row as gates, the archive, the
# Redivis draft).
#
#   every day
#     dm_eia930_total_interchange   eia930_daily_total_interchange   EIA's API; resumes by month from its checkpoints
#     dm_caiso_ws_forecast          caiso_wind_solar_forecast        CAISO, the last ten days: two requests
#     dm_ercot_ws_forecast          ercot_wind_solar_forecast        ERCOT's week of hourly postings (it keeps a week and no
#                                                                    more: a day not pulled is a day of forecasts lost)
#     dm_nrc_reactor_status         nrc_reactor_status               the NRC's file of the last 365 days: one request
#     dm_caiso_emergencies          caiso_grid_emergencies           CAISO's Grid Emergencies History Report: one document
#     dm_caiso_reliability          caiso_reliability_daily          derived (EIA-930's CISO workbook, CAISO's batteries,
#                                                                    the notices just read); no request
#   once a month (the first run on or after the third, or any run with MONTHLY=1)
#     dm_caiso_curtailment          caiso_curtailment_intervals      --new-only: the library's index, a page a month of
#                                                                    2026, and the daily reports not yet saved
#     dm_storage_owners             storage_owners_monthly           derived (EIA-860M); no request
#     dm_shoulder_hours             shoulder_hours_monthly           derived (EIA-930's workbooks); no request
#     dm_scarcity_hours             scarcity_hours_by_grid           derived (session 254: the price histories, ERCOT's
#                                                                    adders, CAISO's notices just read); no request. Its
#                                                                    window is the 36 whole months before the month
#   then, every day
#     dm_live_set                   the tables above that the live set holds, and ercot_rtm_price_adders: loaded from
#                                   this machine, which is the only one that builds them (the loader writes what changed)
#
# Not here, each with its reason in archive/sessions/SESSION_247_REPORT.md: NOAA's weather (its approved ceiling of
# 3,000,000 rows is reached at the next refresh), the page files of /mix and /storage/owners (a page file is committed
# only with its own tests, as the files of warehouse/run_data_machine.sh are), the price board's statistics table (its
# page is retired: a ruling), ERCOT's 15-minute history (the live table already holds every interval after it).
#
#   bash warehouse/run_data_machine.sh                      the daily run, which sources this file
#   MONTHLY=1 bash warehouse/run_data_machine_tables.sh     by itself, under the data lock: the monthly steps too
#   MONTHLY=1 MONTHLY_PULLS=0 bash ...                      the monthly steps without CAISO's reports (derived only)
#   bash warehouse/run_data_machine_tables.sh --list        the steps and their commands; runs nothing
#
# By itself it refuses as the daily run does: on the GitHub runner, or on a machine whose role is not data.

if ! declare -F soft_step > /dev/null; then   # run by itself: what warehouse/run_data_machine.sh sets up before it sources this file
  set -uo pipefail
  cd "$(dirname "${BASH_SOURCE[0]}")/.."
  if [ -z "${PYTHON:-}" ]; then
    if [ -x "$(pwd)/.venv/Scripts/python.exe" ]; then PYTHON="$(pwd)/.venv/Scripts/python.exe"
    elif [ -x "$(pwd)/.venv/bin/python" ]; then PYTHON="$(pwd)/.venv/bin/python"
    else PYTHON=python; fi
  fi
  export PYTHON
  if [ "${1:-}" != "--list" ]; then
    if [ "${GITHUB_ACTIONS:-}" = "true" ]; then
      echo "run_data_machine_tables REFUSED: this is the GitHub runner (GITHUB_ACTIONS is true); nothing is asked or built here."
      exit 0
    fi
    role="$("$PYTHON" warehouse/lock.py role 2>/dev/null | tr -d '\r' | sed -n -E 's/.*"role": *"([a-z]+)".*/\1/p')"
    if [ "$role" != "data" ]; then
      echo "run_data_machine_tables REFUSED: this machine's role is '${role:-not set}', not data; nothing is asked or built here."
      exit 0
    fi
  fi
  mkdir -p runs
  status="${STATUS_FILE:-runs/data_machine_tables_status.txt}"
  : > "$status"
  . warehouse/soft_step.sh
  sha_of() { sha256sum "warehouse/output/$1.csv" 2>/dev/null | cut -d' ' -f1; }
  table_stores() {  # table_stores <step> <table> <its sha256 before the step that writes it>: as in warehouse/run_data_machine.sh
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
fi

# step name | table | cadence | the command after the interpreter
TABLE_STEPS=(
  "dm_eia930_total_interchange|eia930_daily_total_interchange|daily|warehouse/connectors/eia930_daily_total_interchange.py"
  "dm_caiso_ws_forecast|caiso_wind_solar_forecast|daily|warehouse/connectors/caiso_wind_solar_forecast.py --start SINCE"
  "dm_ercot_ws_forecast|ercot_wind_solar_forecast|daily|warehouse/connectors/ercot_wind_solar_forecast.py"
  "dm_nrc_reactor_status|nrc_reactor_status|daily|warehouse/connectors/nrc_reactor_status.py --recent"
  "dm_caiso_emergencies|caiso_grid_emergencies|daily|warehouse/connectors/caiso_emergencies.py"
  "dm_caiso_reliability|caiso_reliability_daily|daily|warehouse/derived/caiso_reliability.py"
  "dm_caiso_curtailment|caiso_curtailment_intervals|monthly pull|warehouse/connectors/caiso_curtailment_intervals.py --new-only"
  "dm_storage_owners|storage_owners_monthly|monthly|warehouse/derived/storage_owners.py"
  "dm_shoulder_hours|shoulder_hours_monthly|monthly|warehouse/derived/shoulder_hours.py"
  "dm_scarcity_hours|scarcity_hours_by_grid|monthly|warehouse/derived/scarcity_hours_by_grid.py"
)
# the tables of this block that the live set holds (warehouse/supabase/live_set.yaml gives each its rule; the others
# are histories, or held out of the catalogue, and are not loaded), and session 244's table, which only this machine builds
LIVE_ONLY='^(caiso_reliability_daily|caiso_grid_emergencies|storage_owners_monthly|shoulder_hours_monthly|ercot_rtm_price_adders|scarcity_hours_by_grid)$'
MONTHLY_DAY=3

if [ "${1:-}" = "--list" ]; then
  for line in "${TABLE_STEPS[@]}"; do
    IFS='|' read -r name table cadence cmd <<< "$line"
    echo "$name: $table ($cadence): python $cmd"
  done
  echo "dm_live_set: python warehouse/supabase/load.py --no-vacuum --only '$LIVE_ONLY'"
  exit 0
fi

month="$(date -u +%Y-%m)"
stamp="runs/dm_monthly_${month}.done"
monthly=0
if [ "${MONTHLY:-0}" = "1" ]; then
  monthly=1
elif [ ! -f "$stamp" ] && [ "$((10#$(date -u +%d)))" -ge "$MONTHLY_DAY" ]; then
  monthly=1
fi
SINCE="$("$PYTHON" -c "import datetime as d; print((d.datetime.now(d.timezone.utc) - d.timedelta(days=10)).date())")"
echo "== the tables no other schedule refreshes (session 247): the daily steps$([ "$monthly" = "1" ] && echo ", and the monthly ones ($month)")"
for line in "${TABLE_STEPS[@]}"; do
  IFS='|' read -r name table cadence cmd <<< "$line"
  case "$cadence" in
    monthly*)
      if [ "$monthly" != "1" ]; then
        echo "$name skipped: monthly, and $month's run is done ($stamp)" >> "$status"
        continue
      fi
      if [ "$cadence" = "monthly pull" ] && [ "${MONTHLY_PULLS:-1}" = "0" ]; then
        echo "$name skipped: MONTHLY_PULLS=0, the month's pull is left out of this run" >> "$status"
        continue
      fi ;;
  esac
  was="$(sha_of "$table")"
  # shellcheck disable=SC2086  # the command is words, split on purpose
  soft_step "$name" "$PYTHON" ${cmd//SINCE/$SINCE}
  table_stores "${name}_stores" "$table" "$was"
done
if [ "$monthly" = "1" ]; then
  echo "the monthly steps ran on $(date -u +%FT%TZ)$([ "${MONTHLY_PULLS:-1}" = "0" ] && echo " (MONTHLY_PULLS=0: without CAISO's reports)")" > "$stamp"
fi
echo "== the live set, for the tables only this machine builds"
soft_step dm_live_set "$PYTHON" warehouse/supabase/load.py --no-vacuum --only "$LIVE_ONLY"
grep -E "^(match|MISMATCH|refused)|pg_database_size:" runs/daily_dm_live_set.out
