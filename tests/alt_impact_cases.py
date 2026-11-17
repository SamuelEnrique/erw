"""Helper of the ruling alternatives of /impact (session 7706, 17 November 2026; the wip/alt-impact-* branches, not a
default on main): runs the page's own model (site/scripts/alt-impact-figures.mjs) on cases, with JEDI's rows read from
nlr_jedi_multipliers.csv in warehouse/output or the folder ERW_TABLES_DIR names. JEDI_CSV is None where the table is not
on the machine; a test then skips."""

import json
import os
import subprocess
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")
TABLES = os.environ.get("ERW_TABLES_DIR") or os.path.join(ROOT, "warehouse", "output")
_csv = os.path.join(TABLES, "nlr_jedi_multipliers.csv")
JEDI_CSV = _csv if os.path.exists(_csv) else None


def run_cases(cases):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "cases.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cases, f)
        p = subprocess.run(["node", "--import", "./scripts/tsx-register.mjs", "scripts/alt-impact-figures.mjs", JEDI_CSV, path],
                           cwd=SITE, capture_output=True, text=True, timeout=600)
    if p.returncode != 0:
        raise AssertionError(p.stderr[-2000:])
    return json.loads(p.stdout)


def M(v):
    """A figure in millions, to two decimals, as the impact file writes it; None stays None."""
    return None if v is None else round(v / 1e6, 2)
