"""Session 10219 (chain 710, the conditions audit, finding 10): /conditions calls CAISO's megawatts "out of service",
and the table sums every curtailment CAISO's report lists, derates filed as forced (ambient conditions, transmission
induced, fuel) included (docs/methods/grid_outages.md, decision 3), while SPP's figure is generation on outage. Words
only: CAISO's two outage charts say what the figure holds. docs/reviews/conditions-model-audit-2026-11-26.md.
"""
import os
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def src(*p):
    with open(os.path.join(ROOT, *p), encoding="utf-8") as fh:
        return fh.read()


class CaisosFigureHoldsDerates(unittest.TestCase):
    def test_the_outage_note_says_derates_are_summed(self):
        self.assertIn("derates the operator files as forced (ambient conditions, transmission induced, fuel)", src("docs", "methods", "grid_outages.md"))

    def test_caisos_charts_say_it(self):
        s = src("site", "app", "conditions", "page.tsx")
        self.assertEqual(s.count('why={`${src("out")}${f.op === "caiso" ? `. ${CAISO_OUT_WORDS}` : ""}`} />}>'), 2)
        self.assertNotIn('why={src("out")} />', s)
        self.assertIn("megawatts unavailable, not only plants out of service", s)
        self.assertNotIn("export const CAISO_OUT_WORDS", s)

    def test_the_note_says_it(self):
        self.assertIn("CAISO's is every curtailment its report lists, derates included", src("docs", "methods", "grid_conditions.md"))


if __name__ == "__main__":
    unittest.main()
