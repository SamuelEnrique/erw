"""Session 1897: the Roundup's faults of W45 in docs/reviews/periodicals-faults-2026-11-05.md, rows 76 and 65, proved on
fixtures. No model call, no network, no warehouse table read: the policy_reads rows are written here in the columns and
words of the real rows (the table is the data machine's).

Row 76, the line: "**9 November 2026**: Cheniere Corpus Christi Pipeline, LP, Corpus Christi Liquefaction Stage IV, LLC,
Corpus... (FERC). FERC must receive comments on the draft EIS by 5:00 p.m. Eastern Time on November 9, 2026." (with an NRC
and a BLM comment deadline the same day)
The fault: "Row 36, re-seen: a title cut on \"...\" with no short name kept, three comment deadlines on one day, and each
item two sentences where chain 131 asks one line"
The fix: "- **9 November 2026**: Corpus Christi Liquefaction Stage IV (FERC): comments on the draft EIS due 17:00 Eastern.
([source](...))"
next_week writes one line an item (the title's short name, the agency, a colon, the deadline as one clause); a docket of
several companies cut by its length keeps the company its subject names (docket_company); a comment deadline is said in
the row's form (deadline_words). The three deadlines of one day are three agencies' (FERC, NRC, BLM): session 1447's rule
(one item of a kind an agency a day) stands.
"""

import os
import sys
import unittest
from unittest import mock

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "warehouse", "news"))
import roundup  # noqa: E402

EM, EN = chr(0x2014), chr(0x2013)
DAY = pd.Timestamp("2026-11-09")
END = pd.Timestamp("2026-11-09", tz="UTC")


def quiet(*_a, **_k):
    pass


FERC_TITLE = ("Cheniere Corpus Christi Pipeline, LP, Corpus Christi Liquefaction Stage IV, LLC, Corpus Christi Liquefaction, LLC; "
              "Notice of Availability of the Draft Environmental Impact Statement for the Proposed Corpus Christi Liquefaction Stage 4 "
              "Project and the CCPL Expansion Project")
FERC_URL = ("https://www.federalregister.gov/documents/2026/09/23/2026-19447/cheniere-corpus-christi-pipeline-lp-corpus-christi-"
            "liquefaction-stage-iv-llc-corpus-christi")
READS = pd.DataFrame([
    {"title": "Regulatory Enhancements for Reactor Licensing, Decommissioning, and Operational Oversight", "agency": "NRC",
     "significance": "7", "source_url": "https://www.federalregister.gov/nrc",
     "timeline": "Comments are due by 11:59 p.m. eastern time on November 9, 2026, through regulations.gov under Docket ID "
                 "NRC-2025-1138. The final rule follows."},
    {"title": FERC_TITLE, "agency": "FERC", "significance": "7", "source_url": FERC_URL,
     "timeline": "FERC must receive comments on the draft EIS by 5:00 p.m. Eastern Time on November 9, 2026. The final EIS and the "
                 "Commission's decision come later."},
    {"title": "National Petroleum Reserve in Alaska Production Site Development", "agency": "BLM", "significance": "6",
     "source_url": "https://www.federalregister.gov/blm", "timeline": "Comments on the proposed rule are due to the BLM by November 9, 2026."},
])
FERC_LINE = f"- **9 November 2026**: Corpus Christi Liquefaction Stage IV (FERC): comments on the draft EIS due 17:00 Eastern. ([source]({FERC_URL}))"


class Row76NextWeek(unittest.TestCase):
    def lines(self, reads=READS):
        with mock.patch.object(roundup, "read_table", return_value=reads):
            return roundup.next_week(END, quiet)

    def test_the_ferc_item_in_the_row_s_form(self):
        self.assertIn(FERC_LINE, self.lines())

    def test_one_line_an_item_one_clause(self):
        out = self.lines()
        self.assertEqual(len(out), 3)
        for ln in out:
            body = ln.split(" ([source]")[0]
            self.assertEqual(body.count(". "), 0, ln)          # one sentence: no second sentence after the agency
            self.assertTrue(body.endswith("."), ln)
            self.assertNotIn("...", ln)
            self.assertNotIn("p.m.", ln)
            self.assertNotIn("November 9, 2026", ln)            # the day is the bold date, not said again
        self.assertIn("- **9 November 2026**: Regulatory Enhancements for Reactor Licensing, Decommissioning, and Operational Oversight "
                      "(NRC): comments due 23:59 Eastern (docket NRC-2025-1138).", out[0] + out[1] + out[2])
        self.assertTrue(any(ln.startswith("- **9 November 2026**: National Petroleum Reserve in Alaska Production Site Development (BLM): "
                                          "comments on the proposed rule due. ([source]") for ln in out))

    def test_the_docket_s_short_name(self):
        self.assertEqual(roundup.short_title(FERC_TITLE), "Corpus Christi Liquefaction Stage IV")
        self.assertEqual(roundup.docket_company(FERC_TITLE), "Corpus Christi Liquefaction Stage IV")
        names, subject = roundup.docket_companies(FERC_TITLE)
        self.assertEqual(names, ["Cheniere Corpus Christi Pipeline", "Corpus Christi Liquefaction Stage IV", "Corpus Christi Liquefaction"])
        self.assertTrue(subject.startswith("Notice of Availability"))
        three = ("Corpus Christi Liquefaction, LLC; Corpus Christi Liquefaction Stage IV, LLC; and Cheniere Marketing, LLC; Application "
                 "for Long-Term Authorization To Export Liquefied Natural Gas to Non-Free Trade Agreement Nations")
        self.assertEqual(roundup.docket_companies(three)[0], ["Corpus Christi Liquefaction", "Corpus Christi Liquefaction Stage IV",
                                                              "Cheniere Marketing"])

    def test_one_company_or_a_place_keeps_the_cut_at_a_word(self):
        t = ("Northern Natural Gas Company; Notice of Availability of the Environmental Assessment for the Proposed Ventura "
             "to Farmington A-Line Abandonment and Capacity Replacement Project")
        self.assertEqual(roundup.short_title(t), "Northern Natural Gas Company, Notice of Availability of the Environmental Assessment for...")
        place = "City of Austin, Texas; Notice of a very long application title that goes on and on past the limit of ninety characters"
        self.assertEqual(roundup.docket_company(place), "")
        self.assertEqual(roundup.short_title("Ohio Regulatory Program"), "Ohio Regulatory Program")

    def test_the_deadline_words(self):
        w = roundup.deadline_words
        self.assertEqual(w("FERC must receive comments on the draft EIS by 5:00 p.m. Eastern Time on November 9, 2026.", DAY),
                         "comments on the draft EIS due 17:00 Eastern")
        self.assertEqual(w("Comments must reach the Commission by 5:00 p.m. Eastern Time on November 9, 2026.", DAY), "comments due 17:00 Eastern")
        self.assertEqual(w("Motions to intervene and comments are due by 4:30 p.m. Eastern time on November 9, 2026.", DAY),
                         "motions to intervene and comments due 16:30 Eastern")
        self.assertEqual(w("Comments are due by 12:00 a.m. on November 9, 2026.", DAY), "comments due 00:00")

    def test_other_sentences_as_written_in_one_clause(self):
        w = roundup.deadline_words
        self.assertEqual(w("The final rule is effective on November 9, 2026.", DAY), "the final rule is effective on November 9, 2026")
        self.assertEqual(w("Comments are due by midnight EST on November 9, 2026.", DAY), "comments are due by midnight EST on November 9, 2026")
        self.assertEqual(w("FERC will hold a technical conference on November 9, 2026.", DAY), "FERC will hold a technical conference on November 9, 2026")
        # a sentence whose comment date is not the item's day is left as written
        self.assertEqual(w("Comments are due on November 20, 2026.", DAY), "comments are due on November 20, 2026")

    def test_no_dash(self):
        for p in (__file__, roundup.__file__):
            with open(p, encoding="utf-8") as f:
                src = f.read()
            self.assertNotIn(EM, src)
            self.assertNotIn(EN, src)


if __name__ == "__main__":
    unittest.main()
