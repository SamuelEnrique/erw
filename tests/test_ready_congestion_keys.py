"""Session 11407 (chain 770, part C): the ruling on congestion audit finding 2 readied, an element's keys joined.

The table's key is the element under one contingency, and SPP's files until November 2021 name no contingency, so
TEXAS_CO_TXPS_TXCO_PHSHFT_PS stood as rows 1 and 2 of SPP's "every year held" list by hours (60,293 and 31,835 hours,
one label). Carried over from tests/test_audit_congestion_2.py (branch wip/audit-congestion-2): here the builder's
join_elements makes the page's constraint the element (x_constraint), an hour bound under several contingencies one
hour with the sizes summed, so that element is one row of 92,128 hours (summed size 396,339.0).

The builder's input, constraints_binding_hourly, is on the data machine only: the page file is rebuilt at landing by
the desk. The first class runs the builder's own functions on a few rows written here; the second measures the join
from the page file as it stands (built before the join); the third holds the page file once rebuilt; the fourth the
words.
"""
import json
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FILE = os.path.join(ROOT, "site", "data", "conditions", "congestion.json")


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def load():
    with open(FILE, encoding="utf-8") as f:
        return json.load(f)


def joined_file():
    return os.path.exists(FILE) and any("contingencies" in c for c in load()["constraints"]["spp"]["constraints"].values())


class TheBuilderJoinsAnElementsKeys(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pandas as pd
        sys.path.insert(0, os.path.join(ROOT, "warehouse", "derived"))
        import congestion_page as cp
        rows = [  # entity, ts_utc, value, market, x_constraint, x_contingency
            ("spp:EL1", "2021-11-10T05:00:00Z", -2.0, "spp_dam", "EL1", ""),
            ("spp:EL1|BASE", "2021-11-10T06:00:00Z", -3.0, "spp_dam", "EL1", "BASE"),
            ("spp:EL1|BASE", "2021-11-10T07:00:00Z", -5.0, "spp_dam", "EL1", "BASE"),
            ("caiso:BR9|C1", "2025-03-01T20:00:00Z", 4.0, "caiso_dam", "BR9", "C1"),
            ("caiso:BR9|C2", "2025-03-01T20:00:00Z", 6.0, "caiso_dam", "BR9", "C2"),
            ("caiso:BR9|C2", "2025-03-01T21:00:00Z", 1.0, "caiso_dam", "BR9", "C2"),
            ("caiso:ND7|Base Case", "2025-03-01T20:00:00Z", 2.5, "caiso_dam", "ND7", "Base Case"),
        ]
        c = pd.DataFrame(rows, columns=["entity", "ts_utc", "value", "market", "x_constraint", "x_contingency"])
        for col in ("x_monitored", "x_constraint_type", "x_nerc_id"):
            c[col] = ""
        c = cp.localize(c)
        c["abs"] = c["value"].abs()
        cls.page = cp.constraint_page(c)

    def test_spp_name_alone_and_base_are_one_row(self):
        O = self.page["spp"]
        self.assertEqual(list(O["constraints"]), ["spp:EL1"])
        e = O["constraints"]["spp:EL1"]
        self.assertEqual(e["hours"], 3)
        self.assertEqual(e["cost"], 10.0)
        self.assertEqual(e["contingencies"], ["", "BASE"])
        self.assertIsNone(e["contingency"])
        self.assertEqual(O["hours_by_year"], {"2021": 3})
        self.assertEqual(O["constraints_by_year"], {"2021": 1})

    def test_an_hour_under_two_contingencies_counts_once_with_the_sizes_summed(self):
        O = self.page["caiso"]
        e = O["constraints"]["caiso:BR9"]
        self.assertEqual(e["hours"], 2)
        self.assertEqual(e["cost"], 11.0)
        self.assertEqual(e["abs_max"], 10.0)
        self.assertEqual(e["abs_mean"], 5.5)
        self.assertEqual(e["contingencies"], ["C1", "C2"])
        self.assertEqual(O["hours_by_year"], {"2025": 3})
        self.assertEqual(O["constraints_by_year"], {"2025": 2})
        one = O["constraints"]["caiso:ND7"]
        self.assertEqual(one["contingency"], "Base Case")
        self.assertIsNone(one["contingencies"])


@unittest.skipUnless(os.path.exists(FILE), "the congestion file is not on this machine")
class TheJoinMeasuredFromTheFileBeforeIt(unittest.TestCase):
    def setUp(self):
        if joined_file():
            self.skipTest("the page file already joins an element's keys")
        self.spp = load()["constraints"]["spp"]["constraints"]

    def test_texas_phase_shifter_is_92128_hours_once_joined(self):
        a = self.spp["spp:TEXAS_CO_TXPS_TXCO_PHSHFT_PS"]
        b = self.spp["spp:TEXAS_CO_TXPS_TXCO_PHSHFT_PS|BASE"]
        self.assertLess(a["last"], b["first"], "the two keys never share an hour")
        self.assertEqual(a["hours"] + b["hours"], 92128)
        self.assertAlmostEqual(a["cost"] + b["cost"], 396339.0, delta=0.05)


@unittest.skipUnless(joined_file(), "the page file is rebuilt with the join at landing by the desk")
class TheFileOnceRebuilt(unittest.TestCase):
    def test_no_name_stands_on_two_rows(self):
        for op, O in load()["constraints"].items():
            names = [c["name"] for c in O["constraints"].values()]
            self.assertEqual(len(names), len(set(names)), op)

    def test_texas_phase_shifter_is_one_row(self):
        e = load()["constraints"]["spp"]["constraints"]["spp:TEXAS_CO_TXPS_TXCO_PHSHFT_PS"]
        self.assertGreaterEqual(e["hours"], 92128)
        self.assertEqual(e["contingencies"], ["", "BASE"])


class TheWordsSayIt(unittest.TestCase):
    def test_the_page_labels_a_joined_row(self):
        s = src("site", "app", "congestion", "page.tsx")
        self.assertIn("if (c.contingencies && c.contingencies.length > 1) return `${c.name} (${c.contingencies.length} listings joined)`;", s)
        self.assertIn("an hour it bound under two contingencies counts once, as one constraint-hour", s)
        self.assertNotIn("counts as two constraint-hours", s)
        self.assertIn("contingencies?: string[] | null;", src("site", "lib", "congestion.ts"))

    def test_the_decision_and_the_note_say_it(self):
        d = src("site", "app", "congestion", "Decisions.tsx")
        self.assertIn("the listings are joined into one row and one constraint in the counts", d)
        self.assertNotIn("counts twice", d)
        n = src("docs", "methods", "grid_congestion.md")
        self.assertIn("The page file joins an element's keys (session 11407", n)
        self.assertIn("def join_elements(d):", src("warehouse", "derived", "congestion_page.py"))
        self.assertIn('d.assign(entity=op + ":" + d["x_constraint"]).groupby(["entity", "ts_utc"]', src("replication", "congestion", "replicate.py"))

    def test_no_em_dash(self):
        for p in (("site", "app", "congestion", "page.tsx"), ("site", "app", "congestion", "Decisions.tsx"),
                  ("docs", "methods", "grid_congestion.md"), ("warehouse", "derived", "congestion_page.py"),
                  ("site", "lib", "congestion.ts")):
            self.assertNotIn(chr(0x2014), src(*p), p)


if __name__ == "__main__":
    unittest.main()
