#!/usr/bin/env bash
# The energy mix (/mix): its refresh (session 133). WRITTEN, NOT SCHEDULED: no workflow and no line of run_daily.sh
# calls this while the review freeze is on. To switch it on, a person adds one step to warehouse/run_daily.sh:
#
#   run_other mix "$PYTHON" warehouse/health.py run --step "mix" -- bash warehouse/refresh_mix.sh
#
# adds '^(caiso|ercot)_wind_solar_forecast$' and '^nrc_reactor_status$' to the tables the runner restores
# (warehouse/redivis/config.yaml: each keeps its history by merging the newest days), and lets the run's commit step
# add site/data/mix_forecast.json and site/data/mix_history.json.
#
#   bash warehouse/refresh_mix.sh            # under the data lock, each step recorded in erw_health
#
# What it asks for each day: CAISO's wind and solar forecast and actual for the last ten days (two requests), ERCOT's
# week of hourly postings (about 345 small files; ERCOT keeps only a week, so a day missed is a day of forecasts
# lost), and the NRC's file of the last 365 days. The two histories are not asked for again: CAISO's supply to May
# 2025 is closed, and the retired generators are read once a month with EIA's inventory (the last line, off by default).
#
# What it does not rebuild: the hourly views (site/data/mix, clean, stress, mixplus). They read EIA-930's workbooks,
# which only a data machine holds. On one, after the workbooks are refreshed (warehouse/connectors/eia930_emissions.py):
#
#   python warehouse/derived/mix_profile.py --snapshot
#   python warehouse/derived/mix_views.py --hours-to runs/mix_hours
#   python warehouse/derived/mix_stress.py --snapshot --hours-from runs/mix_hours
#   python warehouse/derived/mix_clean.py --snapshot --hours-from runs/mix_hours
#
# Every step goes through warehouse/health.py, so a failure is retried once, recorded, and never fails a job.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python}"
SINCE="$("$PY" -c "import datetime as d; print((d.datetime.now(d.timezone.utc) - d.timedelta(days=10)).date())")"
"$PY" warehouse/health.py run --step "caiso_wind_solar_forecast" -- "$PY" warehouse/connectors/caiso_wind_solar_forecast.py --start "$SINCE"
"$PY" warehouse/health.py run --step "ercot_wind_solar_forecast" -- "$PY" warehouse/connectors/ercot_wind_solar_forecast.py
"$PY" warehouse/health.py run --step "nrc_reactor_status" -- "$PY" warehouse/connectors/nrc_reactor_status.py --recent
if [ "${MIX_WITH_RETIRED:-0}" = "1" ]; then
  "$PY" warehouse/health.py run --step "eia860m_retired_all" -- "$PY" warehouse/connectors/eia860m_retired_all.py
fi
"$PY" warehouse/health.py run --step "mix validate" --retries 0 -- "$PY" warehouse/validate/erw_validate.py \
  warehouse/output/caiso_wind_solar_forecast.csv warehouse/output/ercot_wind_solar_forecast.csv warehouse/output/nrc_reactor_status.csv
"$PY" warehouse/health.py run --step "mix_views" -- "$PY" warehouse/derived/mix_views.py --only forecast history
