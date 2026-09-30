"""Session 45: the loader's daily vacuum, and severance v0.2, the lease tool.

Energy Research Warehouse (ERW). No network, no model.
1. warehouse/supabase/load.py ends a daily load with a plain VACUUM (ANALYZE); VACUUM (FULL, ANALYZE) runs only with
   --vacuum-full (a stub connection records the statements; nothing reaches a database).
2. site/scripts/test-lease.mjs runs lib/lease.ts on lib/severance.ts (Node 23.6 or later runs the TypeScript as it is):
   a hand-computed three-well, two-month lease for each state, the flags at each threshold, and no network call while
   the sample is parsed, analysed and written.

    python -m unittest tests.test_session45 -v
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import types
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SITE = os.path.join(ROOT, "site")


def load_module():
    spec = importlib.util.spec_from_file_location("erw_supabase_load_s45", os.path.join(ROOT, "warehouse", "supabase", "load.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class StubConn:
    def __init__(self, log):
        self.log = log

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql):
        self.log.append(sql)
        return self

    def fetchone(self):
        return (1048576,)


class Vacuum(unittest.TestCase):
    def run_vacuum(self, full):
        log = []
        stub = types.SimpleNamespace(connect=lambda *a, **k: StubConn(log))
        saved = sys.modules.get("psycopg")
        sys.modules["psycopg"] = stub
        try:
            load_module().vacuum("postgresql://stub", full=full)
        finally:
            if saved is None:
                sys.modules.pop("psycopg", None)
            else:
                sys.modules["psycopg"] = saved
        return [s for s in log if s.startswith("VACUUM")]

    def test_the_daily_load_runs_a_plain_vacuum(self):
        got = self.run_vacuum(full=False)
        self.assertEqual(len(got), 6)
        self.assertTrue(all(s.startswith("VACUUM (ANALYZE) public.") for s in got), got)

    def test_full_only_on_request(self):
        got = self.run_vacuum(full=True)
        self.assertEqual(len(got), 6)
        self.assertTrue(all(s.startswith("VACUUM (FULL, ANALYZE) public.") for s in got), got)

    def test_the_flag_defaults_off_and_the_workflow_does_not_pass_it(self):
        src = open(os.path.join(ROOT, "warehouse", "supabase", "load.py"), encoding="utf-8").read()
        self.assertIn("vacuum(url, full=args.vacuum_full)", src)
        for wf in ("daily-prices.yml", "roundup.yml"):
            text = open(os.path.join(ROOT, ".github", "workflows", wf), encoding="utf-8").read()
            self.assertNotIn("--vacuum-full", text, wf)
        self.assertIn("--vacuum-full", open(os.path.join(ROOT, "docs", "runbook.md"), encoding="utf-8").read())


class Lease(unittest.TestCase):
    def test_hand_computed_leases_thresholds_and_no_network(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is not installed")
        r = subprocess.run([node, os.path.join("scripts", "test-lease.mjs")], cwd=SITE, capture_output=True, text=True,
                           timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("makes no network call", r.stdout)

    def test_the_page_says_the_file_stays_in_the_browser(self):
        page = open(os.path.join(SITE, "app", "severance", "lease", "page.tsx"), encoding="utf-8").read()
        self.assertIn("Your file stays on your computer.", page)
        self.assertIn("/severance/lease", open(os.path.join(SITE, "app", "severance", "page.tsx"), encoding="utf-8").read())

    def test_no_em_dash_in_the_new_files(self):
        for f in ("site/lib/lease.ts", "site/app/severance/lease/page.tsx", "site/app/severance/lease/LeaseTool.tsx",
                  "site/scripts/test-lease.mjs", "tests/test_session45.py"):
            self.assertNotIn(chr(0x2014), open(os.path.join(ROOT, f), encoding="utf-8").read(), f)


if __name__ == "__main__":
    unittest.main()
