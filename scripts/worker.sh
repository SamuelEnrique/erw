#!/usr/bin/env bash
# ERW: the queue worker (session 59). macOS and Linux wrapper of scripts/worker.py; arguments pass through.
# Runs until stopped (Ctrl+C); docs/machines.md says how to start it at logon.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
py="$root/.venv/bin/python"; [ -x "$py" ] || py=python3
cd "$root"
exec "$py" "$root/scripts/worker.py" "$@"
