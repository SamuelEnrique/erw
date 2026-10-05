# Energy Research Warehouse (ERW), session 114: a step that is recorded and never stops the run.
#
# Sourced by warehouse/run_daily.sh and warehouse/run_monthly.sh. Needs $PYTHON and $status (the run's status file).
#
#   soft_step <name> <command...>
#
# runs the command under warehouse/health.py without --strict: a failure is tried once more, then written to erw_health
# (and so to the day's health summary) and to the status file as "failed", and the exit is 0, so the run goes on to the
# validator, coverage and the stores with the tables it has. A step that decides it should not run (its inputs are not
# on the machine) exits ERW_SKIP_EXIT and is a skip with its reason. Nothing here is a gate.
soft_step() {
  local name="$1"; shift
  local out="runs/daily_${name}.out"
  "$PYTHON" warehouse/health.py run --step "$name" -- "$@" > "$out" 2>&1
  local rc=$?
  grep -E "\.csv: rows=|FAILED|SKIPPED|^::(notice|warning)" "$out" | grep -vE " - (INFO|DEBUG|WARNING) - "
  if [ "$rc" -ne 0 ]; then
    # health.py itself did not finish (it returns 0 for every outcome of the step)
    echo "$name failed: warehouse/health.py exit $rc; the run goes on" >> "$status"
    tail -5 "$out"
  elif grep -q "^::warning title=${name} failed" "$out"; then
    echo "$name failed: $(grep -m1 "^::warning title=${name} failed" "$out" | sed 's/^::warning title=[^:]*:://' | cut -c1-200) (recorded in erw_health; the run goes on)" >> "$status"
  elif grep -q "^::notice::${name} skipped" "$out"; then
    echo "$name skipped: $(grep -m1 "^::notice::${name} skipped" "$out" | sed "s/^::notice::${name} skipped: //" | sed "s/^${name} SKIPPED: //" | cut -c1-300)" >> "$status"
  else
    echo "$name ok" >> "$status"
  fi
  return 0
}
