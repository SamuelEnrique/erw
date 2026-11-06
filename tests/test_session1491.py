"""Session 1491 (chain 158): the datacenter's replication a reader can run (replication/datacenter/). It reads only the
page's public hourly and carbon files and its own assumptions, recomputes the page's headline figures with the page's
published mirror, and meets the page's figures for the same months to half of the last shown digit, but for the one
difference page_figures.json names (the flat load's carbon over the hourly window: 309.84 against the page's 311.68).

No network, no warehouse table, no model. Nothing here sets the environment at import.
"""
import copy
import importlib.util
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REP = os.path.join(ROOT, "replication", "datacenter")
CSV = os.path.join(ROOT, "site", "public", "datacenter", "erw_2026_datacenter_hourly.csv")


def module():
    spec = importlib.util.spec_from_file_location("replicate_datacenter", os.path.join(REP, "replicate.py"))
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
        cls.n = cls.r.numbers_of(cls.r.mirror(cls.a), CSV)

    def test_every_figure_inside_its_tolerance_but_the_known_one(self):
        rows = self.r.compare(self.n, self.page)
        self.assertEqual(len(rows), 14)
        self.assertEqual([r[0] for r in rows if not r[6]], ["a flat load's own hours over the window, kg CO2 per MWh"])
        self.assertEqual([r[0] for r in rows if not r[5]], [])
        self.assertEqual(list(self.page["known_differences"]), ["window_kg_mwh"])

    def test_the_script_exits_0(self):
        p = subprocess.run([sys.executable, os.path.join(REP, "replicate.py")], capture_output=True, text=True, timeout=300)
        self.assertEqual(p.returncode, 0, p.stdout[-2000:] + p.stderr[-2000:])
        self.assertIn("13 of 14 inside the tolerance, 1 a known difference (window_kg_mwh)", p.stdout)

    def test_the_assumptions_drive_the_figures(self):
        a = copy.deepcopy(self.a)
        a["pue"]["value"] = 1.3
        n = self.r.numbers_of(self.r.mirror(a), CSV)
        self.assertNotEqual(round(n["gpu_hour"], 6), round(self.n["gpu_hour"], 6))
        self.assertEqual(n["l12_usd_mwh"], self.n["l12_usd_mwh"])   # the price of energy does not move with the overhead

    def test_the_assumptions_are_the_mirrors_defaults(self):
        m = self.r.mirror(self.a)
        spec = importlib.util.spec_from_file_location("mirror_plain_dc", self.r.MIRROR)
        plain = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plain)
        for const in self.r.CONSTANTS:
            self.assertEqual(getattr(m, const), getattr(plain, const), const)


if __name__ == "__main__":
    unittest.main()
