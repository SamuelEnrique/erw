"""Session 1489 (chain 158): the generator's replication a reader can run (replication/generator/). It reads only the page's
public hourly file and its own assumptions, recomputes the page's headline figures with the page's published mirror,
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
REP = os.path.join(ROOT, "replication", "generator")
CSV = os.path.join(ROOT, "site", "public", "seller", "erw_2026_generator_hourly.csv")


def module():
    spec = importlib.util.spec_from_file_location("replicate_generator", os.path.join(REP, "replicate.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheReplication(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(CSV):
            raise unittest.SkipTest("the public hourly file is not in this copy")
        cls.r = module()
        cls.a = cls.r.load(os.path.join(REP, "assumptions.json"))
        cls.page = cls.r.load(os.path.join(REP, "page_figures.json"))
        m = cls.r.mirror(cls.a)
        cls.rows = m.read(CSV)
        cls.n = cls.r.numbers_of(m, CSV)

    def test_every_figure_inside_its_tolerance(self):
        rows = self.r.compare(self.n, self.page)
        self.assertEqual(len(rows), 13)
        self.assertEqual([r[0] for r in rows if not r[5]], [])

    def test_the_script_exits_0(self):
        p = subprocess.run([sys.executable, os.path.join(REP, "replicate.py")], capture_output=True, text=True, timeout=300)
        self.assertEqual(p.returncode, 0, p.stdout[-2000:] + p.stderr[-2000:])
        self.assertIn("13 of 13 inside the tolerance", p.stdout)

    def test_the_assumptions_drive_the_figures(self):
        a = copy.deepcopy(self.a)
        a["degradation"]["value"] = 0.0   # no degradation, the default until session 298's ruling 7a
        n = self.r.mirror(a).numbers(self.rows)
        self.assertEqual(round(n["npv_million"], 2), -74.16)   # docs/methods/generator_earns_algorithm.md: -74.16 until 7a
        self.assertEqual(n["debt_service"], self.n["debt_service"])

    def test_the_assumptions_are_the_mirrors_defaults(self):
        m = self.r.mirror(self.a)
        spec = importlib.util.spec_from_file_location("mirror_plain", self.r.MIRROR)
        plain = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plain)
        for const in self.r.CONSTANTS:
            self.assertEqual(getattr(m, const), getattr(plain, const), const)


if __name__ == "__main__":
    unittest.main()
