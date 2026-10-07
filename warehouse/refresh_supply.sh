#!/usr/bin/env bash
# Supply and trade (/supply): its weekly refresh (session 134). SCHEDULED since 6 October 2026, on the owner's
# instruction in that day's chain prompt. The reports it reads come out on Wednesday (petroleum), Thursday (gas
# storage) and Friday afternoon (CFTC), all after the daily run's hour on their day, so warehouse/run_daily.sh calls
# it once a week, on Saturday (UTC), when the week's three reports are out (SUPPLY=1 forces it on any day):
#
#   run_other supply "$PYTHON" warehouse/health.py run --step "supply" -- bash warehouse/refresh_supply.sh
#
# and the run's commit step adds site/data/supply.json and warehouse/metadata/release_schedule.json. The page is in
# review; no open page reads these files. The page's file is written through warehouse/derived/page_keep.py: a row
# whose new build is blank, older or shorter than the held one is kept as it was.
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
# Session 136: day-ahead energy cleared, one connector an operator that publishes it openly (MISO is paused and PJM
# licensed: neither is asked). Each reads its last days and merges them into its table; ERCOT's report lists 31 days
# only and reads about 23,000 rows a day to make 24, so its week is the large one (about 185,000 rows read)
CLEARED=""
for iso in ercot caiso nyiso isone spp; do
  "$PY" warehouse/health.py run --step "${iso}_dam_cleared" -- "$PY" "warehouse/connectors/${iso}_dam_cleared.py"
  [ -f "warehouse/output/${iso}_dam_cleared_energy.csv" ] && CLEARED="$CLEARED warehouse/output/${iso}_dam_cleared_energy.csv"
done
# Session 138: hourly load by zone or area, one connector an operator (MISO is paused and PJM licensed: neither is
# asked). Each asks for what is new and merges it into its table: NYISO this month's file (about 8,000 lines), CAISO
# its newest one or two 30-day windows for six areas (up to about 8,600 lines), ERCOT and ISO-NE the current year's
# workbook, and only when the kept copy is old (ERCOT, 13 days) or the operator's list shows a newer one (ISO-NE)
LOADS=""
for t in ercot_zone nyiso_zone isone_zone caiso_area; do
  "$PY" warehouse/health.py run --step "${t}_load" -- "$PY" "warehouse/connectors/${t}_load.py"
  [ -f "warehouse/output/${t}_load_hourly.csv" ] && LOADS="$LOADS warehouse/output/${t}_load_hourly.csv"
done
# Session 138: the files of "What a datacenter pays" (/cost-of-power, in review): the newest hours of every hub and zone
# price held and the grids' tight hours from the load tables above, merged into the kept files (an hour only the kept
# file holds is kept, so the runner, which holds no ERCOT price history, adds hours and never thins a file). No pull.
# The daily run's commit step adds site/data/datacenter
"$PY" warehouse/health.py run --step "datacenter_page" -- "$PY" warehouse/derived/datacenter_page.py
"$PY" warehouse/health.py run --step "release_schedule" -- "$PY" warehouse/connectors/release_schedule.py
"$PY" warehouse/health.py run --step "supply validate" --retries 0 -- "$PY" warehouse/validate/erw_validate.py \
  warehouse/output/eia_gas_storage_weekly.csv warehouse/output/eia_petroleum_supply_weekly.csv warehouse/output/eia_gas_trade_monthly.csv \
  warehouse/output/eia_basin_production_monthly.csv warehouse/output/cftc_cot_positions.csv $CLEARED $LOADS
# the fuel burn needs the hourly generation workbooks; where none is held (or the build with them fails), the page is
# built without them and page_keep.py keeps the held fuel burn rows as they were
if [ "${SUPPLY_NO_BURN:-0}" = "1" ] || [ -z "$(find warehouse/raw/eia930_emissions -name '*.xlsx' 2>/dev/null | head -n 1)" ]; then
  "$PY" warehouse/health.py run --step "supply_page" -- "$PY" warehouse/derived/page_keep.py supply --no-burn
else
  "$PY" warehouse/health.py run --step "supply_page" --retries 0 -- "$PY" warehouse/derived/page_keep.py supply     || "$PY" warehouse/health.py run --step "supply_page without the fuel burn" -- "$PY" warehouse/derived/page_keep.py supply --no-burn
fi
