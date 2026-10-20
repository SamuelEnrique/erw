"""Session 335 (the chain of 20 October 2026, night): /learn/bill finished to the five tools' standard, lighter (its
method note, its Method link, its one table to download), and the chain's night note. Energy Research Warehouse (ERW)."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DASH = chr(0x2014)


def src(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


class TheBill(unittest.TestCase):
    def test_the_page_links_its_note_and_offers_its_table(self):
        page = src("site", "app", "learn", "bill", "page.tsx")
        self.assertIn('<Link href="/data/methods/bill">Method</Link>', page)
        self.assertIn("<TableDownloads tables={[M]} />", page)
        self.assertIn('const M = "cost_of_power_monthly";', page)

    def test_the_note_says_what_the_page_and_its_file_hold(self):
        note = src("docs", "methods", "bill.md")
        self.assertIn("every default home uses 600 kWh a month", note)
        rules = json.loads(src("site", "data", "bill_rules.json"))
        self.assertEqual({b["defaults"]["kwh"] for b in rules["bills"].values()}, {600})
        self.assertIn("const wUsd = w ? (bills[s].kwh * w.row.value) / 1000 : null;", src("site", "app", "learn", "bill", "page.tsx"))
        self.assertIn('export const BILL_KEYS = ["CA", "SCE", "SDGE", "TX", "TXC"] as const;', src("site", "lib", "bill.ts"))


class NoEmDash(unittest.TestCase):
    def test_none_in_what_the_session_wrote(self):
        for parts in (("site", "app", "learn", "bill", "page.tsx"), ("docs", "methods", "bill.md"), ("tests", "test_session335.py")):
            self.assertNotIn(DASH, src(*parts), "/".join(parts))


if __name__ == "__main__":
    unittest.main()
