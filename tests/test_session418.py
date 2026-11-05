"""Session 418: the Digest of 21 October 2026, checked (session 402's two waiting checks).

What is held here, without a network and without a database: the eleven figures session 418 traced (nine against the
Supabase live set, the chart's two against the local CSVs) are the Digest's own, as docs/digest/2026-10-21.md prints
them; the report and session 402's "Finished" section name each check with its exit code; neither file holds an em
or en dash. The recomputation itself is scripts/check_digest.py's, tested by tests/test_session402.py.
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIGEST = os.path.join(ROOT, "docs", "digest", "2026-10-21.md")
REPORT = os.path.join(ROOT, "archive", "sessions", "SESSION_418_REPORT.md")
R402 = os.path.join(ROOT, "archive", "sessions", "SESSION_402_REPORT.md")

# the figures check_digest.py traced on 21 October 2026, 16:28 UTC (runs/chain_021/s418/check_digest*.out)
TRACED = {
    "ERCOT HB_NORTH day-ahead": "28.38",
    "CAISO TH_SP15_GEN-APND day-ahead": "45.01",
    "NYISO N.Y.C. day-ahead": "49.25",
    "SPP SPPSOUTH_HUB day-ahead": "23.33",
    "ISO-NE .H.INTERNAL_HUB day-ahead": "40.64",
    "SPP SPPNORTH_HUB real-time": "276.41",
    "Henry Hub": "3.22",
    "WTI Cushing": "101.91",
    "Brent": "126.55",
    "chart value": "99.90",
    "chart old record": "91.70",
}


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


@unittest.skipUnless(os.path.exists(DIGEST), "the Digest of 21 October is not in this checkout")
class TheDigestOf21October(unittest.TestCase):
    def test_every_traced_figure_is_the_digests_own(self):
        text = read(DIGEST)
        for name, v in TRACED.items():
            self.assertIn(v, text, name)

    def test_eleven_figures(self):
        self.assertEqual(len(TRACED), 11)


class TheRecords(unittest.TestCase):
    def test_no_dashes(self):
        for p in (REPORT, R402):
            t = read(p)
            self.assertNotIn("—", t, p)
            self.assertNotIn("–", t, p)

    def test_the_report_names_both_checks_with_exit_codes(self):
        t = read(REPORT)
        self.assertIn("check_digest.py --supabase --date 2026-10-21", t)
        self.assertIn("CHECK_VALUES_PAGES=/digest", t)
        self.assertRegex(t, r"exit[ =]0")

    def test_402_records_the_check_under_finished(self):
        t = read(R402)
        head, _, tail = t.partition("## Finished on the combined branch (21 October)")
        self.assertTrue(tail, "402's Finished section is there")
        self.assertIn("Session 418", tail)
        self.assertIn("check_digest.py --supabase --date 2026-10-21", tail)


if __name__ == "__main__":
    unittest.main()
