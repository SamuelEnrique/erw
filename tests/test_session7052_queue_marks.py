"""Session 7052 (chain 370, the data machine): done-line request 189.

ERCOT's file types none of its withdrawn or suspended requests as a hybrid, so its solar-with-storage shares are the
file's labels, not a count. The builder marks them (and the United States' pair, which counts them) as not comparable
in the site's copy, with the reason; the figures stand as written.
"""

import importlib.util
import json
import os
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def builder():
    spec = importlib.util.spec_from_file_location("queue_summary_7052", os.path.join(ROOT, "warehouse", "derived", "queue_summary.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TheMarks(unittest.TestCase):
    def test_a_grid_without_closed_hybrids_is_marked(self):
        m = builder()
        # test data written here by hand, never a reported figure
        rows = [{"region": "ERCOT", "status": "withdrawn", "type_2": None}] * 25 + [{"region": "ERCOT", "status": "active", "type_2": "Battery"}] * 3
        rows += [{"region": "CAISO", "status": "withdrawn", "type_2": "Battery"}] * 2 + [{"region": "CAISO", "status": "withdrawn", "type_2": None}] * 30
        d = pd.DataFrame(rows)
        summary = {("ercot", "solar_battery"): {"whole": {"past_requests": 7}}}
        out = m.not_comparable(d, summary)
        self.assertEqual(sorted(out), ["ercot|solar_battery", "us|solar_battery"])
        self.assertIn("25 withdrawn", out["ercot|solar_battery"])
        self.assertIn("ERCOT's 7 past requests", out["us|solar_battery"])

    def test_no_mark_when_closed_hybrids_are_typed(self):
        m = builder()
        d = pd.DataFrame([{"region": "CAISO", "status": "withdrawn", "type_2": "Battery"}] * 30 + [{"region": "CAISO", "status": "active", "type_2": "Battery"}])
        self.assertEqual(m.not_comparable(d, {}), {})

    def test_the_site_copy_carries_the_marks(self):
        with open(os.path.join(ROOT, "site", "data", "queues.json"), encoding="utf-8") as f:
            d = json.load(f)
        self.assertEqual(sorted(d["not_comparable"]), ["ercot|solar_battery", "us|solar_battery"])
        self.assertIn("past_withdrawn_share_pct", d["views"]["ercot|solar_battery"]["whole"])  # the figures stand


if __name__ == "__main__":
    unittest.main()
