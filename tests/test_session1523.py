"""Session 1523 (chain 163): the datacenter replication's one open difference settled. The page's own code
(site/lib/datacenter/answers.ts, run on the public carbon file by site/scripts/datacenter-window-on-file.mjs, no request
made) and the published mirror (site/public/datacenter/erw_2026_datacenter_replication.py, through
replication/datacenter/replicate.py) give the same carbon over the hourly window on the same rows: the hours, the
window's ends, and a flat load's kg CO2 per MWh, which is the grid's mean over those hours. Session 1491's 311.68 was a
local build's reading of the live set, whose window moves each day.

Needs node and the site's node_modules for the page's side; skipped without them. No network, no warehouse table, no
model. Nothing here sets the environment at import.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
REP = os.path.join(ROOT, "replication", "datacenter")
CSV = os.path.join(SITE, "public", "datacenter", "erw_2026_datacenter_hourly.csv")
SCRIPT = os.path.join(SITE, "scripts", "datacenter-window-on-file.mjs")


def mirror_numbers():
    spec = importlib.util.spec_from_file_location("replicate_datacenter_1523", os.path.join(REP, "replicate.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.numbers_of(m.mirror(m.load(os.path.join(REP, "assumptions.json"))), CSV)


class TheWindowOnTheFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(CSV):
            raise unittest.SkipTest("the public hourly file is not in this copy")
        if shutil.which("node") is None or not os.path.isdir(os.path.join(SITE, "node_modules")):
            raise unittest.SkipTest("node or the site's node_modules is not here")
        p = subprocess.run(["node", SCRIPT], cwd=SITE, capture_output=True, text=True, timeout=300)
        if p.returncode != 0:
            raise AssertionError(p.stdout[-2000:] + p.stderr[-2000:])
        cls.page = json.loads(p.stdout.strip().splitlines()[-1])["window"]
        cls.n = mirror_numbers()

    def test_the_same_hours(self):
        self.assertEqual(self.page["hours"], self.n["window_hours"])
        self.assertEqual(self.page["from"], self.n["window_from"])
        self.assertEqual(self.page["to"], self.n["window_to"])

    def test_the_same_carbon(self):
        self.assertAlmostEqual(self.page["ways"]["flat"], self.n["window_kg_mwh"], places=6)

    def test_a_flat_load_is_the_grid_mean(self):
        self.assertAlmostEqual(self.page["ways"]["flat"], self.page["grid"], places=9)

    def test_the_package_states_the_page_code_figure(self):
        with open(os.path.join(REP, "page_figures.json"), encoding="utf-8") as f:
            d = json.load(f)
        fig = next(x for x in d["figures"] if x["field"] == "window_kg_mwh")
        self.assertLessEqual(abs(fig["page"] - self.page["ways"]["flat"]), fig["tolerance"])
        self.assertEqual(d["known_differences"], {})


if __name__ == "__main__":
    unittest.main()
