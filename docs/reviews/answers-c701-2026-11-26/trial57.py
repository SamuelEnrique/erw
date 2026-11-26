"""Window D's request 57 (chain 701): run one of the held builders (warehouse/derived/<name>.py) with its tables written
to a trial folder instead of warehouse/output. The folder holds hard links to main's tables (made by trial57_tree.py);
every writer in iso_prices and the builders writes a temporary file and renames it over the path, so a rewritten table
replaces only the trial folder's link and main's file is never opened for writing. The run's status file goes to the
trial folder, and sources.csv is not touched (update_sources does nothing here). No data lock: nothing is written in
warehouse/output (iso_prices._require_lock exempts a path outside it). Set ERW_SCREEN_TRIAL=1 for the build with the rule.

    .venv/Scripts/python.exe runs/c701/trial57.py warehouse/derived/carbon_intensity.py runs/c701/trial57/after [builder args]
"""
import os
import runpy
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
builder = os.path.abspath(sys.argv[1])
out = os.path.abspath(sys.argv[2])
if os.path.commonpath([out, os.path.join(ROOT, "warehouse", "output")]) == os.path.join(ROOT, "warehouse", "output"):
    raise SystemExit("the trial folder must not be warehouse/output")
sys.argv = [builder] + sys.argv[3:]
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
sys.path.insert(0, os.path.dirname(builder))
import iso_prices as ip  # noqa: E402

ip.OUT_DIR = out
ip.STATUS_DIR = os.path.join(out, "_status")
ip.update_sources = lambda *a, **k: None
print(f"trial: {os.path.basename(builder)} writing to {out}; ERW_SCREEN_TRIAL={os.environ.get('ERW_SCREEN_TRIAL', '')}", flush=True)
runpy.run_path(builder, run_name="__main__")
