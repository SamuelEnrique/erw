#!/usr/bin/env bash
# The price board (/board): its daily refresh (session 132). SCHEDULED since 6 October 2026, on the owner's
# instruction in that day's chain prompt: warehouse/run_daily.sh calls it once a day after "price_board" and
# "trader_view" (the price tables the board reads are refreshed by then), as
#
#   run_other board "$PYTHON" warehouse/health.py run --step "board" -- bash warehouse/refresh_board.sh
#
# and the daily run's commit step adds site/data/board.json and site/public/board/ (the page reads those files).
# The page is in review; no open page reads these files. The last step goes through warehouse/derived/page_keep.py:
# on the runner the long price histories are absent, and a row whose new build is older or shorter than the held one
# is kept as it was, never replaced by less.
#
#   bash warehouse/refresh_board.sh            # under the data lock, each step recorded in erw_health
#
# The six series session 132 added are pulled here, each from 2019 whole (EIA's revisions are picked up): about 44,000
# rows a day from EIA's API, 6,100 from FRED, 460 from the IMF and one workbook from California's Air Resources Board.
# Weekly and monthly publishers answer the same rows on most days; the tables are rewritten only where a row changed.
# The board's own files are then built from the tables as they stand: board_page.py makes no request and needs no lock
# (it writes under site/, not warehouse/output). The futures are a closed history and are not asked for.
# Every step goes through warehouse/health.py, so a failure is retried once, recorded, and never fails a job; the
# board is built from whatever the tables hold.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python}"
NEW="eia_regional_retail_fuel_prices eia_crude_stream_prices eia_power_plant_fuel_costs fred_treasury_yields imf_commodity_prices carb_lcfs_credit_prices"
"$PY" warehouse/health.py run --step "eia_board" -- "$PY" warehouse/connectors/eia_board.py
"$PY" warehouse/health.py run --step "fred_treasury" -- "$PY" warehouse/connectors/fred_treasury.py
"$PY" warehouse/health.py run --step "imf_pcps" -- "$PY" warehouse/connectors/imf_pcps.py
"$PY" warehouse/health.py run --step "carb_lcfs" -- "$PY" warehouse/connectors/carb_lcfs.py
FILES=""
# session 166: only the tables on this machine (on the runner carb_lcfs_credit_prices is never there, a known gap, and
# the validator answered exit 2 "bad input" for the missing file, so "board validate" failed every day)
for t in $NEW; do [ -f "warehouse/output/$t.csv" ] && FILES="$FILES warehouse/output/$t.csv"; done
# shellcheck disable=SC2086
"$PY" warehouse/health.py run --step "board validate" --retries 0 -- "$PY" warehouse/validate/erw_validate.py $FILES
"$PY" warehouse/health.py run --step "board_page" -- "$PY" warehouse/derived/page_keep.py board
