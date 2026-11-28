"""Audit of /equities, finding 7 (session 11403, docs/reviews/equities-model-audit-2026-11-28.md): the two weightings'
written rule (docs/state/page_files_equities.md) leaves open what an equity analyst would ask first, and on today's
files it would build lines that are not what their names say.

- "the mean of its companies' daily returns": the close's return or the adjusted close's (dividends): not said, and
  for utilities and partnerships the difference is most of the return.
- "market value is close times the latest shares outstanding filed": the balance-sheet count only. At the newest
  period 107 of the 243 companies with filed figures have none, and 64 companies have no filed figures at all: the
  "larger companies count more" line would hold 136 of 307 companies (44 percent), and in some segments far fewer.
- Five companies are listed by a preferred share (CMS-PB, ETI-P, PCG-PE, PHXE-P, SCE-PG): their close would be a
  preferred share's price, not the common's, and four are subsidiaries of a listed parent.
- 104 of the 307 companies sit in two segments (finding 3), and two businesses are listed twice (finding 2).

The test measures these on main's files (it passes on main). Each is a rule for Samuel's ruling before any line is
built; nothing is changed."""
import json
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
D = os.path.join(ROOT, "site", "data", "equities")
CONTRACT = os.path.join(ROOT, "docs", "state", "page_files_equities.md")


class WeightingRuleOpen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(D, "index.json"), encoding="utf-8") as f:
            cls.cos = json.load(f)["companies"]

    def test_return_not_said(self):
        text = open(CONTRACT, encoding="utf-8").read()
        self.assertIn("the mean of its companies' daily returns chained", text)
        self.assertNotRegex(text, r"(?i)total return|dividends? (are|is) (re)?invested|return of the adjusted close")

    def test_value_line_would_hold_under_half(self):
        withshares = [c for c in self.cos if c.get("newest_filed") and c["newest_filed"]["shares_outstanding"]]
        shown = [c for c in self.cos if c["fundamentals_status"] == "shown"]
        self.assertEqual(len(self.cos), 307)
        self.assertEqual(len(shown), 243)
        self.assertEqual(len(shown) - len(withshares), 107)
        self.assertEqual(len(withshares), 136)
        out = {}
        for sid in ("integrated_oil_gas", "exploration_production", "midstream_pipelines", "oilfield_services",
                    "regulated_utilities", "independent_power"):
            cs = [c for c in self.cos if sid in c["segments"]]
            out[sid] = sum(1 for c in cs if c in withshares) / len(cs)
        self.assertLess(out["integrated_oil_gas"], 0.25)
        print("\nshare of each segment with a balance-sheet share count at its newest period: "
              + "; ".join(f"{k} {v * 100:.0f} percent" for k, v in out.items()))

    def test_preferred_listings_and_two_segments(self):
        pref = sorted(c["ticker"] for c in self.cos if "-" in c["ticker"])
        self.assertEqual(pref, ["CMS-PB", "ETI-P", "PCG-PE", "PHXE-P", "SCE-PG"])
        self.assertEqual(sum(1 for c in self.cos if len(c["segments"]) > 1), 104)


if __name__ == "__main__":
    unittest.main()
