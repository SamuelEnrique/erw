#!/usr/bin/env bash
# ERW: set up a macOS or Linux machine (session 59). docs/machines.md.
#
#   bash scripts/setup.sh --role data --name lab-machine
#   bash scripts/setup.sh --role code --name portable-laptop [--skip-site] [--skip-sync]
#
# Checks git, Python, Node and Claude Code; makes .venv and installs the Python requirements; installs the site's packages;
# checks that .env names every key the role needs (never prints a value); sets the machine's role; syncs from the cloud.
# Keeping the machine awake and starting the worker at logon need the system's own tools; the script prints the commands
# (pmset or caffeinate on macOS, systemd-inhibit and a user service on Linux) rather than changing system settings.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
role="" name="$(hostname -s 2>/dev/null || hostname)" site=1 dosync=1
while [ $# -gt 0 ]; do
  case "$1" in
    --role) role="$2"; shift 2 ;;
    --name) name="$2"; shift 2 ;;
    --skip-site) site=0; shift ;;
    --skip-sync) dosync=0; shift ;;
    *) echo "unknown argument: $1"; exit 2 ;;
  esac
done
[ "$role" = data ] || [ "$role" = code ] || { echo "--role data or --role code"; exit 2; }
problems=()

echo "== tools"
for t in git python3 node npm; do command -v "$t" >/dev/null || problems+=("$t is not installed or not on PATH"); done
command -v claude >/dev/null || problems+=("Claude Code is not installed (npm install -g @anthropic-ai/claude-code, then run claude once to sign in); the worker needs it")

echo "== Python environment (.venv)"
[ -x .venv/bin/python ] || python3 -m venv .venv
py=.venv/bin/python
ver="$($py -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
$py -m pip install -q --upgrade pip
if [ "$ver" = "3.14" ]; then $py -m pip install -q --no-deps -r requirements-py314.txt; else $py -m pip install -q -r requirements.txt; fi
echo "  Python $ver, requirements installed"

if [ "$site" = 1 ]; then echo "== site packages"; (cd site && npm ci --silent); fi

echo "== .env"
need=(SUPABASE_URL SUPABASE_SERVICE_KEY SUPABASE_ANON_KEY)
[ "$role" = data ] && need+=(SUPABASE_DB_URL EIA_API_KEY REDIVIS_API_TOKEN REDIVIS_OWNER ANTHROPIC_API_KEY)
if [ ! -f .env ]; then problems+=(".env is missing: copy it from the password manager into $root")
else
  for k in "${need[@]}"; do grep -qE "^$k=.+" .env || problems+=(".env has no value for $k (needed by a $role machine)"); done
  echo "  ${#need[@]} keys checked (values not shown)"
fi

echo "== role"
$py warehouse/lock.py role "$role" --name "$name"

if [ "$dosync" = 1 ]; then
  echo "== sync"
  if [ "$role" = data ]; then $py scripts/sync.py; else $py scripts/sync.py --check; fi
fi

echo "== keep awake and the worker (by hand, once)"
case "$(uname -s)" in
  Darwin)
    echo "  never sleep on AC power:   sudo pmset -c sleep 0 disksleep 0"
    echo "  or only while the worker runs: caffeinate -s bash scripts/worker.sh"
    echo "  worker at logon: a LaunchAgent in ~/Library/LaunchAgents running $root/scripts/worker.sh with KeepAlive true" ;;
  *)
    echo "  while the worker runs: systemd-inhibit --what=sleep bash scripts/worker.sh"
    echo "  worker at logon: a systemd user service (ExecStart=$root/scripts/worker.sh, Restart=always), then systemctl --user enable --now erw-worker" ;;
esac

if [ ${#problems[@]} -gt 0 ]; then
  echo "== not ready:"; for p in "${problems[@]}"; do echo "  - $p"; done; exit 1
fi
echo "== ready: $name is a $role machine"
