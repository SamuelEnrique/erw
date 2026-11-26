"""Audit of Automated Analysis, finding 13 (session 10204, docs/reviews/analysis-model-audit-2026-11-26.md): every deep
hunt measure in dollars says its dollars are nominal.

Of the 34 candidates in a dollar unit under warehouse/analysis/findings/deep/, 32 said "nominal" in their limits;
prices.py's hub_basis and spark_spread did not. Their limits now begin "Nominal dollars, not adjusted for inflation".
Words only: no measure, unit or figure changes; a draft already built keeps its words until it is rebuilt.
Fails on main, passes on the branch.

No table, no request, no model call; the environment is read, never set."""
import glob
import importlib
import os
import sys
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEEP = os.path.join(ROOT, "warehouse", "analysis", "findings", "deep")
SKIP = {"__init__", "builder", "check", "check_cards", "check_do", "rank", "redraw"}


class DollarsSayNominal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for p in (os.path.join(ROOT, "warehouse", "analysis", "findings"), DEEP, os.path.join(ROOT, "warehouse")):
            if p not in sys.path:
                sys.path.insert(0, p)

    def candidates(self):
        out = []
        for path in sorted(glob.glob(os.path.join(DEEP, "*.py"))):
            name = os.path.basename(path)[:-3]
            if name in SKIP:
                continue
            m = importlib.import_module(name)
            out += [(name, P) for P in getattr(m, "CANDIDATES", None) or []]
        return out

    def test_every_dollar_candidate_says_nominal(self):
        usd = [(m, P) for m, P in self.candidates() if "USD" in str(P.get("unit", ""))]
        self.assertGreaterEqual(len(usd), 30)
        missing = [f"{m}.{P['name']}" for m, P in usd if "nominal" not in str(P.get("limits", "")).lower()]
        self.assertEqual(missing, [])

    def test_the_two_measures_are_unchanged(self):
        import prices
        got = {P["name"]: P for P in prices.CANDIDATES}
        self.assertEqual(got["hub_basis"]["unit"], "USD per MWh")
        self.assertEqual(got["spark_spread"]["unit"], "USD per MWh")

    def test_no_em_dash(self):
        for p in ("warehouse/analysis/findings/deep/prices.py", "tests/test_audit_analysis_13.py"):
            with open(os.path.join(ROOT, p), encoding="utf-8") as f:
                self.assertNotIn(chr(0x2014), f.read())


if __name__ == "__main__":
    unittest.main()
