"""Session 1616 (chain 165): the board's checks, extended to what the chain added, run on the board's files.

Held here: scripts/check-board.mjs --file runs the file's own checks (lib/board.ts boardFileChecks) with no served page
and passes on the site's file; on a file the builder writes from this chain's fixtures (ERCOT's zones, gas storage and
LNG, the coincident peaks), every check but the floors (a fixture is a few rows) passes and judges the day extremes,
the twelve-month means and the year-to-date moves; a file broken on purpose fails the check that should catch it. No
network, no model. Nothing here sets the environment at import.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "warehouse", "derived")
SITE = os.path.join(ROOT, "site")
FIXTURES = os.path.join(ROOT, "tests", "fixtures")


def builder():
    if DERIVED not in sys.path:
        sys.path.insert(0, DERIVED)
    import board_page  # noqa: E402
    return board_page


def node_ready():
    exe = shutil.which("node")
    if not exe or not os.path.isdir(os.path.join(SITE, "node_modules")):
        raise unittest.SkipTest("node or the site's packages are not here")
    return exe


def built_file(tmp):
    """A board file from the fixtures, through the builder's own steps and write_site."""
    bp = builder()
    saved, absent, intervals = bp.ip.OUT_DIR, list(bp.ABSENT), dict(bp.INTERVALS)
    try:
        b = bp.Board()
        bp.ip.OUT_DIR = os.path.join(FIXTURES, "board_1601")
        store = bp.hourly_store(lambda s: None, tables=["ercot_zone_prices_history"])
        bp.build_power(b, store, bp.pb.nerc_holidays(range(2025, 2028)), lambda s: None)
        bp.ip.OUT_DIR = os.path.join(FIXTURES, "board_1602")
        bp.build_gasflows(b, lambda s: None)
        bp.ip.OUT_DIR = os.path.join(FIXTURES, "board_1604")
        bp.build_costs(b, lambda s: None)
        bp.write_site(b, [], [], tmp, "2026-10-15T00:00:00Z", lambda s: None)
    finally:
        bp.ip.OUT_DIR, bp.ABSENT[:] = saved, absent
        bp.INTERVALS.clear(); bp.INTERVALS.update(intervals)
    return os.path.join(tmp, "data", "board.json")


def checks(exe, path, breaker=""):
    script = ("import fs from 'node:fs'; const b = await import('./lib/board.ts');"
              f"const f = JSON.parse(fs.readFileSync({json.dumps(path)}, 'utf-8'));" + breaker +
              "process.stdout.write(JSON.stringify(b.boardFileChecks(f)));")
    r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "--input-type=module", "-e", script], cwd=SITE,
                       capture_output=True, text=True, timeout=300, encoding="utf-8")
    if r.returncode != 0 and "Unknown file extension" in r.stderr:
        raise unittest.SkipTest("this node does not read TypeScript files")
    if r.returncode != 0:
        raise AssertionError(r.stderr)
    return json.loads(r.stdout)


class TheChecks(unittest.TestCase):
    def test_the_site_file_passes_with_no_server(self):
        exe = node_ready()
        r = subprocess.run([exe, "--import", "./scripts/alias-register.mjs", "scripts/check-board.mjs", "--file"], cwd=SITE,
                           capture_output=True, text=True, timeout=300, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("checks of the file passed", r.stdout)

    def test_a_file_of_the_new_builder(self):
        exe = node_ready()
        with tempfile.TemporaryDirectory() as tmp:
            got = checks(exe, built_file(tmp))
        whats = {c["what"].split(" (")[0]: c for c in got}
        failed = [c["what"] for c in got if not c["ok"]]
        self.assertTrue(all("floor" in w for w in failed), failed)               # a fixture is a few rows: only the floors fail
        ext = next(c for c in got if c["what"].startswith("every day's high"))
        self.assertTrue(ext["ok"] and "(0 rows)" not in ext["what"], ext["what"])
        avg = next(c for c in got if c["what"].startswith("every twelve-month mean"))
        self.assertTrue(avg["ok"], avg["what"])
        self.assertTrue(whats["every row of the groups chain 165 added says its interval or its formula"]["ok"])

    def test_a_broken_file_is_caught(self):
        exe = node_ready()
        with tempfile.TemporaryDirectory() as tmp:
            path = built_file(tmp)
            broken = checks(exe, path, "const r = f.rows.find((x) => x.ext); r.ext.lo.v = r.ext.hi.v + 1;"
                                       "const g = f.rows.find((x) => x.status !== 'ok'); g.last = { t: '2026-10-13', v: 1 };")
        failed = [c["what"] for c in broken if not c["ok"]]
        self.assertTrue(any(w.startswith("every day's high") for w in failed), failed)
        self.assertTrue(any(w.startswith("every row with no value") for w in failed), failed)


if __name__ == "__main__":
    unittest.main()
