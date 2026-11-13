"""Session 1907: the second choice of the Roundup's faults file row 68 (docs/reviews/periodicals-faults-2026-11-05.md),
proved on fixtures. No model call, no network, no warehouse table read: every frame is written here.

Row 68, the line: "**Largest new datacenter load first reported this week:** no facility ... passes the datacenter table's
floor (3 under it); in its place, the week's next price move: WTI Cushing crude closed at 99.64 USD/bbl ..."
The fault: "A second oil price beside Brent's: the five hold two market rows and none of infrastructure or capacity, or of
policy". The fix asked: "The stand-in comes from a part not yet among the five (capacity, then policy: NRC's final rule on
contested licensing hearings, effective 2026-12-03), a second price only when neither is held."
Session 1895 took the first choice (capacity, a plant the week's stories name). This takes the second: with no plant, the
stand-in is the week's Policy of the Week, "in its place, policy: <title> (<agency> <kind>, published <date>), the Policy
of the Week below."; a second price only when neither is held."""

import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import roundup  # noqa: E402

UTC = "UTC"
START = pd.Timestamp("2026-11-02", tz=UTC)
CUT = pd.Timestamp("2026-11-08 23:26", tz=UTC)

ACT = dict(event_id="", event_date="", agency="", action_type="", title="", significance="", source_url="", docket="",
           why="")
NRC = dict(ACT, event_id="fr:2026-21001", event_date="2026-11-03", agency="NRC", action_type="rule", significance="8",
           title="Contested Licensing Hearings", source_url="https://www.federalregister.gov/d/2026-21001")
EPA = dict(ACT, event_id="fr:2026-21002", event_date="2026-11-04", agency="EPA", action_type="proposed_rule", significance="8",
           title="Emission Guidelines for Turbines", source_url="https://www.federalregister.gov/d/2026-21002")
LOW = dict(ACT, event_id="fr:2026-21003", event_date="2026-11-05", agency="DOE", action_type="notice", significance="6",
           title="Notice of a Meeting", source_url="https://www.federalregister.gov/d/2026-21003")
OLD = dict(ACT, event_id="fr:2026-20000", event_date="2026-10-28", agency="FERC", action_type="rule", significance="10",
           title="A Rule of the Week Before", source_url="https://www.federalregister.gov/d/2026-20000")
NONE = dict(ACT, event_id="fr:2026-21004", event_date="2026-11-05", agency="FERC", action_type="rule", significance="",
            title="Not Scored", source_url="https://www.federalregister.gov/d/2026-21004")


def acts(*rows):
    return pd.DataFrame(list(rows))


class ThePick(unittest.TestCase):
    def pick(self, frame):
        with mock.patch.object(roundup, "read_table", lambda n: frame if n == "policy_actions" else None):
            return roundup.policy_pick(START, CUT)

    def test_the_most_significant_then_the_final_rule(self):
        self.assertEqual(self.pick(acts(LOW, EPA, NRC, OLD, NONE))["event_id"], "fr:2026-21001")

    def test_a_week_with_no_scored_action_has_none(self):
        self.assertIsNone(self.pick(acts(OLD, NONE)))

    def test_no_table_no_pick(self):
        self.assertIsNone(self.pick(None))

    def test_the_policy_of_the_week_takes_the_same_action(self):
        with mock.patch.object(roundup, "read_table", lambda n: acts(LOW, EPA, NRC, OLD, NONE) if n == "policy_actions" else None):
            L = roundup.policy_of_the_week(START, CUT, lambda *a: None)
        self.assertTrue(L[0].startswith("**Contested Licensing Hearings** (NRC final rule, published 2026-11-03"), L[0])
        self.assertIn("Emission Guidelines for Turbines", "\n".join(L))


class TheStandIn(unittest.TestCase):
    def facts(self):
        def fuel(label, v1, v0):
            return {"label": label, "a": {"value": v1, "unit": "USD/bbl", "ts_utc": pd.Timestamp("2026-11-03", tz=UTC)},
                    "b": {"value": v0, "unit": "USD/bbl", "ts_utc": pd.Timestamp("2026-10-27", tz=UTC)}, "ref": "[5]"}
        return {"fuel": [fuel("Brent crude", 107.03, 123.10), fuel("WTI Cushing crude", 99.64, 103.37),
                         {"label": "Henry Hub natural gas", "a": {"value": 2.70, "unit": "USD/MMBtu", "ts_utc": pd.Timestamp("2026-11-03", tz=UTC)},
                          "b": {"value": 2.63, "unit": "USD/MMBtu", "ts_utc": pd.Timestamp("2026-10-27", tz=UTC)}, "ref": "[5]"}]}

    def five(self, picked, capacity=None):
        dcs = pd.DataFrame([{"entity_id": "dc:x", "first_story_at": "2026-11-05T10:00:00Z", "capacity_mw": "702", "operator": "Google",
                             "site_name": "", "city": "Cheyenne", "state": "WY", "confidence": "0.55"}])
        with tempfile.TemporaryDirectory() as d, \
                mock.patch.object(roundup, "read_table", lambda n: dcs if n == "datacenter_projects" else None), \
                mock.patch.object(roundup, "ANALYSIS_DIR", d):
            return roundup.five_numbers("2026-W45", START, CUT, self.facts(), lambda *a: None, picked, capacity)

    def row(self, L):
        return next(ln for ln in L if "datacenter load" in ln)

    def test_neither_held_the_second_price_as_before(self):
        # session 1992 (faults file row 97): the next unused move at the bar (WTI's 3.6%), not the third by index (Henry
        # Hub's 2.7%, under the 3% bar)
        self.assertIn("in its place, the week's next price move: WTI Cushing crude closed", self.row(self.five({})))

    def test_the_policy_line_before_a_second_price(self):
        L = self.five({"policy": NRC})
        self.assertEqual(self.row(L), "- **Largest new datacenter load first reported this week:** no facility first reported this "
                                      "week with its MW passes the datacenter table's floor (1 under it); in its place, policy: "
                                      "Contested Licensing Hearings (NRC final rule, published 2026-11-03), the Policy of the Week below.")
        self.assertIn("the policy, `policy_actions` fr:2026-21001", L[-1])
        self.assertNotIn("WTI Cushing crude closed", "\n".join(L))

    def test_capacity_comes_first(self):
        plant = {"plant": {"plant_id": "65500", "ids": ["eia860:65500:REVWD"], "name": "Revolution Wind", "mw": 715.0,
                           "technology": "Offshore Wind Turbine", "state": "RI", "date": "2026-11-01", "vintage": "2026-09", "n": 1},
                 "rec": {"links": [("POWER Magazine", "https://www.powermag.com/x")]}}
        with mock.patch.object(roundup, "capacity_words", lambda c: "Revolution Wind (the table's words)"):
            L = self.five({"policy": NRC}, plant)
        self.assertIn("in its place, capacity: Revolution Wind", self.row(L))
        self.assertEqual(sum("in its place, policy:" in ln for ln in L), 0)

    def test_the_policy_line_is_used_once(self):
        self.assertEqual(sum("in its place, policy:" in ln for ln in self.five({"policy": NRC})), 1)

    def test_the_line_is_no_item_of_the_repeat_checks(self):
        import brief
        L = self.five({"policy": NRC})
        below = ["**Contested Licensing Hearings** (NRC final rule, published 2026-11-03)", ""]
        self.assertEqual(brief.without_repeats(below, L, lambda *a: None), below)
        brief.assert_unique(L + below)

    def test_the_checker_reads_no_load_from_the_stand_in(self):
        import check_roundup as cr
        self.assertIsNone(cr.five_keyed("\n".join(self.five({"policy": NRC})))[2])

    def test_main_passes_the_pick(self):
        with open(os.path.join(ROOT, "warehouse", "news", "roundup.py"), encoding="utf-8") as f:
            src = f.read()
        self.assertIn('picked["policy"] = policy_pick(start, cut)', src)
        self.assertLess(src.index('picked["policy"] = policy_pick(start, cut)'),
                        src.index("five = five_numbers(label, start, cut, facts, log, picked)"))


if __name__ == "__main__":
    unittest.main()
