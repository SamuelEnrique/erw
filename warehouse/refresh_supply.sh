#!/usr/bin/env bash
# Supply and trade (/supply): its weekly refresh (session 134). WRITTEN, NOT SCHEDULED: no workflow and no line of
# run_daily.sh calls this while the review freeze is on. The reports it reads come out on Wednesday (petroleum),
# Thursday (gas storage) and Friday afternoon (CFTC), so a person who switches it on runs it once a day on those three
# days, or once on Saturday, as a step of its own:
#
#   run_other supply "$PYTHON" warehouse/health.py run --step "supply" -- bash warehouse/refresh_supply.sh
#
# and lets the run's commit step add site/data/supply.json and warehouse/metadata/release_schedule.json.
#
#   bash warehouse/refresh_supply.sh            # under the data lock, each step recorded in erw_health
#
# What it asks for: EIA's four supply tables whole (about 72,000 rows returned, of which about 36,000 are kept: the gas
# trade route answers every country and terminal and the connector keeps the totals and the terminals), the CFTC's four
# contracts from 2015 (about 2,500 rows), and EIA's two schedule pages. The tables are rewritten only where a row changed.
#
# The fuel burned for power reads EIA-930's hourly workbooks, which only a data machine holds. There the builder is run
# as it stands; anywhere else it is run with --no-burn (SUPPLY_NO_BURN=1) and those rows read "working on it".
# Every step goes through warehouse/health.py, so a failure is retried once, recorded, and never fails a job; the page
# is built from whatever the tables hold.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python}"
"$PY" warehouse/health.py run --step "eia_supply" -- "$PY" warehouse/connectors/eia_supply.py
"$PY" warehouse/health.py run --step "cftc_cot" -- "$PY" warehouse/connectors/cftc_cot.py
"$PY" warehouse/health.py run --step "release_schedule" -- "$PY" warehouse/connectors/release_schedule.py
"$PY" warehouse/health.py run --step "supply validate" --retries 0 -- "$PY" warehouse/validate/erw_validate.py \
  warehouse/output/eia_gas_storage_weekly.csv warehouse/output/eia_petroleum_supply_weekly.csv warehouse/output/eia_gas_trade_monthly.csv \
  warehouse/output/eia_basin_production_monthly.csv warehouse/output/cftc_cot_positions.csv
if [ "${SUPPLY_NO_BURN:-0}" = "1" ]; then
  "$PY" warehouse/health.py run --step "supply_page" -- "$PY" warehouse/derived/supply_page.py --no-burn
else
  "$PY" warehouse/health.py run --step "supply_page" -- "$PY" warehouse/derived/supply_page.py
fi
