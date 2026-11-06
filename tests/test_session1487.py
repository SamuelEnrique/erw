"""Session 1487 (chain 158): the battery's replication a reader can run (replication/battery/). It reads only the page's
public dispatch file and its own assumptions, recomputes the page's headline figures with the page's published mirror,
and meets every figure the page shows for the same months to half of the page's last shown digit.

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import copy
import importlib.util
import json
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "replication", "battery")
CSV = os.path.join(ROOT, "site", "public", "battery", "erw_2026_battery_dispatch.csv")


def module():
    spec = importlib.util.spec_from_file_location("replicate_battery", os.path.join(REP, "replicate.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(CSV):
            raise unittest.SkipTest("the public dispatch file is not in this copy")
        cls.r = module()
        cls.a = cls.r.load(os.path.join(REP, "assumptions.json"))
        cls.page = cls.r.load(os.path.join(REP, "page_figures.json"))
        m = cls.r.mirror(cls.a)
        cls.rows = m.read(CSV)
        cls.n = m.numbers(cls.rows)

    def test_every_figure_inside_its_tolerance(self):
        rows = self.r.compare(self.n, self.page)
        self.assertEqual(len(rows), 22)
        self.assertEqual([r[0] for r in rows if not r[5]], [])

    def test_the_script_exits_0(self):
        p = subprocess.run([sys.executable, os.path.join(REP, "replicate.py")], capture_output=True, text=True, timeout=300)
        self.assertEqual(p.returncode, 0, p.stdout[-2000:] + p.stderr[-2000:])
        self.assertIn("22 of 22 inside the tolerance", p.stdout)

    def test_the_assumptions_drive_the_figures(self):
        a = copy.deepcopy(self.a)
        a["debt_share"]["value"] = 0.6   # the default until the owner's ruling of 12 October 2026
        n = self.r.mirror(a).numbers(self.rows)
        self.assertEqual(n["debt_service"], 6783357)   # docs/methods/battery_earns_algorithm.md, section 4.3
        self.assertEqual(n["l12_total_usd"], self.n["l12_total_usd"])   # the revenue does not move with the debt

    def test_the_assumptions_are_the_mirrors_defaults(self):
        m = self.r.mirror(self.a)
        spec = importlib.util.spec_from_file_location("mirror_plain", self.r.MIRROR)
        plain = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plain)
        for const in self.r.CONSTANTS:
            self.assertEqual(getattr(m, const), getattr(plain, const), const)


if __name__ == "__main__":
    unittest.main()
