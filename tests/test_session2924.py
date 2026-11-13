"""Session 2924 (chain 153): large_load_connection_rules, the steps a grid operator's or a utility's document states for
connecting a large load, from the registry warehouse/sources/large_load_connection_rules/.

Held here: the registry's files pass the connector's check; a step's duration must be in its printed words (as a figure
or a word), a unit needs a duration, a load size must be printed; the rows carry the stated date as event_date where
one is printed; the committed registry gives 26 steps of two documents, and ERCOT's PCLR energization step has no
duration (the siting gaps' controllable load row). No request, no model call.
"""
import importlib.util
import os
import tempfile
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def load():
    spec = importlib.util.spec_from_file_location("llcr_2924", os.path.join(ROOT, "warehouse", "connectors", "large_load_connection_rules.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


GOOD = """body: A Grid
grid: ERCOT
state: TX
document: A guide
document_date: 2026-07-11
document_url: https://example.org/guide.docx
retrieved_at: 2026-11-06T04:18:20Z
license: public
steps:
  - {section: "1(a)", step: posts security, party: ILLE, duration: 7, unit: business days, printed: "shall have seven Business Days to post"}
  - {section: "1(b)", step: the report, party: ERCOT, date: 2027-04-09, printed: "on or before April 9, 2027"}
  - {section: "1(c)", step: a threshold, mw: 75, printed: "by 75 MW or more"}
  - {section: "1(d)", step: energized capped, printed: "shall not consume at a level greater than the LPC"}
"""


class TheRegistry(unittest.TestCase):
    def setUp(self):
        self.m = load()

    def run_on(self, body):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "a.yaml"), "w", encoding="utf-8") as f:
                f.write(body)
            return self.m.read_registry(d)

    def test_a_good_file_gives_its_rows(self):
        regs, problems = self.run_on(GOOD)
        self.assertEqual(problems, [])
        d = self.m.rows(regs).set_index("x_section")
        self.assertEqual((d.loc["1(a)", "x_duration"], d.loc["1(a)", "x_duration_unit"], d.loc["1(a)", "event_date"], d.loc["1(a)", "x_date_kind"]),
                         ("7", "business days", "2026-07-11", "document date"))
        self.assertEqual((d.loc["1(b)", "event_date"], d.loc["1(b)", "x_date_kind"]), ("2027-04-09", "stated date"))
        self.assertEqual(d.loc["1(c)", "mw"], "75")
        self.assertEqual(d.loc["1(d)", "x_duration"], "")

    def test_a_duration_not_printed_is_refused(self):
        _, problems = self.run_on(GOOD.replace("duration: 7,", "duration: 8,"))
        self.assertTrue(any("not in its printed words" in p for p in problems), problems)

    def test_a_unit_without_a_duration_and_a_bad_unit_are_refused(self):
        _, p1 = self.run_on(GOOD.replace("duration: 7, ", ""))
        self.assertTrue(any("a unit with no duration" in p for p in p1), p1)
        _, p2 = self.run_on(GOOD.replace("unit: business days", "unit: weeks"))
        self.assertTrue(any("unit 'weeks'" in p for p in p2), p2)

    def test_a_load_size_not_printed_is_refused(self):
        _, problems = self.run_on(GOOD.replace("mw: 75", "mw: 100"))
        self.assertTrue(any("mw 100" in p for p in problems), problems)

    def test_a_license_other_than_public_is_refused(self):
        _, problems = self.run_on(GOOD.replace("license: public", "license: internal"))
        self.assertTrue(any("only a public document" in p for p in problems), problems)


class TheCommittedRegistry(unittest.TestCase):
    def test_the_documents_held(self):
        m = load()
        regs, problems = m.read_registry()
        self.assertEqual(problems, [])
        d = m.rows(regs)
        # session 2938 (chain 155): SPP's HILL process, as FERC's order of 14 January 2026 states it, joined (13 steps)
        # session 3762 (chain 211): PJM's Board letter (7) and show-cause proposal (5), CAISO's straw proposal (3), ERCOT's batch
        # deck (2) and PUCT Project 58000's proposal (3) joined, each step read in its document
        # session 3783 (chain 212): Utah's S.B. 132 (8 steps, PacifiCorp's PACE), read from the Legislature's enrolled copy
        # session 3863 (chain 223): the Pennsylvania PUC's Large Load Customer Model Tariff (8 steps, PJM), from its Final Order
        self.assertEqual(len(d), 75)
        self.assertEqual(sorted(d["x_grid"].unique()), ["CAISO", "ERCOT", "PACE", "PJM", "SPP"])
        self.assertEqual(int((d["x_date_kind"] == "stated date").sum()), 4)
        pclr = d[d["event_id"] == "rule:ercot_planning_guide_section_9:9_6_1_1"].iloc[0]
        self.assertEqual(pclr["x_duration"], "")                 # no faster path's duration is stated
        sec = d[d["event_id"] == "rule:ercot_planning_guide_section_9:9_3_1_2_a_ii"].iloc[0]
        self.assertEqual((sec["x_duration"], sec["x_duration_unit"]), ("7", "business days"))


if __name__ == "__main__":
    unittest.main()
