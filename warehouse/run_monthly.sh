#!/usr/bin/env bash
# Energy Research Warehouse (ERW), the monthly job (session 114): the six builders that were run by hand.
#
# Session 112's state document listed seven pages in review that read a file someone built by hand. The network's
# replay is rebuilt by the daily run (warehouse/run_daily.sh). The other six are rebuilt here, once a month:
#
#   mix_profile          /mix/v2            generation_mix_hourly_profile, generation_mix_records, site/data/mix/
#   price_compare        /prices/compare    hub_price_comparison, site/data/price_compare.json
#   demand_growth        /demand            eia930_demand_growth, site/data/demand_growth.json
#   curtailment_profile  /curtailment/v2    caiso_curtailment_profile, site/data/curtailment_profile.json
#   project_map          /map/v2            site/data/map_v2.json (no warehouse table)
#   large_load_snapshot  /datacenters/v2    site/data/large_load_status.json (no warehouse table)
#
# The daily run starts it with its first run on or after the third day of each month, UTC (EIA-930's lag of a day or
# two is past, so the month before is whole; warehouse/scheduled.py --monthly-due reads whether the month's job has
# run), or on any day with MONTHLY=1, after its last connector and before its validator, so the tables
# rebuilt here pass the same gate, coverage, archive, live-set load and Redivis draft as every other table of the run.
# By hand, on the data machine, under the data lock:
#
#   python warehouse/lock.py run --task "monthly builds" --minutes 60 -- bash warehouse/run_monthly.sh
#   PYTHON=.venv/Scripts/python bash warehouse/run_monthly.sh        # then the validator, coverage and the stores
#
# Each step runs under warehouse/health.py without --strict (warehouse/soft_step.sh): a failure is tried once more,
# recorded in erw_health and in the status file, and never fails the run. Each builder is started by
# warehouse/scheduled.py, which looks for the builder's inputs first: where one is not on the machine (the GitHub runner
# holds only what the daily run restores or pulls) it is rebuilt from the ERW's own archive if the step allows it, and
# otherwise the step is a skip with the reason and the page keeps the copy it has. No builder here makes a request to a
# publisher, and none writes a partial table. Each page prints the date its copy was built.
#
# What the GitHub runner cannot rebuild (python warehouse/scheduled.py <step> --check says so on any machine):
# price_compare needs the ERCOT price history (ercot_all_hub_prices_history, never restored there), so on the runner it
# is a skip each month and is rebuilt on the data machine. The curtailment profile and the large-load figures are only
# as new as their tables, which a person pulls (caiso_curtailment_intervals, ercot_large_load_status).

set -uo pipefail

PYTHON="${PYTHON:-python}"
cd "$(dirname "$0")/.."
mkdir -p runs
status="${STATUS_FILE:-runs/monthly_status.txt}"
[ -n "${STATUS_FILE:-}" ] || : > "$status"
. warehouse/soft_step.sh

echo "== ERW monthly builds $(date -u +%FT%TZ) (session 114)"
for name in mix_profile price_compare demand_growth curtailment_profile project_map large_load_snapshot; do
  soft_step "$name" "$PYTHON" warehouse/scheduled.py "$name"
done
if [ -z "${STATUS_FILE:-}" ]; then
  echo "== monthly status"
  cat "$status"
fi
echo "== monthly builds done"
