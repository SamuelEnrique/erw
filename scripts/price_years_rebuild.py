#!/usr/bin/env python3
"""The price years, rebuilt and loaded in one command (session 5504, chain 269): data request row 4, made ready.

Energy Research Warehouse (ERW). `price_years_by_window` feeds the "Price years" choice of the three economics pages
(docs/methods/price_years.md). The live set's copy was built once, on 2026-10-20T09:08:39Z, so on 13 November the
battery page's CAISO default read 79.31 beside its headline's 79.80 and the datacenter page's 33.73 beside 34.07
(battery faults row 10, datacenter faults row 4; docs/state/data_requests_five_tools.md, rows 4 and 5). Rebuilding it
is four commands and a load; this script runs them in order, reads every exit code, stops at the first failure, and
proves the result against the live set before and after.

    python scripts/price_years_rebuild.py             # check: a trial in a temporary folder (no lock; nothing in the
                                                      # repository but the builder's run log in warehouse/output/logs,
                                                      # not in git), its default windows set beside the live set's
    python scripts/price_years_rebuild.py --apply     # the data machine (window A): the data lock, the build into
                                                      # warehouse/output, the validator, the coverage row, the load of
                                                      # this one table, the read back, the lock released

On Windows run it with the repository's interpreter, `.venv\\Scripts\\python.exe scripts\\price_years_rebuild.py`;
every step it starts runs with the same interpreter. Run `scripts/sync.py` first, so the tables the build reads (the
live set's battery rows, site/data/merchant_snapshot.json, site/data/datacenter/) are main's.

--apply refuses on a machine whose role is not "data" (.erw/machine.json, warehouse/lock.py), and while
scripts/freeze.py says a freeze holds. If any of the three pages is live in site/lib/release.ts, the load needs rule 8's
snapshot before and after: the script takes both and compares them (`node site/scripts/snapshot-live.mjs`). On
14 November 2026 none is live, so no snapshot is required.

Standard library only. Exit 0 done (check: the trial was built and proved); 1 a step failed (named); 2 refused or bad
input.
"""

import argparse
import csv
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = "price_years_by_window"
PAGES = ("/cost-of-power/battery", "/cost-of-power/seller", "/cost-of-power")
# the default windows the faults rows name, read first in the comparison (entity, variable)
WATCHED = [
    ("caiso:TH_SP15_GEN-APND", "battery_foresight_4h_last_12"),
    ("ercot:HB_HUBAVG", "battery_foresight_4h_last_12"),
    ("ercot:LZ_NORTH", "datacenter_flat_rt_last_12"),
    ("caiso:TH_SP15_GEN-APND", "datacenter_flat_rt_last_12"),
    ("ercot:HB_HUBAVG", "generator_solar_last_12"),
]
CENT = 0.005


def env(name):
    """A setting from the environment, else the repository's .env (never printed)."""
    if os.environ.get(name):
        return os.environ[name]
    path = os.path.join(ROOT, ".env")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                m = re.match(r"^([A-Z_]+)=(.*)$", line.strip())
                if m and m.group(1) == name:
                    return m.group(2).strip().strip('"')
    return None


def run(cmd, label):
    """One step, its own exit code read (never piped); the command printed with the repository-relative paths."""
    shown = " ".join(os.path.relpath(c, ROOT) if os.path.isabs(c) and c.startswith(ROOT) else c for c in cmd)
    print(f"\n== {label}: {shown}", flush=True)
    r = subprocess.run(cmd, cwd=ROOT, stdin=subprocess.DEVNULL)
    print(f"== {label}: exit {r.returncode}", flush=True)
    return r.returncode


def read_table(path):
    """The rows of a price years CSV (its '#' header skipped), keyed (entity, variable)."""
    with open(path, encoding="utf-8", newline="") as f:
        lines = [ln for ln in f if not ln.startswith("#")]
    out = {}
    for r in csv.DictReader(lines):
        out[(r["entity"], r["variable"])] = r
    return out


def header_line(path, starts):
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if not ln.startswith("#"):
                break
            if ln[2:].startswith(starts):
                return ln[2:].strip()
    return None


def live_rows(variable_like="*last_12", fetch=None):
    """The live set's rows of the table whose variable matches, read with the anon key as the site reads them."""
    url, key = env("SUPABASE_URL"), env("SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_ANON_KEY is not set: the live set cannot be read")
    p = urllib.parse.urlparse(url)
    base = f"{p.scheme}://{p.netloc}"
    out = {}
    for offset in range(0, 100_000, 1000):
        q = urllib.parse.urlencode(dict(select="entity,variable,ts_utc,value,freq,retrieved_at,loaded_at", table_name=f"eq.{TABLE}",
                                        variable=f"like.{variable_like}", order="entity,variable", limit=1000, offset=offset))
        req = urllib.request.Request(f"{base}/rest/v1/series?{q}", headers=dict(apikey=key, Authorization=f"Bearer {key}"))
        page = (fetch or (lambda r: json.load(urllib.request.urlopen(r, timeout=60))))(req)
        for r in page:
            out[(r["entity"], r["variable"])] = r
        if len(page) < 1000:
            break
    return out


def months(freq):
    m = re.match(r"^P(\d+)M$", str(freq or ""))
    return int(m.group(1)) if m else None


def compare(live, built):
    """Each default window (last_12) beside the live set's: the watched ones first, then every other one that moved.
    Returns the lines and the count of windows that moved."""
    keys = [k for k in WATCHED if k in live or k in built]
    keys += sorted(k for k in set(live) | set(built) if k[1].endswith("_last_12") and k not in WATCHED)
    lines, moved = [], 0
    for k in keys:
        a, b = live.get(k), built.get(k)
        fa = f"{a['ts_utc'][:7]} +{months(a['freq'])}m {float(a['value']):.2f}" if a else "not in the live set"
        fb = f"{b['ts_utc'][:7]} +{months(b['freq'])}m {float(b['value']):.2f}" if b else "not built"
        same = a is not None and b is not None and a["ts_utc"][:10] == b["ts_utc"][:10] and abs(float(a["value"]) - float(b["value"])) < CENT
        if not same:
            moved += 1
        if k in WATCHED or not same:
            lines.append(f"{k[0]} {k[1]}: live {fa}; built {fb}{'' if same else '  (moves)'}")
    return lines, moved


def live_pages():
    """The three pages' status in site/lib/release.ts: those marked live (rule 8 then asks for a snapshot)."""
    text = open(os.path.join(ROOT, "site", "lib", "release.ts"), encoding="utf-8").read()
    return [p for p in PAGES if re.search(rf'"{re.escape(p)}":\s*"live"', text)]


def role():
    path = os.path.join(ROOT, ".erw", "machine.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f).get("role")


def check(py, keep=False):
    tmp = tempfile.mkdtemp(prefix="erw-price-years-")
    try:
        code = run([py, os.path.join(ROOT, "warehouse", "derived", "price_years.py"), "--out-dir", tmp, "--live"], "the trial build")
        path = os.path.join(tmp, TABLE + ".csv")
        if code != 0 or not os.path.exists(path):
            print(f"\nFAILED: the trial build (exit {code}); no table was written in the repository (its run log is in warehouse/output/logs)")
            return 1
        built = read_table(path)
        print(f"\nthe trial: {len(built)} rows; {header_line(path, 'Proof of the default window') or 'no proof line'}")
        lines, moved = compare(live_rows(), {k: v for k, v in built.items() if k[1].endswith("_last_12")})
        print("\nthe default windows (last twelve months), the live set beside the trial:")
        for ln in lines:
            print("  " + ln)
        print(f"\n{moved} default windows would move. To build and load on the data machine: python scripts/price_years_rebuild.py --apply")
        return 0
    finally:
        if keep:
            print(f"(the trial kept in {tmp})")
        else:
            shutil.rmtree(tmp, ignore_errors=True)


def apply(py, snapshot_dir):
    if role() != "data":
        print(f"refused: this machine's role is {role() or 'not set'}; the load is the data machine's (.erw/machine.json, warehouse/lock.py)")
        return 2
    if run([py, os.path.join(ROOT, "scripts", "freeze.py"), "status"], "the freeze") != 0:
        print("refused: scripts/freeze.py says a freeze holds (or its file cannot be read); the load waits for a prompt that names it")
        return 2
    live = live_pages()
    started = dt.datetime.now(dt.timezone.utc)
    stamp = started.strftime("%Y%m%dT%H%M%SZ")
    before = after = None
    if live:
        print(f"live pages that read the table: {', '.join(live)}: rule 8's snapshot before and after")
        before = os.path.join(snapshot_dir, f"price-years-before-{stamp}")
        if run(["node", os.path.join(ROOT, "site", "scripts", "snapshot-live.mjs"), "take", before], "the snapshot before") != 0:
            return 1
    else:
        print("no page that reads the table is live (site/lib/release.ts): rule 8's snapshot is not required")
    old = live_rows()
    if run([py, os.path.join(ROOT, "warehouse", "lock.py"), "acquire", "--task", "price-years", "--minutes", "60"], "the data lock") != 0:
        print("refused: the data lock was not taken")
        return 2
    failed = None
    try:
        steps = [
            ([py, os.path.join(ROOT, "warehouse", "derived", "price_years.py"), "--live"], "the build"),
            ([py, os.path.join(ROOT, "warehouse", "validate", "erw_validate.py"), os.path.join(ROOT, "warehouse", "output", TABLE + ".csv")], "the validator"),
            ([py, os.path.join(ROOT, "warehouse", "metadata", "build_coverage.py"), "--only", f"^{TABLE}$"], "the coverage row"),
            ([py, os.path.join(ROOT, "warehouse", "supabase", "load.py"), "--only", f"^{TABLE}$"], "the load"),
        ]
        for cmd, label in steps:
            if run(cmd, label) != 0:
                failed = label
                break
    finally:
        run([py, os.path.join(ROOT, "warehouse", "lock.py"), "release"], "the lock released")
    if failed:
        print(f"\nFAILED at {failed}: nothing after it ran; the live set keeps what it held")
        return 1
    built = read_table(os.path.join(ROOT, "warehouse", "output", TABLE + ".csv"))
    new = live_rows()
    lines, moved = compare(new, {k: v for k, v in built.items() if k[1].endswith("_last_12")})
    stale = [k for k, r in new.items() if (r.get("retrieved_at") or "") < started.strftime("%Y-%m-%dT%H:%M:%S")]
    print("\nthe read back, the live set beside the file just built:")
    for ln in lines:
        print("  " + ln)
    was, _ = compare(old, {k: v for k, v in built.items() if k[1].endswith("_last_12")})
    print("\nbefore the load, the live set beside the same file:")
    for ln in was:
        print("  " + ln)
    if live:
        after = os.path.join(snapshot_dir, f"price-years-after-{stamp}")
        run(["node", os.path.join(ROOT, "site", "scripts", "snapshot-live.mjs"), "take", after], "the snapshot after")
        run(["node", os.path.join(ROOT, "site", "scripts", "snapshot-live.mjs"), "compare", before, after], "the comparison")
    if moved or stale:
        print(f"\nNOT PROVEN: {moved} default windows differ from the file, {len(stale)} rows retrieved before this run")
        return 1
    print(f"\ndone: {len(built)} rows built and loaded at {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC; "
          "every default window of the live set is the file's. Mark data request rows 4 and 5 done with the commit of the "
          "coverage row; window P1 then reads battery faults row 10 and datacenter faults row 4 again.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the price years rebuilt and loaded in one command (session 5504)")
    ap.add_argument("--apply", action="store_true", help="the data machine: lock, build, validate, coverage, load, read back")
    ap.add_argument("--keep", action="store_true", help="check: keep the trial's folder and say where")
    ap.add_argument("--snapshot-dir", default=os.path.join(ROOT, "runs", "snapshots"), help="apply: where rule 8's snapshots go when a page is live")
    a = ap.parse_args(argv)
    py = sys.executable
    try:
        return apply(py, a.snapshot_dir) if a.apply else check(py, keep=a.keep)
    except RuntimeError as e:
        print(f"FAILED: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
