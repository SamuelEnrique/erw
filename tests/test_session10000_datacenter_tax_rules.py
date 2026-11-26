"""Session 10000 (chain 701, request 9 of docs/state/data_requests_forecast.md): impact_tax_rules carries the datacenter
rules /impact applies (site/data/forecast/datacenter_rules.json), a row for each state's sales tax exemption, property
tax treatment and electricity tax the file holds, each with its words and its source's address and day read. Made from
the file in the repository; no request, nothing written to warehouse/output."""
import importlib.util
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "forecast", "datacenter_rules.json")


def load():
    spec = importlib.util.spec_from_file_location("itr_t", os.path.join(ROOT, "warehouse", "derived", "impact_tax_rules.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@unittest.skipUnless(os.path.exists(FILE), "site/data/forecast/datacenter_rules.json is not on this copy")
class TheDatacenterRows(unittest.TestCase):
    def setUp(self):
        self.m = load()
        self.dc = json.load(open(FILE, encoding="utf-8"))
        self.rows = self.m.datacenter_rows(self.dc)

    def test_one_row_a_rule_the_file_holds(self):
        want = sum(1 for s in self.dc["states"].values() for k in self.m.DC_KINDS if isinstance(s.get(k), dict))
        self.assertEqual(len(self.rows), want)
        self.assertEqual(len({r["event_id"] for r in self.rows}), want)

    def test_every_row_has_its_words_address_and_day(self):
        for r in self.rows:
            self.assertTrue(r["source_url"].startswith("http"), r["event_id"])
            self.assertRegex(r["event_date"], r"^\d{4}-\d{2}-\d{2}$", r["event_id"])
            self.assertEqual(r["source"], "forecast:datacenter_rules")
            self.assertEqual(r["x_product"], "datacenter")

    def test_virginia_as_the_file_holds_it(self):
        va = next(r for r in self.rows if r["event_id"] == "erw_tax:va:dc_sales_exemption")
        d = json.loads(va["x_detail"])
        src = self.dc["states"]["va"]["sales_exemption"]
        self.assertEqual(d["min_investment_usd"], src["min_investment_usd"])
        self.assertEqual(d["min_jobs"], src["min_jobs"])
        self.assertEqual(va["x_quote"], " ".join(src["quote"].split()) if "\n" in src["quote"] else src["quote"])
        self.assertEqual(va["x_how_long"], f"purchases through {src['last_year']}")


if __name__ == "__main__":
    unittest.main()
