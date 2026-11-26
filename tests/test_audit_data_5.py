"""Audit of the data pages, finding 6 (session 10233, docs/reviews/data-model-audit-2026-11-26.md): the data standard's
license rule, drawn on /data/standard, says "PJM data are `internal`; every other source is `public`. A table is
`internal` if any of its sources is." The source registry (warehouse/metadata/sources.csv) holds many internal sources
that are not PJM (the news outlets, among others); news_index is public with internal sources, by its own header line
(Decision 16 (d)); and since 21 October 2026 public tables are held for a license (license_status.csv), which the rule
did not mention.

1. The registry's internal sources are mostly not PJM's; news_index is public and has internal sources; the hold has
   rows. Passes on main.
2. The fix on this branch, words only: the rule names the other internal sources, the declared exception and the hold.
   No table's license moves. Fails on main."""
import csv
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as f:
        return f.read()


def rows(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def flat(s):
    return " ".join(s.split())


class TheLicenseRuleNamesMoreThanPJM(unittest.TestCase):
    def test_the_registry_and_the_hold(self):
        src_ = rows("warehouse", "metadata", "sources.csv")
        internal = [r for r in src_ if r["license"] == "internal"]
        not_pjm = [r for r in internal if "pjm" not in (r["source"] + r["publisher"]).lower()]
        self.assertGreater(len(not_pjm), len(internal) - len(not_pjm))
        cov = {r["table"]: r for r in rows("warehouse", "metadata", "coverage.csv")}
        self.assertEqual(cov["news_index"]["license"], "public")
        self.assertTrue(any("news_index" in r["tables"].split(";") for r in internal))
        self.assertGreater(len(rows("warehouse", "metadata", "license_status.csv")), 0)

    def test_the_standard_says_so(self):
        std = flat(src("docs", "datastandard.md"))
        self.assertNotIn("PJM data are `internal`; every other source is `public`. A table is `internal` if any of its sources is.", std)
        self.assertIn("PJM data are `internal`, and so is every source whose terms do not allow the ERW to redistribute it, third-party news text among them (Decision 15)", std)
        self.assertIn("unless the table declares its own license in a header line (Decision 16 (d): `news_index` is public", std)
        self.assertIn("Since 21 October 2026 a public table whose publisher's own page asks for permission or a license is also held", std)


if __name__ == "__main__":
    unittest.main()
