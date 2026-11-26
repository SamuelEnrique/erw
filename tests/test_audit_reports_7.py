"""Session 10232, the report library audit (docs/reviews/reports-model-audit-2026-11-26.md), finding 7.

The AI gigawatts draft's methods appendix (docs/reports/ai_gigawatts_methods.md) said the year was "the latest twelve
complete months that every price input holds" (the builder asks only for a row a month, and ISO-NE's hub priced 8,160
of the year's 8,760 hours); it said the headline import share was the pair sums (the builder makes it EIA's balance);
it named a check, ng_check_import_share_pct, the builder does not write, and left out six measures the draft prints.
The fix is words only: every measure the draft reads is in the note, and each row says what the builder does.
"""
import os
import re
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
NOTE = os.path.join(ROOT, "docs", "reports", "ai_gigawatts_methods.md")
PAGE = os.path.join(ROOT, "site", "app", "reports", "draft", "ai-gigawatts", "page.tsx")
BUILDER = os.path.join(ROOT, "warehouse", "derived", "ai_power_regions.py")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


class TheNoteSaysWhatTheBuilderDoes(unittest.TestCase):
    def test_every_measure_the_draft_reads_is_in_the_note(self):
        page, note = read(PAGE), read(NOTE)
        names = sorted(set(re.findall(r'get\(g\.id, "([a-z0-9_]+)"\)', page)))
        self.assertGreater(len(names), 20)
        missing = [n for n in names if f"`{n}`" not in note]
        self.assertEqual(missing, [], f"measures the draft prints that the note does not name: {missing}")

    def test_no_measure_the_builder_does_not_write(self):
        note, builder = read(NOTE), read(BUILDER)
        self.assertNotIn("ng_check_import_share_pct", note)
        self.assertNotIn("ng_check", builder)

    def test_the_headline_import_share_is_the_balance(self):
        note = read(NOTE)
        row = [ln for ln in note.splitlines() if ln.startswith("| Net import share, the headline")]
        self.assertEqual(len(row), 1)
        self.assertIn("EIA's own balance", row[0])
        self.assertIn("(demand less net generation) over demand", row[0])

    def test_the_year_is_not_called_complete(self):
        note = read(NOTE)
        self.assertNotIn("the latest twelve complete months that every price input holds", note.replace(
            '(session 10232: this line said "the latest twelve complete months", which the code does not ask)', ""))
        self.assertIn("They are not all complete months", note)
        self.assertIn('WINDOW = ("2025-09-01", "2026-09-01")', read(BUILDER))

    def test_the_events_are_as_built(self):
        self.assertIn("an event studied since (`cold_2026`, added 19 October 2026) is not in it until the table is rebuilt", read(NOTE))

    def test_no_em_dash(self):
        self.assertNotIn(chr(0x2014), read(NOTE))
        self.assertNotIn(chr(0x2014), read(__file__))


if __name__ == "__main__":
    unittest.main()
