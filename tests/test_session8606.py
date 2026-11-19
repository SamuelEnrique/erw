"""Session 8606 (chain 504, 19 November 2026): the done line of the Grid tool's regions, its cross-check.

Energy Research Warehouse (ERW). replication/grid/crosscheck_regions.py sets the region files' hours beside EIA's own
published regional series (Form EIA-930, the open data API). What is held here: the folding of EIA's energy source
codes is the contract's, the latest hour is found by the page's rule, a source EIA returns no code for is not held
(never zero), the key is never written, and the output on the branch says what it found.
Nothing here makes a request or reads a key.
"""

import csv
import importlib.util
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
EM = chr(0x2014)


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def module():
    spec = importlib.util.spec_from_file_location("crosscheck_regions", os.path.join(ROOT, "replication", "grid", "crosscheck_regions.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheFolding(unittest.TestCase):
    def test_it_is_the_contracts(self):
        m = module()
        self.assertEqual(m.SOURCES, ["natural_gas", "coal", "nuclear", "wind", "solar", "hydro", "storage", "other"])
        self.assertEqual(m.ONE["hydro"], ["WAT", "PS"])
        self.assertEqual(m.ONE["storage"], ["BAT", "OES", "UES"])
        self.assertEqual(m.ONE["other"], ["OIL", "GEO", "OTH", "UNK"])
        self.assertEqual((m.ONE["solar"], m.ONE["wind"]), (["SUN", "SNB"], ["WND", "WNB"]))
        contract = src("docs", "state", "page_files_regions.md")
        self.assertIn("`hydro` is EIA's hydropower excluding pumped storage plus pumped storage", contract)
        self.assertIn("`storage` is battery, other and unknown energy storage", contract)
        self.assertIn("`other` is petroleum, geothermal, other and unknown fuel sources", contract)
        self.assertIn('Solar and wind include EIA\'s "with integrated battery storage" columns', contract)

    def test_every_code_of_the_connector_is_in_one_source(self):
        m = module()
        folded = sorted(c for cs in m.ONE.values() for c in cs)
        self.assertEqual(len(folded), len(set(folded)))
        connector = src("warehouse", "connectors", "eia930.py")
        for code in folded:
            self.assertIn(f'"{code}":', connector, code)


class TheHours(unittest.TestCase):
    def test_the_latest_hour_is_the_newest_with_a_net_generation(self):
        m = module()
        self.assertEqual(m.latest({"net_generation": [1, 2, None, 4, None, None]}), 3)
        self.assertIsNone(m.latest({"net_generation": [None, None]}))
        self.assertIsNone(m.latest({}))

    def test_an_hour_and_its_period(self):
        m = module()
        t = m.hour_of({"start": "2026-10-13T05:00:00Z", "step_hours": 1}, 840)
        self.assertEqual(m.period(t), "2026-11-17T05")

    def test_a_value_not_held_is_none(self):
        m = module()
        self.assertIsNone(m.at({"wind": [1.0, None]}, "wind", 1))
        self.assertIsNone(m.at({"wind": [1.0]}, "wind", 5))
        self.assertIsNone(m.at({}, "wind", 0))
        self.assertEqual(m.at({"wind": [0]}, "wind", 0), 0.0)


class TheScript(unittest.TestCase):
    def setUp(self):
        self.s = src("replication", "grid", "crosscheck_regions.py")

    def test_the_key_is_sent_and_never_written(self):
        self.assertIn('shown = API + route + "/data/?" + urllib.parse.urlencode(params)', self.s)
        self.assertIn('"source_url": (fuel_url if', self.s)
        self.assertNotIn("print(k", self.s)
        self.assertNotIn("print(key", self.s)

    def test_a_source_eia_returns_no_code_for_is_not_held(self):
        self.assertIn("eia[s] = sum(part) if part else None", self.s)
        self.assertIn('"not held" if e_v is None', self.s)

    def test_the_period_is_read_both_ways(self):
        self.assertIn("for shift in (0, 1):", self.s)
        self.assertIn("the hour's end", self.s)

    def test_no_em_dash(self):
        for p in (("replication", "grid", "crosscheck_regions.py"), ("tests", "test_session8606.py")):
            self.assertNotIn(EM, src(*p), p)


class TheOutput(unittest.TestCase):
    """The file on the branch, as the run of 19 November wrote it."""

    @classmethod
    def setUpClass(cls):
        path = os.path.join(ROOT, "replication", "grid", "crosscheck_regions.csv")
        with open(path, encoding="utf-8") as f:
            lines = f.readlines()
        cls.head = [l for l in lines if l.startswith("#")]
        cls.rows = list(csv.DictReader(l for l in lines if not l.startswith("#")))

    def test_the_header_names_the_source_and_the_time(self):
        text = "".join(self.head)
        self.assertIn("Form EIA-930", text)
        self.assertIn("# Retrieved: 2026-11-", text)
        self.assertNotIn("api_key", text + "".join(r["source_url"] for r in self.rows))

    def test_thirteen_regions_three_hours_each(self):
        regions = sorted({r["region"] for r in self.rows})
        self.assertEqual(len(regions), 13)
        for reg in regions:
            self.assertEqual(len({r["which"] for r in self.rows if r["region"] == reg}), 3, reg)

    def test_the_files_hour_is_eias_period_at_the_hours_end(self):
        d = [r for r in self.rows if r["figure"] == "demand" and r["same"]]
        end = [r for r in d if r["eia_period_is"] == "the hour's end"]
        start = [r for r in d if r["eia_period_is"] == "the hour's start"]
        self.assertGreaterEqual(sum(r["same"] == "yes" for r in end), 30)
        self.assertEqual(sum(r["same"] == "yes" for r in start), 0)

    def test_most_figures_are_eias_to_one_megawatt_and_the_rest_are_written(self):
        end = [r for r in self.rows if r["eia_period_is"] == "the hour's end" and r["same"]]
        same = sum(r["same"] == "yes" for r in end)
        self.assertGreaterEqual(len(end), 400)
        self.assertGreaterEqual(same / len(end), 0.85)
        self.assertTrue(all(r["difference_mw"] != "" for r in end))            # a figure that differs keeps its difference


if __name__ == "__main__":
    unittest.main()
