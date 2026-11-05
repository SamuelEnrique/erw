"""Session 577: the Digest and Roundup audits' fixes that session 470 left open and that need no ruling
(docs/reviews/digest-audit-2026-10-21.md, roundup-audit-2026-10-21.md; the state of all 30 is at the foot of each).

Digest audit fix 8, its second half: a why line ends with a stop before the figures or the links that follow it.
Digest audit fix 9, past detail(): the why lines carry the one money style too.
Roundup audit fix 10, its second half: the deals-by-month chart names each deal type in words.

No test here calls a model, reaches the network or writes the warehouse: the fixtures are strings, small frames and files
written to a temporary folder.
"""

import inspect
import os
import sys
import tempfile
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in ("warehouse", os.path.join("warehouse", "news")):
    if os.path.join(ROOT, p) not in sys.path:
        sys.path.insert(0, os.path.join(ROOT, p))

import brief  # noqa: E402
import roundup  # noqa: E402


def quiet(_msg):
    pass


class AStopBeforeTheFigures(unittest.TestCase):
    """Digest audit fix 8: "affecting global oil markets and prices parties: Iran." (20 October, top 8)."""

    def test_the_20_october_line_reads_as_two_sentences(self):
        r = {"why": "Escalation affecting global oil markets and prices", "mw": "", "price": "", "parties": "Iran"}
        line = f"{brief.why_line(r['why'])} {brief.detail(r)}Sources: x"
        self.assertIn("prices. parties: Iran. Sources:", line)

    def test_the_14_october_line(self):
        r = {"why": "Long-term LNG supply for 20-year supply agreement", "mw": "", "price": "$4.4 Billion",
             "parties": "QatarEnergy"}
        line = f"{brief.why_line(r['why'])} {brief.detail(r)}"
        self.assertEqual(line, "Long-term LNG supply for 20-year supply agreement. USD 4.4 billion; parties: QatarEnergy. ")

    def test_a_line_that_ends_already_is_left_as_it_is(self):
        for t in ("Prices rose.", "Will it hold?", 'He said "no."', "A rise (of 5%).", "Ends here!"):
            self.assertEqual(brief.why_line(t), t)

    def test_trailing_space_and_an_empty_line(self):
        self.assertEqual(brief.why_line("Prices rose  "), "Prices rose.")
        self.assertEqual(brief.why_line(""), "")

    def test_the_audit_s_worst_line(self):
        out = brief.why_line("Major AI datacenter infrastructure deal signals massive power demand and capital commitment")
        self.assertEqual(out, "AI datacenter infrastructure deal signals power demand and capital commitment.")


class OneMoneyStyleInTheWhyLines(unittest.TestCase):
    """Digest audit fix 9: "$45 Billion", "$3.2bn", "$4.2B", "$800MM", "USD120 billion" in the why lines too."""

    def test_the_five_styles(self):
        cases = {"A $45 Billion deal": "A USD 45 billion deal.",
                 "Raises $3.2bn for LNG": "Raises USD 3.2 billion for LNG.",
                 "Sells assets for $4.2B": "Sells assets for USD 4.2 billion.",
                 "An $800MM loan": "A USD 800 million loan.",
                 "an A$2 billion grant": "an AUD 2 billion grant.",
                 "A USD120 billion framework": "A USD 120 billion framework.",
                 "C$14.3 Billion takeover": "CAD 14.3 billion takeover."}
        for given, want in cases.items():
            self.assertEqual(brief.why_line(given), want)

    def test_a_price_per_unit_keeps_its_unit(self):
        self.assertEqual(brief.why_line("WTI at $93.78 per barrel"), "WTI at USD 93.78 per barrel.")

    def test_a_currency_code_is_not_read_inside_a_word(self):
        for t in ("amateur 5 teams", "fraud 5 times over", "Europe 2030 plan"):
            self.assertEqual(brief.money_style(t), t)

    def test_an_earlier_issue_s_sum_is_still_read_after_the_new_style(self):
        """not_shown_before reads the amounts an earlier issue printed; the new style must still be read as a sum."""
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "2026-10-08.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write("1. **Voltus raises funds** (grid)  \n   " + brief.why_line("Voltus raises $225MM for VPPs")
                        + " Sources: [X](https://example.org/v)\n")
            items = brief.issue_items([p])
        self.assertEqual(len(items), 1)
        self.assertIn(("usd", 225), items[0]["figs"])

    def test_the_session_470_cases_hold(self):
        self.assertEqual(brief.money_style("$45 Billion"), "USD 45 billion")
        self.assertEqual(brief.money_style("$800MM"), "USD 800 million")
        self.assertEqual(brief.money_style("C$14.3 Billion"), "CAD 14.3 billion")


class EveryWhyLineGoesThroughIt(unittest.TestCase):
    """Each place an issue prints a why line uses why_line, the Digest's and the Roundup's."""

    def test_no_why_is_printed_through_plain_alone(self):
        for mod in (brief, roundup):
            src = inspect.getsource(mod)
            self.assertNotIn("plain(r['why'])}", src.replace("why_line(r['why'])}", ""))
            self.assertNotIn("plain(x['why'])}", src.replace("why_line(x['why'])}", ""))
            self.assertNotIn('brief.plain(top["why"])', src)
        self.assertGreaterEqual(inspect.getsource(brief.main).count("why_line(r['why'])"), 3)

    def test_the_digest_s_policy_lines(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "policy_actions.csv"), "w", encoding="utf-8", newline="") as f:
                f.write("# fixture\n")
                pd.DataFrame([{"event_date": "2026-10-20", "significance": "6", "title": "A notice", "agency": "DOE",
                               "action_type": "notice", "why": "Funds a $1.2B pipeline",
                               "source_url": "https://example.org/p"}]).to_csv(f, index=False)
            with mock.patch.object(brief.ip, "OUT_DIR", d):
                lines = brief.policy_actions_lines(pd.Timestamp("2026-10-20", tz="UTC"),
                                                   pd.Timestamp("2026-10-21", tz="UTC"), quiet)
        self.assertEqual(len(lines), 1)
        self.assertIn("Funds a USD 1.2 billion pipeline. [DOE](https://example.org/p)", lines[0])

    def test_the_roundup_s_policy_of_the_week(self):
        acts = pd.DataFrame([
            {"event_id": "a1", "event_date": "2026-10-06", "significance": "7", "title": "First notice", "agency": "FERC",
             "action_type": "notice", "docket": "", "why": "Opens a $3bn program", "source_url": "https://example.org/1"},
            {"event_id": "a2", "event_date": "2026-10-07", "significance": "6", "title": "Second notice", "agency": "DOE",
             "action_type": "notice", "docket": "", "why": "Sets a rule", "source_url": "https://example.org/2"}])

        def table(name):
            return acts if name == "policy_actions" else None
        with mock.patch.object(roundup, "read_table", table):
            L = roundup.policy_of_the_week(pd.Timestamp("2026-10-05", tz="UTC"), pd.Timestamp("2026-10-12", tz="UTC"),
                                           quiet)
        text = "\n".join(L)
        self.assertIn("Opens a USD 3 billion program. [Source](https://example.org/1)", text)
        self.assertIn("Sets a rule. [source](https://example.org/2)", text)


class DealTypesInWordsInTheChart(unittest.TestCase):
    """Roundup audit fix 10: W40's chart of the week printed "m and a" in its legend and its note."""

    def setUp(self):
        t = os.path.join(ROOT, "warehouse", "analysis", "templates")
        if t not in sys.path:
            sys.path.insert(0, t)
        import deals_by_month
        self.mod = deals_by_month

    def test_every_type_has_a_word(self):
        for k in self.mod.TYPES + ["other"]:
            self.assertIn(k, self.mod.LABEL)
            self.assertNotIn("_", self.mod.LABEL[k])
        self.assertEqual(self.mod.LABEL["m_and_a"], roundup.DEAL_LABEL["m_and_a"])

    def test_the_legend_and_the_note(self):
        rows = []
        for month, kinds in (("2026-08", ["m_and_a", "m_and_a", "ppa"]), ("2026-09", ["m_and_a", "fuel_supply", "smr"])):
            rows += [{"event_date": f"{month}-10T00:00:00Z", "deal_type": k, "ai_power": "false"} for k in kinds]
        with mock.patch.object(self.mod, "fetch", lambda _t: pd.DataFrame(rows)), \
                mock.patch.object(self.mod, "result", lambda *a: a):
            out = self.mod.compute(months=6)
        chart, facts = out[6], out[8]
        names = [s["name"] for s in chart["series"]]
        self.assertIn("acquisition", names)
        self.assertFalse([n for n in names if "_" in n or n == "m and a"])
        self.assertIn("the most common type was acquisition, with 3", facts[0])


if __name__ == "__main__":
    unittest.main()
