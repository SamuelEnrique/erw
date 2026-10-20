"""Session 378: the licensing sweep to the point of Samuel's signature. docs/licenses.md gives every table of coverage.csv
one verdict word (public, internal, unsettled), a table flagged internal is never called public, the four letters are
drafts naming their tables, and the prices for the letter of intent close the document."""

import csv
import os
import re
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import licenses as L  # noqa: E402

DOC = os.path.join(ROOT, "docs", "licenses.md")
LETTERS = os.path.join(ROOT, "docs", "reviews", "licenses")


def doc():
    with open(DOC, encoding="utf-8") as f:
        return f.read()


class Verdicts(unittest.TestCase):
    def test_every_table_has_one_word(self):
        with open(os.path.join(ROOT, "warehouse", "metadata", "coverage.csv"), encoding="utf-8", newline="") as f:
            cov = {r["table"]: r["license"] for r in csv.DictReader(f)}
        rows = {}
        for ln in doc().split("## Every table", 1)[1].split("\n## ", 1)[0].splitlines():
            m = re.match(r"\| `([a-z0-9_]+)` \|.*\| (public|internal|unsettled) \|$", ln)
            if m:
                rows[m.group(1)] = m.group(2)
        self.assertEqual(set(rows), set(cov))
        for t, v in rows.items():
            if cov[t] != "public":
                self.assertEqual(v, "internal", t)

    def test_the_rule(self):
        self.assertEqual(L.erw_verdict("internal", "agrees"), "internal")
        self.assertEqual(L.erw_verdict("public", "agrees"), "public")
        self.assertEqual(L.erw_verdict("public", "not settled"), "unsettled")
        self.assertEqual(L.erw_verdict("public", "ruled: license needed from 2026-10-21"), "unsettled")

    def test_the_hourly_node_table_is_ruled_internal(self):
        self.assertIn("ercot_node_prices_hourly", L.RULED_INTERNAL)
        self.assertIn("- **0 tables are flagged internal where the sentence read allows them.**", doc())


class Letters(unittest.TestCase):
    def test_four_drafts_not_sent(self):
        for key, tables in (("nyiso", ["nyiso_dam_zone_prices", "nyiso_as_prices"]), ("spp", ["spp_as_prices"]),
                            ("pjm", ["pjm_rpm_capacity_prices"]), ("miso", ["miso_interconnection_queue"])):
            with open(os.path.join(LETTERS, f"{key}-permission-letter.md"), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("Nothing here was sent", text)
            self.assertIn("Samuel [surname]", text)
            for t in tables:
                self.assertIn(f"`{t}`", text)
            self.assertNotIn(chr(0x2014), text)

    def test_the_prices_close_the_document(self):
        text = doc()
        i = text.index("## The publishers' prices, for the letter of intent (session 378)")
        self.assertNotIn("\n## ", text[i + 5:])
        for key in ("nyiso", "spp", "pjm", "miso"):
            self.assertIn(f"docs/reviews/licenses/{key}-permission-letter.md", text[i:])


if __name__ == "__main__":
    unittest.main()
