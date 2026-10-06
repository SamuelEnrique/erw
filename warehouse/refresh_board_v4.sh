#!/usr/bin/env bash
# The price board, version 4: its daily refresh (session 127). WRITTEN, NOT SCHEDULED: no workflow and no line of
# run_daily.sh calls this while the review freeze is on. To switch it on, a person adds the one step below to
# warehouse/run_daily.sh after "price_board" (the tables it reads are already refreshed by then) and, once /board/v4
# opens, takes price_board_stats off catalogue_hold and gives it a live-set rule so the page reads the live set.
#
#   bash warehouse/refresh_board_v4.sh            # under the data lock, each step recorded in erw_health
#
# It makes no request of its own for the board: price_board_v4.py reads eia_fuel_spot_prices,
# eia_product_spot_prices, iso_hub_prices_history and ercot_hub_prices_daily, which the daily run keeps. Run alone (not
# after the daily run), it first refreshes EIA's two spot tables, which is the pull session 127 was approved for.
# EIA's futures are a closed history (they end on 5 April 2024): warehouse/connectors/eia_futures.py is not run here.
# Every step goes through warehouse/health.py, so a failure is retried once, recorded, and never fails a job.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python}"
if [ "${BOARD_V4_WITH_SPOT:-0}" = "1" ]; then
  "$PY" warehouse/health.py run --step "eia_fuels" -- "$PY" warehouse/connectors/eia_fuels.py
  "$PY" warehouse/health.py run --step "eia_series" -- "$PY" warehouse/connectors/eia_series.py
fi
"$PY" warehouse/health.py run --step "price_board_v4" -- "$PY" warehouse/derived/price_board_v4.py
"$PY" warehouse/health.py run --step "price_board_v4 validate" --retries 0 -- "$PY" warehouse/validate/erw_validate.py warehouse/output/price_board_stats.csv
