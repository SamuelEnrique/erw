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
#   session 271 (the owner's rulings of 14 October 2026), every day
#     dm_ercot_large_load           ercot_large_load_status          ERCOT's meeting pages, about 76 requests: the guard
#                                                                    (the runner's monthly job and Monday watch are kept)
#     dm_ercot_hub_append           ercot_all_hub_prices_history     the live window's ERCOT hub rows after the history's
#                                                                    newest interval (hub_history.py append-ercot); no request
#   session 310, once a week: dm_mix_profile (generation_mix_hourly_profile, generation_mix_records), derived from the
#   EIA-930 workbooks and CAISO's own supply; no request (warehouse/refresh_mix.sh, which held it, is called by no job)
#   session 271, once a week (the first run of each ISO week, Monday to Sunday, or any run with WEEKLY=1)
#     dm_ercot_sced_pull            (the reduced days, warehouse/raw) ERCOT's 60-Day SCED Disclosure, the days not yet
#                                                                    held, within the approved 12 GB of downloads (at the
#                                                                    ceiling the step is a skip that says so)
#     dm_ercot_sced_write           ercot_sced_esr_hourly            the table, from the reduced days; no request
#     dm_ercot_storage_rt           ercot_storage_rt_monthly,        derived (the disclosure, the awards, the hub and node
#                                   ercot_storage_node_basis         prices); no request
#     dm_eia930_workbooks           (EIA-930's workbooks, warehouse/raw) eia930_emissions.py --dry-run: the eight
#                                                                    workbooks fetched, no table written
#     dm_clean_energy               clean_energy_hourly,             derived from those workbooks (mix_clean.py); the
#                                   clean_energy_summary             site's copy (site/data/clean/) is not rebuilt here
#     dm_noaa_weather               noaa_grid_weather_hourly, _daily, NOAA, the days since a week before the newest hour
#                                   _stations, noaa_station_weather_hourly  held, under 6,000,000 rows a year
#   session 277, once a week: the zone price history's CAISO part (ZP26), which refresh_supply.sh asked only on the
#   GitHub runner, where the table is not held, so no run refreshed it (NYISO's and SPP's parts are not this machine's
#   to ask: a ruling)
#     dm_zone_history_pull          (the saved files, warehouse/raw) zone_price_history.py --pull --iso caiso --recent 9
#     dm_zone_history_write         iso_zone_prices_history          --write --iso caiso --recent 9, merged into the table
#   then, every day
#     dm_live_set                   the tables above that the live set holds, and ercot_rtm_price_adders: loaded from
#                                   this machine, which is the only one that builds them (the loader writes what changed)
#   and once a week (session 271)
#     dm_live_set_weekly            every table this machine's steps write that a live-set rule names (the loader
#                                   writes what changed and leaves a table no rule names)
#
# Not here, each with its reason in archive/sessions/SESSION_247_REPORT.md: the page files of /mix and /storage/owners
# (a page file is committed only with its own tests, as the files of warehouse/run_data_machine.sh are). Session 271:
# NOAA's weather, clean_energy_hourly and ERCOT's 15-minute history are here now; the price board's statistics table
# is retired (warehouse/metadata/retired_tables.csv).
#
#   bash warehouse/run_data_machine.sh                      the daily run, which sources this file
#   MONTHLY=1 bash warehouse/run_data_machine_tables.sh     by itself, under the data lock: the monthly steps too
#   MONTHLY=1 MONTHLY_PULLS=0 bash ...                      the monthly steps without CAISO's reports (derived only)
#   WEEKLY=1 bash warehouse/run_data_machine_tables.sh      by itself: the weekly steps too (session 271)
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
  "dm_ercot_large_load|ercot_large_load_status|daily|warehouse/connectors/ercot_large_load_status.py"
  "dm_ercot_hub_append|ercot_all_hub_prices_history|daily|warehouse/connectors/hub_history.py append-ercot"
  "dm_ercot_sced_pull|-|weekly|warehouse/connectors/ercot_sced_esr.py --pull --from 2026-02-01"
  "dm_ercot_sced_write|ercot_sced_esr_hourly|weekly|warehouse/connectors/ercot_sced_esr.py --write"
  "dm_ercot_storage_rt|ercot_storage_rt_monthly,ercot_storage_node_basis|weekly|warehouse/derived/ercot_storage_realtime.py"
  "dm_eia930_workbooks|-|weekly|warehouse/connectors/eia930_emissions.py --days 3 --dry-run"
  "dm_clean_energy|clean_energy_hourly,clean_energy_summary|weekly|warehouse/derived/mix_clean.py"
  "dm_noaa_weather|noaa_grid_weather_hourly,noaa_grid_weather_daily,noaa_grid_weather_stations,noaa_station_weather_hourly|weekly|warehouse/connectors/noaa_grid_weather.py --refresh"
  "dm_zone_history_pull|-|weekly|warehouse/connectors/zone_price_history.py --pull --iso caiso --recent 9"
  "dm_zone_history_write|iso_zone_prices_history|weekly|warehouse/connectors/zone_price_history.py --write --iso caiso --recent 9"
  "dm_mix_profile|generation_mix_hourly_profile,generation_mix_records|weekly|warehouse/derived/mix_profile.py"
)
# session 271: the weekly load of every table this block and warehouse/run_data_machine.sh write (the loader takes
# only those a live-set rule names, and writes what changed)
WEEKLY_LIVE='^(iso_zone_prices_history|caiso_reliability_daily|caiso_grid_emergencies|storage_owners_monthly|shoulder_hours_monthly|ercot_rtm_price_adders|scarcity_hours_by_grid|eia930_daily_total_interchange|caiso_wind_solar_forecast|ercot_wind_solar_forecast|nrc_reactor_status|caiso_curtailment_intervals|ercot_large_load_status|ercot_all_hub_prices_history|ercot_sced_esr_hourly|ercot_storage_rt_monthly|ercot_storage_node_basis|clean_energy_hourly|clean_energy_summary|noaa_grid_weather_hourly|noaa_grid_weather_daily|noaa_grid_weather_stations|noaa_station_weather_hourly|ercot_rtm_node_prices|ercot_zone_prices_history|carb_auction_allowance_prices|carb_lcfs_credit_prices|merchant_revenue_monthly|generation_mix_hourly_profile|generation_mix_records)$'

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
  echo "dm_live_set_weekly (weekly): python warehouse/supabase/load.py --no-vacuum --only '$WEEKLY_LIVE'"
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
# session 271: the weekly steps, on the first run of an ISO week that falls on a Monday or later (or WEEKLY=1)
week="$(date -u +%G-W%V)"
wstamp="runs/dm_weekly_${week}.done"
weekly=0
if [ "${WEEKLY:-0}" = "1" ] || [ ! -f "$wstamp" ]; then
  weekly=1
fi
SINCE="$("$PYTHON" -c "import datetime as d; print((d.datetime.now(d.timezone.utc) - d.timedelta(days=10)).date())")"
echo "== the tables no other schedule refreshes (session 247): the daily steps$([ "$monthly" = "1" ] && echo ", and the monthly ones ($month)")$([ "$weekly" = "1" ] && echo ", and the weekly ones ($week)")"
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
    weekly)
      if [ "$weekly" != "1" ]; then
        echo "$name skipped: weekly, and $week's run is done ($wstamp)" >> "$status"
        continue
      fi ;;
  esac
  # session 271: a step may write several tables (comma-separated), or none ("-": its files are raw, not a table)
  tables=()
  [ "$table" != "-" ] && IFS=',' read -r -a tables <<< "$table"
  declare -A before=()
  for t in "${tables[@]}"; do before[$t]="$(sha_of "$t")"; done
  # shellcheck disable=SC2086  # the command is words, split on purpose
  soft_step "$name" "$PYTHON" ${cmd//SINCE/$SINCE}
  i=0
  for t in "${tables[@]}"; do
    suffix="_stores"
    [ "$i" -gt 0 ] && suffix="_stores_${t}"
    table_stores "${name}${suffix}" "$t" "${before[$t]}"
    i=$((i + 1))
  done
  unset before
done
if [ "$monthly" = "1" ]; then
  echo "the monthly steps ran on $(date -u +%FT%TZ)$([ "${MONTHLY_PULLS:-1}" = "0" ] && echo " (MONTHLY_PULLS=0: without CAISO's reports)")" > "$stamp"
fi
echo "== the live set, for the tables only this machine builds"
soft_step dm_live_set "$PYTHON" warehouse/supabase/load.py --no-vacuum --only "$LIVE_ONLY"
grep -E "^(match|MISMATCH|refused)|pg_database_size:" runs/daily_dm_live_set.out
if [ "$weekly" = "1" ]; then
  echo "== the live set, once a week: every table this machine writes that a live-set rule names (session 271)"
  soft_step dm_live_set_weekly "$PYTHON" warehouse/supabase/load.py --no-vacuum --only "$WEEKLY_LIVE"
  grep -E "^(match|MISMATCH|refused)|pg_database_size:" runs/daily_dm_live_set_weekly.out
  echo "the weekly steps ran on $(date -u +%FT%TZ)" > "$wstamp"
fi
