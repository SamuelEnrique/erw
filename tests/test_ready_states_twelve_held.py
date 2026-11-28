"""Session 11407 (chain 770, part C): the states audit's finding 4 readied for Samuel's ruling, twelve months held or none.

Carried over from session 10223's tests/test_audit_states_4.py (branch wip/audit-states-4), which showed that the page
printed a source's share of "the last twelve months" when EIA printed it in only some of them: the District of
Columbia's natural gas, its headline's largest source, 9 of 12 months, 40.05 percent. On this branch the builder
(warehouse/derived/states_page.py, build_generation) prints a source for the twelve months only when all twelve are held;
the total still counts every figure EIA prints. DC's natural gas becomes null and its largest source solar, 21.83 percent.
The page files are the data machine's: the builder is run here on each file's own monthly arrays (the site file is
rebuilt at landing by the desk). docs/reviews/states-model-audit-2026-11-26.md, finding 4.
"""
import importlib.util
import json
import os
import sys
import unittest

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIR = os.path.join(ROOT, "site", "data", "states")


def load_builder():
    sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
    spec = importlib.util.spec_from_file_location("states_page_ready_twelve", os.path.join(ROOT, "warehouse", "derived", "states_page.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load(st):
    with open(os.path.join(DIR, f"{st}.json"), encoding="utf-8") as f:
        return json.load(f)


def rebuilt(m, st):
    """The builder's last12 on the file's own monthly generation, put back into the table's shape."""
    g = load(st.lower())["generation"]
    recs = [(st, mo, s, v) for s, arr in g["by_source"].items() for mo, v in zip(g["months"], arr) if v is not None]
    return g, m.build_generation(pd.DataFrame(recs, columns=["st", "month", "src", "value"]), st)["last12"]


class MadeUpMonths(unittest.TestCase):
    def test_a_source_with_a_withheld_month_is_null_and_the_total_keeps_it(self):
        m = load_builder()
        months = m.month_range("2025-09", "2026-08")
        recs = [("DC", mo, "solar", 10.0) for mo in months]
        recs += [("DC", mo, "natural_gas", 30.0) for mo in months[:9]]
        recs += [("DC", mo, "not_itemized", 30.0) for mo in months[9:]]
        l12 = m.build_generation(pd.DataFrame(recs, columns=["st", "month", "src", "value"]), "DC")["last12"]
        self.assertIsNone(l12["mwh"]["natural_gas"])
        self.assertIsNone(l12["share_pct"]["natural_gas"])
        self.assertIsNone(l12["mwh"]["not_itemized"])
        self.assertEqual(l12["mwh"]["solar"], 120.0)
        self.assertEqual(l12["total_mwh"], 480.0)            # every figure held: 120 + 270 + 90
        self.assertEqual(l12["share_pct"]["solar"], 25.0)
        self.assertIsNone(l12["mwh"]["coal"])                 # no month at all: null, as before


@unittest.skipUnless(os.path.exists(os.path.join(DIR, "index.json")), "the states' page files are not on this machine")
class ThePageFiles(unittest.TestCase):
    def setUp(self):
        self.m = load_builder()

    def test_dc_headline_becomes_solar(self):
        g, l12 = rebuilt(self.m, "DC")
        self.assertEqual(sum(v is None for v in g["by_source"]["natural_gas"][-12:]), 3)
        self.assertIsNone(l12["share_pct"]["natural_gas"])
        self.assertAlmostEqual(l12["total_mwh"], g["last12"]["total_mwh"], places=1)
        held = {s: v for s, v in l12["share_pct"].items() if v is not None}
        self.assertEqual(max(held, key=held.get), "solar")
        self.assertAlmostEqual(held["solar"], 21.83, places=2)

    def test_whole_sources_do_not_move(self):
        g, l12 = rebuilt(self.m, "TX")
        for s, v in l12["share_pct"].items():
            if all(x is not None for x in g["by_source"][s][-12:]):
                self.assertEqual(v, g["last12"]["share_pct"][s])


class TheWords(unittest.TestCase):
    def test_the_page_the_decision_and_the_note(self):
        with open(os.path.join(ROOT, "site", "app", "states", "page.tsx"), encoding="utf-8") as f:
            page = f.read()
        self.assertIn("A source is printed for the twelve months only when EIA prints it in all twelve", page)
        self.assertIn("in all twelve of these months", page)
        with open(os.path.join(ROOT, "site", "app", "states", "Decisions.tsx"), encoding="utf-8") as f:
            self.assertIn("a source is shown for the twelve months, and a year, only when all twelve of its months are held", f.read())
        with open(os.path.join(ROOT, "docs", "methods", "states_page.md"), encoding="utf-8") as f:
            note = f.read()
        self.assertIn("held only on twelve months it is null and DC's largest source is solar, 21.83 percent", note)
        for text in (page, note):
            self.assertNotIn(chr(0x2014), text)


if __name__ == "__main__":
    unittest.main()
