"""Audit of the company database, finding 7 (session 10228, docs/reviews/companies-model-audit-2026-11-26.md): the
deals page's companies tab cites energy_companies with the note "Found by warehouse/thesis/build.py from public web
sources", but 541 of its 562 rows (25 November 2026) were seeded from the deals' parties by
warehouse/companies/seed_from_deals.py and are marked "from deals; not yet researched"; 21 were researched. The tab's own
paragraph above says both; the note under the table says one.

1. energy_companies (the copy in git) holds more rows seeded from the deals than researched rows, and its header names
   both scripts. Passes on main.
2. The fix on this branch, words only: the note names both sources and which rows each wrote. No figure moves. Fails
   on main."""
import csv
import io
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


class TheTabsSourceNote(unittest.TestCase):
    def test_most_rows_are_seeded_from_the_deals(self):
        text = src("warehouse", "output", "energy_companies.csv")
        head = [ln for ln in text.splitlines() if ln.startswith("#")]
        self.assertTrue(any("seed_from_deals.py" in ln and "thesis/build.py" in ln for ln in head))
        rows = list(csv.DictReader(io.StringIO("\n".join(ln for ln in text.splitlines() if not ln.startswith("#")))))
        seeded = sum(1 for r in rows if r["confidence_note"].startswith("from deals"))
        self.assertGreater(seeded, len(rows) - seeded)

    def test_the_note_names_both(self):
        view = src("site", "app", "companies", "view.tsx")
        self.assertNotIn('note="Found by warehouse/thesis/build.py from public web sources', view)
        self.assertIn("are the deals\\' parties, seeded by warehouse/companies/seed_from_deals.py from the deal tracker\\'s rows", view)
        self.assertIn("the others were researched by warehouse/thesis/build.py from the public web sources each row links", view)


if __name__ == "__main__":
    unittest.main()
