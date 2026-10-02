#!/usr/bin/env bash
# ERW: sync this machine from the cloud (session 59). macOS and Linux wrapper of scripts/sync.py; arguments pass through.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
py="$root/.venv/bin/python"; [ -x "$py" ] || py=python3
exec "$py" "$root/scripts/sync.py" "$@"
